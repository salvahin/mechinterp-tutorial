#!/usr/bin/env python3
"""Assemble the ONE-HOUR solo variant of the tutorial deck.

    python3 build_1h.py            # -> slides/deck_1h.html

The 4-hour tutorial deck is untouched: this script never writes to slides/deck.html
and never adds files to slides/parts/ (which build.py globs).

How it works
------------
Blocks 1-4 are compressed to a 13-minute speed-run by selecting a subset of the
sections in parts/part1_miguel.html and parts/part2_salvador.html. Block 5 is kept
whole from parts/part3_victor.html, minus its hands-on slides, plus the three
results slides in parts_1h/extra_1h.html that stand in for the 22-minute NB5
work block. Every kept slide gets a fresh <aside class="notes"> speaker script
from script_1h.py, re-timed to a 0:00-0:54 solo run.

Top-level <style> and <script> blocks of each source part are carried over as a
whole. Unused CSS is harmless, and deck.js only fires Deck.on(id, ...) handlers
when the active slide carries that id, so handlers for dropped slides never run.
"""
import re, pathlib, sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import build as build4                                   # reuse HEAD/TAIL/inline_assets
from script_1h import SCRIPT, PATCHES

ROOT = pathlib.Path(__file__).resolve().parents[1]        # slides/
PARTS = ROOT / "parts"
EXTRA = ROOT / "parts_1h" / "extra_1h.html"

TITLE = ("Opening the Black Box — Mechanistic Interpretability of LLMs · "
         "one-hour solo run")

# ---------------------------------------------------------------- slide order
# Part A: blocks 1-4 in nine minutes. Every hands-on and audience-poll slide is
# dropped, and so is everything Block 5 does not actually lean on. What survives
# is one chain: concepts are directions -> the stream you read them from -> you
# can watch an answer form -> but reading is not cause -> so you intervene.
#
# Deliberately cut, and why: p2-heatmap (a result about a mechanism Block 5 never
# revisits), p2-super and p2-sae (Block 5 needs only "features are directions",
# which p1-pr-direction already gives), p2-graph (attribution graphs never come
# back). Their speaker scripts stay in script_1h.py in case one is put back.
PART_A = [
    ("part1_miguel",   "p1-title"),          # retitled by PATCHES
    ("extra_1h",       "h-roadmap"),         # new: what this hour is
    ("part1_miguel",   "p1-hook"),           # why read the computation
    ("part1_miguel",   "p1-pr-direction"),   # a direction can mean something -> the probe
    ("part1_miguel",   "p1-residual-bus"),   # the residual stream
    ("part1_miguel",   "p1-logit-lens"),     # block 1 payoff
    ("part1_miguel",   "p1-limits"),         # correlation, not cause -> block 2
    ("part2_salvador", "p2-transplant"),     # activation patching -> the grounding check
    ("part2_salvador", "p2-recap"),          # intervention is the test -> Block 5
]

# Part B: Block 5 whole, with the 22-minute hands-on replaced by a results tour.
# Dropped: p3-predict (audience commitment device, needs the hands-on to pay off).
PART_B = [
    ("part3_victor", "p3-section"),
    ("part3_victor", "p3-open"),
    ("part3_victor", "p3-grid"),
    ("part3_victor", "p3-iso"),
    ("part3_victor", "p3-rule"),
    ("part3_victor", "p3-verdict"),
    ("part3_victor", "p3-probe"),
    ("part3_victor", "p3-ground"),
    ("part3_victor", "p3-why"),
    ("part3_victor", "p3-a10"),
    ("part3_victor", "p3-conformal"),
    ("part3_victor", "p3-legal"),
    ("part3_victor", "p3-nb5"),              # reframed by PATCHES: a tour, not a work block
    ("extra_1h",     "h-nb5-result"),        # new: what the probe wins
    ("extra_1h",     "h-nb5-shift"),         # new: where it breaks
    ("extra_1h",     "h-nb5-routing"),       # new: the threshold an auditor would sign
    ("part3_victor", "p3-debrief"),
    ("part3_victor", "p3-map"),
    ("part3_victor", "p3-transfer"),
    ("part3_victor", "p3-field"),
    ("part3_victor", "p3-res"),
    ("part3_victor", "p3-thanks"),
]

ORDER = PART_A + PART_B
SECTION_RE = re.compile(r'<section class="[^"]*\bslide\b[^"]*"[^>]*?\bid="([^"]+)"[^>]*>.*?</section>', re.S)


def load(stem):
    """Return (sections_by_id, top_level_styles, top_level_scripts) for one part file.

    Styles and scripts are kept apart because their position matters: the parts'
    scripts do top-level DOM lookups (document.getElementById('p3-grid') and the
    like), so they have to run *after* the sections exist, exactly as they do in
    the source files. Styles can go anywhere and are emitted first.
    """
    path = EXTRA if stem == "extra_1h" else PARTS / f"{stem}.html"
    text = path.read_text(encoding="utf-8")
    sections, spans = {}, []
    for m in SECTION_RE.finditer(text):
        sections[m.group(1)] = m.group(0)
        spans.append((m.start(), m.end()))

    def inside(pos):
        return any(a <= pos < b for a, b in spans)

    styles, scripts = [], []
    for m in re.finditer(r"<(style|script)\b[^>]*>.*?</\1>", text, re.S):
        if inside(m.start()):
            continue
        (styles if m.group(1) == "style" else scripts).append(m.group(0))
    return sections, styles, scripts


def set_notes(section, sid):
    """Replace the slide's speaker notes with the one-hour script."""
    body = SCRIPT.get(sid)
    if body is None:
        print(f"  ! no script for {sid}")
        return section
    aside = '<aside class="notes">\n' + body.strip() + "\n  </aside>"
    if re.search(r'<aside class="notes">.*?</aside>', section, re.S):
        return re.sub(r'<aside class="notes">.*?</aside>', lambda _: aside, section, count=1, flags=re.S)
    return section[: section.rindex("</section>")] + "  " + aside + "\n</section>"


def main():
    css = (ROOT / "engine" / "deck.css").read_text(encoding="utf-8")
    js = (ROOT / "engine" / "deck.js").read_text(encoding="utf-8")

    cache, styles, scripts, body = {}, [], [], []
    for stem in dict.fromkeys(s for s, _ in ORDER):          # preserve first-seen order
        cache[stem] = load(stem)
        styles += cache[stem][1]
        scripts += cache[stem][2]

    missing = [sid for stem, sid in ORDER if sid not in cache[stem][0]]
    if missing:
        sys.exit(f"missing sections: {missing}")

    for stem, sid in ORDER:
        section = cache[stem][0][sid]
        for pat, repl in PATCHES.get(sid, []):
            if pat not in section:
                sys.exit(f"patch for {sid} did not match: {pat[:60]!r}")
            section = section.replace(pat, repl, 1)
        body.append(f"\n<!-- {sid} -->\n" + set_notes(section, sid))

    doc = (build4.HEAD.format(title=TITLE, css=css, js=js)
           + "\n".join(styles) + "".join(body) + "\n" + "\n".join(scripts)
           + build4.TAIL)
    doc = build4.inline_assets(doc)
    out = ROOT / "deck_1h.html"
    out.write_text(doc, encoding="utf-8")
    print(f"wrote {out}  ({len(ORDER)} slides, {len(doc)//1024} KB)")


if __name__ == "__main__":
    main()
