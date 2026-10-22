"""Generator for NB2 (activation patching on IOI). Run: python3 notebooks/src/build_nb2.py"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from nbgen import md, code, exercise, build, PINS, SLIDES_LINK  # noqa: E402

P = PINS
cells = [
    md(f"""
# NB2 · Activation patching: which parts *cause* the answer?

**MICAI 2026 · Mechanistic Interpretability, Hands-on**
**Presenter:** Salvador Hinojosa · **Block 2 · Intervene** · **Time budget:** ~15 min hands-on
**Runtime:** CPU is fine (GPT-2 small; each patching sweep takes ≈1–2 min on a Colab CPU, seconds on a GPU)

{SLIDES_LINK}

**Goal.** NB1 showed *where the answer becomes readable*. Readable is not the same as *used*. Here we **intervene**: run the model on a *corrupted* prompt, transplant one activation from the *clean* run, and measure how much of the clean behaviour comes back. If transplanting a component restores the answer, that component carries information the model **causally relies on**.

Task: **indirect object identification (IOI)** in GPT-2 small (Wang et al., 2022, *Interpretability in the Wild*):

> *When Mary and John went to the store, John gave a drink to* → **Mary**
"""),
    md("""
## 0 · Install and load (≈1–2 min on Colab)
"""),
    code(f"""
%pip install -q transformer_lens=={P['transformer_lens']}
"""),
    code("""
import warnings
warnings.filterwarnings("ignore", message=".*deprecated.*")  # TransformerLens 3.x deprecation notice: harmless

import time
import torch
import matplotlib.pyplot as plt
from transformer_lens import HookedTransformer, patching, utils

torch.set_grad_enabled(False)
device = "cuda" if torch.cuda.is_available() else "cpu"
print("device:", device)
model = HookedTransformer.from_pretrained("gpt2-small", device=device)
"""),
    md("""
## 1 · Clean and corrupted prompts

The **corrupted** prompt swaps which name is repeated, so the correct answer flips from *Mary* to *John*. Everything else (length, positions, words) stays the same, so any difference in behaviour comes from that one swap.

To avoid a story built on one sentence, we use **8 prompts**: 4 name pairs × both orders. Every name is a single GPT-2 token, so all prompts align position by position (checked below).
"""),
    code("""
TEMPLATE = "When {A} and {B} went to the store, {S} gave a drink to"
PAIRS = [("Mary", "John"), ("Tom", "James"), ("Dan", "Sid"), ("Amy", "Martin")]

def make_ioi(template, pairs):
    \"\"\"clean: S = B (answer A);  corrupted: S = A (answer B). Returns tokens and answer ids.\"\"\"
    pairs = pairs + [(b, a) for a, b in pairs]                   # both orders
    clean = [template.format(A=a, B=b, S=b) for a, b in pairs]
    corrupt = [template.format(A=a, B=b, S=a) for a, b in pairs]
    io = torch.tensor([model.to_single_token(" " + a) for a, b in pairs], device=device)  # raises if multi-token
    s = torch.tensor([model.to_single_token(" " + b) for a, b in pairs], device=device)
    clean_tok, corrupt_tok = model.to_tokens(clean), model.to_tokens(corrupt)
    assert clean_tok.shape == corrupt_tok.shape, "clean/corrupted prompts must have the same token length"
    return clean, corrupt, clean_tok, corrupt_tok, io, s

clean_prompts, corrupt_prompts, clean_tokens, corrupt_tokens, io_ids, s_ids = make_ioi(TEMPLATE, PAIRS)
print("clean    :", model.to_str_tokens(clean_prompts[0]))
print("corrupted:", model.to_str_tokens(corrupt_prompts[0]))
print("batch shape:", tuple(clean_tokens.shape))
"""),
    md("""
## 2 · The metric: normalised logit difference

**Logit difference** = logit(correct name) − logit(other name) at the last position, here logit(IO) − logit(S), e.g. *Mary − John*. We **normalise** it so that

