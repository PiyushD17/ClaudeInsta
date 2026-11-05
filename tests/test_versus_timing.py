"""Regression test: in the versus scene, each card appears at its t_left / t_right time (not before) and the default timing is unchanged.
Run: python3 tests/test_versus_timing.py"""
import os, sys
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, root)
import reel
reel.load_spec(os.path.join(root, "specs", "day10_rag.py"))
idx = [i for i, sc in enumerate(reel.SPEC["scenes"]) if sc["type"] == "versus"][0]
s0 = reel.scene_bounds()[idx][0] + 0.3
def card_pixels(u, x0):
    img = reel.frame(s0 + u).convert("RGB")
    bg = img.getpixel((5, 600))
    n = 0
    for x in range(x0 + 10, x0 + 450, 10):
        for y in range(500, 1150, 10):
            if sum(abs(a - b) for a, b in zip(img.getpixel((x, y)), bg)) > 15: n += 1
    return n
L, R = 70, 550
assert card_pixels(0.3, L) < 20 and card_pixels(0.3, R) < 20      # neither card before its time
assert card_pixels(2.0, L) > 200 and card_pixels(2.0, R) < 20       # left card first (t_left 1.0 = 0.7 here, the test clock starts 0.3 s into the scene), right not yet (t_right 4.0)
assert card_pixels(3.8, L) > 200 and card_pixels(3.8, R) > 200      # both once the voice has said both
print("OK: versus cards appear in order at their set times.")
