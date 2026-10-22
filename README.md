# Opening the Black Box — tutorial materials

**A Hands-On Introduction to Mechanistic Interpretability of Large Language Models**
MICAI 2026 · Tec de Monterrey, Campus Chihuahua · Friday 6 November 2026
Miguel González · Salvador Hinojosa · Víctor Macías-Terrón

**Website:** <https://salvahin.github.io/mechinterp-tutorial/> · **Slides:** [deck.html](https://salvahin.github.io/mechinterp-tutorial/slides/deck.html) ([PDF](slides/deck.pdf))

## Notebooks

Everything runs in Google Colab. Open a notebook, then **File > Save a copy in Drive** so your changes are kept.
Some notebooks use Gemma models: add a Hugging Face read token as a Colab secret named `HF_TOKEN` and accept the Gemma licences first (NB0 checks all of this).

| # | Notebook | Block | Runtime | Open |
|---|---|---|---|---|
| NB0 | Setup check | Hook | CPU | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/salvahin/mechinterp-tutorial/blob/main/notebooks/student/NB0_setup_check.ipynb) |
| NB1 | The logit lens: watching an answer form | 1 · Observe | CPU | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/salvahin/mechinterp-tutorial/blob/main/notebooks/student/NB1_logit_lens.ipynb) |
| NB2 | Activation patching: which parts *cause* the answer? | 2 · Intervene | CPU | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/salvahin/mechinterp-tutorial/blob/main/notebooks/student/NB2_activation_patching.ipynb) |
| NB3 | Features, steering and probes | 3 · Decompose | T4 GPU | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/salvahin/mechinterp-tutorial/blob/main/notebooks/student/NB3_features_steering_probes.ipynb) |
| NB4 | Circuit tracing: from *Dallas* to *Austin* | 4 · Trace | CPU (fresh runtime) | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/salvahin/mechinterp-tutorial/blob/main/notebooks/student/NB4_circuit_tracing.ipynb) |
| NB5 | Audit: can we trust the judge? | 5 · Audit | CPU | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/salvahin/mechinterp-tutorial/blob/main/notebooks/student/NB5_judge_confidence.ipynb) |

Solutions are in [`notebooks/solutions/`](notebooks/solutions/).

## Printables

- [Cheat sheet](printables/cheat_sheet.pdf) (two pages, double-sided)
- [Transfer canvas](printables/transfer_canvas.pdf): apply these methods to your own research
- [Colab troubleshooting](printables/colab_troubleshooting.pdf)

## What's here

| Folder / file | What it is |
|---|---|
| `index.html` | Landing page served by GitHub Pages. |
| `slides/deck.html` | The whole deck in one offline file (71 slides). Open in Chrome. |
| `slides/deck.pdf` | Same deck as PDF, every animation at its final frame. |
| `notebooks/student/` | NB0–NB5 as participants get them (exercises, outputs cleared). |
| `notebooks/solutions/` | Same notebooks with complete code. |
| `notebooks/instructor/NB5_prepare_cache.ipynb` | Builds NB5's judge cache (Gemma 3 4B on a T4). |
| `data/nb5/` | Small fallback cache built with Qwen2.5-0.5B (lets NB5 run if the Gemma cache is missing). |
| `printables/` | Cheat sheet, transfer canvas, Colab troubleshooting (PDF + HTML source). |
| `slides/parts/`, `slides/engine/`, `notebooks/src/` | Sources. Edit these, then rebuild (below). |

## Presenting

Open `slides/deck.html`, press **F** for fullscreen. **→ / Space** next step, **←** back, **N** speaker notes (with cumulative clock), **T** elapsed timer, type a number + **Enter** to jump. The deck works offline; with internet it loads its web fonts.

| Time | Presenter | Slides | Notebook |
|---|---|---|---|
| 0:00–0:30 | Miguel González | 1–20 (hook, primer, Block 1 Observe) | NB0, NB1 |
| 0:30–2:10 (break 1:00–1:10) | Salvador Hinojosa | 21–50 (Blocks 2–4: cause → units → circuits) | NB2, NB3, NB4 |
| 2:10–3:00 | Víctor Macías-Terrón | 51–71 (Block 5 Audit, wrap) | NB5 |

## Rebuilding

```bash
python3 slides/engine/build.py                         # -> slides/deck.html
python3 slides/engine/make_pdf.py slides/deck.html slides/deck.pdf
python3 slides/engine/overflow.py slides/deck.html     # layout check
cd notebooks/src && for n in 0 1 2 3 4 5; do python3 build_nb$n.py; done
```

Do not hand-edit the `.ipynb` files; change the generators in `notebooks/src/` and rebuild.

## What was tested, and what was not

- **Tested (CPU):** NB0–NB2 end to end (student + solutions); NB3 on the GPT-2 fallback and Gemma 3 1B via an ungated mirror (CPU, bf16); NB4 on the Neuronpedia path and the Gemma 3 270M CPU path; NB5 end to end on the Qwen2.5-0.5B cache. All GPT-2 numbers on the slides were recomputed and checked by an independent review.
- **Not tested:** anything needing a Hugging Face token or a GPU — Gemma on a Colab T4 (NB3 default, NB4 `gemma2` opt-in path, NB5 live judge and the instructor cache run), Colab-specific UI (secrets, iframes), and Neuronpedia under 20 simultaneous users.
- Numbers on slides are either computed (labelled with their source) or marked *illustrative* / *synthetic*.