- **0** = the corrupted run (the model prefers the wrong name),
- **1** = the clean run.

A patch scoring 0.4 recovers 40% of the clean behaviour.
"""),
    code("""
def logit_diff(logits, io=io_ids, s=s_ids):
    \"\"\"Mean over the batch of logit(IO) - logit(S) at the last position.\"\"\"
    last = logits[:, -1, :]
    return (last.gather(1, io[:, None]) - last.gather(1, s[:, None])).mean()

clean_logits, clean_cache = model.run_with_cache(clean_tokens)
corrupt_logits = model(corrupt_tokens)
CLEAN_LD = logit_diff(clean_logits).item()
CORRUPT_LD = logit_diff(corrupt_logits).item()
print(f"clean logit diff     = {CLEAN_LD:+.2f}   (positive: prefers the IO, e.g. Mary)")
print(f"corrupted logit diff = {CORRUPT_LD:+.2f}   (negative: prefers S, e.g. John)")

def ioi_metric(logits):
    return (logit_diff(logits) - CORRUPT_LD) / (CLEAN_LD - CORRUPT_LD)

print("metric(clean) =", round(ioi_metric(clean_logits).item(), 3), " metric(corrupted) =", round(ioi_metric(corrupt_logits).item(), 3))
"""),
    md("""
### ✍️ Predict

We will patch the **residual stream** at every (layer, position): take the clean value at that one spot, put it into the corrupted run, measure the metric.

Clean and corrupted prompts differ at **one position only** (the second occurrence of the subject, `S2`).

1. **Which positions** can possibly matter? Which ones *cannot*, and why?
2. **At which layers** do you expect the information to move from the `S2` position to the last position (`to`), where the prediction is made?

✍️ My prediction: ____
"""),
    md("""
## 3 · Residual-stream patching, by hand

A **hook** is a function TransformerLens calls on an activation during the forward pass; whatever it returns replaces the activation. Patching = a hook that overwrites part of the corrupted activation with the clean one.

### Your turn (≈3 min): write the patching hook

`resid` has shape `[batch, position, d_model]`. Overwrite position `pos` with the clean value from `clean_cache[hook.name]`, and return the tensor. (If you skip it, a reference hook is used and everything still runs.)
"""),
    exercise(
        student="""
def patch_resid_hook(resid, hook, pos):
    # TODO: replace resid at position `pos` (all batch items, all of d_model)
    #       with the clean activation clean_cache[hook.name] at the same position, then return resid
    raise NotImplementedError("write the patching hook (or skip: the reference hook will be used)")
""",
        solution="""
def patch_resid_hook(resid, hook, pos):
    resid[:, pos, :] = clean_cache[hook.name][:, pos, :]
    return resid
""",
    ),
    code("""
def _reference_hook(resid, hook, pos):
    resid[:, pos, :] = clean_cache[hook.name][:, pos, :]
    return resid

# Use the student's hook if it works, otherwise fall back to the reference one
try:
    test = model.run_with_hooks(corrupt_tokens, fwd_hooks=[
        (utils.get_act_name("resid_pre", 0), lambda r, hook: patch_resid_hook(r, hook, pos=-1))])
    HOOK = patch_resid_hook
    print("✓ your hook runs")
except NotImplementedError:
    HOOK = _reference_hook
    print("(using the reference hook)")

# Sanity check: patching the WHOLE residual stream before layer 0 must give metric = 1
full = model.run_with_hooks(corrupt_tokens, fwd_hooks=[
    (utils.get_act_name("resid_pre", 0), lambda r, hook: clean_cache[hook.name].clone())])
print("metric when patching everything:", round(ioi_metric(full).item(), 3))
"""),
    code("""
n_layers, n_pos = model.cfg.n_layers, clean_tokens.shape[1]
resid_results = torch.zeros(n_layers, n_pos)

