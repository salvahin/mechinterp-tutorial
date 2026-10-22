"""Generator for NB3 (features, steering and probes). Run: python3 notebooks/src/build_nb3.py

One source -> notebooks/student/NB3_features_steering_probes.ipynb
            + notebooks/solutions/NB3_features_steering_probes_solutions.ipynb

Model switch inside the notebook: MODEL_CHOICE = "gemma3" (Gemma 3 1B IT + Gemma Scope 2)
or "gpt2" (GPT-2 small + gpt2-small-res-jb, ungated, runs anywhere).
For local testing, env vars NB3_MODEL_CHOICE / NB3_GEMMA_REPO / NB3_GEMMA_DTYPE override defaults.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from nbgen import md, code, exercise, build, PINS, SLIDES_LINK  # noqa: E402

P = PINS

# ---------------------------------------------------------------------------
# Built-in data (hand-written, balanced). 4 topics x (25 about Mexico + 25 not).
# "Not Mexico" deliberately includes Spanish-speaking places (Spain, Argentina,
# Peru, Cuba, Colombia...) so "Spanish words" alone is not enough to solve it.
# ---------------------------------------------------------------------------
DATA = r'''
DATA = {
 "food": {
  "mexico": [
   "We ate tacos al pastor from a street stand in Mexico City.",
   "My aunt cooks mole poblano with more than twenty ingredients.",
   "Tamales wrapped in corn husks are a Christmas tradition in Mexico.",
   "The chilaquiles came with green salsa, cream and a fried egg.",
   "Pozole is a hominy stew that people eat on Independence Day in Mexico.",
   "He ordered cochinita pibil, a slow-roasted pork dish from Yucatán.",
   "Elote vendors sell grilled corn with mayonnaise, cheese and chili.",
   "A good guacamole needs ripe avocados, lime, onion and serrano pepper.",
   "Birria tacos from Jalisco are served with a cup of consommé.",
   "We drank horchata and agua de jamaica with lunch.",
   "Chiles en nogada are decorated in the colours of the Mexican flag.",
   "The tortillería on our street makes fresh corn tortillas every morning.",
   "Tlayudas are large crispy tortillas topped with beans and Oaxaca cheese.",
   "Pan de muerto is baked for the Day of the Dead celebrations.",
   "Mezcal is distilled from agave in the hills of Oaxaca.",
   "She learned to make sopes and gorditas from her grandmother in Puebla.",
   "Carnitas are pork pieces slowly cooked in lard, a speciality of Michoacán.",
   "A plate of enchiladas suizas arrived covered in melted cheese.",
   "Churros with hot chocolate are a popular breakfast in Mexico City.",
   "Tequila can only be produced in certain regions of Mexico.",
   "The market in Oaxaca sells chapulines, toasted grasshoppers with lime.",
   "Quesadillas in Mexico City do not always contain cheese.",
   "Atole is a warm corn drink often served with tamales.",
   "Cajeta is a goat milk caramel made in Celaya, Guanajuato.",
   "We shared a molcajete full of grilled meat, nopales and salsa.",
  ],
  "other": [
   "We ate ramen from a small stand in Tokyo.",
   "My aunt cooks a lamb tagine with dried apricots and cumin.",
   "Mince pies are a Christmas tradition in England.",
   "The pancakes came with maple syrup, butter and fried bacon.",
   "Borscht is a beet soup that many families eat in Ukraine.",
   "He ordered pad thai with shrimp and crushed peanuts in Bangkok.",
   "Pretzel vendors in Munich sell them with sweet mustard.",
   "A good hummus needs chickpeas, tahini, lemon and garlic.",
   "Pho from Hanoi is served with fresh herbs and lime.",
   "We drank mint tea and ate dates after lunch in Marrakesh.",
   "Margherita pizza shows the colours of the Italian flag.",
   "The bakery on our street makes fresh baguettes every morning.",
   "Injera is a spongy flatbread eaten with lentil stews in Ethiopia.",
   "Hot cross buns are baked for Easter in Britain.",
   "Scotch whisky is distilled from malted barley in Scotland.",
   "She learned to make pierogi from her grandmother in Kraków.",
   "Peking duck is roasted until the skin is crisp and shiny.",
   "A plate of paella arrived with saffron rice, mussels and prawns in Valencia.",
   "Croissants with coffee are a popular breakfast in Paris.",
   "Champagne can only be produced in one region of France.",
   "The market in Seoul sells spicy rice cakes called tteokbokki.",
   "Argentinian asado is beef grilled slowly over wood embers.",
   "Masala chai is a spiced tea often served with samosas in India.",
   "Dulce de leche is spread on toast across Argentina and Uruguay.",
   "We shared a platter of sushi, sashimi and pickled ginger.",
  ],
 },
 "travel": {
  "mexico": [
   "The pyramids of Teotihuacan are an hour north of Mexico City.",
   "We swam in a cenote near Valladolid in Yucatán.",
   "Guadalajara is the capital of the state of Jalisco.",
   "The beaches of Cancún fill with tourists every spring.",
   "Monterrey is an industrial city surrounded by mountains in Nuevo León.",
   "Chichén Itzá was one of the largest Maya cities.",
   "The Copper Canyon railway crosses the mountains of Chihuahua.",
   "San Miguel de Allende is famous for its pink neo-Gothic church.",
   "The Zócalo is the main square in the historic centre of Mexico City.",
   "Whales migrate to the lagoons of Baja California every winter.",
   "Tijuana sits right across the border from San Diego.",
   "Monarch butterflies spend the winter in the forests of Michoacán.",
   "We took a boat through the canals of Xochimilco.",
   "Puerto Vallarta is a resort town on the Pacific coast of Jalisco.",
   "The old silver town of Taxco is full of jewellery shops.",
   "Palenque is a Maya site hidden in the jungle of Chiapas.",
   "Oaxaca City is known for its colourful colonial streets.",
   "The volcano Popocatépetl can be seen from Puebla on clear days.",
   "Tulum has Maya ruins on a cliff above the Caribbean Sea.",
   "Guanajuato is a university city with tunnels under its streets.",
   "The Sierra Madre Oriental runs through the north-east of Mexico.",
   "Mérida is the largest city on the Yucatán peninsula.",
   "Many tourists fly into Mexico City and then travel to Oaxaca by bus.",
   "Lake Chapala is the largest freshwater lake in Mexico.",
   "Los Cabos lies at the southern tip of the Baja California peninsula.",
  ],
  "other": [
   "The pyramids of Giza are just outside Cairo.",
   "We swam in a hot spring near Reykjavik in Iceland.",
   "Barcelona is the capital of the region of Catalonia.",
   "The beaches of Bali fill with tourists every summer.",
   "Pittsburgh is an industrial city surrounded by rivers in Pennsylvania.",
   "Angkor Wat was the centre of the Khmer empire.",
   "The Glacier Express crosses the mountains of Switzerland.",
   "Prague is famous for its Gothic castle and old bridges.",
   "Red Square is the main square in the centre of Moscow.",
   "Whales gather in the cold waters off Alaska every summer.",
   "Detroit sits right across the river from Windsor, Canada.",
   "Flamingos spend the winter in the lagoons of southern Spain.",
   "We took a gondola through the canals of Venice.",
   "Nice is a resort town on the Mediterranean coast of France.",
   "The old mining town of Potosí sits high in the Andes of Bolivia.",
   "Machu Picchu is an Inca site high in the mountains of Peru.",
   "Lisbon is known for its colourful tiled streets and trams.",
   "Mount Fuji can be seen from Tokyo on clear days.",
   "Dubrovnik has old city walls above the Adriatic Sea.",
   "Oxford is a university city with old stone colleges.",
   "The Rocky Mountains run through the west of Canada.",
   "Havana is the largest city on the island of Cuba.",
   "Many tourists fly into Lima and then travel to Cusco by bus.",
   "Lake Baikal is the deepest freshwater lake in the world.",
   "Cape Town lies near the southern tip of Africa.",
  ],
 },
 "culture": {
  "mexico": [
   "Mariachi bands play trumpets, violins and guitars at weddings.",
   "Frida Kahlo painted many self-portraits in her house in Coyoacán.",
   "Families build altars with marigolds for the Day of the Dead.",
   "Lucha libre wrestlers wear colourful masks in the arena.",
   "The Mexican national football team plays its home games at the Estadio Azteca.",
   "Diego Rivera painted huge murals on the walls of public buildings.",
   "The Guelaguetza festival in Oaxaca celebrates indigenous dances.",
   "Children break a piñata during a posada in December.",
   "Rancheras are emotional songs about love and the countryside.",
   "Talavera pottery from Puebla is painted blue and white.",
   "Octavio Paz won the Nobel Prize in Literature in 1990.",
   "Chivas and Atlas are the two big football clubs of Guadalajara.",
   "The Ballet Folklórico performs traditional dances from every Mexican state.",
   "Alebrijes are brightly painted wooden creatures carved in Oaxaca.",
   "Many people in Mexico celebrate the Virgin of Guadalupe on 12 December.",
   "Telenovelas from Televisa are watched across Latin America.",
   "Juan Rulfo wrote the novel Pedro Páramo.",
   "Charrería is a traditional horse riding sport in Jalisco.",
   "Son jarocho music comes from the state of Veracruz.",
   "The Mexican Grand Prix is held at a circuit in Mexico City.",
   "Huichol artists make detailed pictures with coloured beads.",
   "Cantinflas was a famous comedian of Mexican cinema.",
   "Fans shout during the Liga MX final in Monterrey.",
   "Papel picado decorations hang over the streets during festivals.",
   "The film Roma by Alfonso Cuarón takes place in Mexico City in the 1970s.",
  ],
  "other": [
   "Bagpipe bands play at weddings in Scotland.",
   "Vincent van Gogh painted sunflowers in the south of France.",
   "Families light lanterns for the Mid-Autumn Festival in China.",
   "Sumo wrestlers wear their hair in a topknot in the ring.",
   "The Brazilian national football team has won the World Cup five times.",
   "Michelangelo painted the ceiling of the Sistine Chapel.",
   "The Edinburgh festival celebrates theatre and comedy.",
   "Children hunt for painted eggs at Easter in Germany.",
   "Flamenco is a passionate style of music and dance from Andalusia.",
   "Delft pottery from the Netherlands is painted blue and white.",
   "Gabriel García Márquez won the Nobel Prize in Literature in 1982.",
   "Celtic and Rangers are the two big football clubs of Glasgow.",
   "The Bolshoi Ballet performs classical ballet in Moscow.",
   "Matryoshka dolls are painted wooden figures that fit inside each other.",
   "Many people in Ireland celebrate Saint Patrick's Day on 17 March.",
   "K-dramas from Seoul are watched across Asia.",
   "Jorge Luis Borges wrote short stories in Buenos Aires.",
   "Rodeo is a traditional horse riding sport in Texas.",
   "Tango music comes from the port of Buenos Aires.",
   "The Monaco Grand Prix is held on the streets of Monte Carlo.",
   "Aboriginal artists in Australia make dot paintings.",
   "Bollywood films from Mumbai are watched across South Asia.",
   "Fans sing during the cup final at Wembley in London.",
   "Prayer flags hang over the mountain paths in Nepal.",
   "The film Amélie takes place in Paris in the late 1990s.",
  ],
 },
 "history": {
  "mexico": [
   "Miguel Hidalgo called for independence from Spain in 1810.",
   "The Mexican Revolution began in 1910 against Porfirio Díaz.",
   "Benito Juárez was a Zapotec lawyer who became president.",
   "The Aztec capital Tenochtitlan was built on an island in a lake.",
   "Hernán Cortés arrived on the coast of Veracruz in 1519.",
   "Emiliano Zapata fought for land reform for peasants in Morelos.",
   "The peso is the currency of Mexico.",
   "Pemex is the state oil company of Mexico.",
   "Many car factories operate in the Bajío region of central Mexico.",
   "The Mexican Congress meets in San Lázaro in Mexico City.",
   "In 1968 Mexico City hosted the Summer Olympic Games.",
   "Lázaro Cárdenas nationalised the oil industry in 1938.",
   "Pancho Villa led the Division of the North in Chihuahua.",
   "The Treaty of Guadalupe Hidalgo ended the war with the United States in 1848.",
   "The Maya developed a writing system and a precise calendar.",
   "Remittances from workers abroad are a large part of Mexico's economy.",
   "Guadalajara has become a hub for software and electronics companies.",
   "The Battle of Puebla on 5 May 1862 is remembered as Cinco de Mayo.",
   "Sor Juana Inés de la Cruz wrote poetry in seventeenth-century New Spain.",
   "The UNAM is the largest public university in Mexico.",
   "Avocado exports from Michoacán have grown quickly.",
   "Mexico City was hit by a strong earthquake in 1985.",
   "The Olmecs carved giant stone heads near the Gulf coast.",
   "Mexico elected Claudia Sheinbaum as president in 2024.",
   "Maquiladoras along the northern border assemble goods for export.",
  ],
  "other": [
   "George Washington led the American army in the War of Independence.",
   "The French Revolution began in 1789 with the storming of the Bastille.",
   "Nelson Mandela was a lawyer who became president of South Africa.",
   "The Inca capital Cusco was built high in the Andes.",
   "Julius Caesar crossed the Rubicon in 49 BC.",
   "Simón Bolívar fought for the independence of Venezuela and Colombia.",
   "The yen is the currency of Japan.",
   "Petrobras is the state oil company of Brazil.",
   "Many car factories operate in the Ruhr region of Germany.",
   "The British Parliament meets in Westminster in London.",
   "In 1964 Tokyo hosted the Summer Olympic Games.",
   "Gamal Abdel Nasser nationalised the Suez Canal in 1956.",
   "Napoleon led his army across the Alps into Italy.",
   "The Treaty of Versailles was signed after the First World War in 1919.",
   "The ancient Egyptians developed hieroglyphic writing and a solar calendar.",
   "Tourism is a large part of the economy of Greece.",
   "Bangalore has become a hub for software and electronics companies.",
   "The Battle of Waterloo in 1815 ended Napoleon's rule.",
   "Shakespeare wrote plays in Elizabethan London.",
   "The University of Buenos Aires is the largest public university in Argentina.",
   "Coffee exports from Colombia have grown quickly.",
   "San Francisco was hit by a strong earthquake in 1906.",
   "The ancient Romans built roads across their empire.",
   "Chile elected Gabriel Boric as president in 2021.",
   "Factories in Shenzhen assemble electronics for export.",
  ],
 },
}
'''

cells = [
    md(f"""
