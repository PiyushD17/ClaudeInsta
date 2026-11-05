"""Stage engine: one persistent animated diagram that evolves across several script lines (the 'story canvas' style).

A reel spec can use scenes of {"type": "stage", "objects": [...], "events": [...], "clear": ...}. Objects created in a scene stay on screen
(across the following stage scenes) until they are hidden, so the picture builds up and keeps its state (a disk meter that fills in chapter 2 is still
there in chapter 5). Times are seconds after the voice starts the scene's script line, or "wN" = the moment the N-th word of that line begins
(so pictures can be locked to words and keep their sync when the voice is retimed).

Object kinds (all take id, t, out, x, y; colours: cyan amber pink purple mint white gray):
  panel     x y w h, title, icon, color, dashed                    a rounded container with a small caps title
  text      x y text size color align(l|c|r) font(bold|med|mono) maxw
  brush     x y parts:[(text,color)] size                          hand-lettered chapter title with a wavy underline
  chip      x y text color filled                                  small rounded label (centered on x,y)
  question  x y text                                               dark pill with a pink ? badge (a second hook shown on screen)
  icon      x y size name color                                    database server browser document lock unlock key container cloud disk terminal magnifier check cross calendar gear user folder chat bolt
  meter     x y w h value(0-1) label right color segs              segmented bar, `value` can be tweened by events
  terminal  x y w h title lines:[{"text","color","type"(bool),"hl"(bool),"pause"}] cps    typed command line output
  grid      x y w h cols rows n color label                        cells that light up, `n` can be tweened
  arrow     points:[(x,y)...] color dashed head dur                 draws itself
  packet    path:[(x,y)...] text color dur hold w h                 a labelled block travelling along a path
  callout   x y text color tx ty(arrow target) parts:[(text,color)] hand-lettered note with an arrow to (tx,ty)
  dots      x y n active color                                     numbered progress circles (active can be tweened)
  badge     x y name(check|cross) size                             round status stamp
  follow    x y                                                    end-card follow button that gets clicked
Events (in a scene's "events"): {"id": "disk", "t": 1.0, "dur": 1.5, "set": {"value": 0.6}} tweens numeric props and switches others at t;
{"id": "x", "t": 2, "hide": true}; {"id": "x", "t": 2, "move": {"x": 100, "y": 200}, "dur": 0.6}. A scene's "clear": true fades out everything on stage
at the scene start (new chapter); "clear": ["id", ...] fades out just those.
"""
import math, os, random
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1080, 1920
F = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts") + os.sep
BOLD = lambda s: ImageFont.truetype(F + "InterDisplay-Bold.otf", int(s))
MED = lambda s: ImageFont.truetype(F + "Inter-Medium.otf", int(s))
REG = lambda s: ImageFont.truetype(F + "Inter-Regular.otf", int(s))
MONO = lambda s: ImageFont.truetype(F + "DejaVuSansMono.ttf", int(s))
MONOB = lambda s: ImageFont.truetype(F + "DejaVuSansMono-Bold.ttf", int(s))
FONTS = {"bold": BOLD, "med": MED, "reg": REG, "mono": MONO, "monob": MONOB}
COL = {"cyan": (62, 190, 220), "amber": (255, 190, 60), "pink": (255, 95, 140), "purple": (160, 130, 255), "mint": (95, 220, 190),
       "white": (240, 243, 248), "gray": (146, 156, 178), "dark": (10, 12, 22), "red": (255, 85, 85), "green": (80, 210, 120)}
PANEL, PANEL2, EDGE = (22, 26, 42), (30, 35, 56), (52, 60, 88)
NUMERIC_SKIP = {"x", "y"}

def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def ease(u): u = clamp(u); return 1 - (1 - u) ** 3
def A(c, a): return tuple(c[:3]) + (int(255 * clamp(a)),)
def col(c): return COL.get(c, c) if isinstance(c, str) else tuple(c)
def lerp(a, b, u): return a + (b - a) * u

# ----------------------------------------------------------------------------- timing
def resolve_t(spec, si, t):
    """Seconds after the voice starts scene si's line; 'wN' = start of the N-th word of that line."""
    if isinstance(t, str) and t.startswith("w"):
        return (int(t[1:]) - 1) / spec.get("pace_wps", 3.2)
    return float(t)

