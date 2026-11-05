"""Regression tests for the stage engine v2 (persistent, nested, object-based diagrams).
Run: python3 tests/test_stage.py

Checks: word anchors; objects appear at their anchor and not before; tweened grid count equals lit cells; persistence across scenes and clear;
unknown clear ids and unknown parents fail loudly; text is WRAPPED inside its box (a long panel label never leaves the panel); the layout check
reports TEXT_OVERFLOW, OVERLAP, OUTSIDE_PARENT and EMPTY_BOX; a clean nested layout passes; terminal lines wait for their word ("at")."""
import os, sys
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, root)
import reel, stage

def make(scenes, lines=None, pace=4.0):
    lines = lines or ["one two three four five six seven eight"] * len(scenes)
    starts, t = [], 0.2
    for l in lines: starts.append(t); t += len(l.split()) / pace + 0.4
    spec = {"tag": "@TECHINABITE", "pace_wps": pace, "captions": False, "dur": round(t + 0.6, 1),
            "lines": [(l, starts[i], starts[i] + 2.0) for i, l in enumerate(lines)], "scenes": scenes}
    return spec, starts

def codes(spec, starts):
    reel.SPEC = spec; reel.DUR = spec["dur"]; stage._CACHE.clear()
    return [c for _, c, _ in stage.layout_check(spec, starts, spec["dur"], None, step=0.5, draw_cls=reel.SoftDraw)]

# 1. anchors, appearance, tween == drawn
spec, ls = make([
    {"type": "stage", "objects": [
        {"kind": "panel", "id": "p", "x": 60, "y": 600, "w": 960, "h": 300, "label": "Rate limiter"},
        {"kind": "grid", "id": "g", "in": "p", "x": 100, "y": 700, "w": 800, "h": 100, "cols": 10, "rows": 2, "n": 0, "color": "amber"},
        {"kind": "pill", "id": "c", "x": 540, "y": 1000, "text": "Chip", "t": "w5"}],
     "events": [{"id": "g", "t": 1.0, "dur": 2.0, "set": {"n": 20}}]},
    {"type": "stage", "objects": [{"kind": "pill", "id": "d", "x": 540, "y": 1100, "text": "Second", "t": -0.2}], "clear": ["c"]},
    {"type": "stage", "objects": [], "clear": True}])