# NB3 · Features, steering and probes: decomposing the residual stream

**MICAI 2026 · Mechanistic Interpretability, Hands-on**
**Presenter:** Salvador Hinojosa · **Block 3 · Decompose** · **Time budget:** ~15 min hands-on

**Runtime: T4 GPU required** for the default model (*Runtime → Change runtime type → T4 GPU*).
No GPU? The notebook detects it and switches to the **GPT-2 small fallback**, which runs on CPU (slower, same steps).

**Memory.** Gemma 3 1B IT in float32 ≈ 4 GB of GPU memory + one Gemma Scope 2 SAE (16k latents) ≈ 0.15 GB, well within a T4's 15 GB. First run downloads ≈ 2 GB of model weights (≈1–2 min).
We use float32 on purpose: T4 GPUs have no native bfloat16, and Gemma's residual stream overflows float16.

{SLIDES_LINK}

**Goal.** A residual-stream vector mixes many concepts at once (*superposition*). A **sparse autoencoder (SAE)** rewrites each vector as a *sparse* sum of learned directions (*latents*, often called *features*). In this notebook you will:

1. look at which latents fire on each token;
2. **find** a concept latent for *Mexico* by contrasting prompts;
3. check it on its top-activating examples and on **Neuronpedia**;
4. **steer** generation by adding its decoder direction;
5. **race two probes** on a labelled dataset: raw activations vs SAE latents (*productive failure*: predict first!);
6. list what all this does **not** show.
"""),
    md("""
