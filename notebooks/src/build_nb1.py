"""Generator for NB1 (logit lens). Run: python3 notebooks/src/build_nb1.py"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from nbgen import md, code, exercise, build, PINS, SLIDES_LINK  # noqa: E402

P = PINS
cells = [
    md(f"""
# NB1 · The logit lens: watching an answer form

**MICAI 2026 · Mechanistic Interpretability, Hands-on**
**Presenter:** Miguel González · **Block 1 · Observe** · **Time budget:** ~12 min hands-on
**Runtime:** CPU is fine (GPT-2 small, 124M parameters)

{SLIDES_LINK}

**Goal.** A transformer writes into a shared *residual stream*, layer after layer, and only reads the answer out at the very end. The **logit lens** (nostalgebraist, 2020) asks: *what if we read the answer out early?* We take the residual stream after each layer, push it through the model's own final read-out, and watch the prediction form.

Rhythm for every experiment: **Predict → Run → Interpret.** Write your prediction down *before* you run the cell.
"""),
    md("""
## 0 · Install and load (≈1–2 min on Colab)

TransformerLens gives us hooks into every activation of GPT-2. The install takes about a minute on Colab; if Colab asks you to *restart the session* afterwards, do it and run from the next cell.
"""),
    code(f"""
%pip install -q transformer_lens=={P['transformer_lens']} circuitsvis=={P['circuitsvis']}
"""),
    code("""
import warnings
warnings.filterwarnings("ignore", message=".*deprecated.*")  # TransformerLens 3.x deprecation notice: harmless

import torch
import pandas as pd
import matplotlib.pyplot as plt
from transformer_lens import HookedTransformer

torch.set_grad_enabled(False)          # we only read activations: no gradients needed
device = "cuda" if torch.cuda.is_available() else "cpu"
print("device:", device)

model = HookedTransformer.from_pretrained("gpt2-small", device=device)
print(f"{model.cfg.n_layers} layers, d_model = {model.cfg.d_model}, vocab = {model.cfg.d_vocab}")
"""),
    md("""
## 1 · The prompt and the model's answer

`run_with_cache` runs the model once and stores **every** intermediate activation in `cache`, keyed by hook name (e.g. `blocks.5.hook_resid_post` = residual stream after block 5).
"""),
    code("""
prompt = "The Eiffel Tower is in the French city of"
target = " Paris"           # note the leading space: GPT-2 tokens usually start with one

print(model.to_str_tokens(prompt))
logits, cache = model.run_with_cache(prompt)

probs = logits[0, -1].softmax(-1)
top = probs.topk(5)
for p, i in zip(top.values, top.indices):
    print(f"{model.to_string(i)!r:>12}  {p:.3f}")
"""),
    md("""
### ✍️ Predict

GPT-2 small has 12 blocks. We will decode the residual stream at the last position after the embedding and after each block.

**At which layer does `' Paris'` first become the top-1 prediction?** Early (0–3), middle (4–7) or late (8–11)? And how confident will the final layer be compared to the middle layers?

✍️ My prediction: ____
"""),
    md("""
## 2 · The logit lens

The model's own read-out is `logits = unembed(ln_final(resid))`. The logit lens applies **exactly that read-out** to the intermediate residual streams:

$$\\text{logits}_\\ell = W_U \\cdot \\mathrm{LN}_{\\text{final}}(x_\\ell)$$

where $x_0$ is the embedding (`blocks.0.hook_resid_pre`) and $x_{\\ell+1}$ is `blocks.ℓ.hook_resid_post`.

