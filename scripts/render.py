#!/usr/bin/env python3
"""Render full.html and short.html to PNG (2x) and run layout checks.

Usage: python3 render.py OUT_DIR

- Installs the @fontsource packages the pages reference into OUT_DIR/fonts (Google Fonts
  is often blocked in sandboxes; npm works).
- full.html grows to fit its content; short.html stays 1080x1350 (4:5).
- Checks: no horizontal overflow, name does not run into the face, nothing spills past
  the footer, short version fits 1350px. Writes check crops (face, hair edges) for a
  visual review and report.json. Exit code 1 if a check fails.
"""
import sys, os, re, json, subprocess
from playwright.sync_api import sync_playwright

out = sys.argv[1]
pkgs = set()
for v in ("full", "short"):
    pkgs |= set(re.findall(r"@fontsource/([a-z0-9-]+)/", open(os.path.join(out, f"{v}.html"), encoding="utf-8").read()))
fdir = os.path.join(out, "fonts")
os.makedirs(fdir, exist_ok=True)
if not os.path.exists(os.path.join(fdir, "package.json")):
    subprocess.run(["npm", "init", "-y"], cwd=fdir, capture_output=True)
need = [p for p in pkgs if not os.path.isdir(os.path.join(fdir, "node_modules/@fontsource", p))]
if need:
    subprocess.run(["npm", "i", *[f"@fontsource/{p}" for p in need]], cwd=fdir, capture_output=True)

report, ok = {}, True
with sync_playwright() as p:
    b = p.chromium.launch()
    for v in ("full", "short"):
        pg = b.new_page(viewport={"width": 1080, "height": 1350}, device_scale_factor=2)
        pg.goto("file://" + os.path.abspath(os.path.join(out, f"{v}.html")))
        pg.wait_for_timeout(900)
        pg.wait_for_selector("body[data-fit]", state="attached", timeout=10000)
        m = pg.evaluate("""() => {
          const r = e => e ? e.getBoundingClientRect() : null;
          const h1 = document.querySelector('h1'); const rg = document.createRange(); rg.selectNodeContents(h1);
          const txt = rg.getBoundingClientRect(); const ph = r(document.querySelector('.photo'));
          const foot = r(document.querySelector('.foot'));
          const blocks = [...document.querySelectorAll('.chips,.roles')].map(e=>r(e).bottom);
          const xs=[...document.querySelectorAll('.z *')].map(e=>e.getBoundingClientRect()).filter(b=>b.width>0);
          return {scrollW: Math.max(...xs.map(b=>b.right)) - Math.min(0, ...xs.map(b=>b.left)), scrollH: Math.ceil(document.querySelector('.foot').getBoundingClientRect().bottom + 48),
                  name: [txt.left, txt.right, txt.top, txt.bottom], photo: [ph.left, ph.right, ph.top, ph.bottom],
                  footTop: foot.top, lastBlock: Math.max(...blocks), dir: document.documentElement.dir};
        }""")
        H = max(1350, m["scrollH"]) if v == "full" else 1350
        pg.set_viewport_size({"width": 1080, "height": H})
        pg.wait_for_timeout(300)
        m = {**m, **pg.evaluate("() => ({footTop: document.querySelector('.foot').getBoundingClientRect().top})")}
        png = os.path.join(out, f"{v}.png")
        pg.screenshot(path=png)
        # the face sits in the middle ~40% of the photo box; the name must not cross it
        pl, pr = m["photo"][0], m["photo"][1]
        face = (pl + (pr - pl) * 0.3, pl + (pr - pl) * 0.7)
        nl, nr = m["name"][0], m["name"][1]
        checks = {
            "no_horizontal_overflow": m["scrollW"] <= 1080,
            "name_clear_of_face": nr < face[0] if m["dir"] == "ltr" else nl > face[1],
            "content_above_footer": m["lastBlock"] <= m["footTop"] + 1,
            "short_fits_4x5": True if v == "full" else m["scrollH"] <= 1350,
        }
        report[v] = {"size": [1080, H], "checks": checks, "metrics": m}
        ok &= all(checks.values())
        # review crops: whole photo area, head/hair edge, chin/beard edge (2x pixels)
        from PIL import Image
        im = Image.open(png)
        s = 2
        x0, x1, y0, y1 = [int(max(0, c) * s) for c in (pl, pr, m["photo"][2], m["photo"][3])]
        x1 = min(x1, im.width); y1 = min(y1, im.height)
        im.crop((x0, y0, x1, y1)).save(os.path.join(out, f"{v}-check-photo.png"))
        hh = y1 - y0
        im.crop((x0, y0, x1, y0 + hh // 2)).save(os.path.join(out, f"{v}-check-hair.png"))
        im.crop((x0, y0 + int(hh * .35), x1, y0 + int(hh * .75))).save(os.path.join(out, f"{v}-check-chin.png"))
        pg.close()
    b.close()

json.dump(report, open(os.path.join(out, "report.json"), "w"), indent=2)
for v, r in report.items():
    print(v, r["size"], {k: ("OK" if x else "FAIL") for k, x in r["checks"].items()})
sys.exit(0 if ok else 1)
