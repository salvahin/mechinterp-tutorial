"""Generator for NB0 (setup check). Run: python3 notebooks/src/build_nb0.py"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from nbgen import md, code, build, PINS, SLIDES_LINK  # noqa: E402

P = PINS
cells = [
    md(f"""
# NB0 · Setup check

**MICAI 2026 · Mechanistic Interpretability, Hands-on**
**Presenter:** Miguel González · **Block:** Hook (0:00–0:08) · **Time budget:** ~5 min, runs while we talk
**Runtime:** CPU is fine (no GPU needed for this notebook)

{SLIDES_LINK}

This notebook checks that your Colab can run the rest of the tutorial:

1. installs the libraries (pinned versions),
2. checks for a GPU,
3. runs a tiny GPT-2 forward pass,
4. logs you in to Hugging Face and checks the **gated Gemma models** you will need after the break.

Click **Runtime → Run all** and read the summary table at the bottom. Nothing here should crash: every check catches its own errors and tells you how to fix them.
"""),
    md("""
## 1 · Install (≈1–2 min on Colab)

Versions are pinned to the ones we tested. TransformerLens pulls in a recent `transformers`; this is the slowest part.

> **This is a smoke test.** NB1 and NB2 re-install what they need, and so do NB3–NB5. You do not have to keep this runtime alive.
>
> `circuit-tracer==0.5.0` (used in NB4) is **not** installed here: it requires an older `transformers` (≤ 4.57.3) and `huggingface_hub` (< 1.0) that conflict with TransformerLens 3.9. NB4 installs it in a fresh runtime.

If Colab shows a *"Restart session"* button after the install, click it, then run the notebook again from section 2.
"""),
    code(f"""
%pip install -q transformer_lens=={P['transformer_lens']} sae-lens=={P['sae-lens']} circuitsvis=={P['circuitsvis']} scikit-learn=={P['scikit-learn']} datasets=={P['datasets']}
"""),
    md("""
## 2 · Environment and GPU
"""),
    code("""
import os, sys, platform, importlib, importlib.util, warnings
from importlib.metadata import version, PackageNotFoundError

CHECKS = []  # rows of the final summary: (check, status, detail / fix)
def record(check, ok, detail=""):
    status = "✓" if ok is True else ("✗" if ok is False else "⚠")
    CHECKS.append((check, status, detail))
    print(f"{status} {check}: {detail}")

IN_COLAB = "google.colab" in sys.modules or importlib.util.find_spec("google.colab") is not None
record("Python", True, f"{platform.python_version()} ({'Colab' if IN_COLAB else 'not Colab'})")

try:
    import torch
    record("torch", True, torch.__version__)
    if torch.cuda.is_available():
        name = torch.cuda.get_device_name(0)
        mem = torch.cuda.get_device_properties(0).total_memory / 1e9
        record("GPU", True, f"{name} ({mem:.0f} GB): ready for NB3–NB5")
    else:
        record("GPU", None, "No GPU: fine for NB1–NB2; switch to T4 at the break "
                            "(Runtime → Change runtime type → T4 GPU)")
except Exception as e:
    record("torch", False, f"import failed: {e!r}. Fix: Runtime → Disconnect and delete runtime, then Run all")
"""),
    code("""
# Which libraries imported correctly, and which versions did we get?
PACKAGES = [("transformer_lens", "transformer_lens"), ("sae_lens", "sae-lens"),
            ("circuitsvis", "circuitsvis"), ("sklearn", "scikit-learn"),
            ("datasets", "datasets"), ("transformers", "transformers"),
            ("huggingface_hub", "huggingface_hub")]
for module, dist in PACKAGES:
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            importlib.import_module(module)
        record(dist, True, version(dist))
    except Exception as e:
        record(dist, False, f"{type(e).__name__}: {str(e)[:120]}. Fix: re-run the install cell, "
                            "then Runtime → Restart session")
"""),
    md("""
## 3 · A tiny forward pass (GPT-2 small, ~30 s)

This downloads GPT-2 small (≈ 500 MB, ungated) and asks it for one next token. If this works, torch + TransformerLens are fine and NB1 will start instantly (the weights are cached).
"""),
    code("""
try:
    import time, torch
    from transformer_lens import HookedTransformer
    warnings.filterwarnings("ignore", message=".*deprecated.*")  # TL 3.x deprecation notice; harmless
    t0 = time.time()
    model = HookedTransformer.from_pretrained("gpt2-small", device="cuda" if torch.cuda.is_available() else "cpu")
    with torch.no_grad():
        logits = model("The Eiffel Tower is in the French city of")
    nxt = model.to_string(logits[0, -1].argmax())
    assert logits.shape[-1] == model.cfg.d_vocab
    record("GPT-2 forward pass", True, f"next token = {nxt!r} ({time.time() - t0:.0f} s incl. download)")
    del model, logits
except Exception as e:
    record("GPT-2 forward pass", False, f"{type(e).__name__}: {str(e)[:150]}. "
                                        "Fix: re-run the install cell; ask the assistant")
"""),
    md("""
## 4 · Hugging Face login and gated models

After the break we use **Gemma** models (NB3–NB5). They are *gated*: you must (a) have a Hugging Face account, (b) accept Google's licence on each model page, and (c) give Colab a token.

