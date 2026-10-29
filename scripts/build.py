#!/usr/bin/env python3
"""Build the two profile-page versions (HTML) from a config JSON.

Usage: python3 build.py config.json OUT_DIR

Writes OUT_DIR/full.html (native language, everything they built, tall page)
and OUT_DIR/short.html (second language, 4:5 card: name, title, roles).
See ../examples/config.example.json for every field.
"""
import json, sys, os, html

DEFAULT_THEME = {
    "bg": "#060B09", "card": "#0C1512", "line": "#16302A", "muted": "#8FA89E",
    "text": "#EAF5EF", "accent": "#3EFFA3",
    "display_font": "Suez One", "body_font": "Heebo", "mono_font": "JetBrains Mono",
    "name_font": "Heebo", "grid": True, "terminal_bar": True,
}

def esc(s):
    return html.escape(str(s), quote=True)

def ltr(s):
    """Wrap Latin/mixed text so punctuation sits correctly inside RTL layouts."""
    s = esc(s)
    return f'<bdi dir="ltr">{s}</bdi>' if any('a' <= c.lower() <= 'z' for c in s) else s

def font_links(theme):
    fams = {theme[k] for k in ("display_font", "body_font", "mono_font", "name_font")}
    out = []
    for fam in sorted(fams):
        pkg = fam.lower().replace(' ', '-')
        for wgt in ("400", "700", "800", "900"):
            p = f"fonts/node_modules/@fontsource/{pkg}/{wgt}.css"
            out.append(f'<link rel="stylesheet" href="{p}">')
    return "\n".join(out)

