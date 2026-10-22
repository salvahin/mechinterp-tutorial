"""Generator for NB5 (Audit: can we trust the judge?) and its instructor cache-preparation notebook.

Run:  python3 notebooks/src/build_nb5.py

Emits
  notebooks/student/NB5_judge_confidence.ipynb
  notebooks/solutions/NB5_judge_confidence_solutions.ipynb
  notebooks/instructor/NB5_prepare_cache.ipynb

The judge prompt / scoring code (JUDGE_SRC) and the task table (TASKS_SRC) are defined once here and
injected into both the instructor notebook and the student live cell, so the cached verdicts and the
live verdicts come from exactly the same code.
"""
import sys
from pathlib import Path

import nbformat
from nbformat.v4 import new_notebook, new_markdown_cell, new_code_cell

sys.path.insert(0, str(Path(__file__).parent))
from nbgen import md, code, exercise, build, PINS, SLIDES_LINK, ROOT  # noqa: E402

# Extra pins tested on the build machine for NB5 (pip show)
NB5_PINS = {
    "transformers": "5.20.2",
    "huggingface_hub": "2.2.0",
    "scikit-learn": PINS["scikit-learn"],
    "datasets": PINS["datasets"],
}

# --------------------------------------------------------------------------------------------
# Single source: placeholders the presenters must fill in
# --------------------------------------------------------------------------------------------
CACHE_CONSTANTS = '''
# ─── TODO (presenters): publish the cache, then fill these in ─────────────────────────────
CACHE_REPO   = "TODO-your-hf-user/micai2026-nb5-judge-cache"   # HF *dataset* repo with cache_<model>.npz
FALLBACK_URL = "https://raw.githubusercontent.com/salvahin/mechinterp-tutorial/main/data/nb5/cache_qwen0.5b.npz"
# ──────────────────────────────────────────────────────────────────────────────────────────
'''

# --------------------------------------------------------------------------------------------
# Single source: tasks (LegalBench contract_nli_*), assertions, held-out assertions
# --------------------------------------------------------------------------------------------
TASKS_SRC = r'''
# LegalBench (Guha et al., NeurIPS 2023) contract_nli_* tasks on HF `nguha/legalbench`, all CC BY 4.0,
# derived from ContractNLI (Koreeda & Manning, 2021). One assertion (= our "rule") per task.
# Assertion text copied from each task's README (LegalBench GitHub); "ome" -> "some" typo fixed.
ASSERTIONS = {
    "confidentiality_of_agreement": "the Receiving Party shall not disclose the fact that Agreement was agreed or negotiated",
    "explicit_identification": "all Confidential Information shall be expressly identified by the Disclosing Party",
    "inclusion_of_verbally_conveyed_information": "Confidential Information may include verbally conveyed information",
    "limited_use": "the Receiving Party shall not use any Confidential Information for any purpose other than the purposes stated in Agreement",
    "no_licensing": "the Agreement shall not grant Receiving Party any right to Confidential Information",
    "notice_on_compelled_disclosure": "the Receiving Party shall notify Disclosing Party in case Receiving Party is required by law, regulation or judicial process to disclose any Confidential Information",
    "permissible_acquirement_of_similar_information": "the Receiving Party may acquire information similar to Confidential Information from a third party",
    "permissible_copy": "the Receiving Party may create a copy of some Confidential Information in some circumstances",
    "permissible_development_of_similar_information": "the Receiving Party may independently develop information similar to Confidential Information",
    "permissible_post-agreement_possession": "the Receiving Party may retain some Confidential Information even after the return or destruction of Confidential Information",
    "return_of_confidential_information": "the Receiving Party shall destroy or return some Confidential Information upon the termination of Agreement",
    "sharing_with_employees": "the Receiving Party may share some Confidential Information with some of Receiving Party's employees",
    "sharing_with_third-parties": "the Receiving Party may share some Confidential Information with some third-parties (including consultants, agents and professional advisors)",
    "survival_of_obligations": "some obligations of Agreement may survive termination of Agreement",
}
# Held out entirely (never seen by the probe): stands in for "a new 29110 process" -> distribution shift
HELDOUT = ["notice_on_compelled_disclosure", "return_of_confidential_information", "survival_of_obligations"]
'''

# --------------------------------------------------------------------------------------------
# Single source: judge prompt and scoring
# --------------------------------------------------------------------------------------------
JUDGE_SRC = r'''
import re
import numpy as np
import torch

JUDGE_MODELS = {
    # name: HF id, residual-stream layers we cache (index into hidden_states: 0 = embeddings)
    "gemma3-4b": dict(hf_id="google/gemma-3-4b-it", layers=list(range(2, 35, 2))),     # 34 blocks -> 17 layers
    "qwen0.5b":  dict(hf_id="Qwen/Qwen2.5-0.5B-Instruct", layers=[3, 6, 9, 12, 15, 18, 21, 24]),  # 24 blocks
}
SYSTEM_PROMPT = "You are a compliance auditor."

def judge_messages(assertion, excerpt):
    """Rule = LegalBench assertion, evidence = contract excerpt. One chat turn, answer = next token."""
    return [{"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Contract clause:\n{excerpt}\n\n"
                                        f"Does this clause state that {assertion}? Answer Yes or No."}]

CONF_QUESTION = "How confident are you that your answer is correct? Reply with only a number from 0 to 100."

def load_judge(choice, device, dtype=None):
    from transformers import AutoTokenizer
    hf_id = JUDGE_MODELS[choice]["hf_id"]
    tok = AutoTokenizer.from_pretrained(hf_id)
    tok.padding_side = "left"                      # last prompt token sits at position -1 for every row
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    if dtype is None:   # bf16 where the GPU supports it natively (L4/A100); fp16 on a T4; bf16 on CPU (half the RAM)
        if device == "cuda":
            dtype = torch.bfloat16 if torch.cuda.is_bf16_supported(including_emulation=False) else torch.float16
        else:
            dtype = torch.bfloat16
    if choice.startswith("gemma"):
        from transformers import Gemma3ForConditionalGeneration as Cls   # the 4B IT checkpoint is multimodal
    else:
        from transformers import AutoModelForCausalLM as Cls
    model = Cls.from_pretrained(hf_id, dtype=dtype).to(device).eval()
    yes_id = tok.encode("Yes", add_special_tokens=False)[0]
    no_id = tok.encode("No", add_special_tokens=False)[0]
    return model, tok, yes_id, no_id

def _encode(tok, conversations, device):
    texts = [tok.apply_chat_template(c, tokenize=False, add_generation_prompt=True) for c in conversations]
    return tok(texts, return_tensors="pt", padding=True, add_special_tokens=False).to(device)

@torch.no_grad()
def judge_batch(model, tok, yes_id, no_id, assertions, excerpts, layers=None):
    """One forward pass, no generation. Returns p_yes = P(Yes)/(P(Yes)+P(No)) at the answer position,
    the probability mass on {Yes, No}, and (optionally) the residual stream at the last prompt token."""
    enc = _encode(tok, [judge_messages(a, x) for a, x in zip(assertions, excerpts)], model.device)
    out = model(**enc, output_hidden_states=layers is not None, logits_to_keep=1)
    lp = out.logits[:, -1].float().log_softmax(-1)
    p_yes = torch.sigmoid(lp[:, yes_id] - lp[:, no_id]).cpu().numpy()
    mass = (lp[:, yes_id].exp() + lp[:, no_id].exp()).cpu().numpy()
    hidden = None
    if layers is not None:
        hidden = torch.stack([out.hidden_states[l][:, -1] for l in layers], 1).float().cpu().numpy()
    return p_yes, mass, hidden

@torch.no_grad()
def verbalized_confidence(model, tok, assertions, excerpts, verdicts, max_new_tokens=4):
    """Second turn: the judge's own verdict is in context; ask for 0-100 confidence (greedy)."""
    convs = [judge_messages(a, x) + [{"role": "assistant", "content": v},
                                     {"role": "user", "content": CONF_QUESTION}]
             for a, x, v in zip(assertions, excerpts, verdicts)]
    enc = _encode(tok, convs, model.device)
    gen = model.generate(**enc, max_new_tokens=max_new_tokens, do_sample=False, pad_token_id=tok.pad_token_id)
    raw = tok.batch_decode(gen[:, enc["input_ids"].shape[1]:], skip_special_tokens=True)
    vals = []
    for r in raw:
        m = re.search(r"\d{1,3}", r)
        vals.append(min(100.0, float(m.group())) / 100 if m else np.nan)
    return np.array(vals, dtype=np.float32), [r.strip() for r in raw]

# Grounding check helpers ------------------------------------------------------------------
IRRELEVANT_CLAUSES = [   # invented boilerplate, unrelated to any of the assertions
    "This Agreement shall be governed by and construed in accordance with the laws of the State of New York.",
    "All notices under this Agreement shall be in writing and delivered to the addresses set out above.",
    "This Agreement may be executed in counterparts, each of which shall be deemed an original.",
]

def split_segments(text):
    """Split an excerpt into sentence/clause segments (on . ; and enumerations like (a), (ii))."""
    parts = re.split(r"(?<=[.;])\s+|\s+(?=\(?[a-z0-9ivx]{1,4}\)\s)", text.strip())
    return [p.strip() for p in parts if len(p.strip()) > 3]

def truncate(text, max_chars):
    text = " ".join(str(text).split())
    if len(text) <= max_chars:
        return text
    return text[:max_chars].rsplit(" ", 1)[0] + " ..."
'''

