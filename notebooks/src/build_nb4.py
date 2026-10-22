"""Generator for NB4 (circuit tracing with circuit-tracer). Run: python3 notebooks/src/build_nb4.py

One source -> notebooks/student/NB4_circuit_tracing.ipynb
            + notebooks/solutions/NB4_circuit_tracing_solutions.ipynb

PATH switch inside the notebook:
  "gemma2"     Gemma 2 2B + Gemma Scope transcoders (session default, T4, the library's documented setup)
  "gemma3-270m" Gemma 3 270M + Gemma Scope 2 transcoders (nnsight backend; light, runs on CPU in minutes)
  "neuronpedia" no model at all: load the pre-generated, featured graph from Neuronpedia
Env vars for local testing: NB4_PATH, NB4_GEMMA3_REPO.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from nbgen import md, code, exercise, build, SLIDES_LINK  # noqa: E402

# NB4 stack, verified to resolve and run together (fresh venv, Python 3.13, CPU torch 2.14.1):
CT_PINS = {
    "circuit-tracer": "0.5.0",
    "nnsight": "0.7.0",            # 0.8.x breaks circuit-tracer 0.5.0 (import of nnsight.intervention.tracing)
    "transformers": "4.57.3",      # circuit-tracer 0.5.0 requires <=4.57.3
    "huggingface_hub": "0.36.2",   # circuit-tracer 0.5.0 requires <1.0
    "transformer_lens": "3.2.1",   # last TransformerLens that works with transformers 4.57
}

FEATURED = ("https://www.neuronpedia.org/gemma-2-2b/graph?slug=gemma-fact-dallas-austin"
            "&pruningThreshold=0.6&densityThreshold=0.99")

cells = [
    md(f"""
# NB4 · Circuit tracing: how does the model get from *Dallas* to *Austin*?

**MICAI 2026 · Mechanistic Interpretability, Hands-on**
**Presenter:** Salvador Hinojosa · **Block 4 · Trace** · **Time budget:** ~15 min hands-on

**Runtime: none needed for the default path.** The room default `PATH = "neuronpedia"` runs in any Colab runtime (CPU is fine) and uses Neuronpedia's public circuit-tracing servers, where Gemma 2 2B and its transcoders are already loaded. No Hugging Face token needed.
**Use a fresh runtime** if you pick a model path: NB4 needs older library versions than NB0–NB3 (circuit-tracer 0.5.0 pins `transformers<=4.57.3`), so do *Runtime → Disconnect and delete runtime* first.

### 🧭 Which path should I pick?

| Your situation | `PATH` | What you do | Time |
|---|---|---|---|
| **No GPU, or short on time (most of the room)** | `"neuronpedia"` *(default)* | Generate a graph for your own prompt on Neuronpedia, find the *Texas* features, ablate/steer them and watch *Austin* drop: in the browser **and** from this notebook through Neuronpedia's API | ≈ 14 min |
| **T4 GPU and you started the pre-download at the break** (section 0b) | `"gemma2"` | Run `circuit-tracer` yourself on Gemma 2 2B + Gemma Scope transcoders, then intervene in code | ≈ 5 min load + 1–3 min attribution |
| **Curious, CPU only** | `"gemma3-270m"` | Same code on Gemma 3 270M + Gemma Scope 2 transcoders. This model is too small for the two-hop prompt, so it traces the **one-hop** prompt *"…the state of Texas is the city of"* | ≈ 3 min on CPU |

Memory for `"gemma2"`: model ≈ 5 GB (bfloat16) + 26 transcoders (≈ 8 GB on disk); with `offload="disk"` and batch size 256 it fits a 15 GB T4. First-time download ≈ 18 GB (≈ 5–8 min on Colab).

{SLIDES_LINK}

**Goal.** NB2 asked *which component* matters. NB3 gave us *features* at one layer. An **attribution graph** connects features across **all layers and positions**: nodes are input tokens, transcoder features, error nodes and output logits; edges are *direct linear effects* in a **local replacement model** where each MLP is replaced by a sparse *transcoder*. Then we **test** the story by intervening on the model.

> *Fact: the capital of the state containing Dallas is* → **Austin**

This is the two-hop example from Anthropic's *On the Biology of a Large Language Model* (2025), tools from the open-source `circuit-tracer` library (Hanna, Piotrowski et al.; Anthropic + Decode Research, May 2025).
"""),
    md("""
### ✍️ Predict

To answer *Austin*, the model must compute something that **never appears in the prompt**. What is that intermediate concept, at which **token position** would you expect it to be represented, and roughly at which **layers** (early / middle / late)?

✍️ My prediction: ____
"""),
    md("""
## 0 · Choose a path and install (≈1 min)

The install is skipped on the `neuronpedia` path (it only needs the Python standard library).
"""),
    code("""
import os
PATH = os.environ.get("NB4_PATH", "neuronpedia")   # "neuronpedia" (default, any runtime) | "gemma2" (T4 + pre-download) | "gemma3-270m" (CPU, one-hop)
AUTO_FALLBACK = True                               # "gemma2" without a GPU, or a failed model load -> "neuronpedia"
"""),
    code(f"""
# Separate, pinned stack for circuit-tracer 0.5.0 (PyPI). Run in a FRESH runtime.
if PATH != "neuronpedia" and os.environ.get("NB4_SKIP_INSTALL") != "1":
    %pip install -q circuit-tracer=={CT_PINS['circuit-tracer']} nnsight=={CT_PINS['nnsight']} transformers=={CT_PINS['transformers']} huggingface_hub=={CT_PINS['huggingface_hub']} transformer_lens=={CT_PINS['transformer_lens']}