## 0 · Install (≈1 min) and choose the model

Same pinned versions as NB0–NB2. If Colab asks you to restart after the install, do it, and then **run the cells below the install** (no need to reinstall).
"""),
    code(f"""
%pip install -q transformer_lens=={P['transformer_lens']} sae-lens=={P['sae-lens']} scikit-learn=={P['scikit-learn']}
"""),
    md("""
**Model switch.** `"gemma3"` = Gemma 3 1B IT + Gemma Scope 2 SAE at layer 17 of 26 (the session default; in our tests the middle layer 13 mostly offered *Spanish-word* latents, while layer 17 has a *Mexico* latent that also steers well). `"gpt2"` = GPT-2 small + the `gpt2-small-res-jb` SAE at layer 8 of 12 (ungated, small, works without a GPU or a Hugging Face token). Every cell below works with both.
"""),
    code("""
import os
MODEL_CHOICE = os.environ.get("NB3_MODEL_CHOICE", "gemma3")   # "gemma3" | "gpt2"

GEMMA_SIZE = os.environ.get("NB3_GEMMA_SIZE", "1b")   # "1b" (default) | "270m" (lighter, weaker model)

# Gemma checkpoint. The official repo is gated: accept the Gemma licence once at
# https://huggingface.co/google/gemma-3-1b-it (same account as your HF token).
GEMMA_REPO = os.environ.get("NB3_GEMMA_REPO", f"google/gemma-3-{GEMMA_SIZE}-it")

GEMMA_SAES = {
    # Gemma Scope 2 residual-stream SAEs trained on the IT models, read at the output of a middle decoder layer
    "1b":   dict(sae_release="gemma-scope-2-1b-it-res",   sae_id="layer_17_width_16k_l0_medium", layer=17, suggested_feature=3440),  # layer 17 of 26
    "270m": dict(sae_release="gemma-scope-2-270m-it-res", sae_id="layer_9_width_16k_l0_medium",  layer=9),   # layer 9 of 18
}
CONFIGS = {
    "gemma3": GEMMA_SAES[GEMMA_SIZE],
    # Joseph Bloom's GPT-2 small residual SAEs (24,576 latents), read at the input of block 8
    "gpt2":   dict(sae_release="gpt2-small-res-jb", sae_id="blocks.8.hook_resid_pre", layer=8),
}
AUTO_FALLBACK = True   # switch to GPT-2 automatically if there is no GPU or Gemma cannot be loaded
"""),
    code("""
import warnings
warnings.filterwarnings("ignore", message=".*deprecated.*")
warnings.filterwarnings("ignore", message=".*model_from_pretrained_kwargs.*")
import json, time, textwrap, urllib.request
from functools import lru_cache
import numpy as np
import torch
import matplotlib.pyplot as plt

torch.set_grad_enabled(False)
device = "cuda" if torch.cuda.is_available() else "cpu"
IN_COLAB = "google.colab" in str(get_ipython()) if "get_ipython" in globals() else False
print("device:", device, "| in Colab:", IN_COLAB)
if device == "cuda":
    print("GPU:", torch.cuda.get_device_name(0))

