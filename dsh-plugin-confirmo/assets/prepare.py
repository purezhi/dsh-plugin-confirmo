#!/usr/bin/env python3
"""
Prepare a Confirmo sprite sheet: normalize any AI-generated 8x7 sheet into a
clean, runtime-ready 2048x1792 RGBA sheet (8x7 @ 256x256 frames).

Input : <dir>/source.png|jpeg|jpg  — raw sheet, ANY size, 8x7 grid,
                                     magenta-keyed OR transparent background
Output: <dir>/sheet.png            — 2048x1792 RGBA, magenta keyed to
                                     transparent, every frame horizontally
                                     centered and feet aligned to a baseline
        <dir>/thumb.png            — small menu thumbnail (first frame)

Why: raw sheets have uneven row pitch and column drift (AI generators rarely
produce a mathematically perfect grid). Naively slicing at W/8 x H/7 crops
the previous row's feet into the next row / neighbouring frames. This script
locates the REAL content boundaries (row blank bands, then per-frame content
runs), crops each character by its own bounding box, and re-composes them
centered on a clean 2048x1792 canvas, feet aligned to a common baseline.

Usage:
  /tmp/pyimg/bin/python assets/prepare.py [dir]
  # default dir: assets/mj2 ; pass another sprite dir to reuse it, e.g.
  #   /tmp/pyimg/bin/python assets/prepare.py assets/mj3
"""
import sys
from pathlib import Path

from PIL import Image

COLS, ROWS = 8, 7
CELL = 256            # output frame size
OUT_W, OUT_H = COLS * CELL, ROWS * CELL

MIN_COL = 3           # columns with fewer content pixels than this are noise
RUN_GAP = 16          # columns gap wider than this splits runs
MIN_ROW_GAP = 6       # blank rows shorter than this are noise, not a row split
ROW_BAND = 160        # row-boundary minimum: density below this (sampled every
                      # 3px) marks a valley between rows; typical row content is
                      # ~200+ so 160 cleanly separates them
TARGET_H = int(CELL * 0.80)   # 204px on a 256px cell
BASELINE = CELL - 14          # 242px from the top: feet rest here


def is_transparent(r, g, b, a):
    """Background = fully transparent OR pure/near magenta."""
    if a < 128:
        return True
    return r > 200 and g < 80 and b > 200


def find_source(d):
    for name in ("source.png", "source.jpeg", "source.jpg", "source.webp"):
        p = d / name
        if p.exists():
            return p
    raise FileNotFoundError(f"no source.png/jpeg/jpg/webp in {d}")