def display_strings(sc):
    """All on-screen strings of a stage scene as (key, text) for check_spec (settings such as ids and colours are skipped)."""
    out = []
    for o in sc.get("objects", []):
        k = o.get("kind")
        if k in ("text", "chip", "question", "packet", "callout", "follow") and o.get("text"): out.append(("text", o["text"]))
        if k == "panel" and o.get("title"): out.append(("title", o["title"]))
        if k in ("brush", "callout"):
            for p in o.get("parts", []): out.append(("title" if k == "brush" else "text", p[0]))
        if k == "meter":
            for key in ("label", "right"):
                if o.get(key): out.append((key, o[key]))
        if k == "grid" and o.get("label"): out.append(("label", o["label"]))
        if k == "terminal":
            if o.get("title"): out.append(("title", o["title"]))
            for ln in o.get("lines", []): out.append(("code", ln["text"] if isinstance(ln, dict) else ln))
    for e in sc.get("events", []):
        for key in ("text", "label", "right"):
            if isinstance(e.get("set", {}).get(key), str): out.append((key, e["set"][key]))
    return out

# ----------------------------------------------------------------------------- object model
class Obj:
    def __init__(self, spec, si, o, line_start):
        self.o = dict(o); self.kind = o["kind"]; self.id = o.get("id")
        self.t0 = line_start + resolve_t(spec, si, o.get("t", 0.0))
        self.t_out = line_start + resolve_t(spec, si, o["out"]) if "out" in o else None
        self.events = []
        self.fade_out = None                       # set when a scene clears it
    def add_event(self, t, dur, e): self.events.append((t, dur, e))
    def props(self, t):
        p = dict(self.o)
        for t0, dur, e in sorted(self.events, key=lambda x: x[0]):
            if t < t0: break
            u = ease((t - t0) / dur) if dur > 0 else 1.0
            for k, v in {**e.get("set", {}), **e.get("move", {})}.items():
                if isinstance(v, (int, float)) and isinstance(p.get(k), (int, float)) and not isinstance(v, bool):
                    p[k] = lerp(p[k], v, u) if u < 1 else v
                    if u < 1: p["_tween_" + k] = True
                elif t >= t0: p[k] = v
        return p
    def alpha(self, t):
        if t < self.t0: return 0.0
        a = ease((t - self.t0) / 0.35)
        end = self.t_out
        for t0, dur, e in self.events:
            if e.get("hide") and t >= t0: end = t0 if end is None else min(end, t0)
        if self.fade_out is not None: end = self.fade_out if end is None else min(end, self.fade_out)
        if end is not None and t >= end: a *= 1 - clamp((t - end) / 0.3)
        return a

_CACHE = {}
def build(spec, line_starts):
    key = id(spec)
    if key in _CACHE and _CACHE[key][0] == tuple(line_starts): return _CACHE[key][1]
    objs, by_id = [], {}
    for si, sc in enumerate(spec["scenes"]):
        if sc.get("type") != "stage": continue
        ls = line_starts[si]
        clear = sc.get("clear")
        for ob in objs:
            if ob.fade_out is None and (clear is True or (isinstance(clear, list) and ob.id in clear)): ob.fade_out = ls
        for o in sc.get("objects", []):
            ob = Obj(spec, si, o, ls); objs.append(ob)
            if ob.id: by_id[ob.id] = ob
        for e in sc.get("events", []):
            ob = by_id.get(e["id"])
            if ob is None: raise KeyError(f"event for unknown object id {e['id']!r} in scene {si + 1}")
            ob.add_event(ls + resolve_t(spec, si, e.get("t", 0.0)), e.get("dur", 0.5 if ("set" in e or "move" in e) else 0), e)
    _CACHE[key] = (tuple(line_starts), objs)
    return objs

def stage_scene_indices(spec): return [i for i, s in enumerate(spec["scenes"]) if s.get("type") == "stage"]

def stage_alpha(t, bounds, idxs):
    """Stage visibility: fades in at the start of the first stage scene of a run and out at the end of the last (no dip between neighbours)."""
    runs, cur = [], []
    for i in idxs:
        if cur and i == cur[-1] + 1: cur.append(i)
        else:
            if cur: runs.append(cur)
            cur = [i]
    if cur: runs.append(cur)
    a = 0.0
    for r in runs:
        s0, s1 = bounds[r[0]][0], bounds[r[-1]][1]
        a = max(a, clamp(min((t - s0) / 0.3, (s1 - t) / 0.3)))
    return a