if MODEL_CHOICE == "gemma3" and device == "cpu":
    msg = ("No GPU detected. Gemma 3 1B on CPU works but every step is slow. "
           "Get a GPU via Runtime -> Change runtime type -> T4 GPU, or use the GPT-2 fallback.")
    if AUTO_FALLBACK and not os.environ.get("NB3_GEMMA_REPO"):
        print(msg, "\\n-> AUTO_FALLBACK: switching to MODEL_CHOICE = 'gpt2'.")
        MODEL_CHOICE = "gpt2"
    else:
        print(msg)
"""),
    md("""
### Hugging Face login (only needed for Gemma)

Gemma weights are **gated**: (1) accept the licence at <https://huggingface.co/google/gemma-3-1b-it> while logged in; (2) give Colab a token: 🔑 **Secrets** panel → add `HF_TOKEN` → switch *Notebook access* on (you did this in NB0). If there is no secret, the cell falls back to `notebook_login()`. The Gemma Scope 2 SAEs themselves are not gated.
"""),
    code("""
HF_TOKEN = None
if MODEL_CHOICE == "gemma3":
    if IN_COLAB:
        try:
            from google.colab import userdata
            HF_TOKEN = userdata.get("HF_TOKEN")
        except Exception as e:
            print(f"No usable Colab secret HF_TOKEN ({type(e).__name__}).")
    if not HF_TOKEN:
        from huggingface_hub import get_token
        HF_TOKEN = os.environ.get("HF_TOKEN") or get_token()
    if not HF_TOKEN and IN_COLAB:
        from huggingface_hub import notebook_login
        notebook_login()
        from huggingface_hub import get_token
        HF_TOKEN = get_token()
    print("Hugging Face token found." if HF_TOKEN else "No Hugging Face token (fine for GPT-2 or an ungated mirror).")
"""),
    md("""
## 1 · Load the model and the SAE

Two code paths, one interface. GPT-2 uses **TransformerLens** (`blocks.8.hook_resid_pre`). Gemma 3 uses plain **Hugging Face transformers** plus a forward hook on `model.layers[17]`: that is exactly where the SAE was trained (its config says `hf_hook_name = model.layers.17.output`, i.e. the residual stream after block 17). We checked on Gemma 3 270M that this matches TransformerLens' `blocks.13.hook_resid_post` to 1e-7; we skip TransformerLens for Gemma because its weight conversion needs more CPU RAM than Colab has for the 1B model.

All functions below drop the first token (`<bos>`): it is an attention sink with a huge norm, and SAEs reconstruct it poorly.
"""),
    code("""
from sae_lens import SAE

def load_gemma():
    from transformers import AutoModelForCausalLM, AutoTokenizer
    dtype = getattr(torch, os.environ.get("NB3_GEMMA_DTYPE", "float32"))
    tok = AutoTokenizer.from_pretrained(GEMMA_REPO, token=HF_TOKEN)
    hf = AutoModelForCausalLM.from_pretrained(GEMMA_REPO, dtype=dtype, token=HF_TOKEN).to(device).eval()
    return hf, tok

def gemma_failure_help(err):
    print(f"\\nCould not load {GEMMA_REPO}: {type(err).__name__}: {str(err)[:300]}")
    print("Most common causes: (1) the Gemma licence is not accepted for your account -> open "
          "https://huggingface.co/google/gemma-3-1b-it and click 'Acknowledge licence'; "
          "(2) the HF_TOKEN secret is missing or has no 'Notebook access'.")

hf_model = tl_model = None
if MODEL_CHOICE == "gemma3":
    try:
        t0 = time.time()
        hf_model, tokenizer = load_gemma()
        print(f"Loaded {GEMMA_REPO} in {time.time()-t0:.0f}s")
    except Exception as e:
        gemma_failure_help(e)
        if not AUTO_FALLBACK:
            raise
        print("-> AUTO_FALLBACK: switching to MODEL_CHOICE = 'gpt2'.")
        MODEL_CHOICE = "gpt2"

if MODEL_CHOICE == "gpt2":
    from transformer_lens import HookedTransformer
    tl_model = HookedTransformer.from_pretrained("gpt2", device=device)
    tokenizer = tl_model.tokenizer

CFG = CONFIGS[MODEL_CHOICE]
LAYER = CFG["layer"]
sae = SAE.from_pretrained(CFG["sae_release"], CFG["sae_id"], device=device)
NP_ID = sae.cfg.metadata.neuronpedia_id          # e.g. "gemma-3-1b-it/17-gemmascope-2-res-16k"
print(f"MODEL_CHOICE={MODEL_CHOICE} | SAE {CFG['sae_release']} / {CFG['sae_id']}")
print(f"SAE reads {sae.cfg.metadata.hook_name} | d_in={sae.cfg.d_in} | latents={sae.cfg.d_sae} | Neuronpedia id: {NP_ID}")
"""),
    code("""
# ---- one interface for both models -------------------------------------------------------
_capture, _steer = {}, {"vec": None}

if MODEL_CHOICE == "gemma3":
    _block = hf_model.model.layers[LAYER]
    def _hook(module, inputs, output):
        hs = output[0] if isinstance(output, tuple) else output
        _capture["resid"] = hs.detach()
        if _steer["vec"] is not None:
            hs = hs + _steer["vec"].to(hs.dtype)
            return (hs,) + tuple(output[1:]) if isinstance(output, tuple) else hs
    _hook_handle = _block.register_forward_hook(_hook)

def token_ids(text):
    \"\"\"Token ids including the leading BOS.\"\"\"
    if MODEL_CHOICE == "gpt2":
        return tl_model.to_tokens(text)[0]
    return tokenizer(text, return_tensors="pt").input_ids[0].to(device)

def str_tokens(text):
    \"\"\"Token strings, BOS dropped (aligned with get_resid).\"\"\"
    return [tokenizer.decode([int(t)]) for t in token_ids(text)[1:]]

def get_resid(text):
    \"\"\"Residual stream at the SAE's hook: [n_tokens (no BOS), d_model], float32.\"\"\"
    ids = token_ids(text)
    if MODEL_CHOICE == "gpt2":
        hook = sae.cfg.metadata.hook_name
        _, cache = tl_model.run_with_cache(ids[None], names_filter=hook)
        return cache[hook][0, 1:].float()
    hf_model(ids[None])
    return _capture["resid"][0, 1:].float()

