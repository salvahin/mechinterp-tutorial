#!/usr/bin/env python3
"""Assemble the tutorial deck into ONE self-contained HTML file.

Usage:
  python3 build.py                 # full deck  -> slides/deck.html
  python3 build.py part1_miguel    # one part   -> slides/preview_part1_miguel.html

Parts live in slides/parts/*.html and contain only <section class="slide"> elements
(plus optional <style> and <script> blocks). They are concatenated in filename order.
CSS and JS from slides/engine/ are inlined, so the output works offline (fonts fall
back to system fonts when offline).
"""
import sys, pathlib, re, html

ROOT = pathlib.Path(__file__).resolve().parents[1]          # slides/
ENGINE = ROOT / "engine"
PARTS = ROOT / "parts"

HEAD = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Serif:ital,wght@0,400;0,600;1,400&family=Inter:wght@400;500;600;700&family=Sora:wght@500;600;700;800&display=swap" rel="stylesheet">
<style>
{css}
</style>
<script>
{js}
</script>
</head>
<body>
<div class="viewport"><div class="stage">
"""
TAIL = """
</div></div>
</body>
</html>
"""


MIME = {".png": "image/png", ".webp": "image/webp", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".svg": "image/svg+xml"}


def inline_assets(doc):
    """Replace src="assets/<file>" with a base64 data URI so the deck stays one file."""
    import base64

    def repl(m):
        p = ROOT / "assets" / m.group(1)
        data = base64.b64encode(p.read_bytes()).decode()
        return f'src="data:{MIME[p.suffix.lower()]};base64,{data}"'

    return re.sub(r'src="assets/([^"]+)"', repl, doc)


def build(part_names=None, out=None, title="Opening the Black Box — Mechanistic Interpretability of LLMs · MICAI 2026"):
    css = (ENGINE / "deck.css").read_text()
    js = (ENGINE / "deck.js").read_text()
    files = sorted(PARTS.glob("*.html"))
    if part_names:
        files = [f for f in files if any(f.stem.startswith(p) for p in part_names)]
    if not files:
        sys.exit("no parts found")
    body = []
    for f in files:
        body.append(f"\n<!-- ===== {f.name} ===== -->\n")
        body.append(f.read_text())
    doc = HEAD.format(title=html.escape(title), css=css, js=js) + "".join(body) + TAIL
    doc = inline_assets(doc)
    out = out or (ROOT / ("deck.html" if not part_names else f"preview_{'_'.join(part_names)}.html"))
    out.write_text(doc)
    n = len(re.findall(r'<section\s+class="[^"]*\bslide\b', "".join(body)))
    print(f"wrote {out}  ({n} slides, {len(doc)//1024} KB)")
    return out


if __name__ == "__main__":
    build(sys.argv[1:] or None)
