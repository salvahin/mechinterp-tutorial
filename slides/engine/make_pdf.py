#!/usr/bin/env python3
"""Export the deck to PDF (one slide per page, every build and animation at its final frame).

Usage: python3 make_pdf.py <deck.html> <out.pdf>
"""
import sys, asyncio, pathlib
from playwright.async_api import async_playwright


async def main():
    deck = pathlib.Path(sys.argv[1]).resolve()
    out = pathlib.Path(sys.argv[2]).resolve()
    errors = []
    async with async_playwright() as p:
        b = await p.chromium.launch()
        page = await b.new_page(viewport={"width": 1600, "height": 900})
        page.on("pageerror", lambda e: errors.append(str(e)))
        await page.goto(deck.as_uri())
        await page.wait_for_function("window.__deckReady === true")
        await page.wait_for_timeout(1500)            # web fonts
        await page.emulate_media(media="print")
        await page.evaluate("Deck.preparePrint()")
        await page.wait_for_timeout(1200)            # let any rAF-based final frames settle
        await page.pdf(path=str(out), width="1600px", height="900px", print_background=True,
                       margin={"top": "0", "right": "0", "bottom": "0", "left": "0"})
        await b.close()
    print(f"wrote {out}")
    if errors:
        print(f"{len(errors)} page errors:"); [print("  ", e) for e in errors]


asyncio.run(main())