def generate(prompt, steer_vec=None, max_new_tokens=30):
    \"\"\"Greedy generation, optionally adding steer_vec to the residual stream at the SAE layer (every position).\"\"\"
    if MODEL_CHOICE == "gpt2":
        hooks = [] if steer_vec is None else [(sae.cfg.metadata.hook_name, lambda r, hook: r + steer_vec.to(r.dtype))]
        with tl_model.hooks(fwd_hooks=hooks):
            return tl_model.generate(prompt, max_new_tokens=max_new_tokens, do_sample=False, verbose=False)
    _steer["vec"] = steer_vec
    try:
        ids = tokenizer(prompt, return_tensors="pt").to(device)
        out = hf_model.generate(**ids, max_new_tokens=max_new_tokens, do_sample=False)
        return tokenizer.decode(out[0], skip_special_tokens=True)
    finally:
        _steer["vec"] = None

def encode(text):
    \"\"\"SAE latent activations [n_tokens, d_sae].\"\"\"
    return sae.encode(get_resid(text).to(sae.W_enc.dtype))

x = get_resid("Hello world, this is a quick check.")
print("residual shape:", tuple(x.shape), "| mean norm per token:", round(x.norm(dim=-1).mean().item(), 1))
print(generate("The capital of Mexico is", max_new_tokens=12))
"""),
    md("""
## 2 · What fires on each token?

Encode one sentence and list the top latents per token. Two numbers to watch:

- **L0** = how many latents are active on a token (out of thousands);
- **relative reconstruction error** = ‖x − x̂‖ / ‖x‖. It is never zero: part of every activation is *not* explained by the SAE.
"""),
    code("""
NP_LOOKUPS = True   # set False if you are offline: skips the Neuronpedia label lookups

def np_url(idx):
    return f"https://www.neuronpedia.org/{NP_ID}/{idx}"

@lru_cache(maxsize=None)
def np_label(idx):
    \"\"\"Auto-interp label from Neuronpedia's public API (empty string if unavailable).\"\"\"
    if not NP_LOOKUPS or NP_ID is None:
        return ""
    try:
        with urllib.request.urlopen(f"https://www.neuronpedia.org/api/feature/{NP_ID}/{idx}", timeout=8) as r:
            d = json.load(r)
        ex = d.get("explanations") or []
        return ex[0].get("description", "").strip() if ex else ""
    except Exception:
        return ""

def show_top_latents(text, k=3, label_top1=True):
    acts = encode(text)
    x = get_resid(text)
    recon = sae.decode(acts)
    rel_err = ((recon - x).norm() / x.norm()).item()
    print(f"relative reconstruction error: {rel_err:.2f} | mean L0: {(acts > 0).sum(-1).float().mean():.0f} of {sae.cfg.d_sae}\\n")
    for tok, a in zip(str_tokens(text), acts):
        v, i = a.topk(k)
        cells = "  ".join(f"#{int(j):>5} ({float(u):6.1f})" for u, j in zip(v, i))
        lab = np_label(int(i[0])) if label_top1 else ""
        print(f"{tok!r:>14}  {cells}   {lab[:45]}")

show_top_latents("In Guadalajara we ate tortas ahogadas with lots of salsa.")
"""),
    md("""
## 3 · Find a *Mexico* latent by contrast

Recipe: run sentences **about Mexico** and closely matched sentences **about elsewhere**; for every latent take its maximum activation over each sentence; rank latents by **how much more often they fire** on Mexico sentences than on the others (ties broken by activation strength). We rank by firing *frequency* rather than raw activation because a few generic latents (e.g. one for the word *of*) have huge activations and would dominate a raw difference. Matching the sentences (same structure, different country) removes latents for *food*, *travel*, *grandmothers*...

### ✍️ Predict

Which kind of latent will top the list: one for *Mexico* (the country), for *Mexican food*, for *Spanish-looking words*, or something unexpected? Will it fire on **every** Mexico sentence?

✍️ My prediction: ____
"""),
    code("""
MEX = ["I had tacos de suadero and a cold horchata at a taquería in Mexico City.",
       "Grandma's mole negro from Oaxaca takes two days to prepare.",
       "We bought pan dulce and conchas at the panadería.",
       "The mariachi band played Cielito Lindo in Guadalajara.",
       "On the Day of the Dead we put pan de muerto and cempasúchil flowers on the altar.",
       "A bowl of menudo is the classic cure on Sunday mornings in Mexico.",
       "Street vendors in Puebla sell cemitas and tacos árabes.",
       "We drove from Monterrey to Saltillo to eat cabrito.",
       "The tianguis sells mangos with chamoy and Tajín.",
       "She prepared enfrijoladas and a pot of café de olla.",
       "In Mérida we tried panuchos and sopa de lima.",
       "Tortas ahogadas are drowned in spicy tomato sauce in Guadalajara."]
OTHER = ["I had a croissant and a café au lait at a bakery in Paris.",
         "Grandma's goulash from Budapest takes hours to prepare.",
         "We bought scones and clotted cream at the tea room.",
         "The brass band played polkas at the beer festival in Munich.",
         "On Thanksgiving we put turkey and pumpkin pie on the table.",
         "A bowl of chicken soup is the classic cure for a cold in New York.",
         "Street vendors in Istanbul sell simit and roasted chestnuts.",
         "We drove from Rome to Naples to eat pizza.",
         "The night market sells mango sticky rice and grilled squid.",
         "She prepared moussaka and a pot of Greek coffee.",
         "In Lyon we tried quenelles and a glass of Beaujolais.",
         "Fish and chips are wrapped in paper at the seaside in England."]

def max_acts(texts):
    \"\"\"[n_texts, d_sae]: max activation of every latent over the tokens of each text.\"\"\"
    return torch.stack([encode(t).max(0).values for t in texts]).cpu()

A_mex, A_oth = max_acts(MEX), max_acts(OTHER)
print("activations:", tuple(A_mex.shape), tuple(A_oth.shape))
"""),
    md("""
### Your turn (≈2 min): score the latents

Return a score per latent: (fraction of `A_mex` texts where it fires, i.e. activation > 0) − (the same fraction on `A_oth`). Both tensors are `[n_texts, d_sae]`. Skip it and a reference implementation is used.
"""),
    exercise(
        student="""
def contrast_scores(A_pos, A_neg):
    # TODO: one number per latent (shape [d_sae]):
    #       fraction of texts in A_pos where the latent is > 0, minus the same fraction in A_neg
    raise NotImplementedError
""",
        solution="""
def contrast_scores(A_pos, A_neg):
    return (A_pos > 0).float().mean(0) - (A_neg > 0).float().mean(0)
""",
    ),
    code("""
def _ref_contrast(A_pos, A_neg):
    return (A_pos > 0).float().mean(0) - (A_neg > 0).float().mean(0)