t0 = time.time()
for layer in range(n_layers):
    for pos in range(n_pos):
        hook_fn = lambda r, hook, pos=pos: HOOK(r, hook, pos)
        patched_logits = model.run_with_hooks(
            corrupt_tokens, fwd_hooks=[(utils.get_act_name("resid_pre", layer), hook_fn)])
        resid_results[layer, pos] = ioi_metric(patched_logits).item()
print(f"{n_layers * n_pos} forward passes in {time.time() - t0:.0f} s")
"""),
    code("""
# Position labels: tokens of the first clean prompt, with the IOI roles
toks = model.to_str_tokens(clean_prompts[0])
roles = {2: "IO", 4: "S1", 10: "S2", n_pos - 1: "END"}
pos_labels = [f"{t!r}" + (f"\\n{roles[i]}" if i in roles else "") for i, t in enumerate(toks)]

def heatmap(data, xlabels, ylabels, title, xlabel, ylabel, figsize=(10, 4.8)):
    lim = max(abs(data.min().item()), abs(data.max().item()), 1e-6)
    plt.figure(figsize=figsize)
    plt.imshow(data, cmap="RdBu", vmin=-lim, vmax=lim, aspect="auto")
    plt.colorbar(label="normalised logit diff (1 = clean)")
    plt.xticks(range(len(xlabels)), xlabels, fontsize=8); plt.yticks(range(len(ylabels)), ylabels)
    plt.xlabel(xlabel); plt.ylabel(ylabel); plt.title(title); plt.tight_layout(); plt.show()

heatmap(resid_results, pos_labels, [f"L{l}" for l in range(n_layers)],
        "Patching the residual stream (resid_pre) per layer × position", "position", "layer")
"""),
    md("""
### 🔍 Interpret

- Every position **before `S2`** shows 0: those tokens are identical in both prompts, so their clean and corrupted activations are the same (attention is causal: later tokens cannot change them).
- In the early layers, **all** the effect sits at `S2` (≈ 1.0 up to layer 6): the name difference simply lives there.
- In the late layers it sits at **`END`** (≈ 1.0 from layer 9 on). The handover happens in **layers 7–8**: at `resid_pre` of layer 8 the `S2` cell has dropped to ≈ 0.75 and `END` has risen to ≈ 0.39; at layer 9 `S2` ≈ 0.05 and `END` ≈ 0.99.
- A faint trace (≈ 0.04) sits at `' gave'`, right after `S2`.

So **attention heads in layers 7–8 move the information from `S2` to `END`**. Patching tells us *where* and *when*; next we ask *which heads*.

*(For the record: `transformer_lens.patching.get_act_patch_resid_pre(model, corrupt_tokens, clean_cache, ioi_metric)` computes the same grid with one call; we checked it gives identical numbers.)*
"""),
    md("""
## 4 · Which heads? Patching each attention head's output

Now we patch the output of **one attention head at a time** (`hook_z`, all positions at once) using TransformerLens's built-in helper. That is 12 × 12 = 144 forward passes (≈1 min on CPU).

### ✍️ Predict

Wang et al. (2022) describe **name-mover heads** (copy the IO name into the output: L9H9, L9H6, L10H0) and **S-inhibition heads** (tell name movers *not* to attend to S: L7H3, L7H9, L8H6, L8H10). Will the top heads in our patching heatmap be exactly these? Will any head have a **negative** effect?

✍️ My prediction: ____
"""),
    code("""
t0 = time.time()
head_results = patching.get_act_patch_attn_head_out_all_pos(model, corrupt_tokens, clean_cache, ioi_metric).cpu()
print(f"done in {time.time() - t0:.0f} s")

heatmap(head_results, [str(h) for h in range(12)], [f"L{l}" for l in range(12)],
        "Patching each head's output (all positions)", "head", "layer", figsize=(7, 5.5))

def fmt(idx_vals):
    return ", ".join(f"L{i // 12}H{i % 12} ({v:+.2f})" for i, v in idx_vals)
