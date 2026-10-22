#!/usr/bin/env python3
"""Flag slides whose content overflows the stage or runs into the footer zone.

Usage: python3 overflow.py <deck.html>
Checks every slide at its last step: any visible element whose box extends past the right
edge (1600 - 24) or below the footer line (900 - 78), and any text element whose
scrollWidth/scrollHeight exceeds its box (clipped text). Prints offenders per slide.
"""
import sys, asyncio, pathlib, json
from playwright.async_api import async_playwright

JS = r"""
(i) => {
  Deck.go(i, 999);
  const s = Deck.slides[i];
  const sr = s.getBoundingClientRect();
  const out = [];
  const label = el => (el.id ? '#' + el.id : el.tagName.toLowerCase() + (el.className && typeof el.className === 'string' ? '.' + el.className.split(' ').join('.') : '')) + ' "' + (el.textContent || '').trim().slice(0, 50) + '"';
  for (const el of s.querySelectorAll('*')) {
    if (el.closest('aside.notes') || el.closest('svg') && el.tagName.toLowerCase() !== 'svg') continue;
    const cs = getComputedStyle(el);
    if (cs.display === 'none' || cs.visibility === 'hidden' || parseFloat(cs.opacity) === 0) continue;
    const r = el.getBoundingClientRect();
    if (r.width === 0 || r.height === 0) continue;
    const x2 = r.right - sr.left, y2 = r.bottom - sr.top;
    if (x2 > 1600 - 24 + 1) out.push(['right', Math.round(x2), label(el)]);
    if (y2 > 900 - 78 + 1 && !el.closest('.t-photo') && !el.classList.contains('t-photo')) out.push(['bottom', Math.round(y2), label(el)]);
    const hasText = [...el.childNodes].some(n => n.nodeType === 3 && n.textContent.trim());
    if (hasText && (cs.overflow !== 'visible' || cs.textOverflow === 'ellipsis') && (el.scrollWidth > el.clientWidth + 2 || el.scrollHeight > el.clientHeight + 2))
      out.push(['clipped', 0, label(el)]);
  }
  return {id: s.id, issues: out};
}
"""


async def main():
    deck = pathlib.Path(sys.argv[1]).resolve()
    async with async_playwright() as p:
        b = await p.chromium.launch()
        page = await b.new_page(viewport={"width": 1600, "height": 900})
        await page.goto(deck.as_uri())
        await page.wait_for_function("window.__deckReady === true")
        await page.wait_for_timeout(1500)  # fonts
        n = await page.evaluate("Deck.slides.length")
        bad = 0
        for i in range(n):
            res = await page.evaluate(JS, i)
            # keep the outermost offenders only (dedupe by kind)
            if res["issues"]:
                bad += 1
                print(f"slide {i+1} {res['id']}:")
                seen = set()
                for kind, v, lab in res["issues"]:
                    key = (kind, lab[:40])
                    if key in seen: continue
                    seen.add(key)
                    print(f"   {kind:7} {v:5}  {lab}")
        print(f"\n{bad} slides with possible overflow out of {n}")
        await b.close()

asyncio.run(main())
