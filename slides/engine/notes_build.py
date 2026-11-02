#!/usr/bin/env python3
"""Turn the parts' speaker notes into labelled, bilingual notes.

Two jobs, both done at build time so parts/*.html stays the English source:

1. cues(text)  - the notes write their builds inline as "Step 2: ..." (sometimes
   with a leading arrow). Each marker becomes its own <p class="cue" data-cue="n">
   block, which deck.js then labels and highlights: dim for a build already on
   screen, blue for the current one, amber "press ->" for the one the next arrow
   will reveal. Paragraph boundaries come from the newlines the notes already use,
   so trailing commentary ("Key sentence: ...") stays outside the last step block
   instead of being swallowed by it.

2. wrap(part_html, es) - wraps each note in <div data-lang="en"> and appends the
   Spanish translation from notes_es.py as <div data-lang="es">. Slides with no
   translation yet keep a single English block, and deck.js falls back to it.
"""
import re

# "Step 3:", "-> Step 3:", "Step 1 (->):", "Steps 3 and 4:", "Step 2, Decompose:"
# and the Spanish notes' "Paso 3:", "Pasos 3 y 4:", "Paso 2, Descomponer:".
MARK = re.compile(
    r'(?:&rarr;|&#8594;|→)?\s*'
    r'\b(?:Step|Paso)(s)?\s+(\d+)'
    r'(?:\s*\((?:&rarr;|→)\))?'
    r'(?:\s*(?:and|to|y|a|&ndash;|–|-)\s*(\d+))?'
    r'(?:\s*,\s*(?:<[^>]+>)?([A-Za-z][A-Za-z ]{0,18}?)(?:</[^>]+>)?)?'   # "Step 1, <b>Edit</b>:"
    # ends in a colon, or in a comma that opens a new sentence ("Step 1, NB4's default ...").
    # A comma followed by lowercase is prose ("in Step 3, the model ...") and is left alone.
    r'\s*(?::|,(?=\s*[A-Z]))\s*',
    re.I)

CUE_OPEN = '<p class="cue" data-cue="{n}"{label}>'


def _label(first, second, suffix):
    """Emit the raw pieces; deck.js composes the wording so it can be localised."""
    if second:
        return f' data-range="{first}-{second}"'
    if suffix:
        return f' data-suffix="{suffix.strip().lower()}"'
    return ''


def cues(text):
    """Rewrite one note body, marker by marker, keeping every character of prose."""
    out = []
    for chunk in text.split('\n'):
        if not chunk.strip():
            continue
        marks = list(MARK.finditer(chunk))
        if not marks:
            out.append(f'<p>{chunk.strip()}</p>')
            continue
        head = chunk[:marks[0].start()].strip()
        if head:
            out.append(f'<p>{head}</p>')
        for i, m in enumerate(marks):
            end = marks[i + 1].start() if i + 1 < len(marks) else len(chunk)
            body = chunk[m.end():end].strip()
            plural, first, second, suffix = m.groups()
            out.append(CUE_OPEN.format(n=first, label=_label(first, second, suffix))
                       + body + '</p>')
    return '\n    '.join(out)


SECTION = re.compile(r'<section class="[^"]*\bslide\b[^"]*"[^>]*?\bid="([^"]+)"[^>]*>.*?</section>', re.S)
ASIDE = re.compile(r'<aside class="notes">(.*?)</aside>', re.S)


def wrap(part_html, es=None):
    """Make every note in one part file bilingual. Returns (html, n_en, n_es)."""
    es = es or {}
    stats = [0, 0]

    def one_section(sm):
        sid, block = sm.group(1), sm.group(0)
        am = ASIDE.search(block)
        if not am:
            return block
        stats[0] += 1
        parts = [f'<div data-lang="en">\n    {cues(am.group(1))}\n  </div>']
        if sid in es:
            stats[1] += 1
            parts.append(f'<div data-lang="es">\n    {cues(es[sid])}\n  </div>')
        new = '<aside class="notes">\n  ' + '\n  '.join(parts) + '\n  </aside>'
        return block[:am.start()] + new + block[am.end():]

    return SECTION.sub(one_section, part_html), stats[0], stats[1]