def detect_row_bounds(px, W, H):
    """Find the real top/bottom of each of the 7 rows.

    Rather than requiring a fully blank band (AI rows often touch), split at
    the local MINIMA of the per-row content density: each minimum between two
    content-heavy areas is a row boundary candidate, and we keep the 6 deepest
    valleys (7 rows).
    """
    density = []
    for y in range(H):
        cnt = 0
        for x in range(0, W, 3):
            if px[x, y][3] > 0:
                cnt += 1
        density.append(cnt)

    # smooth lightly
    sm = []
    for y in range(H):
        lo = max(0, y - 2)
        hi = min(H, y + 3)
        sm.append(sum(density[lo:hi]) / (hi - lo))

    # candidates: local minima that are clearly below the neighbouring peaks,
    # excluding the extreme top/bottom edges (they are always "blank")
    margin = max(2, H // 30)
    candidates = []
    for y in range(margin, H - margin):
        if sm[y] <= sm[y - 1] and sm[y] <= sm[y + 1] and sm[y] < ROW_BAND:
            if not candidates or y - candidates[-1] > MIN_ROW_GAP * 2:
                candidates.append(y)
    # keep the 6 deepest minima = boundaries between the 7 rows
    candidates.sort(key=lambda y: sm[y])
    cuts = sorted(candidates[:ROWS - 1])
    print("row boundary cuts (y):", cuts)

    bounds = []
    top = 0
    for cut in cuts:
        bounds.append((top, cut))
        top = cut + 1
    bounds.append((top, H - 1))
    return bounds


def main():
    arg = sys.argv[1] if len(sys.argv) > 1 else "assets/mj2"
    d = Path(arg)
    d.mkdir(parents=True, exist_ok=True)
    src_path = find_source(d)
    out_sheet = d / "sheet.png"
    out_thumb = d / "thumb.png"

    src = Image.open(src_path).convert("RGBA")
    W, H = src.size
    px = src.load()
    print(f"source: {src_path} {W}x{H}")

    # 1) key magenta -> transparent on the whole source
    for y in range(H):
        for x in range(W):
            r, g, b, a = px[x, y]
            if is_transparent(r, g, b, a):
                px[x, y] = (0, 0, 0, 0)

    # 2) real row boundaries (top..bottom of each row's content)
    row_bounds = detect_row_bounds(px, W, H)
    print("row content spans:", row_bounds)

    # ---- pass 1: measure every frame's character crop & natural size ----
    # We need the crop bbox per frame to (a) decide each row's unified scale
    # and (b) reuse for the actual paste in pass 2.
    frames = []          # per (r,c): dict or None
    for r, (y0, y1) in enumerate(row_bounds):
        for c in range(COLS):
            x0 = int(round(c * W / COLS))
            x1 = int(round((c + 1) * W / COLS))
            col_cnt = []
            for x in range(x0, x1):
                cnt = 0
                for y in range(y0, y1 + 1):
                    if px[x, y][3] > 0:
                        cnt += 1
                col_cnt.append(cnt)

            runs = []
            start = None
            prev = -1
            for i, cnt in enumerate(col_cnt):
                if cnt >= MIN_COL:
                    if start is None or i - prev > RUN_GAP:
                        if start is not None:
                            runs.append((start, prev))
                        start = i
                    prev = i
            if start is not None:
                runs.append((start, prev))
            if not runs:
                frames.append(None)
                continue

            run = max(runs, key=lambda rg: rg[1] - rg[0] + 1)
            minx, maxx = run

            miny, maxy = (y1 - y0), -1
            for y in range(y0, y1 + 1):
                for x in range(x0 + minx, x0 + maxx + 1):
                    if px[x, y][3] > 0:
                        if y - y0 < miny:
                            miny = y - y0
                        if y - y0 > maxy:
                            maxy = y - y0
                        break
            if maxy < 0:
                frames.append(None)
                continue

            frames.append({
                "r": r, "c": c,
                "x0": x0, "minx": minx, "maxx": maxx,
                "y0": y0, "miny": miny, "maxy": maxy,
                "w": maxx - minx + 1,
                "h": maxy - miny + 1,
            })

    # ---- per-row unified scale ----
    # Standing rows (tall) scale up toward TARGET_H so the pet is a decent
    # size; wide rows (lying Sleepy / spread arms) must not overflow the cell
    # width, so their scale is width-limited. All frames in a row share one
    # scale so the loop animation keeps a constant size.
    row_scales = []
    for r in range(ROWS):
        fr = [f for f in frames[r * COLS:(r + 1) * COLS] if f]
        if not fr:
            row_scales.append(1.0)
            continue
        # use the widest & tallest frame of the row as the constraint
        w = max(f["w"] for f in fr)
        h = max(f["h"] for f in fr)
        scale_h = TARGET_H / h          # fit height to ~80% of the cell
        scale_w = (CELL - 8) / w        # never overflow width
        row_scales.append(min(scale_h, scale_w))
    print("per-row scales:", [round(s, 3) for s in row_scales])

    # ---- pass 2: compose the output sheet ----
    out = Image.new("RGBA", (OUT_W, OUT_H), (0, 0, 0, 0))
    for f in frames:
        if f is None:
            continue
        r, c = f["r"], f["c"]
        pad = 3
        crop_left = max(0, f["x0"] + f["minx"] - pad)
        crop_top = max(0, f["y0"] + f["miny"] - pad)
        crop_right = min(W - 1, f["x0"] + f["maxx"] + 1 + pad)
        crop_bottom = min(H - 1, f["y0"] + f["maxy"] + 1 + pad)
        char = src.crop((crop_left, crop_top, crop_right, crop_bottom))

        scale = row_scales[r]
        nw = max(1, int(round(char.width * scale)))
        nh = max(1, int(round(char.height * scale)))
        char = char.resize((nw, nh), Image.LANCZOS)

        ox = (CELL - nw) // 2
        oy = BASELINE - nh
        oy = max(0, min(oy, CELL - nh))
        cell = out.crop((c * CELL, r * CELL, (c + 1) * CELL, (r + 1) * CELL))
        cell.paste(char, (ox, oy), char)
        out.paste(cell, (c * CELL, r * CELL))

    out.save(out_sheet, "PNG")
    print(f"sheet -> {out_sheet} ({OUT_W}x{OUT_H})")

    # thumbnail: first frame, trimmed
    thumb = out.crop((0, 0, CELL, CELL))
    bbox = thumb.getbbox()
    if bbox:
        thumb = thumb.crop(bbox)
    thumb.thumbnail((160, 160), Image.LANCZOS)
    thumb.save(out_thumb, "PNG")
    print(f"thumb -> {out_thumb} ({thumb.size[0]}x{thumb.size[1]})")


if __name__ == "__main__":
    main()
