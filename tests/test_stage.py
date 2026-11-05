"""Regression test for the stage engine (persistent animated-diagram scenes).
Checks, on a synthetic spec: objects appear at their anchor time and not before; a meter's tweened value equals the drawn segments at every in-between
time; typed terminal text grows monotonically; a grid's n equals the lit cells; objects persist across stage scenes until cleared; a cleared object is gone
before the next scene's first objects appear; word anchors 'wN' equal (N-1)/pace.  Run: python3 tests/test_stage.py"""
import os, sys
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, root)
import reel, stage

SPEC = {"tag": "@TECHINABITE", "pace_wps": 4.0, "captions": False, "dur": 14.0,
        "lines": ["one two three four five six seven eight", "alpha beta gamma delta epsilon zeta eta theta", "last scene words here now"],
        "scenes": [
            {"type": "stage", "objects": [
                {"kind": "meter", "id": "m", "x": 100, "y": 600, "w": 800, "h": 40, "value": 0.0, "segs": 20, "color": "mint", "t": 0.0},
                {"kind": "grid", "id": "g", "x": 100, "y": 800, "w": 800, "h": 100, "cols": 10, "rows": 2, "n": 0, "color": "amber", "t": 0.0},
                {"kind": "chip", "id": "c", "x": 540, "y": 1000, "text": "Chip", "color": "cyan", "t": "w5"}],
             "events": [{"id": "m", "t": 1.0, "dur": 2.0, "set": {"value": 1.0}}, {"id": "g", "t": 1.0, "dur": 2.0, "set": {"n": 20}}]},
            {"type": "stage", "objects": [{"kind": "chip", "id": "d", "x": 540, "y": 1100, "text": "Second", "color": "pink", "t": -0.2}], "clear": ["c"]},
            {"type": "stage", "objects": [], "clear": True},
        ]}
reel.SPEC = SPEC; reel.DUR = SPEC["dur"]
starts = [0.2, 0.2 + 8 / 4.0 + 0.4, 0.2 + 2 * (8 / 4.0 + 0.4)]
SPEC["lines"] = [(l, starts[i], starts[i] + 2.0) for i, l in enumerate(SPEC["lines"])]
ls = [l[1] for l in SPEC["lines"]]

# word anchors
assert abs(stage.resolve_t(SPEC, 0, "w5") - 1.0) < 1e-9, stage.resolve_t(SPEC, 0, "w5")

objs = {o.id: o for o in stage.build(SPEC, ls)}
# chip c appears at its word anchor, not before
assert objs["c"].alpha(ls[0] + 0.9) == 0 and objs["c"].alpha(ls[0] + 1.5) > 0.9

# meter: tweened value matches lit segments at in-between times
def lit_segments(t):
    img = reel.frame(t).convert("RGB"); n = 0
    for i in range(20):
        x = int(100 + (i + 0.5) * 40); r, g, b = img.getpixel((x, 600 + 8 + 20))
        n += (g > 180 and r < 140)
    return n
for dt in (0.5, 1.5, 2.0, 2.5, 3.5):
    t = ls[0] + dt
    v = objs["m"].props(t)["value"]
    want = sum((i + 0.5) / 20 <= v for i in range(20))
    got = lit_segments(t)
    assert got == want, (dt, v, got, want)
# grid: n equals lit cells
def lit_cells(t):
    img = reel.frame(t).convert("RGB"); n = 0
    for i in range(20):
        cx = 100 + (i % 10) * 80 + 40; cy = 800 + (i // 10) * 50 + 25
        r, g, b = img.getpixel((cx, cy)); n += (r > 200 and b < 120)
    return n
for dt in (0.5, 2.0, 3.5):
    t = ls[0] + dt
    assert lit_cells(t) == round(objs["g"].props(t)["n"]), (dt, lit_cells(t), objs["g"].props(t)["n"])

# persistence: the meter is still drawn in scene 2 (after c is cleared); chip c is gone; chip d appears
t2 = ls[1] + 1.0
assert lit_segments(t2) == 20
assert objs["c"].alpha(t2) == 0 and objs["d"].alpha(t2) > 0.9
# clear=True removes everything, before the third scene's own line starts
assert objs["m"].alpha(ls[2] + 0.5) == 0 and objs["d"].alpha(ls[2] + 0.5) == 0

# terminal typing grows monotonically
T = {"type": "stage", "objects": [{"kind": "terminal", "id": "t", "x": 90, "y": 500, "w": 900, "h": 200, "size": 26, "cps": 20, "t": 0.0,
                                   "lines": [{"text": "$ hello world", "type": True}]}]}
SPEC2 = dict(SPEC, scenes=[T], lines=[("x y z", 0.2, 3.0)])
reel.SPEC = SPEC2
prev = -1
for dt in (0.6, 0.9, 1.2, 1.6, 2.2):
    img = reel.frame(0.2 + dt).convert("RGB")
    xs = [x for x in range(90, 600) for y in range(560, 600, 2) if img.getpixel((x, y))[0] > 200]
    right = max(xs) if xs else 0
    assert right >= prev - 16, (dt, right, prev)            # the blinking cursor is 14 px wide; the text itself never shrinks
    prev = max(prev, right)
assert prev > 200, prev
# a clear list naming an object that does not exist must fail loudly (a stale id once left two terminals overlapping)
BAD = dict(SPEC, scenes=[SPEC["scenes"][0], {"type": "stage", "objects": [], "clear": ["nope"]}], lines=SPEC["lines"][:2])
try:
    stage.build(BAD, ls[:2]); raise SystemExit("unknown clear id was accepted")
except KeyError:
    pass
print("OK: stage engine - anchors, tweens, persistence, clear and typing behave.")