def css(t, dirn, photo_side):
    grid = ("body:before{content:'';position:absolute;inset:0;background-image:linear-gradient(var(--line) 1px,transparent 1px),"
            "linear-gradient(90deg,var(--line) 1px,transparent 1px);background-size:54px 54px;opacity:.35;"
            "mask-image:radial-gradient(circle at 50% 20%,#000 0,transparent 70%);z-index:0}") if t.get("grid", True) else ""
    glow_x = "75%" if photo_side == "right" else "25%"
    return f"""
:root{{--g:{t['accent']};--bg:{t['bg']};--card:{t['card']};--line:{t['line']};--mut:{t['muted']};--txt:{t['text']}}}
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:1080px;overflow:hidden}}
body{{background:var(--bg);color:var(--txt);font-family:'{t['body_font']}',system-ui,sans-serif;position:relative;padding:56px 64px 48px;
  min-height:1350px;display:flex;flex-direction:column;overflow:hidden}}
{grid}
.backlight{{position:absolute;inset:0;z-index:0;background:radial-gradient(440px 400px at {glow_x} 340px,color-mix(in srgb,var(--g) 22%,transparent),transparent 70%)}}
.z{{position:relative;z-index:2}}
.mono{{font-family:'{t['mono_font']}',ui-monospace,monospace}}
.bar{{display:flex;justify-content:space-between;align-items:center;border:1px solid var(--line);background:color-mix(in srgb,var(--card) 80%,transparent);
  border-radius:14px;padding:14px 22px;font-size:20px;color:var(--mut)}}
.dots{{display:flex;gap:9px;direction:ltr}}.dots i{{width:13px;height:13px;border-radius:50%;background:var(--line)}}.dots i:first-child{{background:var(--g)}}
.logo{{font-family:'{t['display_font']}';font-size:28px}}.logo b{{color:var(--g);font-weight:400}}
.hero{{position:relative;margin-top:80px;min-height:520px}}
.prompt{{font-size:24px;color:var(--g);direction:ltr;text-align:{'right' if dirn=='rtl' else 'left'}}}
h1{{font-family:'{t['name_font']}';font-weight:900;font-size:var(--nsize,108px);line-height:1;margin-top:16px;letter-spacing:-2px;max-width:620px}}
h1 .dot{{color:var(--g)}}
.title{{display:inline-flex;align-items:center;gap:14px;margin-top:34px;border:2px solid var(--g);color:var(--g);border-radius:999px;
  padding:13px 30px;font-size:38px;font-weight:800;box-shadow:0 0 44px color-mix(in srgb,var(--g) 25%,transparent);background:color-mix(in srgb,var(--bg) 70%,transparent)}}
.tools{{display:flex;flex-wrap:wrap;gap:10px;margin-top:22px;direction:ltr;justify-content:{'flex-end' if dirn=='rtl' else 'flex-start'};max-width:620px;{'margin-right:0;margin-left:auto' if dirn=='rtl' else ''}}}
.tools span{{font-family:'{t['mono_font']}';font-size:18px;color:var(--g);background:color-mix(in srgb,var(--g) 8%,transparent);
  border:1px solid color-mix(in srgb,var(--g) 30%,transparent);padding:6px 14px;border-radius:8px}}
.photo{{position:absolute;{photo_side}:-30px;top:120px;width:var(--psize,700px);height:var(--psize,700px);z-index:1;pointer-events:none}}
.roles{{display:grid;grid-template-columns:1fr 1fr;gap:24px;margin-top:30px}}
.role{{background:var(--card);border:1px solid var(--line);border-radius:22px;padding:26px 30px;position:relative;overflow:hidden}}
.role:before{{content:'';position:absolute;top:0;{'right' if dirn=='rtl' else 'left'}:0;width:6px;height:100%;background:var(--g)}}
.role .k{{font-size:19px;color:var(--mut);font-family:'{t['mono_font']}';letter-spacing:1px}}
.role .n{{font-family:'{t['display_font']}';font-size:48px;margin-top:6px;line-height:1.1}}
.role .d{{font-size:21px;color:var(--mut);margin-top:8px;line-height:1.35}}
.sec{{margin-top:30px;font-size:20px;color:var(--mut);display:flex;align-items:center;gap:16px}}
.sec:after{{content:'';flex:1;height:1px;background:var(--line)}}
.chips{{display:flex;flex-wrap:wrap;gap:10px;margin-top:14px}}
.chip{{border:1px solid var(--line);background:color-mix(in srgb,var(--card) 90%,transparent);border-radius:12px;padding:9px 16px;font-size:21px;font-weight:800}}
.chip span{{color:var(--g)}}
.foot{{margin-top:auto;padding-top:26px;border-top:1px solid var(--line);display:flex;justify-content:space-between;align-items:center}}
.spacer{{height:40px}}.short .roles{{margin-top:auto}}.short .photo{{top:150px;{"left" if photo_side=="left" else "right"}:-140px}}.short h1{{margin-top:24px}}.short .foot{{margin-top:0}}.short .spacer{{height:56px}}
.foot .q{{font-size:27px;font-weight:800}}.foot .q b{{color:var(--g)}}
.foot .mono{{font-size:21px;color:var(--mut);direction:ltr}}
.cur{{display:inline-block;width:14px;height:30px;background:var(--g);vertical-align:-4px;margin-inline-start:8px}}
.grain{{position:absolute;inset:0;z-index:5;pointer-events:none;opacity:.10;mix-blend-mode:overlay;background-image:url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='220' height='220'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='.9' numOctaves='2' stitchTiles='stitch'/></filter><rect width='100%' height='100%' filter='url(%23n)'/></svg>")}}
"""

