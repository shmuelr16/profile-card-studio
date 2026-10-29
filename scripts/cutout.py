#!/usr/bin/env python3
"""Cut a person out of a portrait and blend them into a dark page, in natural colours.

Usage:
  python3 cutout.py PHOTO OUT.png [--bg "#060B09"] [--accent "#3EFFA3"] [--rim 0.25]

Pipeline (each step fixes a problem we hit in practice):
  1. Segmentation with rembg `isnet-general-use` + alpha matting (fine hair/beard edges).
     BiRefNet is sharper but needs >8 GB RAM and gets OOM-killed in small sandboxes.
  2. Remove semi-transparent pixels whose colour matches the ORIGINAL local background
     (grey studio backdrop showing between hairs).
  3. pymatting `estimate_foreground_ml` to recover true hair colour at the edges
     (otherwise a light halo of the old background stays on beard/hair).
  4. Darken any leftover grey fringe in a thin band along the silhouette.
  5. Natural colour grade only: clarity, mild contrast, shadows pulled toward the page bg.
     Never recolour the person (no duotone) unless the user explicitly asks.
  6. Subtle accent rim light from above, soft fade at the bottom and sides.
"""
import argparse, sys
import numpy as np
import cv2


def hex_bgr(h):
    h = h.lstrip('#')
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return np.array([b, g, r], np.float32) / 255


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('photo'); ap.add_argument('out')
    ap.add_argument('--bg', default='#060B09')
    ap.add_argument('--accent', default='#3EFFA3')
    ap.add_argument('--rim', type=float, default=0.25)
    ap.add_argument('--fade-start', type=float, default=0.6, help='fraction of height where bottom fade starts')
    ap.add_argument('--model', default='isnet-general-use')
    a_ = ap.parse_args()
    import os; os.makedirs(os.path.dirname(os.path.abspath(a_.out)), exist_ok=True)

    from rembg import remove, new_session
    from PIL import Image
    from pymatting import estimate_foreground_ml

    pil = Image.open(a_.photo).convert('RGB')
    m = remove(pil, session=new_session(a_.model), alpha_matting=True,
               alpha_matting_foreground_threshold=240,
               alpha_matting_background_threshold=15,
               alpha_matting_erode_size=8)
    alpha = np.asarray(m)[..., 3].astype(np.float64) / 255
    rgb = np.asarray(pil).astype(np.float64) / 255
    o8 = rgb[..., ::-1].astype(np.float32) * 255  # BGR 0..255
    h, w = alpha.shape

    # 2. local background estimate from fully transparent area
    bgm = (alpha < 0.05).astype(np.float32)
    num = cv2.GaussianBlur(o8 * bgm[..., None], (0, 0), 40)
    den = cv2.GaussianBlur(bgm, (0, 0), 40)[..., None]
    est = num / np.maximum(den, 1e-4)
    d = np.abs(o8 - est).max(2)
    sat = o8.max(2) - o8.min(2)
    core = cv2.erode((alpha > 0.97).astype(np.uint8), np.ones((9, 9), np.uint8))
    bgish = np.clip(1 - (d - 10) / 30, 0, 1) * (sat < 26) * (core == 0)
    alpha = alpha * (1 - 0.9 * bgish)
    alpha = np.where(alpha < 0.08, 0, alpha)

    # 3. true foreground colour at the edges
    F = estimate_foreground_ml(rgb, alpha)
    f = F[..., ::-1].astype(np.float32)
    fr = ((alpha > 0) & (alpha < 0.9)).astype(np.float32)
    fr = cv2.GaussianBlur(fr, (0, 0), 1.5)[..., None]
    f = f * (1 - 0.35 * fr)

    # 4. leftover grey fringe along the silhouette (beard, sideburns, hair)
    af = alpha.astype(np.float32)
    hard = (af > 0.08).astype(np.uint8)
    dist = cv2.distanceTransform(hard, cv2.DIST_L2, 5)
    band = (dist > 0) & (dist < 34)
    lum = o8.mean(2)
    grey = band & (sat < 30) & (lum > 75) & (lum < 205) & (np.abs(o8 - est).max(2) < 40)
    g = cv2.GaussianBlur(grey.astype(np.float32), (0, 0), 1.5)
    hair = np.median(f[(dist > 6) & (dist < 20) & (lum < 70)], axis=0) if np.any((dist > 6) & (dist < 20) & (lum < 70)) else np.array([0.09, 0.1, 0.12], np.float32)
    f = f * (1 - 0.8 * g[..., None]) + hair * 0.8 * g[..., None]
    af = af * (1 - 0.75 * g)

    # 5. natural grade
    blur = cv2.GaussianBlur(f, (0, 0), 14)
    f = np.clip(f + 0.25 * (f - blur), 0, 1)
    f = np.clip((f - 0.5) * 1.07 + 0.5, 0, 1)
    l = cv2.cvtColor((f * 255).astype(np.uint8), cv2.COLOR_BGR2GRAY).astype(np.float32) / 255
    sh = ((1 - l) ** 2)[..., None]
    bgc = hex_bgr(a_.bg)
    f = f * (1 - 0.2 * sh) + bgc * 0.2 * sh * 4

    # 6. rim light + fades
    edge = np.clip(af - cv2.erode(af, np.ones((11, 11), np.uint8)), 0, 1)
    edge = cv2.GaussianBlur(edge, (0, 0), 3)
    ys = np.linspace(1, 0, h)[:, None] ** 1.5
    f = np.clip(f + (edge * ys)[..., None] * hex_bgr(a_.accent) * a_.rim, 0, 1)
    fy = np.ones((h, 1), np.float32)
    s = int(h * a_.fade_start)
    fy[s:, 0] = np.linspace(1, 0, h - s) ** 1.6
    xs = np.linspace(0, 1, w)
    fx = np.clip(np.minimum(xs, 1 - xs) / 0.12, 0, 1)[None, :] ** 1.3
    out = np.dstack([(f * 255).astype(np.uint8), (np.clip(af * fy * fx, 0, 1) * 255).astype(np.uint8)])
    cv2.imwrite(a_.out, out)
    print('cutout ->', a_.out)


if __name__ == '__main__':
    sys.exit(main())
