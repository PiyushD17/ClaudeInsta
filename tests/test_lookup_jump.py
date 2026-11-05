"""Regression test: in the lookup scene's jump mode no row is highlighted before jump_at, then only the target row is highlighted, and the page/arrow come after.
Run: python3 tests/test_lookup_jump.py"""
import os, sys
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, root)
import reel
reel.load_spec(os.path.join(root, "specs", "day10_rag.py"))
idx = [i for i, sc in enumerate(reel.SPEC["scenes"]) if sc["type"] == "lookup"][0]
sc = reel.SPEC["scenes"][idx]; ja = sc["jump_at"]; tg = sc["target"]
s0 = reel.scene_bounds()[idx][0]
def amber_rows(u):
    img = reel.frame(s0 + u).convert("RGB")
    rows = []
    for i in range(len(sc["items"])):
        y = 600 + i * 100
        r, g, b = img.getpixel((115, y))          # left edge of the highlight outline area (x=110-114 outline)
        hot = any(img.getpixel((x, y))[0] > 200 and img.getpixel((x, y))[2] < 120 for x in range(108, 118))
        rows.append(hot)
    return rows
def page_visible(u):
    img = reel.frame(s0 + u).convert("RGB")
    return any(img.getpixel((x, 800))[1] > 180 and img.getpixel((x, 800))[0] < 150 for x in range(685, 695))   # mint page outline at x=690
assert not any(amber_rows(ja - 1.0)), amber_rows(ja - 1.0)                       # no stepping highlight before the jump
assert not any(amber_rows(ja - 0.1)), amber_rows(ja - 0.1)
rows = amber_rows(ja + 0.5)
assert rows[tg] and sum(rows) == 1, rows                                           # only the target row, and not other rows on the way
assert not page_visible(ja + 0.1) and page_visible(ja + 1.2)                       # the page appears after the highlight
print("OK: lookup jump mode highlights only the target row at jump_at; page follows.")