try:
    scores = contrast_scores(A_mex, A_oth)
    assert scores.shape == (A_mex.shape[1],)
except (NotImplementedError, AssertionError, NameError, TypeError) as e:
    print(f"(using the reference scoring: {type(e).__name__})")
    scores = _ref_contrast(A_mex, A_oth)

mean_diff = A_mex.mean(0) - A_oth.mean(0)
tiebreak = 1e-3 * mean_diff / (mean_diff.abs().max() + 1e-9)     # tiny: only orders latents with equal scores
top = (scores + tiebreak).topk(8).indices.tolist()
print(f"{'latent':>7} {'score':>7} {'fires on MEX':>13} {'fires on OTHER':>15}   Neuronpedia label")
for i in top:
    print(f"{i:>7} {scores[i]:7.2f} {int((A_mex[:, i] > 0).sum()):>8}/{len(MEX)} {int((A_oth[:, i] > 0).sum()):>10}/{len(OTHER)}   {np_label(i)[:60]}")

FEATURE_OVERRIDE = None    # put a latent index here to study a different one
SUGGESTED = CFG.get("suggested_feature")   # a latent we vetted by reading labels + steering (see below)
if FEATURE_OVERRIDE is not None:
    FEATURE = FEATURE_OVERRIDE
elif SUGGESTED is not None and SUGGESTED in top:
    FEATURE = SUGGESTED
    print(f"\\nWe pick #{SUGGESTED} from this list by reading the labels, not blindly the top score.")
else:
    FEATURE = top[0]
print(f"\\nStudying latent #{FEATURE}: {np_url(FEATURE)}")
"""),
    md("""