**Recommended (once):** create a *Read* token at <https://huggingface.co/settings/tokens>, then in Colab click the 🔑 **Secrets** panel (left sidebar), add a secret named `HF_TOKEN`, paste the token, and switch **Notebook access** on.

If there is no secret, the cell below falls back to `notebook_login()`. With recent `huggingface_hub` versions this shows a **link and a short code**: open the link, enter the code, approve, and the cell continues by itself (older versions show a box where you paste the token, then re-run the cell). Set `USE_INTERACTIVE_LOGIN = False` to skip it. The token is never printed.
"""),
    code("""
USE_INTERACTIVE_LOGIN = True   # set False to skip the login box
HF_TOKEN, TOKEN_SOURCE = None, None

# (a) Colab secret
if IN_COLAB:
    try:
        from google.colab import userdata
        HF_TOKEN = userdata.get("HF_TOKEN")
        TOKEN_SOURCE = "Colab secret HF_TOKEN"
    except Exception as e:   # SecretNotFoundError, NotebookAccessError, ...
        print(f"No usable Colab secret ({type(e).__name__}). Add HF_TOKEN in the 🔑 panel "
              "and switch 'Notebook access' on.")

# (b) environment variable or a previous login on this machine
if not HF_TOKEN:
    try:
        from huggingface_hub import get_token
        HF_TOKEN = os.environ.get("HF_TOKEN") or get_token()
        TOKEN_SOURCE = "environment / cached login" if HF_TOKEN else None
    except Exception as e:
        print(f"Could not look for a cached token: {e!r}")

# (c) interactive login (hub >= 1.x: link + code, waits for you; older: paste box, then re-run)
if not HF_TOKEN and IN_COLAB and USE_INTERACTIVE_LOGIN:
    try:
        from huggingface_hub import notebook_login, get_token
        notebook_login()
        HF_TOKEN = get_token()
        TOKEN_SOURCE = "notebook_login"
        if not HF_TOKEN:
            print("👆 Finish the login above, then RE-RUN this cell.")
    except BaseException as e:   # includes KeyboardInterrupt if you stop the cell
        print(f"Interactive login did not complete ({type(e).__name__}). Use the Colab secret instead.")

if HF_TOKEN:
    os.environ["HF_TOKEN"] = HF_TOKEN   # later libraries pick it up from here
    try:
        from huggingface_hub import whoami
        user = whoami(token=HF_TOKEN).get("name", "?")
        record("HF token", True, f"valid, logged in as {user} ({TOKEN_SOURCE})")
    except Exception as e:
        record("HF token", False, f"token rejected ({type(e).__name__}). Fix: create a new Read token at "
                                  "https://huggingface.co/settings/tokens and update the HF_TOKEN secret")
        HF_TOKEN = None
else:
    record("HF token", False, "missing. Fix: add Colab secret HF_TOKEN (🔑 panel, Notebook access on) "
                              "or finish the notebook_login step and re-run")
"""),
    code("""
# Can we read config.json of each gated repo? (a few KB: no weights are downloaded)
GATED_REPOS = ["google/gemma-3-1b-it", "google/gemma-3-4b-it", "google/gemma-2-2b"]

def check_repo(repo_id, token):
    url = f"https://huggingface.co/{repo_id}"
    try:
        from huggingface_hub import hf_hub_download
        from huggingface_hub.errors import GatedRepoError, RepositoryNotFoundError
    except Exception as e:
        return False, f"huggingface_hub unavailable ({e!r})"
    try:
        hf_hub_download(repo_id, "config.json", token=token or False)
        return True, "access OK"
    except GatedRepoError:
        if not token:
            return False, f"no token. Fix: set HF_TOKEN (above), then open {url} and click Agree"
        return False, f"licence not accepted. Fix: open {url} and click Agree (approval is instant), then re-run"
    except RepositoryNotFoundError:
        return False, f"401/404: token invalid or repo not visible. Fix: check the token; open {url} and click Agree"
    except Exception as e:
        return False, f"{type(e).__name__}: {str(e)[:100]} (network? try again in a minute)"

for repo in GATED_REPOS:
    ok, msg = check_repo(repo, HF_TOKEN)
    record(repo, ok, msg)
"""),
    md("""
## 5 · Summary

All ✓ → you are ready. ⚠ on GPU is expected now. Any ✗ on the Gemma rows: fix it **before the break** (accepting a licence takes 10 seconds, waiting for the room's Wi-Fi does not).
"""),
    code("""
w = max(len(c) for c, _, _ in CHECKS)
print(f"{'check'.ljust(w)} | ok | detail / fix")
print("-" * (w + 3) + "+----+" + "-" * 60)
for check, status, detail in CHECKS:
    print(f"{check.ljust(w)} | {status}  | {detail}")
n_bad = sum(s == "✗" for _, s, _ in CHECKS)
print()
print("✅ All set!" if n_bad == 0 else f"❗ {n_bad} item(s) need a fix: see the last column. "
      "Wave at the assistant if you are stuck.")
"""),
]

if __name__ == "__main__":
    build(cells, "NB0_setup_check.ipynb", "NB0_setup_check_solutions.ipynb")
