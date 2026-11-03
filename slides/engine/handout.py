#!/usr/bin/env python3
"""Print Block 5's speaker text from the built deck: two handouts, one PDF each.

    python3 handout.py                      # -> printables/block5_notes.*, block5_speech.*
    python3 handout.py --html-only          # skip the PDF render

  block5_notes   the director's notes for slides 51-71 (what to do and say, in
                 shorthand) - the same text the N panel shows.
  block5_speech  the word-for-word script for the same slides, the one the
                 presenter window shows in SPEECH mode (speech_victor.py).

Both are bilingual: Spanish first, because that is what Víctor reads from, then
the English the slides are written in. The build reads slides/deck.html rather
than the sources, so the slide numbers, titles and step counts are exactly the
ones the deck shows, and anything that is in the deck is in the handout.
"""
import re, sys, asyncio, pathlib, html

ROOT = pathlib.Path(__file__).resolve().parents[2]        # repository root
DECK = ROOT / "slides" / "deck.html"
OUT = ROOT / "printables"

SECTION = re.compile(r'<section class="(?P<cls>[^"]*\bslide\b[^"]*)"(?P<attrs>[^>]*)>(?P<body>.*?)</section>', re.S)
ASIDE = re.compile(r'<aside class="(notes|speech)">(.*?)</aside>', re.S)
LANG = re.compile(r'<div data-lang="(\w\w)">(.*?)</div>\s*(?=<div data-lang=|$)', re.S)
CUE = re.compile(r'<p class="cue"([^>]*)>', re.S)

CUE_WORDS = {"es": ("paso ", "pasos "), "en": ("step ", "steps ")}


def attr(s, name):
    m = re.search(r'\b%s="([^"]*)"' % name, s)
    return m.group(1) if m else ''


def label_cues(body, lang):
    """Give every build-step paragraph the label deck.js composes on screen."""
    one, many = CUE_WORDS.get(lang, CUE_WORDS["en"])

    def one_cue(m):
        a = m.group(1)
        k, rng, suffix = attr(a, 'data-cue'), attr(a, 'data-range'), attr(a, 'data-suffix')
        if rng:
            text = many + rng
        elif k == '0':
            text = 'al entrar' if lang == 'es' else 'on arrival'
        else:
            text = one + k
        if suffix:
            text += ' · ' + suffix
        return f'<p class="cue" data-label="{text.upper()}">'

    # <i>[ ... ]</i> is a stage direction, not a line to read: grey it out so the
    # eye skips it. Plain <i> inside the prose is emphasis and stays as it is.
    return re.sub(r'<i>(\s*\[)', r'<i class="stage">\1', CUE.sub(one_cue, body))


def slides_of(deck_html):
    """[(number, id, title, block, steps, {'notes': {lang: html}, 'speech': {...}})] for p3-*.

    Scanning starts at the stage: the inlined deck.js documents the slide markup
    in its header comment, and that example would otherwise count as slide 1 and
    shift every number by one.
    """
    stage = deck_html.index('<div class="stage">')
    out = []
    for n, m in enumerate(SECTION.finditer(deck_html, stage), start=1):
        sid = attr(m.group('attrs'), 'id')
        if not sid.startswith('p3-'):
            continue
        body = m.group('body')
        title = re.search(r'<h[12][^>]*>(.*?)</h[12]>', body, re.S)
        title = re.sub(r'<[^>]+>', '', title.group(1)).strip() if title else sid
        steps = attr(m.group('attrs'), 'data-steps') or '0'
        declared = max([int(x) for x in re.findall(r'data-step="(\d+)"', body)] + [int(steps)])
        text = {}
        for am in ASIDE.finditer(body):
            kind, inner = am.group(1), am.group(2)
            blocks = dict(LANG.findall(inner))
            text[kind] = blocks or {'en': inner}
        out.append((n, sid, re.sub(r'\s+', ' ', html.unescape(title)), attr(m.group('attrs'), 'data-block'), declared, text))
    return out


CSS = """
@page { size: Letter portrait; margin: 0.6in 0.7in 0.55in; }
:root {
  --ink: #0C198D; --ink-2: #333A5E; --muted: #6B7090; --rule: #C9C3B5; --victor: #C2187E;
  --sans: "Inter", "Helvetica Neue", Arial, "Liberation Sans", sans-serif;
  --cond: "Sora", "Inter", "Helvetica Neue", Arial, sans-serif;
  --mono: "IBM Plex Mono", Menlo, Consolas, "DejaVu Sans Mono", monospace;
}
* { box-sizing: border-box; }
html, body { margin: 0; background: #fff; }
body { font-family: var(--sans); color: var(--ink-2); font-size: %(fs)s;
       line-height: %(lh)s; -webkit-print-color-adjust: exact; print-color-adjust: exact; }

header.doc { border-bottom: 2.4px solid var(--victor); padding-bottom: 6px; margin-bottom: 14px; }
header.doc h1 { font-family: var(--cond); color: var(--ink); font-size: 17pt; margin: 0 0 3px;
                letter-spacing: -.01em; }
header.doc p { margin: 0; font-size: 8.4pt; color: var(--muted); }
header.doc b { color: var(--ink); }

.slide { break-inside: avoid; margin: 0 0 15px; padding-bottom: 11px;
         border-bottom: 1px solid var(--rule); }
.slide:last-child { border-bottom: 0; }
.slide > h2 { font-family: var(--cond); color: var(--ink); font-size: 11.6pt; margin: 0 0 2px;
              line-height: 1.2; }
.slide > h2 .n { color: var(--victor); font-family: var(--mono); font-size: 9.4pt; margin-right: 6px; }
.slide > .meta { font-size: 7.6pt; color: var(--muted); font-family: var(--mono);
                 margin: 0 0 7px; letter-spacing: .02em; }

.lang { margin: 0 0 8px; padding-left: 10px; border-left: 3px solid var(--rule); }
.lang:last-child { margin-bottom: 0; }
.lang.es { border-left-color: var(--victor); }
.lang > .tag { display: inline-block; font-family: var(--cond); font-weight: 700; font-size: 7pt;
               letter-spacing: .14em; color: #fff; background: var(--muted);
               padding: 2px 6px; border-radius: 4px; margin-bottom: 5px; }
.lang.es > .tag { background: var(--victor); }
.lang p { margin: 0 0 5px; }
.lang p:last-child { margin-bottom: 0; }
.lang b { color: var(--ink); }
.lang i { color: var(--ink); }
.lang i.stage { color: var(--muted); font-weight: 500; }
.lang code, .lang .mono { font-family: var(--mono); font-size: .92em; }
.lang a { color: var(--ink); text-decoration: none; }

p.cue { padding-left: 9px; border-left: 2.5px solid #C9D2EA; }
p.cue::before { content: attr(data-label) " · "; font-family: var(--cond); font-weight: 700;
                font-size: 7pt; letter-spacing: .1em; color: var(--muted); }

footer.doc { margin-top: 10px; font-size: 7.4pt; color: var(--muted); }
"""