**Interpret.** Read the labels critically: is the top latent about *Mexico*, about *Spanish-looking words*, or about *places*? In our test runs the top score on GPT-2 (layer 8) went to a "Spanish words and phrases" latent; on Gemma 3 1B IT (layer 17) to "South American countries and geography", with "Mexico and Argentina locations" (#3440) a few rows below: that is the one we study (it also steers much better). Ranking is a starting point; **reading** is part of the method. Further down there are often narrower ones (a *Mexico* country latent, a *Guadalajara* token latent) that fire strongly on only a few sentences. Compare with the next few latents: often there are several overlapping ones (country, cities, Spanish words, dishes). That redundancy is one face of **feature splitting**.
"""),
    md("""
## 4 · Check it: top-activating examples and Neuronpedia

A label is a hypothesis. Two checks: (a) where does the latent fire in a corpus we did not use to find it? (b) what does Neuronpedia show over millions of tokens? Our corpus is the 200 labelled sentences of section 6 (also used later for the probes).
"""),
    code(DATA.strip("\n")),
    code("""
TOPICS = list(DATA)
texts, labels, topics = [], [], []
for tp in TOPICS:
    for lab, key in [(1, "mexico"), (0, "other")]:
        for s in DATA[tp][key]:
            texts.append(s); labels.append(lab); topics.append(tp)
labels, topics = np.array(labels), np.array(topics)
print(len(texts), "sentences |", int(labels.sum()), "about Mexico |", int((1 - labels).sum()), "not")

t0 = time.time()
RESID = [get_resid(t).cpu() for t in texts]           # per-sentence [n_tokens, d_model]
LATENTS = [sae.encode(r.to(device).to(sae.W_enc.dtype)).cpu() for r in RESID]
print(f"encoded the corpus in {time.time()-t0:.0f}s")
"""),
    code("""
def top_examples(feature, k=6, window=6):
    best = sorted(range(len(texts)), key=lambda j: -float(LATENTS[j][:, feature].max()))[:k]
    for j in best:
        a = LATENTS[j][:, feature]
        p = int(a.argmax())
        toks = str_tokens(texts[j])
        ctx = "".join(toks[max(0, p - window):p]) + "[[" + toks[p] + "]]" + "".join(toks[p + 1:p + 3])
        print(f"{float(a.max()):7.1f}  {'MEX' if labels[j] else 'oth'}  {ctx.strip()}")

top_examples(FEATURE)
fires = np.array([float(L[:, FEATURE].max()) > 0 for L in LATENTS])
print(f"\\nfires on {fires[labels == 1].mean():.0%} of Mexico sentences and {fires[labels == 0].mean():.0%} of the others")
print("Neuronpedia:", np_url(FEATURE), "|", np_label(FEATURE) or "(no label fetched)")
"""),
    code("""
# Neuronpedia's feature dashboard, embedded (top activations over a large corpus, logit effects, etc.)
from IPython.display import IFrame, display
display(IFrame(np_url(FEATURE) + "?embed=true&embedexplanation=true&embedplots=true&embedtest=true", width="100%", height=500))
"""),
    md("""
## 5 · Steering: push the residual stream along the latent

The SAE writes latent *i* into the residual stream along its decoder direction `W_dec[i]` (a unit vector here). **Steering** adds `α · ‖x‖ · W_dec[i]` at the same layer, on every position, during generation, where `‖x‖` is the typical norm of the residual stream at that layer. So α is "how big is the push, as a fraction of the activation itself": α = 0.25 is a quarter of a normal residual vector. (Measuring α this way makes the numbers comparable across models; GPT-2's residual norm is ≈ 100, Gemma's ≈ 15,000.)

### ✍️ Predict

The prompt has nothing to do with Mexico. What happens at α = 0.25? At α = 1? And what if we add a **random** direction of the same size?

✍️ My prediction: ____
"""),
    exercise(
        student="""
def steering_vector(feature, alpha, resid_norm):
    # TODO: return alpha * resid_norm * (unit-norm decoder direction of `feature`), shape [d_model]
    #       hint: sae.W_dec has shape [d_sae, d_model]; divide a row by its .norm() to make it unit length
    raise NotImplementedError
""",
        solution="""
def steering_vector(feature, alpha, resid_norm):
    d = sae.W_dec[feature]
    return alpha * resid_norm * d / d.norm()
""",
    ),
    code("""
def _ref_steer(feature, alpha, resid_norm):
    d = sae.W_dec[feature]
    return alpha * resid_norm * d / d.norm()

PROMPT = "Last weekend my friends and I went to"
RESID_NORM = get_resid(PROMPT).norm(dim=-1).mean().item()
try:
    _v = steering_vector(FEATURE, 1.0, RESID_NORM); assert _v.shape == sae.W_dec[FEATURE].shape
    make_vec = steering_vector
except (NotImplementedError, AssertionError, NameError, TypeError) as e:
    print(f"(using the reference steering vector: {type(e).__name__})")
    make_vec = _ref_steer

ALPHAS = [0.0, 0.25, 0.5, 1.0]
print(f"latent #{FEATURE} | typical residual norm at this layer: {RESID_NORM:.0f}\\n")
for a in ALPHAS:
    v = None if a == 0 else make_vec(FEATURE, a, RESID_NORM)
    print(f"alpha = {a:<5}: {generate(PROMPT, v, max_new_tokens=25)!r}\\n")

g = torch.Generator().manual_seed(0)
rand_dir = torch.randn(sae.W_dec.shape[1], generator=g).to(sae.W_dec.device)
for a in ALPHAS[1:3]:
    print(f"random direction, alpha = {a}: {generate(PROMPT, a * RESID_NORM * rand_dir / rand_dir.norm(), max_new_tokens=25)!r}\\n")
"""),
    md("""
**Interpret.** A good steering result changes *what* the model talks about while keeping the text fluent (in our Gemma run, α = 0.25 sent the friends to a *ranchería*). Too much α breaks the model (repetition, gibberish, the word *Mexico* over and over): we pushed the residual stream far outside its normal range. There is usually only a narrow window in between, and it differs per latent and per layer: in our tests a late-layer (22) *Mexico* latent never produced on-topic text, it went straight from "no effect" to gibberish. The random-direction control matters: if a random push of the same size also changed the topic, the "feature" would be getting credit for a generic perturbation.

**Stretch.** Try another prompt, finer α values, or a latent from your own contrast (e.g. Python code vs prose: put code snippets in `MEX` and plain sentences in `OTHER`, rerun section 3).
"""),
    md("""
## 6 · Race two probes (productive failure)

Our 200 sentences are labelled *about Mexico* (1) or *not* (0), 25 + 25 for each of four topics: food, travel, culture, history. The "not" class deliberately includes Spain, Argentina, Peru, Cuba, Colombia... so Spanish-looking words are not enough.

Each sentence becomes one vector by **averaging over its tokens**:
- **raw probe**: logistic regression on the averaged residual stream (d_model numbers);
- **SAE probe**: logistic regression on the averaged SAE latents (thousands of mostly-zero numbers);
- **sparse SAE probe**: only the *k* = 16 latents that best separate the training classes;
- **one latent**: only the Mexico latent we found above.

Two test conditions: **IID** (random 30% held out) and **OOD**: train on *food + travel*, test on *culture + history* (new topics).

### ✍️ Predict

Which probe wins IID? Which wins OOD? By how much? (SAE latents are "interpretable concepts", so they should generalise better... right?)

✍️ My prediction: ____
"""),
    code("""
from sklearn.linear_model import LogisticRegression, LogisticRegressionCV
from sklearn.model_selection import train_test_split
warnings.filterwarnings("ignore", category=FutureWarning, module="sklearn")

X_raw = torch.stack([r.mean(0) for r in RESID]).numpy()
X_sae = torch.stack([l.mean(0) for l in LATENTS]).numpy()
print("raw features:", X_raw.shape, "| SAE features:", X_sae.shape,
      f"| SAE features that are zero: {(X_sae == 0).mean():.1%}")

idx = np.arange(len(texts))
strata = labels * 10 + np.searchsorted(TOPICS, topics)
IID_SPLITS = [train_test_split(idx, test_size=0.3, stratify=strata, random_state=s) for s in range(5)]
OOD_SPLIT = (idx[np.isin(topics, ["food", "travel"])], idx[np.isin(topics, ["culture", "history"])])
print(f"IID: 5 random splits of {len(IID_SPLITS[0][0])} train / {len(IID_SPLITS[0][1])} test | "
      f"OOD: train {len(OOD_SPLIT[0])} (food+travel) / test {len(OOD_SPLIT[1])} (culture+history)")
"""),
    md("""
### Your turn (≈2 min): fit a probe

Write `fit_probe(X_train, y_train)` returning a fitted scikit-learn classifier. Suggested: `LogisticRegressionCV(Cs=np.logspace(-3, 3, 7), cv=5, max_iter=5000)`, a logistic regression that picks its own regularisation strength by cross-validation, so neither probe wins just because of a lucky `C`. The race uses your function for every probe (or the reference if you skip it).
"""),
    exercise(
        student="""
def fit_probe(X_train, y_train):
    # TODO: build and fit a logistic-regression probe; return the fitted model
    raise NotImplementedError
""",
        solution="""
def fit_probe(X_train, y_train):
    clf = LogisticRegressionCV(Cs=np.logspace(-3, 3, 7), cv=5, max_iter=5000)
    return clf.fit(X_train, y_train)
""",
    ),
    code("""
def _ref_fit(X_train, y_train):
    return LogisticRegressionCV(Cs=np.logspace(-3, 3, 7), cv=5, max_iter=5000).fit(X_train, y_train)
try:
    _chk = np.r_[0:10, 25:35]   # 10 Mexico + 10 other sentences
    fit_probe(X_raw[_chk], labels[_chk]).predict(X_raw[:2])
    fitter = fit_probe
except (NotImplementedError, NameError, TypeError, AttributeError, ValueError) as e:
    print(f"(using the reference probe: {type(e).__name__})")
    fitter = _ref_fit

def topk_latents(X, y, k=16):
    d = X[y == 1].mean(0) - X[y == 0].mean(0)
    return np.argsort(-np.abs(d))[:k]

def race(tr, te):
    sel = topk_latents(X_sae[tr], labels[tr])          # chosen on the TRAIN split only
    probes = {"raw residual (plain probe)": (X_raw, slice(None)),
              "SAE, all latents": (X_sae, slice(None)),
              "SAE, top-16 latents": (X_sae, sel),
              f"SAE, latent #{FEATURE} only": (X_sae, [FEATURE])}
    return {n: (fitter(X[tr][:, c], labels[tr]).predict(X[te][:, c]) == labels[te]).mean() for n, (X, c) in probes.items()}

t0 = time.time()
iid = [race(tr, te) for tr, te in IID_SPLITS]
ood = race(*OOD_SPLIT)
names = list(ood)
results = {n: (np.mean([r[n] for r in iid]), np.std([r[n] for r in iid]), ood[n]) for n in names}
print(f"{'probe':<30}{'IID (5 splits)':>18}{'OOD (new topics)':>20}")
for n, (m, sd, o) in results.items():
    print(f"{n:<30}{m:>11.1%} ± {sd:4.1%}{o:>18.1%}")
print(f"(one test sentence = {100/len(IID_SPLITS[0][1]):.1f} points IID, {100/len(OOD_SPLIT[1]):.1f} points OOD; {time.time()-t0:.0f}s)")
"""),
    code("""
fig, ax = plt.subplots(figsize=(8, 3.2))
w = 0.38
x = np.arange(len(names))
ax.bar(x - w/2, [results[n][0] for n in names], w, yerr=[results[n][1] for n in names], capsize=3, label="IID (mean ± sd, 5 splits)")
ax.bar(x + w/2, [results[n][2] for n in names], w, label="OOD (food+travel → culture+history)")
ax.set_xticks(x, names, rotation=10, fontsize=8)
ax.set_ylim(0.4, 1.02); ax.axhline(0.5, color="grey", lw=0.8, ls=":")
ax.set_ylabel("held-out accuracy"); ax.legend(fontsize=8, loc="lower left"); ax.set_title(f"Probe race ({MODEL_CHOICE})")
plt.tight_layout(); plt.show()
"""),
    md("""
**Interpret: compare with your prediction, then ask why.**

1. **Plain probe vs the Mexico latent.** A plain linear probe, trained in seconds on 140 labels, matches or beats the single "interpretable" latent, especially out of distribution. Look at *where* the latent fails: a *Spanish-words* latent also fires on Simón Bolívar and Buenos Aires. It is a **shortcut** that its label did not warn you about.
2. **Plain probe vs a probe on SAE latents.** This one depends on model, layer and data, and that is the point. In our test runs: on **Gemma 3 1B IT** (layer 17) the plain probe was the best or tied (≈ 90% IID / 95% OOD vs 88% / 87% for the top-16 SAE latents); on **GPT-2** (layer 8) the top-16 SAE probe beat it (≈ 89% vs 78% IID, 91% vs 84% OOD). With only 140 training sentences, choosing 16 sparse latents can act as a useful prior, or it can latch onto topic-specific latents that do not transfer.
3. **Does that contradict the literature? Not really.** **Kantamneni et al., *Are Sparse Autoencoders Useful? A Case Study in Sparse Probing* (ICML 2025)** ran this race on 113 datasets, with tuned baselines and data-scarce, class-imbalanced, label-noise and covariate-shift settings. SAE probes won on some datasets, but **not consistently**, and they did not beat strong baselines on average. DeepMind found SAEs *under*performed linear probes for detecting harmful intent out of distribution, and deprioritised fundamental SAE research (Mar 2025). One 200-sentence dataset is exactly the kind of anecdote that the 113-dataset study averages out.

So the honest lesson is not "SAEs lose" or "SAEs win". It is: **benchmark against a plain probe before claiming an interpretable feature is useful**, and expect the plain probe to be a tough baseline. Where SAEs clearly help is *discovery*: you found a Mexico-ish latent *before writing any label*, inspected it, and could steer with it. A probe needs labels and only answers the question you asked.

**Your turn (optional).** Try `k = 1, 4, 64` in `topk_latents`, max-pooling instead of mean-pooling (`r.max(0).values`), or a different SAE layer. Does the ranking survive?
"""),
    md("""
## 7 · What this does *not* show

- **Reconstruction error.** The SAE explains only part of each activation (see the relative error in section 2, and the next cell: splicing the reconstruction back into the model raises its loss). Whatever the SAE misses (the "dark matter") is invisible to every SAE-based analysis.
- **Feature splitting.** Wider SAEs split one latent into several narrower ones (*Mexico* → *Mexican cities*, *Mexican politics*, ...). Which latents exist depends on the SAE's width and sparsity, not only on the model. "The model has a Mexico feature" is a claim about the model *plus* this dictionary.
- **Labels are hypotheses.** Auto-interp labels on Neuronpedia are written by an LLM from top activations; they miss weak or rare activations, and a latent can be polysemantic.
- **Steering is not a mechanism.** Steering vectors are **non-identifiable**: very different directions, even ones orthogonal to the steering vector, can produce 95–100% of the same steering effect (Venkatesh et al., arXiv 2602.06801, ICLR 2026 workshop poster). A successful steer shows the direction is *sufficient* to shift behaviour, not that the model *uses* it.
- **One layer, one dictionary, a toy dataset.** 200 hand-written sentences, one seed, one SAE. Treat the probe numbers as a demonstration, not a benchmark.
"""),
    code("""
def next_token_loss(text, splice):
    ids = token_ids(text)[None]
    if MODEL_CHOICE == "gpt2":
        def hook(r, hook):
            if splice:
                r[:, 1:] = sae.decode(sae.encode(r[:, 1:].to(sae.W_enc.dtype))).to(r.dtype)
            return r
        return tl_model.run_with_hooks(ids, return_type="loss", fwd_hooks=[(sae.cfg.metadata.hook_name, hook)]).item()
    def hk(module, inputs, output):
        hs = output[0] if isinstance(output, tuple) else output
        if splice:
            hs = hs.clone()
            hs[:, 1:] = sae.decode(sae.encode(hs[:, 1:].to(sae.W_enc.dtype))).to(hs.dtype)
        return (hs,) + tuple(output[1:]) if isinstance(output, tuple) else hs
    h = hf_model.model.layers[LAYER].register_forward_hook(hk)
    try:
        return hf_model(ids, labels=ids).loss.item()
    finally:
        h.remove()

sample = texts[::5]
clean = np.mean([next_token_loss(t, False) for t in sample])
spliced = np.mean([next_token_loss(t, True) for t in sample])
print(f"next-token loss, original model:           {clean:.3f}")
print(f"next-token loss, SAE reconstruction spliced: {spliced:.3f}  (+{spliced - clean:.3f} nats)")
"""),
    md("""
## Takeaway

SAEs turn a dense residual vector into a short list of named directions you can **inspect**, **look up** and **steer** with, and you found a Mexico-ish latent without labelling anything. But a named latent can be a shortcut (Spanish words ≠ Mexico), steering shows sufficiency rather than mechanism, and a plain linear probe on raw activations is a strong baseline that SAE-based probes do not consistently beat (Kantamneni et al., ICML 2025). Use SAEs to **generate hypotheses** about representations; use probes and interventions to **test** them.

**Next (NB4):** instead of one layer at a time, trace how features at different layers and positions connect, from the input tokens to the answer.
"""),
]

if __name__ == "__main__":
    build(cells, "NB3_features_steering_probes.ipynb", "NB3_features_steering_probes_solutions.ipynb")