"""),
    code("""
import json, time, urllib.request
from collections import namedtuple
try:
    import torch
    device = "cuda" if torch.cuda.is_available() else "cpu"
except ImportError:          # the neuronpedia path does not need torch
    torch, device = None, "cpu"
IN_COLAB = "google.colab" in str(get_ipython()) if "get_ipython" in globals() else False
print("device:", device, "| in Colab:", IN_COLAB)
if device == "cuda":
    print("GPU:", torch.cuda.get_device_name(0), f"| {torch.cuda.get_device_properties(0).total_memory/1e9:.1f} GB")
if PATH == "gemma2" and device == "cpu" and AUTO_FALLBACK:
    print("No GPU: Gemma 2 2B attribution is impractical on CPU -> switching to PATH = 'neuronpedia'.\\n"
          "(Alternatively set PATH = 'gemma3-270m', which runs on CPU in a few minutes.)")
    PATH = "neuronpedia"

PROMPT = "Fact: the capital of the state containing Dallas is"
if PATH == "gemma3-270m":
    # Gemma 3 270M is too small to solve the two-hop prompt (it answers " the" / " Dallas"),
    # so the light path traces the ONE-hop version, where it does answer Austin.
    PROMPT = "Fact: the capital of the state of Texas is the city of"
print("PATH:", PATH, "| prompt:", repr(PROMPT))
"""),
    md("""
### 0b · (Optional, at the break) pre-download Gemma 2 2B + transcoders in the background

Only for the `"gemma2"` path. Run this cell **at the break** in the runtime you will use for NB4 (T4, fresh runtime, after the HF login cell below has found your token). It starts a background download of ≈ 18 GB into the Hugging Face cache and returns immediately; the notebook stays usable. Check progress with the next cell. If the runtime is recycled, the cache is lost and you must start again: Colab's free tier gives a fresh disk per runtime (≈ 100 GB, enough for this).
"""),
    code("""
PREDOWNLOAD = False   # set True and run this cell at the break (gemma2 path only)
import subprocess, sys
if PREDOWNLOAD:
    _script = (
        "from huggingface_hub import snapshot_download\\n"
        "snapshot_download('google/gemma-2-2b', allow_patterns=['*.json','*.safetensors','tokenizer*'])\\n"
        "snapshot_download('mwhanna/gemma-scope-transcoders', allow_patterns=['config.yaml','layer_*.safetensors'])\\n"
        "print('DONE')\\n")
    DL = subprocess.Popen([sys.executable, "-c", _script], stdout=open("predownload.log", "w"), stderr=subprocess.STDOUT)
    print("Background download started (pid", DL.pid, "). Check with the next cell; keep working meanwhile.")
else:
    print("Pre-download not requested (PREDOWNLOAD = False).")
"""),
    code("""
# Progress of the background download (re-run whenever you like)
import shutil, pathlib
cache = pathlib.Path(os.environ.get("HF_HUB_CACHE", pathlib.Path.home() / ".cache" / "huggingface" / "hub"))
repos = [cache / "models--google--gemma-2-2b", cache / "models--mwhanna--gemma-scope-transcoders"]
size = sum(f.stat().st_size for r in repos if r.exists() for f in (r / "blobs").glob("*") if f.is_file()) / 1e9
print(f"downloaded so far: {size:.1f} GB of ~18 GB (Gemma 2 2B ~10 GB + transcoders ~8 GB)")
if pathlib.Path("predownload.log").exists():
    print("log tail:", pathlib.Path("predownload.log").read_text()[-300:])
"""),
    md("""
### Hugging Face login (model paths only)

Gemma 2 and Gemma 3 weights are **gated**: accept the licence at <https://huggingface.co/google/gemma-2-2b> (and/or <https://huggingface.co/google/gemma-3-270m>) with your account, and keep the `HF_TOKEN` Colab secret from NB0. The transcoders are not gated.
"""),
    code("""
HF_TOKEN = None
if PATH != "neuronpedia":
    if IN_COLAB:
        try:
            from google.colab import userdata
            HF_TOKEN = userdata.get("HF_TOKEN")
        except Exception as e:
            print(f"No usable Colab secret HF_TOKEN ({type(e).__name__}).")
    from huggingface_hub import get_token, login
    HF_TOKEN = HF_TOKEN or os.environ.get("HF_TOKEN") or get_token()
    if HF_TOKEN:
        login(token=HF_TOKEN, add_to_git_credential=False)
    elif IN_COLAB:
        from huggingface_hub import notebook_login
        notebook_login()
    print("token found" if (HF_TOKEN or get_token()) else "no token (needed for gated Gemma repos)")
"""),
    md("""
## 1 · Load the replacement model

`ReplacementModel` wraps the base model and plugs in one **transcoder** per layer: a sparse dictionary trained to imitate each MLP's input→output map. Whatever the transcoder misses is kept as an **error node**, so the model's output is unchanged.

| PATH | model | transcoders (`transcoder_set`) | backend | Neuronpedia feature pages |
|---|---|---|---|---|
| `gemma2` | `google/gemma-2-2b` | `"gemma"` = `mwhanna/gemma-scope-transcoders` (Gemma Scope, 16k/layer) | TransformerLens | `gemma-2-2b/<layer>-gemmascope-transcoder-16k/<id>` |
| `gemma3-270m` | `google/gemma-3-270m` | `mwhanna/gemma-scope-2-270m-pt/transcoder_all/width_16k_l0_small_affine` (Gemma Scope 2) | nnsight (required for Gemma 3) | some layers only (see note below) |
| `neuronpedia` | none | (graph precomputed with the `gemma` set) | none | as `gemma2` |
"""),
    code("""
