#!/usr/bin/env python3
"""Animation filmstrips for the reviewer: one PNG per scene with frames at fixed time steps, each labelled with its time.

Usage: python3 animsheet.py specs/dayNN_slug.py out/dayNN_anim [--step 0.8]
Writes out/dayNN_anim_s01.png ... one per scene (frames in a 4-column grid, safe zone y 230-1440 only), and prints their paths.
A static single frame per scene (the contact sheet) cannot show a bug like "the wrong token disappears": the filmstrip can.
"""
import argparse, os, sys
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import reel

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("spec"); ap.add_argument("prefix")
    ap.add_argument("--step", type=float, default=0.8, help="seconds between frames")
    ap.add_argument("--cols", type=int, default=4)
    a = ap.parse_args()
    reel.load_spec(a.spec)
    font = ImageFont.truetype(os.path.join(HERE, "fonts", "Inter-Medium.otf"), 18)
    fw = 300; fh = int((1440 - 230) * fw / 1080)
    paths = []
    for i, (s0, s1) in enumerate(reel.scene_bounds()):
        s1 = min(s1, reel.DUR)
        times = []
        t = s0 + 0.35
        while t < s1 - 0.1:
            times.append(t); t += a.step
        if not times: times = [s0 + 0.35]
        rows = (len(times) + a.cols - 1) // a.cols
        sheet = Image.new("RGB", (a.cols * (fw + 6), rows * (fh + 30)), (30, 30, 40))
        d = ImageDraw.Draw(sheet)
        for k, tt in enumerate(times):
            fr = reel.frame(tt).crop((0, 230, 1080, 1440)).resize((fw, fh))
            x, y = (k % a.cols) * (fw + 6), (k // a.cols) * (fh + 30)
            sheet.paste(fr, (x, y + 24))
            d.text((x + 4, y + 2), f"scene {i + 1}  t={tt:.1f}s", font=font, fill=(255, 190, 60))
        p = f"{a.prefix}_s{i + 1:02d}.png"
        sheet.save(p); paths.append(p)
    print("\n".join(paths))

if __name__ == "__main__":
    main()