PAGE = """<!doctype html>
<html lang="es"><head><meta charset="utf-8"><title>%(title)s</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=Inter:ital,wght@0,400;0,500;0,600;0,700;1,400&family=Sora:wght@600;700&display=swap" rel="stylesheet">
<style>%(css)s</style></head><body>
<header class="doc"><h1>%(h1)s</h1><p>%(sub)s</p></header>
%(slides)s
<footer class="doc">%(foot)s</footer>
</body></html>
"""

LANG_NAME = {'es': 'Español', 'en': 'English'}


def document(kind, slides, title, h1, sub, foot, fs, lh):
    chunks = []
    for n, sid, title_text, block, steps, text in slides:
        blocks = text.get(kind, {})
        if not blocks:
            continue
        meta = f'slide {n} · {sid}' + (f' · {block}' if block else '') + f' · {steps} step(s)'
        langs = []
        for tag in ('es', 'en'):
            if tag in blocks:
                langs.append(f'<div class="lang {tag}"><span class="tag">{LANG_NAME[tag]}</span>\n'
                             + label_cues(blocks[tag].strip(), tag) + '</div>')
        chunks.append(f'<div class="slide"><h2><span class="n">{n}</span>{html.escape(title_text)}</h2>'
                      f'<p class="meta">{meta}</p>\n' + '\n'.join(langs) + '</div>')
    return PAGE % dict(title=title, h1=h1, sub=sub, foot=foot,
                       css=CSS % dict(fs=fs, lh=lh), slides='\n'.join(chunks))


async def render(paths):
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        b = await p.chromium.launch()
        page = await b.new_page()
        for src, out in paths:
            await page.goto(src.as_uri())
            await page.wait_for_timeout(1200)                 # web fonts
            await page.emulate_media(media="print")
            await page.pdf(path=str(out), format="Letter", print_background=True,
                           display_header_footer=True, header_template="<div></div>",
                           footer_template='<div style="width:100%;font:8px Inter,sans-serif;'
                                           'color:#6B7090;text-align:center;padding:0 0.7in;">'
                                           '<span class="pageNumber"></span> / <span class="totalPages"></span></div>',
                           margin={"top": "0.6in", "right": "0.7in", "bottom": "0.55in", "left": "0.7in"})
            print(f"wrote {out}")
        await b.close()


def main():
    deck = DECK.read_text(encoding="utf-8")
    slides = slides_of(deck)
    if not slides:
        sys.exit("no p3-* slides found in slides/deck.html — build the deck first")
    first, last = slides[0][0], slides[-1][0]
    common = ("Tutorial · <b>Opening the Black Box: Mechanistic Interpretability of LLMs</b> · "
              "MICAI 2026 · Bloque 5 &ldquo;Audit&rdquo; · Víctor Terrón-Macías · "
              f"slides {first}&ndash;{last} · 2:10&ndash;3:00")
    docs = [
        ("notes", "block5_notes", "Bloque 5 · notas del presentador",
         "Notas de dirección (lo que hay que hacer y decir, en taquigrafía): el mismo texto "
         "que muestra el panel <b>N</b> del deck. Español primero, inglés después.",
         "9.6pt", "1.33"),
        ("speech", "block5_speech", "Bloque 5 · guion palabra por palabra",
         "Guion para leer en voz alta (modo <b>SPEECH</b> de la ventana de presenter, "
         "<code>slides/engine/speech_victor.py</code>). Incluye el bloque práctico de NB5: "
         "la predicción previa, los 22 minutos en parejas y el debrief. "
         "Las indicaciones entre corchetes no se leen.",
         "10.6pt", "1.42"),
    ]
    paths = []
    for kind, stem, h1, sub, fs, lh in docs:
        body = document(kind, slides, h1, h1, common + '<br>' + sub,
                        'Generado desde slides/deck.html · rehacer con '
                        '<code>python3 slides/engine/handout.py</code> después de reconstruir el deck.',
                        fs, lh)
        src = OUT / f"{stem}.html"
        src.write_text(body, encoding="utf-8")
        n = body.count('<div class="slide">')
        print(f"wrote {src}  ({n} slides)")
        paths.append((src, OUT / f"{stem}.pdf"))
    if "--html-only" not in sys.argv:
        asyncio.run(render(paths))


if __name__ == "__main__":
    main()