def page(cfg, version):
    t = {**DEFAULT_THEME, **cfg.get("theme", {})}
    if version == "full":
        lang, dirn = cfg.get("lang", "he"), cfg.get("dir", "rtl")
        name, title = cfg["name"], cfg["title"]
        roles, tagline = cfg["roles"], cfg.get("tagline", "")
    else:
        lang, dirn = cfg.get("short_lang", "en"), cfg.get("short_dir", "ltr")
        name, title = cfg.get("name_short", cfg["name"]), cfg.get("title_short", cfg["title"])
        roles, tagline = cfg.get("roles_short", cfg["roles"]), cfg.get("tagline_short", cfg.get("tagline", ""))
    photo_side = "left" if dirn == "rtl" else "right"
    words = name.split()
    name_html = "<br>".join(esc(w) for w in words) + '<span class="dot">.</span>' if dirn == "ltr" else "<br>".join(esc(w) for w in words)
    longest = max(len(w) for w in words)
    nsize = min(118, int(620 / max(longest * 0.58, 1)))  # keep the name clear of the photo
    bar = ""
    if t.get("terminal_bar", True):
        logo = cfg.get("brand", "")
        if logo and cfg.get("brand_split"):
            a, b = logo[:cfg["brand_split"]], logo[cfg["brand_split"]:]
            logo = f"{esc(a)}<b>{esc(b)}</b>"
        else:
            logo = esc(logo)
        dots = '<span class=dots><i></i><i></i><i></i></span>'
        path = f'<span class=mono style="direction:ltr">~/{esc(cfg.get("bar_path","founder"))} $ whoami</span>'
        lg = f'<span class=logo>{logo}</span>'
        # visual order is always: dots (left) - path - logo (right); flex reverses in RTL
        bar = f'<div class="z bar">{lg}{path}{dots}</div>' if dirn == "rtl" else f'<div class="z bar">{dots}{path}{lg}</div>'
    tools = "".join(f"<span>{esc(x)}</span>" for x in cfg.get("tools", []))
    roles_html = "".join(
        f'<div class=role><div class=k>{ltr(r["kicker"])}</div><div class=n>{ltr(r["name"])}</div><div class=d>{esc(r.get("desc",""))}</div></div>'
        for r in roles)
    secs = ""
    if version == "full":
        for s in cfg.get("sections", []):
            chips = "".join(f'<div class=chip><span>›</span> {ltr(i)}</div>' for i in s["items"])
            secs += f'<div class="z sec">{esc(s["title"])}</div><div class="z chips">{chips}</div>'
    link = cfg.get("link")
    foot_right = f'<div class=mono>{esc(link)}</div>' if link else ""
    hi = cfg.get("tagline_highlight" if version == "full" else "tagline_short_highlight", "")
    tag = esc(tagline)
    if hi and hi in tagline:
        tag = tag.replace(esc(hi), f"<b>{esc(hi)}</b>", 1)
    psize = cfg.get("photo_size_short" if version == "short" else "photo_size", 900 if version == "short" else 640)
    return f"""<!doctype html><html lang="{lang}" dir="{dirn}"><head><meta charset="utf-8"><title>{esc(name)}</title>
{font_links(t)}
<style>{css(t, dirn, photo_side)}</style></head>
<body class="{version}" style="--nsize:{nsize}px;--psize:{psize}px">
<div class=backlight></div>
<img class=photo src="{esc(cfg.get('photo_cut','cut.png'))}" alt="">
{bar}
<div class="z hero">
 <div class="prompt mono">&gt; {esc(cfg.get('prompt','hello, world'))}</div>
 <h1>{name_html}</h1>
 <div class=title><span class=mono style="direction:ltr">&lt;/&gt;</span> {ltr(title)}</div>
 {f'<div class=tools>{tools}</div>' if tools else ''}
</div>
<div class="z roles">{roles_html}</div>
{secs}
<div class=spacer></div>
<div class="z foot"><div class=q>{tag}<span class=cur></span></div>{foot_right}</div>
<div class=grain></div>
<script>
// shrink the name until it clears the face (middle 40% of the photo box)
document.fonts.ready.then(function(){{const h=document.querySelector('h1'),p=document.querySelector('.photo').getBoundingClientRect();
const rtl=document.documentElement.dir==='rtl';const faceL=p.left+p.width*.3,faceR=p.left+p.width*.7;
let fs=parseFloat(getComputedStyle(h).fontSize);const r=document.createRange();
for(let i=0;i<60;i++){{r.selectNodeContents(h);const b=r.getBoundingClientRect();
 if(rtl?b.left>faceR+8:b.right<faceL-8)break;fs-=2;h.style.fontSize=fs+'px';}}
document.body.dataset.fit='1';}});
</script>
</body></html>"""


def main():
    cfg_path, out = sys.argv[1], sys.argv[2]
    cfg = json.load(open(cfg_path, encoding="utf-8"))
    os.makedirs(out, exist_ok=True)
    for v in ("full", "short"):
        with open(os.path.join(out, f"{v}.html"), "w", encoding="utf-8") as fh:
            fh.write(page(cfg, v))
        print("wrote", os.path.join(out, f"{v}.html"))


if __name__ == "__main__":
    main()