**Why care about the layer norm?** The residual stream grows in norm as layers add to it. `ln_final` re-centres and re-scales it, so we must re-compute its statistics **for each intermediate vector** (not reuse the final position's scale, which belongs to the final residual). `cache.accumulated_resid(..., apply_ln=True)` does exactly this in TransformerLens 3.x: it applies `model.ln_final` to every layer's residual separately. (With the default `from_pretrained`, GPT-2's LN weights are folded into `W_U`, so `ln_final` is a parameter-free `LayerNormPre`; the maths is unchanged.)
"""),
    code("""
# resid: [n_layers + 1, batch=1, d_model] at the last position, ALREADY passed through ln_final
resid, labels = cache.accumulated_resid(layer=-1, incl_mid=False, apply_ln=True,
                                        pos_slice=-1, return_labels=True)
lens_probs = model.unembed(resid)[:, 0].softmax(-1)      # [13, d_vocab]

names = ["embed"] + [f"block {l}" for l in range(model.cfg.n_layers)]
tid = model.to_single_token(target)

def lens_table(lens_probs, tid):
    rows = []
    for name, p in zip(names, lens_probs):
        top1 = p.argmax()
        rows.append({"after": name,
                     "top-1 token": model.to_string(top1),
                     "P(top-1)": round(p[top1].item(), 3),
                     f"P({model.to_string(tid)!r})": round(p[tid].item(), 3),
                     "rank of target": int((p > p[tid]).sum()) + 1})
    return pd.DataFrame(rows)

df = lens_table(lens_probs, tid)
df
"""),
    code("""
def plot_lens(df, title):
    pcol = [c for c in df.columns if c.startswith("P('")][0]
    fig, ax = plt.subplots(figsize=(9, 3.6))
    ax.plot(range(len(df)), df[pcol], "o-", color="#0f8b8d", lw=2, label=pcol)
    ax.plot(range(len(df)), df["P(top-1)"], "s--", color="#999", lw=1, label="P(top-1)")
    for i, tok in enumerate(df["top-1 token"]):
        ax.annotate(repr(tok), (i, df["P(top-1)"][i]), textcoords="offset points", xytext=(0, 7),
                    ha="center", fontsize=8, rotation=35)
    ax.set_xticks(range(len(df)), df["after"], rotation=45, ha="right")
    ax.set_ylim(0, 1.15); ax.set_ylabel("probability"); ax.set_title(title)
    ax.legend(loc="upper left"); ax.grid(alpha=.3)
    plt.tight_layout(); plt.show()

plot_lens(df, f"Logit lens: {prompt!r}")
"""),
    md("""
### 🔍 Interpret

Read the table from top to bottom.

- In the early layers the lens decodes to generic tokens (`' the'`, odd fragments): the residual stream is not yet in "output format".
- `' Paris'` becomes top-1 **after block 8** (i.e. after 9 of 12 blocks), peaks at **P ≈ 0.96 after block 9**, then the last two blocks **lower** its probability (0.61 → 0.21 at the output). The final layers are not just "adding more confidence"; they spread probability out (calibration, hedging, other continuations).
- So the answer is *readable* in the middle-to-late residual stream, several layers before the end.

Compare with your prediction. Were you early, late, or right?
"""),
    md("""
### ✍️ Predict (the surprise)

Now remove **one word**: `"The Eiffel Tower is in the city of"` (no *French*).

**Does `' Paris'` ever become the top-1 prediction?** If not, what wins?

✍️ My prediction: ____
"""),
    code("""
prompt2 = "The Eiffel Tower is in the city of"
_, cache2 = model.run_with_cache(prompt2)
resid2 = cache2.accumulated_resid(layer=-1, incl_mid=False, apply_ln=True, pos_slice=-1)
lens_probs2 = model.unembed(resid2)[:, 0].softmax(-1)

df2 = lens_table(lens_probs2, tid)
df2["P(' London')"] = lens_probs2[:, model.to_single_token(" London")].numpy().round(3)
display(df2)
plot_lens(df2.drop(columns="P(' London')"), f"Logit lens: {prompt2!r}")
"""),
    md("""
### 🔍 Interpret

`' Paris'` **never** becomes top-1: from block 9 on, **`' London'`** wins. At the output GPT-2 small says London (P ≈ 0.08) with Paris a close second (P ≈ 0.07). The word *French* is what pushes the late layers to Paris.

Two lessons: (1) a small model's "knowledge" is fragile and prompt-dependent; (2) the logit lens shows **what** the model is converging on, layer by layer, even when it is wrong. That is already useful for debugging.
"""),
    md("""
## 3 · Your turn: write the logit lens yourself (≈5 min)

Fill in the **three core lines** of `logit_lens_probs` without `accumulated_resid`:

1. stack the residual stream at the **last position**: the embedding `cache["blocks.0.hook_resid_pre"]` and every `cache[f"blocks.{l}.hook_resid_post"]` → shape `[13, d_model]`;
2. apply `model.ln_final` (it expects `[batch, pos, d_model]`: add a dummy dimension with `[:, None, :]`);
3. apply `model.unembed` and a softmax → `[13, d_vocab]`.

If you skip this cell, `logit_lens()` below falls back to the library version, so the rest of the notebook still runs.
"""),
    exercise(
        student="""
def logit_lens_probs(prompt):
    \"\"\"Return a [n_layers + 1, d_vocab] tensor of next-token probabilities, one row per layer.\"\"\"
    _, cache = model.run_with_cache(prompt)
    # TODO 1: resid = torch.stack([...])                  # [13, d_model], last position only
    # TODO 2: normed = model.ln_final(...)                # remember the [:, None, :] trick
    # TODO 3: return model.unembed(...)[:, 0].softmax(-1)
    raise NotImplementedError("Fill in the 3 TODO lines (or skip: the fallback will be used)")
""",
        solution="""
def logit_lens_probs(prompt):
    \"\"\"Return a [n_layers + 1, d_vocab] tensor of next-token probabilities, one row per layer.\"\"\"
    _, cache = model.run_with_cache(prompt)
    resid = torch.stack([cache["blocks.0.hook_resid_pre"][0, -1]] +
                        [cache[f"blocks.{l}.hook_resid_post"][0, -1] for l in range(model.cfg.n_layers)])
    normed = model.ln_final(resid[:, None, :])          # recompute LN stats per layer
    return model.unembed(normed)[:, 0].softmax(-1)
""",
    ),
    code("""
def _library_logit_lens_probs(prompt):
    _, c = model.run_with_cache(prompt)
    r = c.accumulated_resid(layer=-1, incl_mid=False, apply_ln=True, pos_slice=-1)
    return model.unembed(r)[:, 0].softmax(-1)

def logit_lens(prompt, target, plot=True):
    \"\"\"Logit-lens table (and plot) for `prompt`, tracking the FIRST token of `target`.\"\"\"
    try:
        probs = logit_lens_probs(prompt)
    except NotImplementedError:
        print("(using the library fallback: your logit_lens_probs is not implemented yet)")
        probs = _library_logit_lens_probs(prompt)
    t = model.to_tokens(target, prepend_bos=False)[0]
    if len(t) > 1:
        print(f"note: {target!r} is {len(t)} tokens {model.to_str_tokens(target, prepend_bos=False)}; "
              f"tracking the first one")
    d = lens_table(probs, t[0].item())
    if plot:
        plot_lens(d, f"Logit lens: {prompt!r}")
    return d

# Self-check: your version must match the library version
try:
    mine = logit_lens_probs(prompt)
    ok = torch.allclose(mine, _library_logit_lens_probs(prompt), atol=1e-4)
    print("✓ matches the library" if ok else "✗ does not match the library yet: check the 3 lines")
except NotImplementedError:
    print("logit_lens_probs not implemented: fallback active")
"""),
    md("""
Now try your own prompts. Suggestions, one of each kind: **a fact**, **a translation**, **simple arithmetic / a sequence**. Before each run, predict the layer where the target becomes top-1.

GPT-2 small is a *small* model: some of these it simply gets wrong. When the final layer is wrong, the lens cannot show the right answer "forming". That is information too: write down which kinds of tasks work.
"""),
    code("""
logit_lens("Monday, Tuesday, Wednesday,", " Thursday")          # a sequence
"""),
    code("""
for p, t in [("The Colosseum is in the city of", " Rome"),       # a fact
             ("English: cheese. French:", " fromage"),             # a translation (multi-token target)
             ("1, 2, 3, 4,", " 5"),                                # counting
             ("2 + 2 =", " 4")]:                                   # arithmetic
    d = logit_lens(p, t, plot=False)
    print(f"{p!r:40} → output {d['top-1 token'].iloc[-1]!r:10} | top-1 per layer: {list(d['top-1 token'])[6:]}")
"""),
    code("""
# ✍️ Your own prompt here
logit_lens("The Eiffel Tower is in the French city of", " Paris")
"""),
    md("""
## 4 · Stretch: find an induction head (optional, ≈3 min)

Some heads implement **induction**: if the sequence contains `… A B … A`, they attend from the second `A` to the token *after* the first `A` (that is, `B`) and copy it. The cleanest test is a **random token sequence repeated twice**: the model cannot know the first half, but it can predict the second half perfectly by copying.

**Induction score** of a head = average attention from position *i* in the second half to position *i − T + 1* (the token right after the earlier copy), where *T* is the length of the random sequence. We compute it for every head instead of guessing.
"""),
    code("""
torch.manual_seed(0)
T, B = 50, 4
rand = torch.randint(1000, 10000, (B, T))
rep_tokens = torch.cat([torch.full((B, 1), model.tokenizer.bos_token_id), rand, rand], dim=1).to(device)

_, rep_cache = model.run_with_cache(rep_tokens, names_filter=lambda n: n.endswith("hook_pattern"))
induction = torch.zeros(model.cfg.n_layers, model.cfg.n_heads)
for l in range(model.cfg.n_layers):
    pat = rep_cache["pattern", l]                                  # [batch, head, query, key]
    # query position q (second half) attends to key q - T + 1  → a diagonal T-1 below the main one
    induction[l] = pat.diagonal(offset=-(T - 1), dim1=-2, dim2=-1)[..., 1:].mean((0, -1)).cpu()

plt.figure(figsize=(6, 4.5))
plt.imshow(induction, cmap="Oranges", vmin=0, vmax=1)
plt.colorbar(label="induction score"); plt.xlabel("head"); plt.ylabel("layer")
plt.xticks(range(12)); plt.yticks(range(12)); plt.title("Induction score per head (GPT-2 small)")
plt.show()

top = induction.flatten().topk(6)
print("Top induction heads:", ", ".join(f"L{i // 12}H{i % 12} ({v:.2f})" for v, i in zip(top.values, top.indices.tolist())))
"""),
    code("""
import circuitsvis as cv

best = induction.flatten().argmax().item()
L = best // model.cfg.n_heads
short = torch.cat([rep_tokens[:1, :1], rep_tokens[:1, 1:16], rep_tokens[:1, 1:16]], dim=1)  # shorter, for display
_, short_cache = model.run_with_cache(short, names_filter=f"blocks.{L}.attn.hook_pattern")
print(f"Attention patterns of layer {L}. Look for the off-diagonal stripe in the induction head(s).")
cv.attention.attention_patterns(tokens=model.to_str_tokens(short[0]),
                                attention=short_cache["pattern", L][0])
"""),
    md("""
### 🔍 Interpret

On GPT-2 small the strongest induction heads are **L5H5, L6H9, L7H10, L5H1** (scores ≈ 0.9) and L7H2 (≈ 0.84), all in the middle layers. In the attention view, an induction head shows a stripe parallel to the diagonal, offset by the length of the repeated chunk. Induction heads come back in Block 2: they are part of the IOI circuit.
"""),
    md("""
## What this does *not* show

- **It is correlational.** The lens shows what is *decodable* from the residual stream at layer ℓ. It does not show that the model *uses* that information, or which component put it there.
- **Early layers decode poorly** partly because of *basis drift*: intermediate residuals are not in the same "format" as the final one, so the final read-out is the wrong decoder for them. The **tuned lens** (Belrose et al., 2023) learns one affine translator per layer and decodes earlier layers much better.
- One prompt, one model. The Paris/London flip shows how fragile single-prompt stories are.

## Takeaway

The answer to a factual prompt becomes readable several layers before the output, and the last layers can *reduce* confidence. The logit lens is a cheap, honest **observation** tool.

> **Next block:** *We can see the answer forming — but does that layer cause it?*
"""),
]

if __name__ == "__main__":
    build(cells, "NB1_logit_lens.ipynb", "NB1_logit_lens_solutions.ipynb")