# ============================================================================================
# Instructor notebook: NB5_prepare_cache.ipynb
# ============================================================================================
P5 = NB5_PINS
instructor_cells = [
    md(f"""
# NB5 · Instructor: prepare the judge cache

**MICAI 2026 · Mechanistic Interpretability, Hands-on** · Block 5 *Audit: can we trust the judge?* (Víctor Macías-Terrón)
**Who runs this:** a presenter, **once, before the session** (not the participants).
**Runtime:** Colab **T4 GPU** for `gemma3-4b` (≈ 10–20 min including the ≈ 8 GB download; see the timing printouts). `qwen0.5b` runs on CPU (measured: 32 min on 2 shared cores, of which 16 min is the verbalized-confidence generation).

**What it does.** Runs the LLM judge over a fixed selection of LegalBench `contract_nli_*` examples and saves a compact cache that NB5 loads, so participants need no GPU:

| field | meaning |
|---|---|
| `uid, task, assertion, excerpt, split, gold` | the example; `split ∈ {{train, cal, test, shift}}` (`shift` = held-out assertions) |
| `p_yes`, `yes_no_mass` | next-token P(Yes)/(P(Yes)+P(No)) at the answer position; mass on {{Yes, No}} (sanity check) |
| `verbal_conf`, `verbal_raw` | the judge's own 0–100 confidence in its verdict (second, short generation) |
| `hidden`, `layers` | residual stream at the last prompt token, selected layers, float16 `[N, L, d_model]` |
| `g_*` | precomputed **grounding check** for confident *Yes* verdicts (evidence replaced / one segment removed) |

**Steps for the presenters**
1. Runtime → Change runtime type → **T4 GPU**. Add your HF token as Colab secret `HF_TOKEN` (accept the Gemma 3 licence on its model page first).
2. Fill in `CACHE_REPO` below (a **dataset** repo you can write to, e.g. `your-user/micai2026-nb5-judge-cache`). Leave `UPLOAD = True`.
3. Run all. Check the sanity printout (judge accuracy should be well above 50 %, Yes/No mass close to 1, no NaNs).
4. Put the same `CACHE_REPO` string in the student notebook generator (`notebooks/src/build_nb5.py`, `CACHE_CONSTANTS`) and rebuild; make the repo **public** so participants do not need a token to read it.

Alternative without HF: download the `.npz` (Files panel) and host it on Google Drive with a public direct-download link; put that link in `FALLBACK_URL`.
"""),
    code(f"""
%pip install -q transformers=={P5['transformers']} huggingface_hub=={P5['huggingface_hub']} datasets=={P5['datasets']}
"""),
    md("## 0 · Configuration"),
    code(CACHE_CONSTANTS + '''
MODEL_CHOICE = "gemma3-4b"        # session judge (T4).  "qwen0.5b" = ungated fallback, runs on CPU
UPLOAD = not CACHE_REPO.startswith("TODO")
N_PER_ASSERTION = 40              # balanced Yes/No where the data allows -> 540 examples (same selection for both models)
SEED = 2026
MAX_EXCERPT_CHARS = 1000          # long excerpts are truncated at a word boundary (keeps prompts < ~350 tokens)
DO_VERBAL = True                  # verbalized confidence (second short generation)
N_GROUNDING = 40                  # most confident Yes verdicts (test + shift) for the grounding check
OUT_DIR = "nb5_cache"
'''),
    code(r'''
import os, sys, time, json, hashlib, importlib.util
import numpy as np, pandas as pd, torch

IN_COLAB = "google.colab" in sys.modules or importlib.util.find_spec("google.colab") is not None
device = "cuda" if torch.cuda.is_available() else "cpu"
if device == "cpu":
    torch.set_num_threads(max(1, os.cpu_count() or 1))
BATCH_SIZE = 8 if device == "cuda" else 4
print("device:", device, "| model:", MODEL_CHOICE, "| batch:", BATCH_SIZE)
if MODEL_CHOICE.startswith("gemma") and device == "cpu":
    print("⚠ Gemma 3 4B on CPU is very slow (and needs ~10 GB RAM). Use a T4 runtime.")
os.makedirs(OUT_DIR, exist_ok=True)
'''),
    md("## 1 · Hugging Face login (Gemma 3 is gated; uploading needs write access)"),
    code(r'''
HF_TOKEN = None
if IN_COLAB:
    try:
        from google.colab import userdata
        HF_TOKEN = userdata.get("HF_TOKEN")
    except Exception as e:
        print(f"No usable Colab secret HF_TOKEN ({type(e).__name__}).")
if not HF_TOKEN:
    from huggingface_hub import get_token
    HF_TOKEN = os.environ.get("HF_TOKEN") or get_token()
if not HF_TOKEN and (MODEL_CHOICE.startswith("gemma") or UPLOAD):
    from huggingface_hub import notebook_login
    notebook_login()
    from huggingface_hub import get_token
    HF_TOKEN = get_token()
if HF_TOKEN:
    from huggingface_hub import login
    login(token=HF_TOKEN, add_to_git_credential=False)
print("token:", "found" if HF_TOKEN else "none (fine for qwen0.5b without upload)")
'''),
    md("## 2 · Task table and example selection"),
    code(TASKS_SRC),
    code(JUDGE_SRC),
    code(r'''
from datasets import load_dataset

def doc_split(doc):
    """Split by NDA (document_name), not by row: the same NDA appears under many assertions."""
    h = int(hashlib.md5(doc.encode()).hexdigest(), 16) % 4
    return ["train", "train", "cal", "test"][h]

rows = []
for task, assertion in ASSERTIONS.items():
    ds = load_dataset("nguha/legalbench", f"contract_nli_{task}", split="test").to_pandas()
    rng = np.random.default_rng(SEED + sum(map(ord, task)))
    yes, no = ds[ds.answer == "Yes"], ds[ds.answer == "No"]
    n_yes = min(len(yes), N_PER_ASSERTION // 2)
    n_no = min(len(no), N_PER_ASSERTION - n_yes)
    pick = pd.concat([yes.iloc[rng.permutation(len(yes))[:n_yes]], no.iloc[rng.permutation(len(no))[:n_no]]])
    for _, r in pick.iterrows():
        rows.append(dict(uid=f"{task}:{r['index']}", task=task, assertion=assertion,
                         excerpt=truncate(r["text"], MAX_EXCERPT_CHARS), document=r["document_name"],
                         gold=int(r["answer"] == "Yes"),
                         split="shift" if task in HELDOUT else doc_split(r["document_name"])))
df = pd.DataFrame(rows).reset_index(drop=True)
df.to_csv(f"{OUT_DIR}/selection.csv", index=False)
print(len(df), "examples")
print(df.groupby("split").agg(n=("gold", "size"), yes_rate=("gold", "mean"), tasks=("task", "nunique")))
'''),
    md("## 3 · Load the judge and sanity-check it"),
    code(r'''
t0 = time.time()
model, tok, YES_ID, NO_ID = load_judge(MODEL_CHOICE, device)
LAYERS = JUDGE_MODELS[MODEL_CHOICE]["layers"]
print(f"loaded {JUDGE_MODELS[MODEL_CHOICE]['hf_id']} in {time.time()-t0:.0f}s; dtype={model.dtype}; caching layers {LAYERS}")
print("Yes/No token ids:", YES_ID, NO_ID, tok.convert_ids_to_tokens([YES_ID, NO_ID]))
print(tok.apply_chat_template(judge_messages("<RULE>", "<EVIDENCE>"), tokenize=False, add_generation_prompt=True))

p, mass, h = judge_batch(model, tok, YES_ID, NO_ID, df.assertion[:4].tolist(), df.excerpt[:4].tolist(), LAYERS)
print("p_yes", p.round(3), "| Yes/No mass", mass.round(3), "| hidden", h.shape, "finite:", np.isfinite(h).all())
if not (np.isfinite(p).all() and np.isfinite(h).all()) and device == "cuda":
    # Gemma models can overflow float16 activations; bfloat16 has float32's range (emulated, slower, on a T4)
    print("⚠ non-finite values in float16 → reloading in bfloat16")
    del model; torch.cuda.empty_cache()
    model, tok, YES_ID, NO_ID = load_judge(MODEL_CHOICE, device, dtype=torch.bfloat16)
    p, mass, h = judge_batch(model, tok, YES_ID, NO_ID, df.assertion[:4].tolist(), df.excerpt[:4].tolist(), LAYERS)
    print("p_yes", p.round(3), "| finite:", np.isfinite(h).all())
assert np.isfinite(p).all() and np.isfinite(h).all(), "Non-finite judge outputs: try dtype=torch.float32 (needs more memory)"
'''),
    md("## 4 · Run the judge over all examples (one forward pass each, no generation)"),
    code(r'''
t0 = time.time()
P, M, H = [], [], []
order = np.argsort(df.excerpt.str.len().values)          # length-sorted batches = less padding
for i in range(0, len(df), BATCH_SIZE):
    idx = order[i:i + BATCH_SIZE]
    p, m, h = judge_batch(model, tok, YES_ID, NO_ID, df.assertion.values[idx].tolist(),
                          df.excerpt.values[idx].tolist(), LAYERS)
    P.append((idx, p, m, h))
    if (i // BATCH_SIZE) % 20 == 0:
        print(f"{i+len(idx)}/{len(df)}  {time.time()-t0:.0f}s")
p_yes = np.zeros(len(df), np.float32); mass = np.zeros(len(df), np.float32)
hidden = np.zeros((len(df), len(LAYERS), P[0][3].shape[-1]), np.float16)
n_clipped = 0
for idx, p, m, h in P:
    n_clipped += int((np.abs(h) > 65000).sum())
    p_yes[idx], mass[idx], hidden[idx] = p, m, np.clip(h, -65000, 65000).astype(np.float16)   # float16 storage
if n_clipped:
    print(f"note: {n_clipped} activation values clipped to the float16 range")
bad = ~np.isfinite(p_yes)
assert not bad.any(), (f"{bad.sum()} examples gave non-finite P(Yes) (float16 overflow?). "
                       "Re-run from section 3 with load_judge(MODEL_CHOICE, device, dtype=torch.bfloat16).")
df["p_yes"], df["yes_no_mass"] = p_yes, mass
df["verdict"] = (df.p_yes > 0.5).astype(int)
df["correct"] = (df.verdict == df.gold).astype(int)
T_JUDGE = time.time() - t0
print(f"judge pass: {T_JUDGE:.0f}s ({T_JUDGE/len(df):.2f}s/example)")
print("accuracy by split:", df.groupby("split").correct.mean().round(3).to_dict())
print("Yes rate (verdicts):", df.verdict.mean().round(3), "| mean Yes/No mass:", mass.mean().round(3))
print(df.groupby("task").correct.mean().round(2).sort_values())
'''),
    md("""
**Check before continuing:** overall accuracy should be clearly above 50 % and clearly below 100 % (the demo needs both right and wrong verdicts; with Qwen 0.5B we measured 67.7 % overall, 52–92 % per assertion). A Yes-rate near 0 or 1 means the judge collapsed to one answer: change the prompt in `judge_messages` (and in the student notebook generator, which shares it).
"""),
    md("## 5 · Verbalized confidence (second, short generation)"),
    code(r'''
t0 = time.time()
verbal = np.full(len(df), np.nan, np.float32); verbal_raw = np.array([""] * len(df), dtype=object)
if DO_VERBAL:
    vb = BATCH_SIZE * 2 if device == "cuda" else BATCH_SIZE
    for i in range(0, len(df), vb):
        idx = order[i:i + vb]
        v, raw = verbalized_confidence(model, tok, df.assertion.values[idx].tolist(), df.excerpt.values[idx].tolist(),
                                       ["Yes" if x else "No" for x in df.verdict.values[idx]])
        verbal[idx], verbal_raw[idx] = v, raw
        if (i // vb) % 20 == 0:
            print(f"{i+len(idx)}/{len(df)}  {time.time()-t0:.0f}s")
df["verbal_conf"], df["verbal_raw"] = verbal, verbal_raw
T_VERBAL = time.time() - t0
print(f"verbalized confidence: {T_VERBAL:.0f}s; unparsable: {np.isnan(verbal).mean():.1%}")
print(df.verbal_conf.describe().round(3))
print("examples:", df.verbal_raw.head(8).tolist())
'''),
    md("""
## 6 · Grounding check (precomputed for participants without a GPU)

For the most confident **Yes** ("compliant") verdicts on unseen documents (`test` + `shift`):
- **irrelevant evidence:** replace the excerpt by an unrelated boilerplate clause → a grounded judge should now say No;
- **leave one segment out:** remove each sentence/clause in turn → which segment does the Yes depend on?
"""),
    code(r'''
t0 = time.time()
cand = df[df.split.isin(["test", "shift"]) & (df.verdict == 1)].sort_values("p_yes", ascending=False).head(N_GROUNDING)
G = dict(g_index=[], g_p_full=[], g_p_irrelevant=[], g_n_segments=[], g_p_drop_min=[], g_drop_segment=[])
for k, (i, r) in enumerate(cand.iterrows()):
    irr = IRRELEVANT_CLAUSES[k % len(IRRELEVANT_CLAUSES)]
    p_irr = judge_batch(model, tok, YES_ID, NO_ID, [r.assertion], [irr])[0][0]
    segs = split_segments(r.excerpt)
    if len(segs) > 1:
        variants = [" ".join(segs[:j] + segs[j + 1:]) for j in range(len(segs))]
        pd_ = np.concatenate([judge_batch(model, tok, YES_ID, NO_ID, [r.assertion] * len(variants[s:s + BATCH_SIZE]),
                                          variants[s:s + BATCH_SIZE])[0] for s in range(0, len(variants), BATCH_SIZE)])
        j = int(np.argmin(pd_)); p_min, seg = float(pd_[j]), segs[j]
    else:
        p_min, seg = np.nan, ""
    for key, val in zip(G, [i, r.p_yes, p_irr, len(segs), p_min, seg]):
        G[key].append(val)
T_GROUND = time.time() - t0
g = pd.DataFrame(G)
print(f"grounding: {len(g)} verdicts in {T_GROUND:.0f}s")
print("still Yes with irrelevant evidence:", (g.g_p_irrelevant > 0.5).mean().round(3))
print("flips to No when one segment is removed:", (g.g_p_drop_min < 0.5).mean().round(3),
      f"(of {np.isfinite(g.g_p_drop_min).sum()} multi-segment excerpts)")
'''),
    md("## 7 · Save the cache (compact `.npz`, no pickle)"),
    code(r'''
cache_path = f"{OUT_DIR}/cache_{MODEL_CHOICE}.npz"
meta = dict(model=JUDGE_MODELS[MODEL_CHOICE]["hf_id"], model_choice=MODEL_CHOICE, layers=LAYERS,
            dtype=str(model.dtype), device=device, n=len(df), seed=SEED, n_per_assertion=N_PER_ASSERTION,
            max_excerpt_chars=MAX_EXCERPT_CHARS, heldout=HELDOUT, system_prompt=SYSTEM_PROMPT,
            prompt_template=judge_messages("{assertion}", "{excerpt}")[1]["content"], conf_question=CONF_QUESTION,
            source="nguha/legalbench contract_nli_* (test split), CC BY 4.0; ContractNLI (Koreeda & Manning 2021)",
            seconds=dict(judge=round(T_JUDGE), verbal=round(T_VERBAL), grounding=round(T_GROUND)),
            accuracy=df.groupby("split").correct.mean().round(4).to_dict(),
            created=time.strftime("%Y-%m-%d %H:%M"))
S = lambda col: np.array(df[col].astype(str).tolist())          # fixed-width unicode, loads without pickle
np.savez_compressed(
    cache_path,
    uid=S("uid"), task=S("task"), assertion=S("assertion"), excerpt=S("excerpt"), split=S("split"),
    gold=df.gold.values.astype(np.int8), verdict=df.verdict.values.astype(np.int8),
    p_yes=df.p_yes.values.astype(np.float32), yes_no_mass=df.yes_no_mass.values.astype(np.float32),
    verbal_conf=df.verbal_conf.values.astype(np.float32), verbal_raw=S("verbal_raw"),
    hidden=hidden, layers=np.array(LAYERS, np.int16),
    g_index=np.array(G["g_index"], np.int32), g_p_full=np.array(G["g_p_full"], np.float32),
    g_p_irrelevant=np.array(G["g_p_irrelevant"], np.float32), g_n_segments=np.array(G["g_n_segments"], np.int16),
    g_p_drop_min=np.array(G["g_p_drop_min"], np.float32), g_drop_segment=np.array([str(s) for s in G["g_drop_segment"]] or [""]),
    meta=np.array(json.dumps(meta)),
)
print(cache_path, f"{os.path.getsize(cache_path)/1e6:.1f} MB")
print(json.dumps(meta, indent=1))
'''),
    md("## 8 · Upload to the Hugging Face dataset repo"),
    code(r'''
if UPLOAD:
    from huggingface_hub import HfApi
    api = HfApi()
    api.create_repo(CACHE_REPO, repo_type="dataset", exist_ok=True, private=False)
    readme = (f"# MICAI 2026 NB5 judge cache\n\nVerdicts, confidences and residual-stream activations of "
              f"`{meta['model']}` acting as a compliance judge on LegalBench contract_nli examples.\n\n"
              "Source data: LegalBench (Guha et al., 2023) `contract_nli_*`, derived from ContractNLI "
              "(Koreeda & Manning, 2021); CC BY 4.0. Excerpts truncated to "
              f"{MAX_EXCERPT_CHARS} characters. Built with notebooks/instructor/NB5_prepare_cache.ipynb.\n")
    open(f"{OUT_DIR}/README.md", "w").write("---\nlicense: cc-by-4.0\n---\n" + readme)
    for f in [cache_path, f"{OUT_DIR}/selection.csv", f"{OUT_DIR}/README.md"]:
        api.upload_file(path_or_fileobj=f, path_in_repo=os.path.basename(f), repo_id=CACHE_REPO, repo_type="dataset")
    print(f"uploaded → https://huggingface.co/datasets/{CACHE_REPO}")
else:
    print("UPLOAD is off (CACHE_REPO still a TODO). The cache is at", cache_path)
    if IN_COLAB:
        print("Download it from the Files panel, or: from google.colab import files; files.download(cache_path)")
'''),
    md("""
**Time budget (fill in after your run):** model download ___ · judge pass ___ · verbalized ___ · grounding ___.
Our CPU reference run (Qwen 0.5B, 2 cores, shared machine): see `meta['seconds']` in `data/nb5/cache_qwen0.5b.npz`.
"""),
]

