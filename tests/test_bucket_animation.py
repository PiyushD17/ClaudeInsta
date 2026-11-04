"""Regression test: in the bucket scene, request N must consume the token it lands on (1, 2, 3 left to right).
Run: python3 tests/test_bucket_animation.py"""
import os, sys
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, root)
import reel
reel.load_spec(os.path.join(root, "specs", "day09_rate_limiting.py"))
s0 = reel.scene_bounds()[3][0]        # scene 4: 4 requests hit a bucket of 3 tokens
def tokens_present(u):
    img = reel.frame(s0 + 0.3 + u).convert("RGB")
    xs = [540 + (i - 1) * 160 for i in range(3)]
    return [img.getpixel((x + 30, 730))[1] > 180 and img.getpixel((x + 30, 730))[0] < 150 for x in xs]   # mint fill = token present
# requests land at about 1.5 s, 3.0 s and 4.5 s after the scene's first 0.3 s
assert tokens_present(0.2) == [True, True, True], tokens_present(0.2)
assert tokens_present(2.0) == [False, True, True], tokens_present(2.0)
assert tokens_present(3.5) == [False, False, True], tokens_present(3.5)
assert tokens_present(5.3) == [False, False, False], tokens_present(5.3)
print("OK: requests 1, 2, 3 consume tokens 1, 2, 3 in order.")