reel.SPEC = spec; reel.DUR = spec["dur"]; stage._CACHE.clear()
assert abs(stage.resolve_t(spec, 0, "w5") - 1.0) < 1e-9
objs = {o.id: o for o in stage.build(spec, ls)}
assert objs["c"].alpha(ls[0] + 0.9) == 0 and objs["c"].alpha(ls[0] + 1.5) > 0.9
def lit_cells(t):
    img = reel.frame(t).convert("RGB"); n = 0
    for i in range(20):
        cx = 100 + (i % 10) * 80 + 40; cy = 700 + (i // 10) * 50 + 25
        r, g, b = img.getpixel((cx, cy)); n += (r > 200 and b < 120)
    return n
for dt in (0.5, 1.6, 2.2, 3.5):
    t = ls[0] + dt
    assert lit_cells(t) == round(objs["g"].props(t)["n"]), (dt, lit_cells(t), objs["g"].props(t)["n"])
t2 = ls[1] + 1.0
assert lit_cells(t2) == 20 and objs["c"].alpha(t2) == 0 and objs["d"].alpha(t2) > 0.9      # persistence + clear by id
assert objs["g"].alpha(ls[2] + 0.5) == 0 and objs["d"].alpha(ls[2] + 0.5) == 0              # clear=True (children fade with the parent)

# 2. loud failures for typos
for bad in ([{"type": "stage", "objects": []}, {"type": "stage", "objects": [], "clear": ["nope"]}],
            [{"type": "stage", "objects": [{"kind": "pill", "id": "x", "in": "missing", "x": 1, "y": 1, "text": "a"}]}]):
    sp, l2 = make(bad); stage._CACHE.clear()
    try:
        stage.build(sp, l2); raise SystemExit("a typo was accepted")
    except KeyError:
        pass

# 3. text wraps inside its box instead of leaving it
sp, l2 = make([{"type": "stage", "objects": [
    {"kind": "panel", "id": "p", "x": 300, "y": 600, "w": 300, "h": 300, "label": "Rate limiter for API requests", "body": "gear"}]}])
reel.SPEC = sp; reel.DUR = sp["dur"]; stage._CACHE.clear()
img = reel.frame(2.0).convert("RGB")
right_of_box = [img.getpixel((x, y)) for x in range(606, 680) for y in range(605, 700, 3)]
assert not any(px[0] > 200 and px[1] > 200 and px[2] > 200 for px in right_of_box), "panel label leaked out of the panel"
inside = [img.getpixel((x, y)) for x in range(330, 590) for y in range(610, 700, 2)]
assert sum(px[0] > 200 and px[1] > 200 and px[2] > 200 for px in inside) > 200, "panel label not drawn inside the panel"
assert "TEXT_OVERFLOW" not in codes(sp, l2)

# 4. the layout check catches overflow, overlap, outside-parent and empty boxes
sp, l2 = make([{"type": "stage", "objects": [
    {"kind": "panel", "id": "tiny", "x": 60, "y": 600, "w": 200, "h": 90, "label": "Concurrent requests limiter for every API", "compact": True},
    {"kind": "panel", "id": "empty", "x": 60, "y": 760, "w": 400, "h": 300, "label": "Store"},
    {"kind": "pill", "id": "a", "x": 700, "y": 800, "text": "requests"},
    {"kind": "pill", "id": "b", "x": 720, "y": 805, "text": "limit"},
    {"kind": "panel", "id": "box", "x": 560, "y": 900, "w": 300, "h": 200, "label": "Redis"},
    {"kind": "pill", "id": "kid", "in": "box", "x": 880, "y": 1000, "text": "outside"}]}])
cs = codes(sp, l2)
for code in ("TEXT_OVERFLOW", "EMPTY_BOX", "OVERLAP", "OUTSIDE_PARENT"):
    assert code in cs, (code, cs)

# 5. a clean nested layout passes
sp, l2 = make([{"type": "stage", "objects": [
    {"kind": "panel", "id": "lim", "x": 60, "y": 560, "w": 960, "h": 380, "label": "Rate limiter", "value": "3/10"},
    {"kind": "store", "id": "st", "in": "lim", "x": 90, "y": 660, "w": 600, "h": 250, "label": "Redis", "rows": [["ratelimit:user123:7", "3"]]},
    {"kind": "terminal", "id": "tm", "x": 60, "y": 980, "w": 960, "h": 260, "title": "redis-cli",
     "lines": [{"text": "> INCR ratelimit:user123:7", "type": True, "at": "w3"}, {"text": "(integer) 4", "color": "mint", "at": "w6"}]}]}])
assert [c for c in codes(sp, l2) if c != "STATIC"] == [], codes(sp, l2)

# 6. a terminal line waits for its word
reel.SPEC = sp; reel.DUR = sp["dur"]; stage._CACHE.clear()
def mint_pixels(t):
    img = reel.frame(t).convert("RGB")
    return sum(1 for x in range(80, 400) for y in range(1080, 1110, 2) if img.getpixel((x, y))[1] > 180 and img.getpixel((x, y))[0] < 150)
assert mint_pixels(l2[0] + 1.1) == 0 and mint_pixels(l2[0] + 1.9) > 20     # "(integer) 4" appears at word 6 (1.25 s), not before
# 7. a terminal that does not change is not "motion": STATIC is reported
sp7, l7 = make([{"type": "stage", "objects": [
    {"kind": "terminal", "id": "tm", "x": 60, "y": 600, "w": 960, "h": 260, "title": "redis-cli", "lines": [{"text": "> PING", "color": "white"}]}]}],
    lines=["one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen twenty twentyone twentytwo"])
assert "STATIC" in codes(sp7, l7), codes(sp7, l7)
print("OK: stage engine v2 - anchors, tweens, persistence, clear, wrapping, layout check, line anchors.")