model = None
TRANSCODERS = {"gemma2": "gemma",
               "gemma3-270m": "mwhanna/gemma-scope-2-270m-pt/transcoder_all/width_16k_l0_small_affine"}
NP_MODEL, NP_SET = "gemma-2-2b", "gemmascope-transcoder-16k"

def np_feature_url(layer, idx):
    return f"https://www.neuronpedia.org/{NP_MODEL}/{layer}-{NP_SET}/{idx}"

if PATH != "neuronpedia":
    from circuit_tracer import ReplacementModel, attribute
    t0 = time.time()
    try:
        if PATH == "gemma2":
            model = ReplacementModel.from_pretrained("google/gemma-2-2b", "gemma", backend="transformerlens",
                                                     dtype=torch.bfloat16, device=torch.device(device))
        else:
            from circuit_tracer.utils.hf_utils import load_transcoder_from_hub
            dtype = torch.bfloat16 if device == "cuda" else torch.float32
            tcs, _ = load_transcoder_from_hub(TRANSCODERS[PATH], device=torch.device(device), dtype=dtype)
            repo = os.environ.get("NB4_GEMMA3_REPO", "google/gemma-3-270m")
            model = ReplacementModel.from_pretrained_and_transcoders(repo, tcs, backend="nnsight",
                                                                     device=torch.device(device), dtype=dtype)
            NP_MODEL, NP_SET = "gemma-3-270m", "gemmascope-2-transcoder-16k"
        print(f"loaded in {time.time()-t0:.0f}s")
    except Exception as e:
        print(f"Could not load the model: {type(e).__name__}: {str(e)[:300]}")
        print("Most common cause: Gemma licence not accepted for your HF account, or no HF_TOKEN. "
              "Falling back to PATH = 'neuronpedia'.")
        if not AUTO_FALLBACK:
            raise
        PATH, model = "neuronpedia", None
"""),
    code("""
def top_next_tokens(logits, k=5):
    p = logits[0, -1].float().softmax(-1)
    v, i = p.topk(k)
    return [(model.tokenizer.decode([int(t)]), round(float(x), 3)) for x, t in zip(v, i)]

if model is not None:
    tok = model.tokenizer
    STR_TOKENS = [tok.decode([t]) for t in tok(PROMPT).input_ids]
    AUSTIN = tok.encode(" Austin", add_special_tokens=False)[0]
    base_logits, base_acts = model.get_activations(PROMPT)
    print("tokens:", STR_TOKENS)
    print("top next tokens:", top_next_tokens(base_logits))
"""),
    md("""
## 2 · Build the attribution graph (≈1–3 min on a T4)

`attribute()` runs one forward pass, records every active transcoder feature, then does backward passes to get the **direct effect of every node on every other node** (with attention patterns and normalisation frozen). We ask it to explain the logit of ` Austin` only.

Memory knobs (from the library's demos): `batch_size` (backward passes per batch), `max_feature_nodes` (cap on feature nodes), `offload` (`"disk"` on Colab, as in the library's own Colab demo: parts of the model not needed during attribution are moved off the GPU). If you hit *CUDA out of memory*, halve `batch_size` and rerun.
"""),
    code("""
graph = None
if model is not None:
    small = PATH == "gemma3-270m" or device == "cpu"
    t0 = time.time()
    graph = attribute(PROMPT, model,
                      attribution_targets=[" Austin"],
                      batch_size=64 if small else 256,
                      max_feature_nodes=1024 if small else 4096,
                      offload=None if small else ("disk" if IN_COLAB else "cpu"),   # as in the library's Colab demo
                      verbose=True)
    print(f"attribution took {time.time()-t0:.0f}s | adjacency matrix {tuple(graph.adjacency_matrix.shape)}")
"""),
    md("""
## 3 · Prune, then list the most important features

A raw graph has thousands of nodes. **Pruning** keeps the smallest set of nodes (and edges) that accounts for a given fraction of the influence on the output logit (here 80% of nodes' influence, 98% of edges').

Node bookkeeping in `circuit-tracer`: the adjacency matrix is ordered `[features | error nodes | token embeddings | logits]`; feature *i* is `graph.active_features[graph.selected_features[i]]` = `(layer, position, feature_index)`.

On the **neuronpedia** path we instead download the featured graph `gemma-fact-dallas-austin` (made with this same library on Gemma 2 2B) and read the same information from its JSON.
"""),
    code(f"""
FEATURED_URL = "{FEATURED}"
Node = namedtuple("Node", ["layer", "pos", "feature", "influence", "activation"])

def nodes_from_graph(graph, node_threshold=0.8, edge_threshold=0.98):
    from circuit_tracer.graph import prune_graph
    node_mask, edge_mask, cum = prune_graph(graph, node_threshold, edge_threshold)
    n_feat = len(graph.selected_features)
    out = []
    for i in range(n_feat):
        if node_mask[i]:
            l, p, f = graph.active_features[graph.selected_features[i]].tolist()
            out.append(Node(int(l), int(p), int(f), float(cum[i]), float(graph.activation_values[graph.selected_features[i]])))
    print(f"kept {{int(node_mask.sum())}} nodes ({{len(out)}} features) and {{int(edge_mask.sum())}} edges")
    return sorted(out, key=lambda n: n.influence)          # lower cumulative score = more important