# ----------------------------------------------------------------------------- drawing helpers
def rr(d, box, fill=None, outline=None, width=2, radius=22, dashed=False):
    if dashed and outline is not None:
        d.rounded_rectangle(box, radius=radius, fill=fill)
        x0, y0, x1, y1 = box
        def seg(a, b, c0, c1, horiz):
            p = a
            while p < b:
                q = min(p + 14, b)
                d.line([(p, c0), (q, c0)] if horiz else [(c0, p), (c0, q)], fill=outline, width=width); p += 24
        seg(x0 + radius, x1 - radius, y0, y0, True); seg(x0 + radius, x1 - radius, y1, y1, True)
        seg(y0 + radius, y1 - radius, x0, x0, False); seg(y0 + radius, y1 - radius, x1, x1, False)
    else:
        d.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)

def wrap(d, text, f, maxw):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if d.textlength(t, font=f) <= maxw: cur = t
        else: lines.append(cur); cur = w
    lines.append(cur)
    return lines

def brush_text(img, cx, cy, parts, size, a, seed=3):
    """Hand-lettered look: bold sans, sheared, with a tiny per-letter wobble and a wavy underline (a real brush font in fonts/brush.ttf is used if present)."""
    f = ImageFont.truetype(F + "brush.ttf", int(size)) if os.path.exists(F + "brush.ttf") else BOLD(size)
    tmp = ImageDraw.Draw(Image.new("RGB", (4, 4)))
    total = sum(tmp.textlength(t + " ", font=f) for t, _ in parts)
    pad = 30
    layer = Image.new("RGBA", (int(total) + 2 * pad, int(size * 1.9)), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer); rnd = random.Random(seed); x = pad
    for t, c in parts:
        for ch in t + " ":
            ld.text((x, int(size * 0.3) + rnd.uniform(-2, 2)), ch, font=f, fill=col(c)); x += tmp.textlength(ch, font=f)
    # wavy underline in the colour of the last part
    y0 = int(size * 1.5); lc = col(parts[-1][1])
    pts = [(pad + i * 6, y0 + 4 * math.sin(i * 0.5)) for i in range(int((total) / 6))]
    if len(pts) > 1: ld.line(pts, fill=lc, width=max(3, int(size / 14)), joint="curve")
    layer = layer.transform(layer.size, Image.AFFINE, (1, 0.16, -0.16 * layer.size[1] / 2, 0, 1, 0), resample=Image.BICUBIC)
    if a < 0.999: layer.putalpha(layer.getchannel("A").point(lambda v: int(v * a)))
    img.paste(layer, (int(cx - layer.size[0] / 2), int(cy - layer.size[1] / 2)), layer)