flat = head_results.flatten()
top = flat.topk(10); bot = (-flat).topk(3)
print("Top positive:", fmt(zip(top.indices.tolist(), top.values.tolist())))
print("Most negative:", fmt(zip(bot.indices.tolist(), (-bot.values).tolist())))
"""),
    code("""
KNOWN = {"name mover": [(9, 9), (9, 6), (10, 0)],
         "S-inhibition": [(7, 3), (7, 9), (8, 6), (8, 10)],
         "induction": [(5, 5), (6, 9)],
         "duplicate token": [(0, 1), (3, 0)],
         "negative name mover": [(10, 7), (11, 10)]}
rank = {i: r + 1 for r, i in enumerate(flat.argsort(descending=True).tolist())}
for cls, heads in KNOWN.items():
    print(f"{cls:20}", "  ".join(f"L{l}H{h}: {head_results[l, h]:+.2f} (rank {rank[l * 12 + h]})" for l, h in heads))
"""),
    md("""
### 🔍 Interpret

On our 8 prompts the largest positive effects are **L5H5 (≈ +0.45), L8H6 (+0.42), L8H10 (+0.34), L9H9 (+0.32), L7H9 (+0.23)**, then L6H9, L3H0, L7H3, L10H0. Mapping to Wang et al.:

- the four **S-inhibition** heads (L7H3, L7H9, L8H6, L8H10) are all in the top 8;
- **name mover** L9H9 is strong and L10H0 moderate, but **L9H6 is tiny (≈ +0.03)** even though it is a name mover;
- **induction** (L5H5, L6H9) and **duplicate-token** (L3H0) heads matter too: they detect that the subject is repeated, which is the first step of the circuit;
- **L10H7 (≈ −0.51) and L11H10 (≈ −0.22) are negative**: restoring them pushes *against* the answer. Wang et al. call them **negative name movers** (they hedge the prediction).

Why is L9H6 small? Single-head patching measures what one head adds **given that all the others stay corrupted**. Heads with redundant jobs (and *backup name movers* that compensate) look weak one at a time. Patching finds important components; a small number does not prove a component is unimportant.
"""),
    md("""
## 5 · Productive failure: attention is not causation

A tempting shortcut: *"the heads that attend most from `END` to the IO name (Mary) must be the ones doing the job."* Let's test it.

### ✍️ Predict

If we plot, for every head, **attention from `END` to the IO token** against the **patching effect**, will the points line up on a diagonal?

✍️ My prediction: ____
"""),
    code("""
IO_POS, END = 2, -1   # in every clean prompt the IO name is token 2 (after BOS and "When")
attn_to_io = torch.stack([clean_cache["pattern", l][:, :, END, IO_POS].mean(0) for l in range(12)]).cpu()  # [layer, head]

x, y = attn_to_io.flatten(), head_results.flatten()
plt.figure(figsize=(7.5, 5))
plt.scatter(x, y, s=18, color="#e07a1f", alpha=.7)
for i in torch.argsort(x, descending=True)[:8].tolist() + torch.argsort(y.abs(), descending=True)[:6].tolist():
    plt.annotate(f"L{i // 12}H{i % 12}", (x[i], y[i]), fontsize=8, xytext=(4, 3), textcoords="offset points")
plt.axhline(0, color="#999", lw=.8)
plt.xlabel("attention END → IO (clean run, mean over prompts)")
plt.ylabel("patching effect (normalised)")
r = torch.corrcoef(torch.stack([x, y]))[0, 1].item()
plt.title(f"Attention to the IO name vs causal effect (Pearson r = {r:.2f})")
plt.tight_layout(); plt.show()

print("Heads with the most attention to IO:")
for i in torch.argsort(x, descending=True)[:6].tolist():
    print(f"  L{i // 12}H{i % 12}: attention {x[i]:.2f}   patching effect {y[i]:+.2f}")
"""),
    md("""
### 🔍 Interpret