def nodes_from_neuronpedia(slug="gemma-fact-dallas-austin"):
    with urllib.request.urlopen(f"https://www.neuronpedia.org/api/graph/gemma-2-2b/{{slug}}", timeout=30) as r:
        meta = json.load(r)
    with urllib.request.urlopen(meta["url"], timeout=60) as r:
        g = json.load(r)
    toks = g["metadata"]["prompt_tokens"]
    out = []
    for n in g["nodes"]:
        if n["feature_type"] == "cross layer transcoder":       # = transcoder feature node
            out.append(Node(int(n["layer"]), int(n["ctx_idx"]), int(n["node_id"].split("_")[1]),
                            float(n["influence"]), float(n["activation"])))
    print(f"featured graph: {{len(g['nodes'])}} nodes ({{len(out)}} features), {{len(g['links'])}} links; "
          f"pruning used: {{g['metadata'].get('pruning_settings')}}")
    return toks, sorted(out, key=lambda n: n.influence), g

if graph is not None:
    NODES = nodes_from_graph(graph)
    TOKS = [tok.decode([int(t)]) for t in graph.input_tokens]
else:
    TOKS, NODES, NP_GRAPH = nodes_from_neuronpedia()
print("tokens:", list(enumerate(TOKS)))
"""),
    code("""
NP_LABELS = os.environ.get("NB4_NP_LABELS", "1") == "1"

def np_label(layer, idx):
    if not NP_LABELS:
        return ""
    try:
        with urllib.request.urlopen(f"https://www.neuronpedia.org/api/feature/{NP_MODEL}/{layer}-{NP_SET}/{idx}", timeout=8) as r:
            ex = json.load(r).get("explanations") or []
        return ex[0]["description"].strip() if ex else ""
    except Exception:
        return ""   # not every (model, transcoder set) has public dashboards

def show_nodes(nodes, k=15, positions=None):
    shown = [n for n in nodes if positions is None or n.pos in positions][:k]
    print(f"{'layer':>5} {'pos':>4} {'token':>12} {'feature':>8} {'act':>7}  label / link")
    for n in shown:
        print(f"{n.layer:>5} {n.pos:>4} {TOKS[n.pos]!r:>12} {n.feature:>8} {n.activation:7.1f}  "
              f"{np_label(n.layer, n.feature)[:40]:<40} {np_feature_url(n.layer, n.feature)}")

show_nodes(NODES)
"""),
    md("""
### Your turn (≈2 min): where is the intermediate concept?

Write `position_of(word)` that returns the index in `TOKS` of the token containing `word` (e.g. `" Dallas"`, or `" Texas"` on the light path), then list the top features **at that position**. Look at their labels and Neuronpedia pages: is there a *Texas* feature? At which layers?
"""),
    exercise(
        student="""
def position_of(word):
    # TODO: return the index i such that TOKS[i] contains `word` (strip spaces when comparing)
    raise NotImplementedError
""",
        solution="""
def position_of(word):
    return next(i for i, t in enumerate(TOKS) if word.strip() and word.strip() in t)
""",
    ),
    code("""
def _ref_position_of(word):
    return next(i for i, t in enumerate(TOKS) if word.strip() and word.strip() in t)
KEY_WORD = " Texas" if PATH == "gemma3-270m" else " Dallas"
try:
    KEY_POS = position_of(KEY_WORD)
except (NotImplementedError, NameError, StopIteration, TypeError) as e:
    print(f"(using the reference position_of: {type(e).__name__})")
    KEY_POS = _ref_position_of(KEY_WORD)
print(f"{KEY_WORD!r} is at position {KEY_POS}; top features there:")
show_nodes(NODES, k=10, positions=[KEY_POS])
print("\\nTop features at the last position (where the answer is produced):")
show_nodes(NODES, k=8, positions=[len(TOKS) - 1])
"""),
    md("""
## 4 · See the whole graph

**Option A, Neuronpedia (works for everyone, recommended in the session).** Open the featured graph, built with this library for the same prompt on Gemma 2 2B. Hover nodes to see their top activations; the annotated *supernodes* group features into **capital → say a capital**, **state**, **Texas** and **say Austin**.
"""),
    code("""
from IPython.display import IFrame, display, HTML
display(HTML(f'<a href="{FEATURED_URL}" target="_blank">Open the featured Dallas → Austin graph on Neuronpedia</a>'))
display(IFrame(FEATURED_URL, width="100%", height=650))
"""),
    md("""
**Option B, your own graph in Colab (model paths).** `create_graph_files` prunes the graph and writes the JSON the frontend reads; `serve` starts the library's local frontend, which Colab shows in an iframe through its kernel-port proxy. Feature *labels and examples* in that viewer are fetched from Neuronpedia's servers and are only available for the Gemma 2 2B `gemma` set.

**Option C, make one on Neuronpedia (no install).** On <https://www.neuronpedia.org/gemma-2-2b/graph> click **+ New Graph**, paste the prompt, and generate. To intervene there, pin nodes and click **Steer**. (Uploading a graph file you made yourself goes through <https://www.neuronpedia.org/graph/validator>; the model must exist on Neuronpedia under the graph's `scan` name.)
"""),
    code("""
SERVER = None
if graph is not None:
    from circuit_tracer.utils import create_graph_files
    create_graph_files(graph_or_path=graph, slug="dallas-austin-mine", output_path="./graph_files",
                       node_threshold=0.8, edge_threshold=0.98)
    print("graph files:", sorted(os.listdir("./graph_files")))
    if IN_COLAB:
        from circuit_tracer.frontend.local_server import serve
        PORT = 8046
        SERVER = serve(data_dir="./graph_files/", port=PORT)
        from google.colab import output as colab_output
        colab_output.serve_kernel_port_as_iframe(PORT, path="/index.html", height="800px", cache_in_notebook=True)
    else:
        print("Outside Colab: run circuit_tracer.frontend.local_server.serve('./graph_files', port=8046) "
              "and open http://localhost:8046/index.html")