def draw_icon(d, name, x, y, s, c, a):
    c = A(c, a); w = max(2, int(s / 14)); h = s / 2
    L, T = x - h, y - h
    if name == "database":
        for k in (0, 1, 2):
            yy = T + s * (0.18 + 0.3 * k)
            if k: d.rectangle([L + s * 0.1, yy - s * 0.1, L + s * 0.9, yy + s * 0.1], fill=A(PANEL, a))
            d.arc([L + s * 0.1, yy - s * 0.14, L + s * 0.9, yy + s * 0.14], 0, 180, fill=c, width=w)
        d.ellipse([L + s * 0.1, T + s * 0.04, L + s * 0.9, T + s * 0.32], outline=c, width=w)
        d.line([L + s * 0.1, T + s * 0.18, L + s * 0.1, T + s * 0.8], fill=c, width=w); d.line([L + s * 0.9, T + s * 0.18, L + s * 0.9, T + s * 0.8], fill=c, width=w)
        d.arc([L + s * 0.1, T + s * 0.66, L + s * 0.9, T + s * 0.94], 0, 180, fill=c, width=w)
    elif name == "server":
        for k in range(3):
            yy = T + s * (0.06 + 0.31 * k)
            d.rounded_rectangle([L + s * 0.05, yy, L + s * 0.95, yy + s * 0.25], radius=int(s * 0.07), outline=c, width=w)
            d.ellipse([L + s * 0.75, yy + s * 0.09, L + s * 0.83, yy + s * 0.17], fill=c)
    elif name == "browser":
        d.rounded_rectangle([L + s * 0.02, T + s * 0.12, L + s * 0.98, T + s * 0.88], radius=int(s * 0.1), outline=c, width=w)
        d.line([L + s * 0.02, T + s * 0.33, L + s * 0.98, T + s * 0.33], fill=c, width=w)
        for k in range(3): d.ellipse([L + s * (0.1 + 0.1 * k), T + s * 0.19, L + s * (0.15 + 0.1 * k), T + s * 0.26], fill=c)
    elif name == "document":
        d.rounded_rectangle([L + s * 0.18, T + s * 0.04, L + s * 0.82, T + s * 0.96], radius=int(s * 0.08), outline=c, width=w)
        for k in range(4): d.line([L + s * 0.3, T + s * (0.3 + 0.15 * k), L + s * (0.7 if k < 3 else 0.5), T + s * (0.3 + 0.15 * k)], fill=c, width=w)
    elif name in ("lock", "unlock"):
        d.rounded_rectangle([L + s * 0.15, T + s * 0.42, L + s * 0.85, T + s * 0.94], radius=int(s * 0.1), outline=c, width=w, fill=A(c[:3], a * 0.25))
        d.arc([L + s * 0.27, T + s * 0.06, L + s * 0.73, T + s * 0.72], 180 if name == "lock" else 150, 360 if name == "lock" else 340, fill=c, width=w)
        d.ellipse([L + s * 0.45, T + s * 0.6, L + s * 0.55, T + s * 0.7], fill=c)
    elif name == "key":
        d.ellipse([L + s * 0.05, T + s * 0.3, L + s * 0.45, T + s * 0.7], outline=c, width=w)
        d.line([L + s * 0.45, y, L + s * 0.95, y], fill=c, width=w); d.line([L + s * 0.78, y, L + s * 0.78, y + s * 0.18], fill=c, width=w); d.line([L + s * 0.92, y, L + s * 0.92, y + s * 0.14], fill=c, width=w)
    elif name == "container":
        d.polygon([(L + s * 0.5, T + s * 0.05), (L + s * 0.93, T + s * 0.27), (L + s * 0.93, T + s * 0.73), (L + s * 0.5, T + s * 0.95), (L + s * 0.07, T + s * 0.73), (L + s * 0.07, T + s * 0.27)], outline=c, width=w)
        d.line([L + s * 0.07, T + s * 0.27, L + s * 0.5, T + s * 0.5, L + s * 0.93, T + s * 0.27], fill=c, width=w); d.line([L + s * 0.5, T + s * 0.5, L + s * 0.5, T + s * 0.95], fill=c, width=w)
    elif name == "cloud":
        for (cx, cy, r) in ((0.3, 0.6, 0.2), (0.5, 0.42, 0.26), (0.72, 0.6, 0.2)):
            d.ellipse([L + s * (cx - r), T + s * (cy - r), L + s * (cx + r), T + s * (cy + r)], outline=c, width=w)
        d.rectangle([L + s * 0.28, T + s * 0.5, L + s * 0.74, T + s * 0.78], fill=A(PANEL, a)); d.line([L + s * 0.3, T + s * 0.8, L + s * 0.72, T + s * 0.8], fill=c, width=w)
    elif name == "disk":
        d.rounded_rectangle([L + s * 0.05, T + s * 0.25, L + s * 0.95, T + s * 0.75], radius=int(s * 0.12), outline=c, width=w)
        d.ellipse([L + s * 0.7, T + s * 0.42, L + s * 0.82, T + s * 0.54], fill=c); d.line([L + s * 0.15, T + s * 0.58, L + s * 0.5, T + s * 0.58], fill=c, width=w)
    elif name == "terminal":
        d.rounded_rectangle([L + s * 0.03, T + s * 0.12, L + s * 0.97, T + s * 0.88], radius=int(s * 0.1), outline=c, width=w)
        d.line([L + s * 0.2, T + s * 0.35, L + s * 0.38, T + s * 0.5, L + s * 0.2, T + s * 0.65], fill=c, width=w); d.line([L + s * 0.5, T + s * 0.66, L + s * 0.75, T + s * 0.66], fill=c, width=w)
    elif name == "magnifier":
        d.ellipse([L + s * 0.08, T + s * 0.08, L + s * 0.62, T + s * 0.62], outline=c, width=w + 1); d.line([L + s * 0.55, T + s * 0.55, L + s * 0.92, T + s * 0.92], fill=c, width=w + 2)
    elif name == "check":
        d.ellipse([L + s * 0.04, T + s * 0.04, L + s * 0.96, T + s * 0.96], outline=c, width=w); d.line([L + s * 0.28, y, L + s * 0.45, y + s * 0.17, L + s * 0.74, y - s * 0.17], fill=c, width=w + 1)
    elif name == "cross":
        d.ellipse([L + s * 0.04, T + s * 0.04, L + s * 0.96, T + s * 0.96], outline=c, width=w); d.line([L + s * 0.32, T + s * 0.32, L + s * 0.68, T + s * 0.68], fill=c, width=w + 1); d.line([L + s * 0.68, T + s * 0.32, L + s * 0.32, T + s * 0.68], fill=c, width=w + 1)
    elif name == "calendar":
        d.rounded_rectangle([L + s * 0.06, T + s * 0.14, L + s * 0.94, T + s * 0.94], radius=int(s * 0.1), outline=c, width=w); d.line([L + s * 0.06, T + s * 0.38, L + s * 0.94, T + s * 0.38], fill=c, width=w)
        for k in (0.28, 0.72): d.line([L + s * k, T + s * 0.04, L + s * k, T + s * 0.24], fill=c, width=w + 1)
        for r in range(2):
            for q in range(3): d.rectangle([L + s * (0.22 + 0.22 * q), T + s * (0.5 + 0.2 * r), L + s * (0.3 + 0.22 * q), T + s * (0.58 + 0.2 * r)], fill=c)
    elif name == "gear":
        d.ellipse([L + s * 0.28, T + s * 0.28, L + s * 0.72, T + s * 0.72], outline=c, width=w + 1)
        for k in range(8):
            ang = k * math.pi / 4; d.line([x + math.cos(ang) * s * 0.3, y + math.sin(ang) * s * 0.3, x + math.cos(ang) * s * 0.46, y + math.sin(ang) * s * 0.46], fill=c, width=w + 2)
    elif name == "user":
        d.ellipse([L + s * 0.32, T + s * 0.08, L + s * 0.68, T + s * 0.44], outline=c, width=w); d.arc([L + s * 0.12, T + s * 0.5, L + s * 0.88, T + s * 1.2], 180, 360, fill=c, width=w)
    elif name == "folder":
        d.polygon([(L + s * 0.05, T + s * 0.25), (L + s * 0.38, T + s * 0.25), (L + s * 0.46, T + s * 0.36), (L + s * 0.95, T + s * 0.36), (L + s * 0.95, T + s * 0.85), (L + s * 0.05, T + s * 0.85)], outline=c)
        d.line([L + s * 0.05, T + s * 0.25, L + s * 0.38, T + s * 0.25, L + s * 0.46, T + s * 0.36, L + s * 0.95, T + s * 0.36, L + s * 0.95, T + s * 0.85, L + s * 0.05, T + s * 0.85, L + s * 0.05, T + s * 0.25], fill=c, width=w)
    elif name == "chat":
        d.rounded_rectangle([L + s * 0.05, T + s * 0.1, L + s * 0.95, T + s * 0.72], radius=int(s * 0.18), outline=c, width=w)
        d.polygon([(L + s * 0.25, T + s * 0.72), (L + s * 0.25, T + s * 0.95), (L + s * 0.45, T + s * 0.72)], fill=c)
        for k in range(3): d.ellipse([L + s * (0.28 + 0.17 * k), T + s * 0.36, L + s * (0.35 + 0.17 * k), T + s * 0.43], fill=c)
    elif name == "bolt":
        d.polygon([(L + s * 0.55, T + s * 0.02), (L + s * 0.2, T + s * 0.55), (L + s * 0.48, T + s * 0.55), (L + s * 0.4, T + s * 0.98), (L + s * 0.82, T + s * 0.4), (L + s * 0.53, T + s * 0.4)], fill=c)

