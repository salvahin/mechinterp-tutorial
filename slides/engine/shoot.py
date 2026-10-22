#!/usr/bin/env python3
"""Screenshot slides of a built deck with headless Chromium, and report JS errors.

Usage:
  python3 shoot.py <deck.html> <outdir> [spec ...]
  spec = "N" (slide N at its last step), "N.S" (slide N at step S), or "N@T" (slide N, last step,
         wait T seconds for animations before the shot). Default: every slide at its last step.

Prints console errors and page errors — fix every one before handing work back.
"""
import sys, asyncio, pathlib
from playwright.async_api import async_playwright


async def main():
    deck = pathlib.Path(sys.argv[1]).resolve()
    outdir = pathlib.Path(sys.argv[2]); outdir.mkdir(parents=True, exist_ok=True)
    specs = sys.argv[3:]
    errors = []
    async with async_playwright() as p:
        b = await p.chromium.launch()
        page = await b.new_page(viewport={"width": 1600, "height": 900})
        page.on("console", lambda m: m.type in ("error", "warning") and errors.append(f"console.{m.type}: {m.text}"))
        page.on("pageerror", lambda e: errors.append(f"pageerror: {e}"))
        await page.goto(deck.as_uri())
        await page.wait_for_function("window.__deckReady === true")
        n = await page.evaluate("Deck.slides.length")
        if not specs:
            specs = [str(i + 1) for i in range(n)]
        for spec in specs:
            wait = 1.6
            if "@" in spec:
                spec, w = spec.split("@"); wait = float(w)
            if "." in spec:
                i, s = spec.split("."); i, s = int(i) - 1, int(s)
            else:
                i, s = int(spec) - 1, None
            if s is None:
                await page.evaluate(f"Deck.go({i}, 999)")
            else:
                # walk the steps so step handlers fire in order
                await page.evaluate(f"Deck.go({i}, 0)")
                for k in range(1, s + 1):
                    await page.wait_for_timeout(250)
                    await page.evaluate(f"Deck.go({i}, {k})")
            await page.wait_for_timeout(int(wait * 1000))
            name = outdir / f"slide{i+1:02d}{'' if s is None else f'_s{s}'}.png"
            await page.screenshot(path=str(name))
            print("shot", name)
        await b.close()
    print(f"\n{len(errors)} console/page errors")
    for e in errors:
        print("  ", e)


asyncio.run(main())