"""),
    md("""
## 4b · Neuronpedia path: your own graph, your own intervention (≈ 8 min)

Everyone on the `neuronpedia` path does this; model-path users can do it too. Neuronpedia runs the **same `circuit-tracer` code** on Gemma 2 2B with the Gemma Scope transcoders, on its own GPUs. No account needed (if you are not signed in, keep your graph links yourself).

### A · Generate a graph for your own prompt, in the browser (≈ 2 min, mostly waiting)

1. Open <https://www.neuronpedia.org/gemma-2-2b/graph>.
2. Click **+ New Graph** (top left). Keep **Model** = *Gemma-2-2B* and **Source Set** = *GEMMASCOPE-TRANSCODER-16K*.
3. In **Prompt to Complete** type a two-hop prompt of your own, e.g. `Fact: the capital of the state containing Ciudad Juárez is` (→ *Chihuahua*) or `Fact: the capital of the state containing Puerto Vallarta is` (→ *Guadalajara*).
4. Look at the **Next Token** list under the prompt: the answer you want to explain should be at or near the top. If it is not, rephrase.
5. Click **Start Generation** (about a minute), then click the link to open your graph.

Prefer code? The next cell does steps 2–5 through Neuronpedia's public API (`/api/graph/generate`) and prints the link.

### B · Read it (≈ 2 min)

- **Link graph** (top left): tokens at the bottom, logits at the top, features in between. **Hover** a node to see its dashboard (bottom right); **click** it to see its inputs/outputs (top right).
- Find features at the **city token** (*Dallas*, *Juárez*...) in the middle layers with labels like *Texas* or *Mexico*. That is the intermediate hop.
- The slider **Show Nodes Accounting for X% of the Influence** prunes the graph; lower it to see only the most important nodes.

### C · Break it on purpose (≈ 3 min)

1. Click a *Texas*-like node, then **Pin Node**: it appears in the **Subgraph** panel (bottom left). Pin 2–3 of them, plus the output logit node.
2. In the subgraph, click **Steer**.
3. Turn the pinned *Texas* features **down** (negative strength, e.g. −1×) and run the steering.
4. Compare the default and steered next tokens. In Neuronpedia's own walkthrough, turning *Texas* down on the Dallas graph gives **Albany** instead of *Austin*.
5. (Stretch) **+ Add Feature**, search for a *California* feature, set it **up** at the *Dallas* position: does *Sacramento* appear?

The cells below do the same intervention from code, via `/api/steer-logits` (the endpoint behind that **Steer** button), so you also get exact numbers.
"""),
    code("""
NP_API = "https://www.neuronpedia.org/api"