# ----------------------------------------------------------------------------- object drawing
def draw_obj(d, img, ob, t, spec):
    a = ob.alpha(t)
    if a <= 0.003: return
    p = ob.props(t); k = ob.kind
    slide = (1 - ease((t - ob.t0) / 0.35)) * 16 if t - ob.t0 < 0.35 else 0
    x = p.get("x", 0); y = p.get("y", 0) + slide
    if k == "panel":
        c = col(p.get("color", "gray")); w, h = p["w"], p["h"]
        rr(d, [x, y, x + w, y + h], fill=A(PANEL, a * (0.55 if p.get("dashed") else 1)), outline=A(c if p.get("color") else EDGE, a), width=3 if p.get("color") else 2, dashed=p.get("dashed", False))
        tx = x + 22
        if p.get("icon"): draw_icon(d, p["icon"], x + 38, y + 36, 30, c if p.get("color") else COL["gray"], a); tx = x + 66
        if p.get("title"): d.text((tx, y + 36), p["title"].upper(), font=BOLD(p.get("tsize", 24)), fill=A(COL["white"], a), anchor="lm")
    elif k == "text":
        f = FONTS[p.get("font", "bold")](p.get("size", 36)); anc = {"l": "la", "c": "ma", "r": "ra"}[p.get("align", "l")]
        lines = wrap(d, p["text"], f, p["maxw"]) if p.get("maxw") else [p["text"]]
        for i, ln in enumerate(lines): d.text((x, y + i * p.get("size", 36) * 1.3), ln, font=f, fill=A(col(p.get("color", "white")), a), anchor=anc)
    elif k == "brush":
        brush_text(img, x, y, p["parts"], p.get("size", 56), a)
    elif k == "chip":
        f = BOLD(p.get("size", 26)); w = d.textlength(p["text"], font=f) + 36; c = col(p.get("color", "cyan"))
        rr(d, [x - w / 2, y - 24, x + w / 2, y + 24], fill=A(c, a) if p.get("filled", True) else A(PANEL, a), outline=A(c, a), width=2, radius=24)
        d.text((x, y), p["text"], font=f, fill=A(COL["dark"] if p.get("filled", True) else c, a), anchor="mm")
    elif k == "question":
        f = BOLD(p.get("size", 30)); w = d.textlength(p["text"], font=f) + 100
        rr(d, [x - w / 2, y - 34, x + w / 2, y + 34], fill=A((12, 14, 24), a), outline=A(EDGE, a), width=2, radius=34)
        d.text((x - w / 2 + 32, y), p["text"], font=f, fill=A(COL["white"], a), anchor="lm")
        d.ellipse([x + w / 2 - 54, y - 20, x + w / 2 - 14, y + 20], fill=A(COL["pink"], a)); d.text((x + w / 2 - 34, y), "?", font=BOLD(26), fill=A(COL["white"], a), anchor="mm")
    elif k == "icon":
        draw_icon(d, p["name"], x, y, p.get("size", 80), col(p.get("color", "white")), a)
    elif k == "meter":
        w, h = p["w"], p.get("h", 26); segs = p.get("segs", 36); v = clamp(p.get("value", 0)); c = col(p.get("color", "pink"))
        if p.get("label"): d.text((x, y - 4), p["label"].upper(), font=BOLD(22), fill=A(COL["white"], a), anchor="ls")
        sw_ = w / segs
        for i in range(segs):
            on = (i + 0.5) / segs <= v
            d.rounded_rectangle([x + i * sw_ + 1.5, y + 8, x + (i + 1) * sw_ - 1.5, y + 8 + h], radius=3, fill=A(c, a) if on else A((38, 42, 62), a))
        if p.get("right"):
            f = BOLD(20); tw = d.textlength(p["right"], font=f) + 24; mid = x + w / 2
            rr(d, [mid - tw / 2, y + 8 + h / 2 - 17, mid + tw / 2, y + 8 + h / 2 + 17], fill=A((12, 14, 24), a), outline=A(c, a), width=2, radius=14)
            d.text((mid, y + 8 + h / 2), p["right"], font=f, fill=A(COL["white"], a), anchor="mm")
    elif k == "terminal":
        w, h = p["w"], p["h"]
        rr(d, [x, y, x + w, y + h], fill=A((14, 16, 26), a), outline=A(EDGE, a), width=2, radius=18)
        for i, cc in enumerate(((255, 95, 86), (255, 189, 46), (39, 201, 63))): d.ellipse([x + 20 + i * 26, y + 16, x + 32 + i * 26, y + 28], fill=A(cc, a))
        if p.get("title"): d.text((x + w - 20, y + 22), p["title"], font=MONO(18), fill=A(COL["gray"], a), anchor="rm")
        cps = p.get("cps", 45); tt = max(0.0, t - ob.t0 - 0.5); yy = y + 62; fs = p.get("size", 24)
        for ln in p["lines"]:
            ln = ln if isinstance(ln, dict) else {"text": ln}; txt = ln["text"]; typed = ln.get("type", txt.startswith("$"))
            n = len(txt) if not typed else int(min(len(txt), max(0.0, tt) * cps))
            if not typed and tt <= 0: n = 0
            shown = txt[:n]
            if ln.get("hl") and n > 0: rr(d, [x + 12, yy - 4, x + w - 12, yy + fs + 8], fill=A(A(COL["pink"], 0.28)[:3], a), outline=A(COL["pink"], a), width=2, radius=8)
            d.text((x + 24, yy), shown, font=MONO(fs), fill=A(col(ln.get("color", "white" if typed else "gray")), a))
            if typed and 0 < n < len(txt) and int(t * 3) % 2 == 0: d.rectangle([x + 24 + d.textlength(shown, font=MONO(fs)) + 2, yy, x + 24 + d.textlength(shown, font=MONO(fs)) + 14, yy + fs + 2], fill=A(COL["white"], a))
            tt -= (len(txt) / cps if typed else 0.15) + ln.get("pause", 0.25); yy += fs * 1.55
    elif k == "grid":
        w, h, cols, rows = p["w"], p["h"], p["cols"], p["rows"]; n = int(round(p.get("n", cols * rows))); c = col(p.get("color", "pink"))
        cw, ch = w / cols, h / rows
        for i in range(cols * rows):
            cx, cy = x + (i % cols) * cw, y + (i // cols) * ch
            d.rounded_rectangle([cx + 2, cy + 2, cx + cw - 2, cy + ch - 2], radius=3, fill=A(c, a) if i < n else A((38, 42, 62), a))
        if p.get("label"): d.text((x, y - 12), p["label"], font=BOLD(24), fill=A(COL["white"], a), anchor="ls")
    elif k == "arrow":
        pts = [tuple(q) for q in p["points"]]; prog = ease((t - ob.t0) / p.get("dur", 0.6)); c = col(p.get("color", "gray"))
        total = sum(math.dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1)); goal = total * prog; acc = 0; drawn = [pts[0]]
        for i in range(len(pts) - 1):
            seg = math.dist(pts[i], pts[i + 1])
            if acc + seg <= goal: drawn.append(pts[i + 1]); acc += seg
            else:
                u = (goal - acc) / seg if seg else 0; drawn.append((lerp(pts[i][0], pts[i + 1][0], u), lerp(pts[i][1], pts[i + 1][1], u))); break
        if len(drawn) > 1:
            d.line(drawn, fill=A(c, a), width=p.get("width", 4), joint="curve")
            if p.get("head", True) and prog > 0.97:
                (x0, y0), (x1, y1) = pts[-2], pts[-1]; ang = math.atan2(y1 - y0, x1 - x0)
                d.polygon([(x1, y1), (x1 - 20 * math.cos(ang - 0.45), y1 - 20 * math.sin(ang - 0.45)), (x1 - 20 * math.cos(ang + 0.45), y1 - 20 * math.sin(ang + 0.45))], fill=A(c, a))
    elif k == "packet":
        path = [tuple(q) for q in p["path"]]; prog = clamp((t - ob.t0) / p.get("dur", 1.0))
        total = sum(math.dist(path[i], path[i + 1]) for i in range(len(path) - 1)); goal = total * ease(prog); acc = 0; pos = path[-1]
        for i in range(len(path) - 1):
            seg = math.dist(path[i], path[i + 1])
            if acc + seg >= goal:
                u = (goal - acc) / seg if seg else 0; pos = (lerp(path[i][0], path[i + 1][0], u), lerp(path[i][1], path[i + 1][1], u)); break
            acc += seg
        if prog >= 1 and not p.get("hold", True): return
        w_, h_ = p.get("w", 110), p.get("h", 44); c = col(p.get("color", "cyan"))
        rr(d, [pos[0] - w_ / 2, pos[1] - h_ / 2, pos[0] + w_ / 2, pos[1] + h_ / 2], fill=A(c, a), radius=12)
        if p.get("text"): d.text(pos, p["text"], font=BOLD(p.get("size", 22)), fill=A(COL["dark"], a), anchor="mm")
    elif k == "callout":
        parts = p.get("parts") or [(p.get("text", ""), p.get("color", "white"))]
        brush_text(img, x, y, parts, p.get("size", 34), a, seed=7)
        if "tx" in p:
            ar = ease((t - ob.t0 - 0.2) / 0.5); sx, sy = x, y - 30 if p["ty"] < y else y + 30
            ex, ey = lerp(sx, p["tx"], ar), lerp(sy, p["ty"], ar)
            d.line([(sx, sy), ((sx + ex) / 2 + 20, (sy + ey) / 2), (ex, ey)], fill=A(COL["white"], a), width=3, joint="curve")
            if ar > 0.97:
                ang = math.atan2(ey - sy, ex - sx); d.polygon([(ex, ey), (ex - 16 * math.cos(ang - 0.5), ey - 16 * math.sin(ang - 0.5)), (ex - 16 * math.cos(ang + 0.5), ey - 16 * math.sin(ang + 0.5))], fill=A(COL["white"], a))
    elif k == "dots":
        n = p.get("n", 4); act = p.get("active", 0); cols = [COL["amber"], COL["cyan"], COL["pink"], COL["purple"], COL["mint"]]
        for i in range(n):
            cx = x + (i - (n - 1) / 2) * 110
            on = i <= round(act)
            if i < n - 1: d.line([(cx + 30, y), (cx + 80, y)], fill=A(EDGE, a), width=4)
            d.ellipse([cx - 30, y - 30, cx + 30, y + 30], fill=A(cols[i % 5], a) if on else A((38, 42, 62), a))
            d.text((cx, y), str(i + 1), font=BOLD(28), fill=A(COL["dark"] if on else COL["gray"], a), anchor="mm")
    elif k == "badge":
        s = p.get("size", 44); c = COL["green"] if p.get("name", "check") == "check" else COL["red"]
        d.ellipse([x - s / 2, y - s / 2, x + s / 2, y + s / 2], fill=A(c, a)); draw_icon(d, "check" if p.get("name", "check") == "check" else "cross", x, y, s * 0.62, COL["white"], a)
    elif k == "follow":
        rr(d, [x - 190, y - 70, x + 190, y + 70], fill=A((14, 16, 26), a), outline=A(EDGE, a), width=2, radius=26)
        d.text((x, y - 28), p.get("text", "Tech in a Bite"), font=BOLD(34), fill=A(COL["white"], a), anchor="mm")
        press = clamp((t - ob.t0 - 1.4) / 0.25)
        rr(d, [x - 150, y + 6, x + 150, y + 54], fill=A(COL["amber"] if press > 0.5 else (0, 150, 255), a), radius=24)
        d.text((x, y + 30), "+ Follow" if press < 0.5 else "Following", font=BOLD(26), fill=A(COL["dark"] if press > 0.5 else COL["white"], a), anchor="mm")
        cx = lerp(x + 190, x + 60, ease((t - ob.t0 - 0.6) / 0.7)); cy = lerp(y + 140, y + 44, ease((t - ob.t0 - 0.6) / 0.7))
        d.polygon([(cx, cy), (cx, cy + 34), (cx + 9, cy + 26), (cx + 18, cy + 40), (cx + 24, cy + 37), (cx + 15, cy + 23), (cx + 26, cy + 22)], fill=A(COL["white"], a), outline=A((0, 0, 0), a))

def render(d, img, t, spec, line_starts):
    """Draw every stage object that is alive at absolute time t, in spec order (later = on top)."""
    for ob in build(spec, line_starts):
        draw_obj(d, img, ob, t, spec)
