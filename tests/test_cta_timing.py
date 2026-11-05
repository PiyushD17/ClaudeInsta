"""Regression test: the closing "Follow" call to action must not appear before its spoken moment (follow_at) and must be visible after it.
Run: python3 tests/test_cta_timing.py"""
import os, sys
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, root)
import reel
reel.load_spec(os.path.join(root, "specs", "day10_rag.py"))
s0 = reel.scene_bounds()[-1][0]
def amber_pixels(u):
    img = reel.frame(s0 + 0.3 + u).convert("RGB")
    n = 0
    for x in range(380, 700, 4):
        for y in range(900, 960, 3):          # the "Follow" word sits around y=930
            r, g, b = img.getpixel((x, y))
            if r > 200 and 150 < g < 215 and b < 110: n += 1
    return n
assert amber_pixels(2.0) == 0, amber_pixels(2.0)       # voice is still on the previous sentence
assert amber_pixels(4.5) == 0, amber_pixels(4.5)       # not yet
assert amber_pixels(6.0) > 20, amber_pixels(6.0)       # "Follow" is shown once the voice says it
def sub_pixels(u):                      # the grey sub line sits around y=770 (two-line big text)
    img = reel.frame(s0 + 0.3 + u).convert("RGB")
    return sum(1 for x in range(200, 880, 4) for y in range(750, 790, 3) if sum(img.getpixel((x, y))) > 330)
assert sub_pixels(0.8) == 0 and sub_pixels(3.0) > 20      # sub_at 1.8: second line appears later so the scene keeps changing
print("OK: Follow call to action appears at its spoken moment, not before.")
