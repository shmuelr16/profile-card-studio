---
name: profile-card-studio
description: Build a designer-grade personal profile page rendered as an image (founder card / LinkedIn visual) with the person's photo cut out and blended into the background, their title, roles and everything they built, in two versions (full native-language page + short English 4:5 card).
---

# Profile Card Studio

Turn one portrait photo + what someone built into two polished profile images:

- **full**: native language (Hebrew/RTL by default), name, title, tools, role cards and every project grouped into sections. Tall page, height grows with content.
- **short**: second language (English by default), 4:5 (1080x1350): name, title, tools, role cards. Made for LinkedIn / WhatsApp posts.

The photo is **cut out and blended into the page in natural colours**, never placed in a circle and never recoloured (no duotone/green skin) unless the user explicitly asks.

Work like a senior designer with 18 years of experience: one strong accent, strict alignment, generous spacing, real hierarchy, nothing that looks templated. The result should look as if an expensive image model produced it, but the person's face must stay 100% real (we only cut, clean and grade; we never redraw the face).

## Scripts

Clone once: `git clone https://github.com/shmuelr16/profile-card-studio` (or use the copy next to this file).

| Script | What it does |
|---|---|
| `scripts/cutout.py PHOTO out/cut.png --bg HEX --accent HEX` | Segments the person (rembg `isnet-general-use` + alpha matting), removes leftover backdrop between hairs, recovers true hair colour on beard/hair edges (pymatting), natural grade, subtle accent rim light, soft bottom/side fade. |
| `scripts/build.py config.json out/` | Writes `out/full.html` and `out/short.html` from the config (see `examples/config.example.json`). Name auto-shrinks so it never covers the face. |
| `scripts/render.py out/` | Installs fonts via npm (@fontsource), renders both pages at 2x, runs layout checks, writes `full.png`, `short.png`, review crops (`*-check-photo/hair/chin.png`) and `report.json`. Exit 1 if a check fails. |

Setup: `pip install --break-system-packages rembg pymatting opencv-python-headless pillow playwright` (Chromium is usually preinstalled). Do not use BiRefNet: it needs more than 8 GB RAM and gets killed.

## Workflow

1. **Collect what they built.** First look in memory (memory files, past conversations, their GitHub/Vercel connectors if connected) for projects, products, roles and links. If you can't find enough, send a short questionnaire with AskUserQuestion (and/or ask for a free-text list):
   - Full name in both languages, and the title for the badge (use their exact wording).
   - Roles (company/brand + role, e.g. "Founder & CEO") and a one-line description each.
   - What they built, grouped (products, sites/guides, apps, games, tools...). Ask which personal/private items to leave out.
   - Tools/stack chips (max ~5).
   - Design: colours, fonts, brand name for the top bar. If they name a brand/design system, use its tokens; otherwise default dark + one neon accent.
2. **Ask about the link**: whether to show their website in the footer, and which URL.
3. **Get the photo**: a clear front portrait with a plain background works best. Run `cutout.py` with the theme's `bg` and `accent`.
4. **Write config.json** (copy the example). Rules:
   - Wrap nothing yourself: `build.py` isolates Latin text inside RTL automatically (fixes "Chat E.D.I." punctuation jumping).
   - Do not print trademarked third-party names as their product names (write "city simulator", not "GTA").
   - Don't list items the user marked private.
5. **Build + render**: `build.py` then `render.py`. All checks must say OK.
6. **Look at the output yourself** before sending: open `full.png`, `short.png` and every `*-check-*.png` crop. Check: no grey/white fringe around hair, beard, ears or glasses; no backdrop left between hairs; name clear of the face; nothing cut at the edges; text readable. Fix and re-run until clean (edge problems → re-run `cutout.py`; layout → adjust config `photo_size`, `photo_size_short`).
7. **Send both PNGs**, say in one line what each is, offer one concrete next tweak.

## Feedback we already learned from (don't repeat)
- A profile circle around the photo was rejected: the photo must be part of the background.
- Duotone/green-tinted skin was rejected: keep natural colours, only light grading.
- Grey/white halos behind the beard and next to the glasses were the #1 complaint: always inspect the chin and hair crops.
- Outlined giant background words and strong outer glows look cheap: keep the backlight subtle.
- The 4:5 card must not have a big empty gap: the photo scales up to fill it.