The heads that look at *Mary* the most are **L10H7 (≈ 0.78), L9H9 (≈ 0.76), L9H6 (≈ 0.57), L11H10 (≈ 0.52)**. Their causal effects: **−0.51, +0.32, +0.03, −0.22**. Two of the four push the *wrong* way, one barely matters. Meanwhile the S-inhibition heads (L7H9, L8H6, L8H10) barely attend to the IO at all, yet they are among the most important, because their job happens at a *different position* (they read `S2`).

The correlation over all 144 heads is slightly *negative* (r ≈ −0.16).

**Attention weights say where a head looks, not what it writes or whether the output is used.** Only the intervention answers the causal question.
"""),
    md("""
## 6 · Stretch: does it transfer to a different template? (optional)

Pick your own IOI template with `{A}`, `{B}` and `{S}` (the subject repeats as `{S}`, the answer is the other name). Keep the IO at token position 2 if you want to reuse the attention analysis; otherwise only the patching part is meaningful. Predict first: **will the same heads show up?**

If you leave the TODO, a default alternative template is used. (≈1 min on CPU.)
"""),
    exercise(
        student="""
MY_TEMPLATE = ...   # TODO e.g. "When {A} and {B} got a snack at the cafe, {S} decided to give it to"
""",
        solution="""
MY_TEMPLATE = "When {A} and {B} got a snack at the cafe, {S} decided to give it to"
""",
    ),
    code("""
if not isinstance(MY_TEMPLATE, str):
    MY_TEMPLATE = "Then, {A} and {B} had a long argument. Afterwards {S} said to"
    print("(using the default alternative template)")

_, _, c_tok, x_tok, io2, s2 = make_ioi(MY_TEMPLATE, PAIRS)
c_logits, c_cache = model.run_with_cache(c_tok)
x_logits = model(x_tok)
c_ld, x_ld = logit_diff(c_logits, io2, s2).item(), logit_diff(x_logits, io2, s2).item()
print(f"{MY_TEMPLATE!r}\\n  clean logit diff {c_ld:+.2f}, corrupted {x_ld:+.2f}")
if c_ld <= 0:
    print("  ⚠ GPT-2 does not solve this template (clean logit diff ≤ 0): results will be noisy")

metric2 = lambda lg: (logit_diff(lg, io2, s2) - x_ld) / (c_ld - x_ld)
heads2 = patching.get_act_patch_attn_head_out_all_pos(model, x_tok, c_cache, metric2).cpu()
t2 = heads2.flatten().topk(8)
print("Top heads (new template):", fmt(zip(t2.indices.tolist(), t2.values.tolist())))
print("Top heads (original)    :", fmt(zip(top.indices[:8].tolist(), top.values[:8].tolist())))
r2 = torch.corrcoef(torch.stack([heads2.flatten(), head_results.flatten()]))[0, 1].item()
print(f"Correlation of the two 12×12 maps: r = {r2:.2f}")
"""),
    md("""
## What this does *not* show

- **Patching says WHERE, not WHAT.** We know L8H6 matters; we do not know *what* it writes (a "which name is duplicated" signal? a position?). That needs decomposing activations into interpretable **features** → Block 3.
- **The answer depends on the corruption.** Swapping the repeated name tests "which name is S"; another corruption (random names, a different sentence) would highlight other components.
- **Single-component patching misses redundancy** (backup heads), and all-position head patching mixes what a head does at different positions.
- 8 prompts, 1 template, 1 small model. A real claim needs more prompts and a circuit-level test (e.g. path patching, ablating everything *except* the circuit).

## Takeaway

Intervening, not observing, separates the components the model **relies on** from the ones that merely **look** relevant. On IOI, patching recovers much of the Wang et al. circuit in ~2 minutes of CPU, and attention patterns alone would have misled us.

> **Next block:** we know *where* the information flows. *What* is it? → features and sparse autoencoders.
"""),
]

if __name__ == "__main__":
    build(cells, "NB2_activation_patching.ipynb", "NB2_activation_patching_solutions.ipynb")