def np_post(path, body, timeout=180):
    req = urllib.request.Request(NP_API + path, data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.load(r)

def np_next_tokens(prompt, k=5):
    \"\"\"Gemma 2 2B's top next tokens for a prompt (Neuronpedia graph server).\"\"\"
    d = np_post("/graph/tokenize", {"modelId": "gemma-2-2b", "prompt": prompt, "maxNLogits": k, "desiredLogitProb": 0.99})
    return d["input_tokens"], [(x["token"], round(x["probability"], 3)) for x in d["salient_logits"]]

MY_PROMPT = "Fact: the capital of the state containing Ciudad Juárez is"   # ✍️ try your own two-hop prompt
try:
    toks, nxt = np_next_tokens(MY_PROMPT)
    print("tokens:", list(enumerate(toks)))
    print("Gemma 2 2B next tokens:", nxt)
except Exception as e:
    print(f"Neuronpedia API not reachable ({type(e).__name__}); use the browser steps.")
"""),
    code("""
GENERATE_MY_GRAPH = True     # set False to skip (e.g. offline)
MY_GRAPH_URL = None
if GENERATE_MY_GRAPH:
    import random
    slug = "micai-" + "".join(c if c.isalnum() else "-" for c in MY_PROMPT.lower())[:30].strip("-") + f"-{random.randint(0, 10**6)}"
    try:
        t0 = time.time()
        r = np_post("/graph/generate", {"prompt": MY_PROMPT, "modelId": "gemma-2-2b", "slug": slug,
                                        "maxNLogits": 10, "desiredLogitProb": 0.95, "nodeThreshold": 0.8,
                                        "edgeThreshold": 0.85, "maxFeatureNodes": 5000}, timeout=300)
        MY_GRAPH_URL, MY_GRAPH_JSON = r["url"], r["s3url"]
        print(f"graph ready in {time.time()-t0:.0f}s: {r['numNodes']} nodes, {r['numLinks']} links")
        print("OPEN IT:", MY_GRAPH_URL)
    except Exception as e:
        print(f"Graph generation failed ({type(e).__name__}: {e}). Use the browser steps above, or the featured Dallas graph.")
"""),
    code("""
# Which features sit at the city token of YOUR graph, ranked by influence?
if MY_GRAPH_URL:
    with urllib.request.urlopen(MY_GRAPH_JSON, timeout=60) as r:
        g_mine = json.load(r)
    TOKS_MINE = g_mine["metadata"]["prompt_tokens"]
    CITY_POS = len(TOKS_MINE) - 2        # the token just before " is" (for 'Ciudad Juárez': ' Juárez')
    mine = [n for n in g_mine["nodes"] if n["feature_type"] == "cross layer transcoder" and n["ctx_idx"] == CITY_POS]
    mine = sorted(mine, key=lambda n: n["influence"])[:10]    # lower cumulative influence = more important
    print(f"top features at position {CITY_POS} ({TOKS_MINE[CITY_POS]!r}):")
    for n in mine:
        l, idx = int(n["layer"]), int(n["node_id"].split("_")[1])
        print(f"  layer {l:>2}  feature {idx:>6}  {np_label(l, idx)[:50]:<50} {np_feature_url(l, idx)}")
"""),
    md("""
### C (in code) · Turn *Texas* down and watch *Austin* drop

`/api/steer-logits` takes a list of features, each with its **layer**, **index**, the **token position** where it is active, and a **delta** (how much to add to its activation; the UI uses *multiplier × the feature's top known activation*). Or `ablate: True` to set it to zero. We use the **Texas supernode** that the library authors annotated in the featured graph, then a **control**: the same intervention on six *other* features active at the *Dallas* position.

### ✍️ Predict

Ablate (zero) vs steer to −1×: which hurts *Austin* more? What will the model say instead?

✍️ My prediction: ____
"""),
    code("""
NP_TEXAS = [(20, 15589), (19, 7477), (16, 25), (4, 13154), (14, 2268), (7, 6861)]   # (layer, feature) at ' Dallas'
NP_CONTROL = [(0, 5626), (17, 9905), (15, 15087), (4, 6931), (17, 6268), (13, 13583)]  # other features, not Texas
DALLAS = "Fact: The capital of the state containing Dallas is"
DALLAS_POS = 9

_MAXACT = {}
def np_max_act(layer, idx):
    if (layer, idx) not in _MAXACT:
        with urllib.request.urlopen(f"{NP_API}/feature/gemma-2-2b/{layer}-gemmascope-transcoder-16k/{idx}", timeout=20) as r:
            _MAXACT[(layer, idx)] = json.load(r)["maxActApprox"]
    return _MAXACT[(layer, idx)]

def np_steer(prompt, feats, pos, multiplier=None, ablate=False):
    \"\"\"Steer (multiplier x top activation) or ablate features at `pos`; returns (default, steered) next-token lists.\"\"\"
    fs = [dict(layer=l, index=i, token_active_position=pos, steer_position=pos, steer_generated_tokens=False,
               delta=None if ablate else multiplier * np_max_act(l, i), ablate=ablate) for l, i in feats]
    d = np_post("/steer-logits", {"modelId": "gemma-2-2b", "sourceSetName": "gemmascope-transcoder-16k", "prompt": prompt,
                                  "features": fs, "nTokens": 2, "topK": 5, "freezeAttention": True,
                                  "temperature": 0, "presencePenalty": 0, "seed": 16})
    first = lambda L: [(x["token"], round(x["prob"], 3)) for x in next(t for t in L if t["top_logits"])["top_logits"]]
    return first(d["DEFAULT_LOGITS_BY_TOKEN"]), first(d["STEERED_LOGITS_BY_TOKEN"])

def p_of(tok, dist):
    return dict(dist).get(tok, 0.0)

try:
    default, _ = np_steer(DALLAS, NP_TEXAS[:1], DALLAS_POS, multiplier=0.0)
    print(f"{'original':<26} P(Austin) = {p_of(' Austin', default):.3f}  {default}")
    for name, feats, kw in [("Texas ablated", NP_TEXAS, dict(ablate=True)),
                            ("Texas steered -1x", NP_TEXAS, dict(multiplier=-1.0)),
                            ("control features -1x", NP_CONTROL, dict(multiplier=-1.0))]:
        _, st = np_steer(DALLAS, feats, DALLAS_POS, **kw)
        print(f"{name:<26} P(Austin) = {p_of(' Austin', st):.3f}  {st}")
except Exception as e:
    print(f"Neuronpedia steering API not reachable ({type(e).__name__}: {e}). Do part C in the browser instead.")
"""),
    code("""
# Stretch: Texas off, California on (California features from the authors' Oakland -> Sacramento graph)
NP_CALIFORNIA = [(6, 13909, 9), (8, 14641, 9), (14, 12562, 9), (22, 4367, 10), (21, 2464, 10)]   # (layer, feature, position)
try:
    fs = [dict(layer=l, index=i, token_active_position=DALLAS_POS, steer_position=DALLAS_POS, steer_generated_tokens=False,
               delta=-1.0 * np_max_act(l, i), ablate=False) for l, i in NP_TEXAS]
    fs += [dict(layer=l, index=i, token_active_position=p, steer_position=p, steer_generated_tokens=False,
                delta=0.5 * np_max_act(l, i), ablate=False) for l, i, p in NP_CALIFORNIA]
    d = np_post("/steer-logits", {"modelId": "gemma-2-2b", "sourceSetName": "gemmascope-transcoder-16k", "prompt": DALLAS,
                                  "features": fs, "nTokens": 2, "topK": 5, "freezeAttention": True,
                                  "temperature": 0, "presencePenalty": 0, "seed": 16})
    st = [(x["token"], round(x["prob"], 3)) for x in next(t for t in d["STEERED_LOGITS_BY_TOKEN"] if t["top_logits"])["top_logits"]]
    print(f"Texas -1x, California +0.5x: P(Sacramento) = {p_of(' Sacramento', st):.3f}  {st}")
    print("Try 1.0x for California: it overshoots into other California cities (Los Angeles, Davis...).")
except Exception as e:
    print(f"(stretch skipped: {type(e).__name__})")
"""),
    md("""
### Your turn (≈ 3 min): break **your** graph

Pick 2–4 features from **your** graph's city-token list above that look like the intermediate hop (e.g. *Mexico*, *Chihuahua*, *Texas*...) and put them in `MY_FEATURES` as `(layer, feature)` pairs. The cell steers them to −1× at `CITY_POS` and reports what happens to your answer. If you skip it, the top 3 features of your graph are used.
"""),
    exercise(
        student="""
MY_ANSWER = " Chihuahua"   # ✍️ the answer token your prompt should produce (leading space!)
MY_FEATURES = []           # TODO: e.g. [(19, 6810), (17, 14871)]  -- (layer, feature) from your graph's list
""",
        solution="""
MY_ANSWER = " Chihuahua"
MY_FEATURES = [(19, 6810), (17, 14871), (14, 10090)]   # 'Mexico', 'discussions of Mexico', 'Latin American locations' (Juárez graph)
""",
    ),
    code("""
if MY_GRAPH_URL:
    feats = MY_FEATURES or [(int(n["layer"]), int(n["node_id"].split("_")[1])) for n in mine[:3]]
    try:
        default, st = np_steer(MY_PROMPT, feats, CITY_POS, multiplier=-1.0)
        print(f"features {feats} at position {CITY_POS} ({TOKS_MINE[CITY_POS]!r}), steered to -1x")
        print(f"before: P({MY_ANSWER!r}) = {p_of(MY_ANSWER, default):.3f}  {default}")
        print(f"after:  P({MY_ANSWER!r}) = {p_of(MY_ANSWER, st):.3f}  {st}")
    except Exception as e:
        print(f"steering failed ({type(e).__name__}: {e})")
else:
    print("No graph of your own (generation skipped or failed): use the browser steps.")
"""),
    md("""
**Interpret.** In our test run (Gemma 2 2B on Neuronpedia): P(Austin) = 0.44 originally; ablating the six *Texas* features → 0.18 (and *Oklahoma*, *Sacramento* appear); steering them to −1× pushes *Austin* out of the top 5 (*Albany* appears instead, as in Neuronpedia's walkthrough); the same −1× on six other active features at *Dallas* → 0.38. Texas off + California on at 0.5× puts *Sacramento* at the top (tied). This is what "validating a graph by intervention" means: the graph *predicted* that these features carry the intermediate hop, and breaking them breaks the answer, while breaking others does not.
"""),
    md("""
## 5 · (Model paths) Break it on purpose in code: turn *Texas* down

A graph is a **hypothesis**; interventions **test** it. If those features carry "Texas", then scaling them to **−2×** their normal value should lower the probability of *Austin*, while the rest of the model stays untouched.

`model.feature_intervention(prompt, [(layer, position, feature_index, new_value), ...])` sets transcoder features to new values and lets the effect propagate through the rest of the model.

Which features do we suppress? On the `gemma2` path we use the **Texas supernode** annotated by the library authors in the featured graph (same features shown on the slides). On the light path we take the top graph features at the *Texas* token. Then a **control**: suppress the same number of *random* active features at that position.

### ✍️ Predict

How much will P(Austin) drop: barely, by half, to almost zero? What will become the top answer instead?

✍️ My prediction: ____
"""),
    code("""
# Texas supernode of the featured graph (layer, position, feature) -- from the library's tutorial annotation
TEXAS_GEMMA2 = [(20, 9, 15589), (19, 9, 7477), (16, 9, 25), (4, 9, 13154), (14, 9, 2268), (7, 9, 6861)]
SCALE = -2.0

def report(logits, tag):
    p = logits[0, -1].float().softmax(-1)
    print(f"{tag:<28} P(Austin) = {float(p[AUSTIN]):.3f}   top-5: {top_next_tokens(logits)}")
    return float(p[AUSTIN])

if model is not None:
    if PATH == "gemma2":
        TEXAS = TEXAS_GEMMA2
    else:
        TEXAS = [(n.layer, n.pos, n.feature) for n in NODES if n.pos == KEY_POS][:8]
    print("features to suppress:", TEXAS)
    with torch.no_grad():
        base, _ = model.feature_intervention(PROMPT, [])
        p0 = report(base, "original")
        iv = [(l, p, f, SCALE * base_acts[l, p, f]) for l, p, f in TEXAS]
        new, _ = model.feature_intervention(PROMPT, iv)
        p1 = report(new, f"Texas features x{SCALE}")
        g = torch.Generator().manual_seed(0)
        active = (base_acts[:, KEY_POS, :] > 0).nonzero().cpu()
        pick = active[torch.randperm(len(active), generator=g)[:len(TEXAS)]]
        iv_rand = [(int(l), KEY_POS, int(f), SCALE * base_acts[int(l), KEY_POS, int(f)]) for l, f in pick]
        rnd, _ = model.feature_intervention(PROMPT, iv_rand)
        p2 = report(rnd, f"random features x{SCALE}")
else:
    print("No local model (neuronpedia path): you already did this intervention in section 4b via Neuronpedia.")
"""),
    md("""
**Interpret.** Compare *Texas features* with the *random* control. A drop that the control does not produce supports the graph's story: the model routes *Dallas → Texas → Austin* through those features. A small effect is also informative: the model may hold the same information redundantly (in other features, other positions, or the error nodes), and a graph only shows **direct** effects in a linearised model.

### Stretch (≈3 min, model paths): swap in another state

Take the features that distinguish a California prompt from ours at the same position, switch *Texas* off and *California* on. Does *Sacramento* appear?
"""),
    exercise(
        student="""
def swap_state(other_prompt, k=10, on_scale=2.0, off_scale=-2.0):
    # TODO: 1) _, other_acts = model.get_activations(other_prompt)
    #       2) at position KEY_POS, find the k features where other_acts - base_acts is largest (California-like)
    #          and the k where base_acts - other_acts is largest (Texas-like); flat index i -> (i // n_feat, i % n_feat)
    #       3) build interventions: Texas-like set to off_scale * base value, California-like set to on_scale * other value
    #       4) return model.feature_intervention(PROMPT, interventions)[0]   (the logits)
    raise NotImplementedError
""",
        solution="""
def swap_state(other_prompt, k=10, on_scale=2.0, off_scale=-2.0):
    _, other_acts = model.get_activations(other_prompt)
    diff = base_acts[:, KEY_POS, :] - other_acts[:, KEY_POS, :]
    n_feat = diff.shape[-1]
    tex = [(int(i) // n_feat, KEY_POS, int(i) % n_feat) for i in diff.flatten().topk(k).indices]
    cal = [(int(i) // n_feat, KEY_POS, int(i) % n_feat) for i in (-diff).flatten().topk(k).indices]
    iv = [(l, p, f, off_scale * base_acts[l, p, f]) for l, p, f in tex]
    iv += [(l, p, f, on_scale * other_acts[l, p, f]) for l, p, f in cal]
    return model.feature_intervention(PROMPT, iv)[0]
""",
    ),
    code("""
OTHER_PROMPT = PROMPT.replace("Dallas", "Oakland").replace("Texas", "California")
if model is not None and len(model.tokenizer(OTHER_PROMPT).input_ids) == len(STR_TOKENS):
    SAC = model.tokenizer.encode(" Sacramento", add_special_tokens=False)[0]
    try:
        with torch.no_grad():
            swapped = swap_state(OTHER_PROMPT)
        p = swapped[0, -1].float().softmax(-1)
        print(f"your swap:  P(Austin) = {float(p[AUSTIN]):.3f}  P(Sacramento) = {float(p[SAC]):.3f}  top-5: {top_next_tokens(swapped)}")
    except NotImplementedError:
        print("(stretch exercise skipped)")
    if PATH == "gemma2":
        # The library authors' annotated California supernodes (graph 'gemma-fact-oakland-sacramento'),
        # set to 2x their activation on the Oakland prompt, while Texas goes to -2x (circuit-tracer tutorial).
        CALIFORNIA_GEMMA2 = [(22, 10, 4367), (21, 10, 2464), (6, 9, 13909), (8, 9, 14641), (14, 9, 12562)]
        with torch.no_grad():
            _, oak_acts = model.get_activations(OTHER_PROMPT)
            iv = [(l, p_, f, -2.0 * base_acts[l, p_, f]) for l, p_, f in TEXAS_GEMMA2]
            iv += [(l, p_, f, 2.0 * oak_acts[l, p_, f]) for l, p_, f in CALIFORNIA_GEMMA2]
            ann, _ = model.feature_intervention(PROMPT, iv)
        p = ann[0, -1].float().softmax(-1)
        print(f"annotated:  P(Austin) = {float(p[AUSTIN]):.3f}  P(Sacramento) = {float(p[SAC]):.3f}  top-5: {top_next_tokens(ann)}")
elif model is not None:
    print("The two prompts tokenize to different lengths; pick another city/state pair.")
"""),
    md("""
**Interpret.** On Gemma 2 2B the library authors report that *Texas off + California on* makes **Sacramento** the top answer. On the light Gemma 3 270M path we observed that suppressing Texas works (P(Austin) 0.49 → 0.21; random control 0.52) but our naive swap did **not** produce Sacramento: turning a concept *off* is easier than writing a new one *in*, and "the features that differ between two prompts" is a crude way to pick what to write.
"""),
    md("""
## 6 · What this does *not* show

- **Local to one prompt.** The graph explains this prompt's ` Austin` logit, not "how the model does geography". Another city, phrasing or language can use different features.
- **Error nodes.** Whatever the transcoders fail to reconstruct becomes error nodes. If they carry much of the influence, part of the mechanism is simply not in the picture.
- **Attention is partly hidden.** Attention patterns are frozen during attribution: the graph shows *that* information moved from the *Dallas* position to the last position, not *why* attention chose to move it (QK circuits are not traced).
- **Direct, linear effects of a replacement model.** Edges are computed in a linearised local replacement model. They are hypotheses about the real model, which is why **interventions are required**, and even interventions can be off-distribution (−2× is not a natural activation).
- **Labels come from somewhere else.** Feature labels are auto-interpretations of top activations; check examples before trusting a name.
- **Small model, small effects.** On the light path (270M) the effects are weaker and the two-hop prompt fails entirely; the model has to be capable of the behaviour before you can trace it.
"""),
    md("""
## Takeaway

An attribution graph turns *"the model knows the capital of the state containing Dallas"* into a concrete, testable hypothesis: **Dallas → Texas features → say-Austin features → Austin**. The graph proposes; interventions dispose. That loop (trace, then break it on purpose) is the core of circuit-level interpretability.

**Next (Block 5):** a plain probe can match an SAE feature, and patching tests what a model relies on. Víctor applies both to an LLM judge.
"""),
    code("""
if SERVER is not None:
    SERVER.stop()   # stop the local graph server when you are done
"""),
]

if __name__ == "__main__":
    build(cells, "NB4_circuit_tracing.ipynb", "NB4_circuit_tracing_solutions.ipynb")