# ============================================================================================
# Student / solutions notebook: NB5_judge_confidence
# ============================================================================================
cells = [
    md(f"""
# NB5 · Audit: can we trust the judge?

**MICAI 2026 · Mechanistic Interpretability, Hands-on**
**Presenter:** Víctor Macías-Terrón · **Block 5 · Audit** · **Time budget:** ~25 min hands-on, in pairs
**Runtime:** CPU is fine with the cache · T4 GPU only for the optional live judging cells

{SLIDES_LINK}

**Goal.** An **LLM judge** reads a *rule* and a piece of *evidence* and says whether the evidence satisfies the rule. Judges are often **overconfident**: when they are wrong they sound just as sure. We will build a **confidence proxy from the judge's residual stream** (a linear probe, as in Blocks 1–3) that predicts *when the verdict is wrong*, and use it to decide which verdicts a **human auditor** must review.

Rhythm: **Predict → Run → Interpret.** Write your prediction down *before* you run.
"""),
    md("""
## Context: rules × evidence

An LLM-assisted audit has two bodies of text: **rules** (what a standard requires) and **evidence** (minutes, tickets, plans). The judge answers *rule × evidence → compliant?* for thousands of pairs.

**Motivating example** (ISO/IEC 29110 style, *invented*: we do not quote the standard; all numbers illustrative):

> **Rule R-PM-07.** *Every change request is recorded, its impact on schedule and cost is assessed, and the customer approves it before work on it starts.*
> **Evidence.** *"12 Mar status meeting. Client asked to add CSV export to the reports module. Dev lead estimates 3 extra days; added to Sprint 4. Action: update the project plan."*
> **Judge:** Compliant, 90 % sure. **Human auditor:** Non-compliant (no cost assessment, no customer approval).

We cannot share real audit evidence, so the hands-on uses a public stand-in with the same shape:

| Audit (motivation) | Hands-on stand-in: LegalBench `contract_nli_*` |
|---|---|
| rule (e.g. R-PM-07) | **assertion**, e.g. *"the Receiving Party may share some Confidential Information with its employees"* |
| evidence (minutes, tickets) | **contract excerpt** from a real NDA |
| auditor's verdict | gold label **Yes / No** (does the excerpt support the assertion?) |
| a new process area | **held-out assertions** the probe never saw |

Data: LegalBench (Guha et al., NeurIPS 2023), tasks derived from ContractNLI (Koreeda & Manning, 2021); CC BY 4.0.
The session judge is **Gemma 3 4B IT**; its verdicts and activations were **precomputed** so this runs on any laptop.
"""),
    md("## 0 · Install and set up (≈ 30 s)"),
    code(f"""
%pip install -q scikit-learn=={P5['scikit-learn']} huggingface_hub=={P5['huggingface_hub']}
"""),
    code(CACHE_CONSTANTS + r'''
MODEL_CHOICE = "gemma3-4b"   # session judge; "qwen0.5b" = Qwen2.5-0.5B-Instruct (ungated, small, runs on CPU)

import os, sys, json, importlib.util, urllib.request
import numpy as np, pandas as pd, matplotlib.pyplot as plt
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.metrics import roc_auc_score

IN_COLAB = "google.colab" in sys.modules or importlib.util.find_spec("google.colab") is not None
try:
    import torch
    HAS_GPU = torch.cuda.is_available()
except ImportError:
    HAS_GPU = False
print("GPU available:", HAS_GPU)
'''),
    md("""
## 1 · (Optional) Watch the judge work, live

Only if you have a **T4** (Runtime → Change runtime type) *and* an HF token with the Gemma 3 licence accepted. Otherwise skip: everything below uses the cache. The judge gets one chat turn and we read **P(Yes) vs P(No) at the answer position**: one forward pass, no text generation.
"""),
    code(r'''
RUN_LIVE = HAS_GPU            # set True to force (qwen0.5b also works on CPU, ≈ 1 GB download)
judge = None
if RUN_LIVE:
    get_ipython().run_line_magic("pip", "install -q transformers==''' + P5["transformers"] + r'''")
    if MODEL_CHOICE.startswith("gemma"):
        HF_TOKEN = None
        if IN_COLAB:
            try:
                from google.colab import userdata
                HF_TOKEN = userdata.get("HF_TOKEN")
            except Exception as e:
                print(f"No usable Colab secret HF_TOKEN ({type(e).__name__})")
        if HF_TOKEN:
            from huggingface_hub import login
            login(token=HF_TOKEN, add_to_git_credential=False)
        else:
            from huggingface_hub import notebook_login
            notebook_login()
else:
    print("Live judging skipped: using the precomputed cache (that is fine!).")
'''),
    code(TASKS_SRC + "\n" + JUDGE_SRC + r'''
if RUN_LIVE:
    device = "cuda" if HAS_GPU else "cpu"
    try:
        judge = load_judge(MODEL_CHOICE, device)       # (model, tok, yes_id, no_id)
        demo = [("sharing_with_employees", "The Recipient may disclose Confidential Information to its employees who need to know it for the Purpose, provided they are bound by obligations of confidentiality."),
                ("sharing_with_employees", "This Agreement shall be governed by the laws of the State of New York."),
                ("no_licensing", "No other right or license, whether expressed or implied, in the Confidential Information is granted to the Parties hereunder.")]
        p, mass, _ = judge_batch(*judge, [ASSERTIONS[t] for t, _ in demo], [x for _, x in demo])
        for (t, x), pi, mi in zip(demo, p, mass):
            print(f"P(Yes)={pi:.2f}  (mass on Yes/No {mi:.2f})  rule: {t}\n   evidence: {x[:110]}...\n")
    except Exception as e:
        judge = None
        print("Could not run the live judge:", repr(e)[:300], "\n→ continue with the cache.")
'''),
    md("""
## 2 · Load the cache

One row per (assertion, excerpt) pair: gold label, the judge's verdict, `p_yes`, its **verbalized** confidence (we asked it *"how confident are you, 0–100?"* after its answer), and the **residual stream at the last prompt token** for a set of layers. Splits: `train` (fit probes), `cal` (choose layer and threshold), `test` (report), `shift` (assertions never seen in train/cal). Splits are by **document** (NDA), so no NDA in `test` was seen in `train`.
"""),
    code(r'''
def fetch_cache(choice):
    fname = f"cache_{choice}.npz"
    tries = []
    if not CACHE_REPO.startswith("TODO"):                          # (1) presenters' HF dataset repo
        try:
            from huggingface_hub import hf_hub_download
            return hf_hub_download(CACHE_REPO, fname, repo_type="dataset")
        except Exception as e:
            tries.append(f"HF {CACHE_REPO}: {type(e).__name__}")
    for p in [f"data/nb5/{fname}", f"../../data/nb5/{fname}", f"../data/nb5/{fname}", fname]:   # (2) repo clone / upload
        if os.path.exists(p):
            return p
    if choice == "qwen0.5b" and FALLBACK_URL.startswith("http"):  # (3) small fallback shipped with the course
        urllib.request.urlretrieve(FALLBACK_URL, fname)
        return fname
    raise FileNotFoundError(f"{fname} not found ({'; '.join(tries) or 'no CACHE_REPO set'})")

try:
    CACHE_PATH = fetch_cache(MODEL_CHOICE)
except FileNotFoundError as e:
    print(e, "\n→ falling back to the small Qwen 0.5B cache")
    CACHE_PATH = fetch_cache("qwen0.5b")

Z = np.load(CACHE_PATH, allow_pickle=False)
META = json.loads(str(Z["meta"]))
df = pd.DataFrame({k: Z[k] for k in ["uid", "task", "assertion", "excerpt", "split", "gold", "verdict",
                                     "p_yes", "verbal_conf", "verbal_raw"]})
df["correct"] = (df.verdict == df.gold).astype(int)
H = Z["hidden"].astype(np.float32)              # [N, n_layers, d_model]
LAYERS = Z["layers"].tolist()
print(f"judge: {META['model']}  |  {len(df)} examples  |  hidden {H.shape}  (layers {LAYERS})")
print(df.groupby("split").agg(n=("gold", "size"), assertions=("task", "nunique"), gold_yes=("gold", "mean")).round(2))
df.sample(3, random_state=0)[["task", "excerpt", "gold", "verdict", "p_yes", "verbal_conf"]]
'''),
    md("""
## 3 · How good is the judge?

### ✍️ Predict
The judge is a small instruction-tuned model reading real NDA clauses. **What accuracy do you expect overall?** And will it be similar across the 14 assertions, or will some rules be much harder?

✍️ My prediction: ____
"""),
    code(r'''
acc = df.groupby("task").agg(accuracy=("correct", "mean"), n=("correct", "size"),
                             judge_says_yes=("verdict", "mean"), gold_yes=("gold", "mean"))
acc["heldout"] = acc.index.isin(HELDOUT_TASKS := sorted(df[df.split == "shift"].task.unique()))
acc = acc.sort_values("accuracy")
print(f"overall accuracy: {df.correct.mean():.1%}   (always-'No' baseline: {1 - df.gold.mean():.1%})")
fig, ax = plt.subplots(figsize=(8, 4.5))
ax.barh(acc.index, acc.accuracy, color=["#d98c2b" if h else "#2a9d8f" for h in acc.heldout])
ax.axvline(0.5, ls="--", c="gray"); ax.set_xlim(0, 1); ax.set_xlabel("judge accuracy")
ax.set_title("Judge accuracy per assertion (orange = held-out assertions)")
plt.tight_layout(); plt.show()
acc.round(2)
'''),
    md("""
**Interpret.** The judge is right only *sometimes*, and how often depends strongly on the rule. Look at `judge_says_yes` vs `gold_yes`: some rules get an almost automatic "Yes" or "No" regardless of the evidence. An auditor cannot accept all verdicts, and cannot review all of them either. We need to know **which** verdicts to trust.
"""),
    md("""
## 4 · Baseline confidence: ask the judge

Two cheap confidence signals for each verdict:
- **token probability**: `conf_tok = max(p_yes, 1 − p_yes)`, the probability the judge put on the answer it gave;
- **verbalized**: the number the judge *says* when asked how confident it is.

A useful confidence score must (1) **rank**: wrong verdicts get lower scores (**AUROC** of the score for "verdict is correct"; 0.5 = useless), and (2) be **calibrated**: among verdicts with confidence 0.8, about 80 % are right (**ECE**, **Brier**, reliability diagram).

### ✍️ Predict
Which signal will separate right from wrong verdicts better: token probability or verbalized confidence? Will either be calibrated?

✍️ My prediction: ____
"""),
    md("""
### Your turn (3 min): expected calibration error
Bin the confidences into 10 equal-width bins; ECE is the weighted average gap between **mean confidence** and **accuracy** in each bin:
$\\mathrm{ECE} = \\sum_b \\frac{n_b}{N}\\,\\lvert \\mathrm{acc}_b - \\mathrm{conf}_b \\rvert$. If you skip this, a reference version is used.
"""),
    exercise(
        student=r'''
def expected_calibration_error(conf, correct, n_bins=10):
    conf, correct = np.asarray(conf, float), np.asarray(correct, float)
    bins = np.minimum((conf * n_bins).astype(int), n_bins - 1)     # bin index of each verdict
    # TODO: for each non-empty bin b: weight = fraction of verdicts in b,
    #       gap = |mean(correct in b) - mean(conf in b)|;  return the weighted sum of gaps
    raise NotImplementedError
''',
        solution=r'''
def expected_calibration_error(conf, correct, n_bins=10):
    conf, correct = np.asarray(conf, float), np.asarray(correct, float)
    bins = np.minimum((conf * n_bins).astype(int), n_bins - 1)     # bin index of each verdict
    ece = 0.0
    for b in range(n_bins):
        m = bins == b
        if m.any():
            ece += m.mean() * abs(correct[m].mean() - conf[m].mean())
    return ece
''',
    ),
    code(r'''
def _ece_reference(conf, correct, n_bins=10):
    conf, correct = np.asarray(conf, float), np.asarray(correct, float)
    bins = np.minimum((conf * n_bins).astype(int), n_bins - 1)
    return sum((bins == b).mean() * abs(correct[bins == b].mean() - conf[bins == b].mean())
               for b in range(n_bins) if (bins == b).any())
try:
    _ok = np.isclose(expected_calibration_error([.9, .9, .6, .2], [1, 0, 1, 1]), _ece_reference([.9, .9, .6, .2], [1, 0, 1, 1]))
    print("✓ your ECE matches the reference" if _ok else "✗ your ECE differs from the reference: check the bins")
except NotImplementedError:
    print("expected_calibration_error not implemented: using the reference version")
    expected_calibration_error = _ece_reference

def bootstrap_auroc(y, s, n=500, seed=0):
    rng, y, s = np.random.default_rng(seed), np.asarray(y), np.asarray(s)
    vals = [roc_auc_score(y[i], s[i]) for i in (rng.integers(0, len(y), len(y)) for _ in range(n)) if 0 < y[i].mean() < 1]
    return np.percentile(vals, [2.5, 97.5])

def report(name, conf, correct):
    conf, correct = np.asarray(conf, float), np.asarray(correct, int)
    ok = np.isfinite(conf)
    conf, correct = conf[ok], correct[ok]
    lo, hi = bootstrap_auroc(correct, conf)
    return dict(score=name, n=len(conf), AUROC=roc_auc_score(correct, conf), AUROC_95CI=f"[{lo:.2f}, {hi:.2f}]",
                ECE=expected_calibration_error(conf, correct), Brier=np.mean((conf - correct) ** 2),
                mean_conf=conf.mean(), accuracy=correct.mean())

def reliability(ax, conf, correct, label, n_bins=10, **kw):
    conf, correct = np.asarray(conf, float), np.asarray(correct, float)
    ok = np.isfinite(conf); conf, correct = conf[ok], correct[ok]
    bins = np.minimum((conf * n_bins).astype(int), n_bins - 1)
    xs = [conf[bins == b].mean() for b in range(n_bins) if (bins == b).sum() >= 3]
    ys = [correct[bins == b].mean() for b in range(n_bins) if (bins == b).sum() >= 3]
    ax.plot(xs, ys, "o-", label=label, **kw)
    ax.plot([0, 1], [0, 1], ":", c="gray"); ax.set_xlim(0, 1); ax.set_ylim(0, 1.02)
    ax.set_xlabel("confidence"); ax.set_ylabel("fraction of verdicts correct")

df["conf_tok"] = np.maximum(df.p_yes, 1 - df.p_yes)
test = df[df.split == "test"]
rows = [report("token prob  max(p,1-p)", test.conf_tok, test.correct),
        report("verbalized 0-100", test.verbal_conf, test.correct)]
print(f"test split: {len(test)} verdicts, judge accuracy {test.correct.mean():.1%}; "
      f"unparsable verbalized answers: {test.verbal_conf.isna().mean():.0%}")
print("verbalized answers, most common:", test.verbal_raw.value_counts().head(5).to_dict())
fig, ax = plt.subplots(figsize=(5, 4.5))
reliability(ax, test.conf_tok, test.correct, "token prob")
reliability(ax, test.verbal_conf, test.correct, "verbalized")
ax.legend(); ax.set_title("Reliability diagram (test)"); plt.show()
pd.DataFrame(rows).round(3)
'''),
    md("""
**Interpret.** Points *below* the diagonal = **overconfident** (the judge claims more than it delivers). Verbalized confidence is typically a handful of values (90, 95, …) regardless of whether the verdict is right: it cannot gate human review. Token probability ranks better than chance but is still poorly calibrated. Keep the AUROC numbers in mind: they are what the probe has to beat.
"""),
    md("""
## 5 · A probe on the judge's residual stream

Same tool as Block 3: a **logistic-regression probe** on the residual stream at the last prompt token, but now the label is **`correct = (verdict == gold)`**, not a property of the input. The probe never sees the gold label at inference time: it reads the judge's internal state and estimates *P(this verdict is correct)* (Radharapu et al., ACL 2026 Industry, arXiv 2512.22245, trained such probes on LLM judges).

Which layer? We do a quick **layer sweep**: fit on `train`, score AUROC on `cal`, pick the best. (`test` stays untouched until the end.)

### ✍️ Predict
Where will the "am I right?" signal be most readable: early, middle or late layers? Will the probe beat token probability on AUROC?

✍️ My prediction: ____
"""),
    code(r'''
tr, ca, te, sh = (df.split == s for s in ["train", "cal", "test", "shift"])
y = df.correct.values

def make_probe(C=0.05):
    # standardize each dimension, then L2-regularized logistic regression (few hundred examples, ~1-3k dims)
    return make_pipeline(StandardScaler(), LogisticRegression(C=C, max_iter=2000))

sweep = []
for j, L in enumerate(LAYERS):
    pr = make_probe().fit(H[tr, j], y[tr])
    sweep.append(dict(layer=L, train_AUROC=roc_auc_score(y[tr], pr.predict_proba(H[tr, j])[:, 1]),
                      cal_AUROC=roc_auc_score(y[ca], pr.predict_proba(H[ca, j])[:, 1])))
sweep = pd.DataFrame(sweep)
BEST_J = int(sweep.cal_AUROC.idxmax()); BEST_LAYER = LAYERS[BEST_J]
plt.figure(figsize=(6, 3.5))
plt.plot(sweep.layer, sweep.train_AUROC, "o--", label="train"); plt.plot(sweep.layer, sweep.cal_AUROC, "o-", label="cal")
plt.axhline(roc_auc_score(y[ca], df.conf_tok[ca]), c="gray", ls=":", label="token prob (cal)")
plt.xlabel("layer"); plt.ylabel("AUROC for 'verdict correct'"); plt.legend(); plt.title("Layer sweep"); plt.show()
print("best layer on cal:", BEST_LAYER)
sweep.round(3)
'''),
    md("""
Train AUROC near 1.0 with a much lower cal AUROC = the probe **memorizes** the training verdicts. That is expected with a few hundred examples and thousands of dimensions; regularization (`C`) keeps it useful.

### Your turn (3 min): fit the final probe
Fit `make_probe()` on the **train** split at the chosen layer and return P(correct) for **every** row of the cache. If you skip it, a reference version runs.
"""),
    exercise(
        student=r'''
def fit_probe(layer_idx):
    X = H[:, layer_idx]
    # TODO: probe = make_probe().fit(X[tr], y[tr]);  return probe, probe.predict_proba(X)[:, 1]
    raise NotImplementedError
''',
        solution=r'''
def fit_probe(layer_idx):
    X = H[:, layer_idx]
    probe = make_probe().fit(X[tr], y[tr])
    return probe, probe.predict_proba(X)[:, 1]
''',
    ),
    code(r'''
try:
    probe, df["probe_raw"] = fit_probe(BEST_J)
except NotImplementedError:
    print("fit_probe not implemented: using the reference version")
    probe = make_probe().fit(H[tr, BEST_J], y[tr]); df["probe_raw"] = probe.predict_proba(H[:, BEST_J])[:, 1]

# The raw probe memorized `train` (train AUROC ≈ 1), so its probabilities are too extreme. Calibrate it on `cal`
# with Platt scaling (a 1-D logistic regression on the probe's logit). Monotone: ranking/AUROC are unchanged.
_logit = lambda p: np.log(np.clip(p, 1e-6, 1 - 1e-6) / np.clip(1 - p, 1e-6, 1))
probe_platt = LogisticRegression().fit(_logit(df.loc[ca, "probe_raw"]).values[:, None], y[ca])
df["probe"] = probe_platt.predict_proba(_logit(df.probe_raw).values[:, None])[:, 1]

# fair comparison: token prob recalibrated on the same data (Platt scaling) -- changes calibration, not ranking
platt = LogisticRegression().fit(df.loc[tr | ca, ["conf_tok"]], y[tr | ca])
df["conf_tok_platt"] = platt.predict_proba(df[["conf_tok"]])[:, 1]

test = df[te]
rows = [report("token prob", test.conf_tok, test.correct),
        report("token prob, Platt-recalibrated", test.conf_tok_platt, test.correct),
        report("verbalized", test.verbal_conf, test.correct),
        report(f"probe @ layer {BEST_LAYER}, raw", test.probe_raw, test.correct),
        report(f"probe @ layer {BEST_LAYER}, Platt on cal", test.probe, test.correct)]
fig, ax = plt.subplots(figsize=(5, 4.5))
for col, lab in [("conf_tok", "token prob"), ("verbal_conf", "verbalized"), ("probe_raw", "probe (raw)"), ("probe", "probe (calibrated)")]:
    reliability(ax, test[col], test.correct, lab)
ax.legend(); ax.set_title("Reliability diagram (test)"); plt.show()
pd.DataFrame(rows).round(3)
'''),
    md("""
**Interpret.** Compare AUROC first (does the score *rank* wrong verdicts below right ones?), then ECE/Brier (are the numbers honest?). Recalibration (Platt) fixes ECE but **cannot** change AUROC: if the probe's AUROC is higher than token probability's, the residual stream carries information about correctness that the output probability does not. The raw probe is overconfident because it memorized its training verdicts; calibrating on held-out data is not optional. Look at the confidence intervals: with ~100 test verdicts, differences of a few AUROC points are noise.
"""),
    md("""
## 6 · Routing: which verdicts go to a human?

Policy: **auto-accept** a verdict if its score ≥ threshold *t*, otherwise **send it to a human auditor**. Two numbers matter:
- **coverage**: fraction of verdicts auto-accepted (auditor time saved);
- **escape rate**: fraction of *all* verdicts that are wrong **and** auto-accepted (errors nobody looks at). We also show the error rate *among* auto-accepted verdicts.

We pick *t* on the **cal** split: the lowest threshold whose auto-accepted error rate is ≤ `TARGET`, then check it on **test**.

### ✍️ Predict
For an error target of 10 % among auto-accepted verdicts, what coverage do you expect with token probability vs the probe? Will the test error rate stay under the target?

✍️ My prediction: ____
"""),
    code(r'''
TARGET = 0.10      # max error rate among auto-accepted verdicts (try 0.05 with the Gemma cache)

def risk_coverage(score, correct):
    order = np.argsort(-np.asarray(score)); c = np.asarray(correct)[order]
    k = np.arange(1, len(c) + 1)
    return k / len(c), np.cumsum(1 - c) / k          # coverage, error among the k most confident

plt.figure(figsize=(6, 4))
for col, lab in [("conf_tok", "token prob"), ("verbal_conf", "verbalized"), ("probe", "probe")]:
    s = test[col].fillna(0)
    cov, risk = risk_coverage(s, test.correct)
    plt.plot(cov, risk, label=lab)
plt.axhline(TARGET, ls="--", c="gray", label=f"target {TARGET:.0%}")
plt.axhline(1 - test.correct.mean(), ls=":", c="k", label="accept everything")
plt.xlabel("coverage (fraction auto-accepted)"); plt.ylabel("error among auto-accepted")
plt.title("Risk–coverage (test)"); plt.legend(); plt.ylim(0, 0.6); plt.show()
'''),
    md("""
### Your turn (3 min): pick the threshold
Return the **smallest** threshold `t` (among the observed cal scores) such that the error rate of cal verdicts with `score >= t` is ≤ `target`. If no threshold works, return `np.inf` (send everything to a human).
"""),
    exercise(
        student=r'''
def pick_threshold(score_cal, correct_cal, target):
    score_cal, correct_cal = np.asarray(score_cal, float), np.asarray(correct_cal, int)
    # TODO: for t in sorted(unique scores): accepted = score_cal >= t; err = 1 - mean(correct_cal[accepted])
    #       return the first t with err <= target (np.inf if none)
    raise NotImplementedError
''',
        solution=r'''
def pick_threshold(score_cal, correct_cal, target):
    score_cal, correct_cal = np.asarray(score_cal, float), np.asarray(correct_cal, int)
    for t in np.unique(score_cal):                       # ascending: the first hit has the largest coverage
        accepted = score_cal >= t
        if 1 - correct_cal[accepted].mean() <= target:
            return t
    return np.inf
''',
    ),
    code(r'''
def _pick_threshold_reference(score_cal, correct_cal, target):
    s, c = np.asarray(score_cal, float), np.asarray(correct_cal, int)
    return next((t for t in np.unique(s) if 1 - c[s >= t].mean() <= target), np.inf)
try:
    pick_threshold([.2, .5, .9], [0, 1, 1], 0.1)
except NotImplementedError:
    print("pick_threshold not implemented: using the reference version")
    pick_threshold = _pick_threshold_reference

def route(score_col, part, t):
    s, c = df.loc[part, score_col].fillna(-1).values, df.loc[part, "correct"].values
    acc_ = s >= t
    return dict(coverage=acc_.mean(), error_among_accepted=(1 - c[acc_]).mean() if acc_.any() else np.nan,
                escape_rate=((1 - c) * acc_).mean(), sent_to_human=(~acc_).sum())

ROUTING = []
for col in ["conf_tok", "verbal_conf", "probe"]:
    cal_ok = ca & df[col].notna()
    t = pick_threshold(df.loc[cal_ok, col], df.loc[cal_ok, "correct"], TARGET)
    for name, part in [("cal", ca), ("test", te)]:
        ROUTING.append(dict(score=col, split=name, threshold=t, **route(col, part, t)))
ROUTING = pd.DataFrame(ROUTING)
ROUTING.round(3)
'''),
    md("""
**Interpret.** On `cal` the error target is met by construction; on `test` it may be exceeded: the threshold was *fitted* on ~100 cal verdicts, so it inherits their noise. That gap is exactly what an auditor will ask about: *"how do you know the escape rate is bounded on the next project?"* (see the debrief). Compare coverages: a better-ranking score lets you auto-accept more verdicts at the same risk.
"""),
    md("""
## 7 · Shift test: a rule the probe has never seen

The `shift` split contains **3 assertions held out entirely** (no example of these rules in train or cal), like a new process area in the next audit.

### ✍️ Predict
Will the probe's AUROC on held-out assertions hold up, drop to token-probability level, or fall to chance? Will the threshold from `cal` still meet the error target?

✍️ My prediction: ____
"""),
    code(r'''
shift = df[sh]
rows = [report(n, shift[c], shift.correct) for n, c in
        [("token prob", "conf_tok"), ("verbalized", "verbal_conf"), (f"probe @ layer {BEST_LAYER}", "probe")]]
print(f"held-out assertions: {sorted(shift.task.unique())}; judge accuracy {shift.correct.mean():.1%}")
display(pd.DataFrame(rows).round(3))
THRESH = ROUTING.drop_duplicates("score").set_index("score").threshold     # thresholds picked on cal
SHIFT_ROUTING = pd.DataFrame([dict(score=c, split="shift", threshold=THRESH[c], **route(c, sh, THRESH[c]))
                              for c in ["conf_tok", "verbal_conf", "probe"]])
display(SHIFT_ROUTING.round(3))
per = [dict(task=t, n=len(g), judge_acc=g.correct.mean(),
            AUROC_tok=roc_auc_score(g.correct, g.conf_tok) if 0 < g.correct.mean() < 1 else np.nan,
            AUROC_probe=roc_auc_score(g.correct, g.probe) if 0 < g.correct.mean() < 1 else np.nan)
       for t, g in shift.groupby("task")]
pd.DataFrame(per).round(3)
'''),
    md("""
**Interpret.** Per held-out assertion, n = 40: read the direction, not the decimals. (In our Qwen 0.5B reference run the probe beat token probability on `test` but fell *below* it on `shift`, and its cal threshold let far more errors escape: a probe that works in-distribution is not evidence that it works on the next process area.) If the probe partly learned "*which rule is this and how often is the judge right on it*" (an easy shortcut with few rules), it will degrade on new rules. Rule-level shortcuts are a real risk: the probe is evidence about *this* judge on *these* rules, not a general truth meter.
"""),
    md("""
## 8 · Grounding check: does the verdict depend on the evidence?

A confident "compliant" verdict that does **not** change when the evidence is removed is the dangerous case (the R-PM-07 judge relied on the schedule clue and ignored the approval clause). Block 2's tool, applied to text: **intervene on the input** and watch the verdict.

For the most confident *Yes* verdicts on unseen documents we (a) replace the excerpt by an irrelevant boilerplate clause and (b) remove one sentence/clause at a time.

### ✍️ Predict
With the evidence replaced by *"This Agreement shall be governed by the laws of New York."*, what fraction of confident Yes verdicts will stay Yes?

✍️ My prediction: ____
"""),
    code(r'''
g = pd.DataFrame({k: Z[k] for k in ["g_index", "g_p_full", "g_p_irrelevant", "g_n_segments", "g_p_drop_min", "g_drop_segment"]})
if len(g):
    g = g.join(df[["task", "excerpt", "gold", "correct", "probe", "split"]], on="g_index")
    g["ungrounded"] = g.g_p_irrelevant > 0.5         # still says Yes with irrelevant evidence
    print(f"{len(g)} confident Yes verdicts (precomputed with {META['model']})")
    print(f"  still Yes with irrelevant evidence: {g.ungrounded.mean():.0%}")
    multi = g[g.g_n_segments > 1]
    print(f"  flip to No when ONE segment is removed: {(multi.g_p_drop_min < 0.5).mean():.0%} of {len(multi)} multi-segment excerpts")
    print(f"  of these verdicts, correct (gold = Yes): {g.correct.mean():.0%}")
    if 0 < g.ungrounded.mean() < 1:
        print(f"  mean probe score, grounded vs ungrounded: {g[~g.ungrounded].probe.mean():.2f} vs {g[g.ungrounded].probe.mean():.2f}")
    display(g.sort_values("g_p_drop_min")[["task", "g_p_full", "g_p_irrelevant", "g_p_drop_min", "g_drop_segment", "gold"]].head(6).round(2))
else:
    print("No grounding results in this cache.")
'''),
    md("""
**Live version** (only if the live judge loaded in section 1): pick a verdict and see which segment it depends on.
"""),
    code(r'''
def grounding_live(i):
    r = df.loc[i]
    segs = split_segments(r.excerpt)
    variants = [r.excerpt, IRRELEVANT_CLAUSES[0]] + [" ".join(segs[:j] + segs[j + 1:]) for j in range(len(segs))] * (len(segs) > 1)
    p = judge_batch(*judge, [r.assertion] * len(variants), variants)[0]
    print(f"rule: {r.assertion}\ngold={r.gold}  cached p_yes={r.p_yes:.2f}  live p_yes={p[0]:.2f}  irrelevant evidence → {p[1]:.2f}")
    for j, s in enumerate(segs if len(segs) > 1 else []):
        print(f"  without segment {j}: p_yes={p[2 + j]:.2f}   | {s[:90]}")

if judge is not None:
    i = int(g.g_index.iloc[0]) if len(g) else int(df[te].index[0])
    grounding_live(i)            # try other rows: grounding_live(<index from the table above>)
else:
    print("No live judge loaded: the precomputed table above is the result of this experiment.")
'''),
    md("""
**Interpret.** A verdict that survives the removal of its evidence is not an *assessment of the evidence*; it is a prior about the rule. Note that such a verdict can still be *correct* (the gold label is Yes): accuracy alone would never reveal that the judge did not read the clause, and neither would the probe if its score is just as high. This is complementary to the probe: the probe estimates *how likely* a verdict is wrong; the grounding check gives an auditor a *reason* (which clause the verdict hangs on), the kind of evidence an audit report can cite.
"""),
    md("""
## 9 · Debrief (pairs, 3 min): what would an auditor accept?

Discuss and note one answer each:
1. You must certify *"at most 5 % of verdicts are wrong and unreviewed"*. Is a threshold tuned on ~100 calibration verdicts enough evidence? What would you add?
2. The probe beat (or did not beat) token probability. What would convince you it reads *the judge's uncertainty* rather than *which rule is hard*?
3. Which is more useful to the auditor: a calibrated score, or the grounding check's "this verdict depends on clause X"?

**Research direction (not a published result).** Use the probe score as the (non)conformity score of a **split-conformal / conformal-risk-control** threshold: choose the smallest *t* on the calibration set such that $\\frac{n}{n+1}\\widehat{\\mathrm{escape}}_{\\mathrm{cal}}(t) + \\frac{1}{n+1} \\le \\alpha$. Under exchangeability between calibration and deployment verdicts, this bounds the **expected escape rate** by α. The guarantee is only as good as exchangeability: the shift test in section 7 shows what happens when a new rule breaks it. This is the thesis line of Víctor Macías-Terrón (LLM-assisted quality/security audits).
"""),
    md("### Stretch (optional): a conformal-style threshold on the escape rate"),
    code(r'''
ALPHA = 0.10           # bound on the expected escape rate (wrong AND auto-accepted, over all verdicts)

def crc_threshold(score_cal, correct_cal, alpha):
    s, c = np.asarray(score_cal, float), np.asarray(correct_cal, int); n = len(s)
    for t in np.unique(s):                                   # ascending → largest coverage first
        escape = ((1 - c) * (s >= t)).mean()                 # loss is monotone (non-increasing) in t
        if n / (n + 1) * escape + 1 / (n + 1) <= alpha:
            return t
    return np.inf

t_crc = crc_threshold(df.loc[ca, "probe"], df.loc[ca, "correct"], ALPHA)
pd.DataFrame([dict(split=n, threshold=t_crc, **route("probe", p, t_crc)) for n, p in [("cal", ca), ("test", te), ("shift", sh)]]).round(3)
'''),
    md("""
## 10 · Transfer: your own LLM-judged task

Pick a task in your research where an LLM *judges* something (grading answers, labeling data, reviewing code, screening papers, checking claims against sources). Fill in:

| | your task |
|---|---|
| rule (what the judge checks) | |
| evidence (what it reads) | |
| gold label (who decides, how many can you get?) | |
| cost of an escaped error vs cost of a human review | |
| the shift you fear (new domain, new rule, new model version) | |
| grounding intervention (what would you remove or swap?) | |

Recipe: run the judge with `output_hidden_states=True`, cache the last-prompt-token residual stream for a few layers, label `correct`, fit a regularized logistic probe, pick the layer and threshold on a calibration split, report coverage and escape rate on a test split **and** on a held-out shift.

## What this does *not* show (honest limits)

- **Cached results**: the verdicts and activations were computed once, with one prompt, greedy decoding, one model. Change the prompt and the numbers change.
- **Small data**: a few hundred verdicts, ~40 per assertion. Confidence intervals are wide; differences of a few points are noise.
- **Probe shortcuts**: with few rules, a probe can learn *which rule is hard* rather than *this verdict is uncertain*; the per-assertion and shift results are the check. Probes can overfit to the assertions they were trained on.
- **Verbalized confidence is prompt-sensitive**: other wordings (or asking before the answer) give different numbers; we tested one.
- **Stand-in data**: NDA clauses are not 29110 evidence; R-PM-07 is invented and its numbers are illustrative.
- **Not a guarantee**: the routing threshold is an empirical estimate; the conformal bound is a research direction and relies on exchangeability.

## Takeaway

> A judge's **verbalized confidence** cannot gate human review. A **probe on its residual stream** is a cheap confidence proxy that can rank wrong verdicts below right ones, and **interventions on the evidence** show what a verdict actually depends on. Both are evidence for an auditor, not a certificate.

**References.** Radharapu et al., *Calibrating LLM Judges: Linear Probes for Fast and Reliable Uncertainty Estimation*, ACL 2026 Industry (arXiv 2512.22245). Kossen, Han et al., *Semantic Entropy Probes* (arXiv 2406.15927, 2024). Guha et al., *LegalBench*, NeurIPS 2023. Koreeda & Manning, *ContractNLI*, Findings of EMNLP 2021. Angelopoulos et al., *Conformal Risk Control*, ICLR 2024.
"""),
]


def build_instructor():
    nb = new_notebook()
    nb.metadata["kernelspec"] = {"name": "python3", "display_name": "Python 3", "language": "python"}
    nb.metadata["language_info"] = {"name": "python"}
    nb.metadata["colab"] = {"provenance": [], "toc_visible": True}
    nb.metadata["accelerator"] = "GPU"
    for kind, a, _ in instructor_cells:
        nb.cells.append(new_markdown_cell(a) if kind == "md" else new_code_cell(a))
    out = ROOT / "instructor" / "NB5_prepare_cache.ipynb"
    out.parent.mkdir(parents=True, exist_ok=True)
    nbformat.validate(nb)
    nbformat.write(nb, out)
    print("wrote", out)


if __name__ == "__main__":
    build(cells, "NB5_judge_confidence.ipynb", "NB5_judge_confidence_solutions.ipynb")
    build_instructor()
