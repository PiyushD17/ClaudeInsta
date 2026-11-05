"""Stage engine v2: persistent, nested, object-based diagrams in the style of the reference explainers (see STYLE_GUIDE.md).

Principles (measured from the two reference videos):
  * the screen shows OBJECTS and STATE (a server, a key-value store, a terminal with real output, a bar that fills), the voice explains;
  * labels are 1-3 words in a heavy italic display face, values in mono pills ("10/10", "TTL 7", "429");
  * containers nest (gateway > rate limiter > store) and every box has content;
  * text never leaves its box: everything is wrapped onto new lines inside its box, never shrunk below MIN_TEXT px;
  * inactive parts dim, the active part gets a highlight, notes have curved arrows;
  * a terminal under the diagram types real commands and shows real output.

A reel spec uses scenes {"type": "stage", "objects": [...], "events": [...], "clear": [...], "focus": [...]}.
Objects persist across stage scenes until cleared. Times: seconds after the scene's line starts, or "wN" (N-th word of that line).

Common keys for every object: id, kind, t (appear), out (disappear), in (parent id: the object lives inside that box; it inherits fade/dim and
is checked for containment), overlay (true: allowed to overlap others, e.g. a travelling packet).

Kinds
  panel    x y w h label icon color value(mono pill in header) bar({value,segs,color,label}) status(play|stop|check|cross) level(0-2 shade)
           dashed hl(highlight outline) body(icon name drawn large in the content area) compact(true: header only, h<=90)
  title    x y parts:[(text,color)] size underline(bool)                 chapter title, heavy italic caps, wraps to 2 lines max
  question x y parts:[(text,color)] size                                 dark pill with a pink ? (second hook on screen)
  note     x y parts:[(text,color)] size tx ty                           short heavy-italic note with a curved arrow to (tx,ty)
  label    x y text color size align(l|c|r) maxw font(label|ui|mono)    plain text, wrapped inside maxw
  pill     x y text color filled mono size maxw                          rounded chip / value pill centered on (x,y), wraps inside maxw
  terminal x y w h title lines:[{text,color,type,at,hl,flag,flagcolor,check}] size cps   typed commands, real output; each line can wait for its word ("at")
  table    x y w cols:[..] rows:[[..]..] hl(row index) size color           output table (e.g. a CLI listing), columns auto-sized, must fit w
  store    x y w h label rows:[[key,value],..] hl(row) color                key-value store (counters), values change by events (set rows)
  browser  x y w h tab url scheme                                         browser window mock with URL bar
  server   x y w h label color                                            server/rack mock
  bar      x y w h value segs color label right                           segmented bar (disk/usage meter), value tweens
  grid     x y w h cols rows n color label                                cells that light up, n tweens
  seq      x y w h left right color msgs:[{text,dir(>|<),at,color}]       sequence diagram: two lifelines, labelled arrows appear at their words
  arrow    points:[(x,y),..] color dashed head dur curve                  draws itself
  packet   path:[(x,y),..] text color dur hold w h                        a labelled block travelling along a path (overlay)
  dots     x y n active color labels:[..] caption                         numbered steps (recap / progress)
  icon     x y size name color ; badge x y name(check|cross) size
  endcard  text                                                           blurred background + follow card with a cursor click
Events: {"id","t","dur","set":{...}} tweens numbers (value, n, dim, x, y, w, h) and switches others (color, hl, status, rows, text, value...).
Scene "focus": [ids] dims every other visible object to 0.3 at the scene start; "focus": [] (empty list) un-dims everything.

layout_check(spec, line_starts, dur) renders sampled frames offscreen and returns problems: TEXT_OVERFLOW, OUTSIDE_PARENT, OVERLAP,
EMPTY_BOX, OUT_OF_ZONE, TOO_MUCH_TEXT, STATIC (no visible change for > 4 s). check_spec.py turns them into FAIL/WARN.
"""

import math, os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1080, 1920
F = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts") + os.sep
_FC = {}
def _font(name, s):
    key = (name, int(s))
    if key not in _FC: _FC[key] = ImageFont.truetype(F + name, int(s))
    return _FC[key]
LABEL = lambda s: _font("brush.ttf" if os.path.exists(F + "brush.ttf") else "InterDisplay-BlackItalic.otf", s)   # heavy italic caps (or a real brush font if the owner adds fonts/brush.ttf)
UI = lambda s: _font("Inter-SemiBold.otf", s)
UIB = lambda s: _font("Inter-Bold.otf", s)
BOLD = lambda s: _font("InterDisplay-Bold.otf", s)
MED = lambda s: _font("Inter-Medium.otf", s)
REG = lambda s: _font("Inter-Regular.otf", s)
MONO = lambda s: _font("DejaVuSansMono.ttf", s)
MONOB = lambda s: _font("DejaVuSansMono-Bold.ttf", s)
FONTS = {"label": LABEL, "ui": UI, "bold": BOLD, "med": MED, "reg": REG, "mono": MONO, "monob": MONOB}
COL = {"cyan": (62, 190, 220), "amber": (255, 190, 60), "pink": (255, 95, 140), "purple": (160, 130, 255), "mint": (95, 220, 190),
       "white": (240, 243, 248), "gray": (146, 156, 178), "dark": (10, 12, 22), "red": (255, 85, 85), "green": (80, 210, 120), "orange": (255, 150, 70)}
SHADES = [(24, 26, 34), (32, 35, 45), (42, 46, 58)]      # nested panel fills, outer -> inner (reference: dark greys, inner boxes lighter)
EDGE = (58, 64, 82)
PANEL = SHADES[0]
MIN_TEXT = 24                                            # px: nothing on screen is smaller (phone readability)
ZONE = (30, 290, 1050, 1420)                             # content zone: below the @tag, above the Instagram caption area
CHECK = {"on": False, "issues": [], "boxes": {}, "typed": {}}

def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def ease(u): u = clamp(u); return 1 - (1 - u) ** 3
def A(c, a): return tuple(c[:3]) + (int(255 * clamp(a)),)
def col(c): return COL.get(c, c) if isinstance(c, str) else tuple(c)
def lerp(a, b, u): return a + (b - a) * u

def issue(ob, code, msg):
    if CHECK["on"]: CHECK["issues"].append((code, ob.id or ob.kind, msg))

def box(ob, x0, y0, x1, y1):
    """Record the object's drawn bounding box (for overlap / containment checks)."""
    if CHECK["on"]: CHECK["boxes"][id(ob)] = (x0, y0, x1, y1)

# ----------------------------------------------------------------------------- text layout: wrap inside a box, never overflow
_FIT = {}
def fit(text, fontfn, size, maxw, maxh=None, min_size=MIN_TEXT, lh=1.25, maxlines=None):
    """Wrap `text` into lines no wider than maxw (shrinking the font only down to min_size). Returns (font, lines, line_height, ok)."""
    key = (text, fontfn, int(size), int(maxw), maxh and int(maxh), min_size, lh, maxlines)
    if key in _FIT: return _FIT[key]
    s = int(size)
    while True:
        f = fontfn(s); lines, cur = [], ""
        for word in text.split(" "):
            t = (cur + " " + word).strip() if cur else word
            if f.getlength(t) <= maxw: cur = t
            else:
                if cur: lines.append(cur)
                cur = word
        lines.append(cur)
        too_wide = any(f.getlength(l) > maxw for l in lines)
        too_tall = (maxh is not None and len(lines) * s * lh > maxh + 0.5) or (maxlines is not None and len(lines) > maxlines)
        if not (too_wide or too_tall) or s <= min_size:
            res = (f, lines, s * lh, not (too_wide or too_tall)); _FIT[key] = res; return res
        s -= 1

def draw_lines(d, x, y, lines, f, lh, fill, align="l"):
    for i, ln in enumerate(lines):
        if align == "c": d.text((x, y + i * lh), ln, font=f, fill=fill, anchor="ma")
        elif align == "r": d.text((x, y + i * lh), ln, font=f, fill=fill, anchor="ra")
        else: d.text((x, y + i * lh), ln, font=f, fill=fill)

def parts_width(parts, f): return sum(f.getlength(t) for t, _ in parts)

def draw_parts(d, cx, y, parts, fontfn, size, maxw, a, ob, maxlines=2):
    """Coloured multi-part heavy text, centred, wrapped inside maxw (word by word, keeping each word's colour)."""
    words = []
    for t, c in parts:
        for wd in t.replace("\n", " \n ").split(" "):
            if wd: words.append((wd, c))
    s = int(size)
    while True:
        f = fontfn(s); sp = f.getlength(" "); lines, cur, cw = [], [], 0
        for wd, c in words:
            if wd == "\n":
                if cur: lines.append(cur)
                cur, cw = [], 0; continue
            w_ = f.getlength(wd)
            if cur and cw + sp + w_ > maxw: lines.append(cur); cur, cw = [], 0
            cw = cw + (sp if cur else 0) + w_; cur.append((wd, c))
        if cur: lines.append(cur)
        widths = [sum(f.getlength(w) for w, _ in ln) + sp * (len(ln) - 1) for ln in lines]
        if (len(lines) <= maxlines and max(widths) <= maxw) or s <= MIN_TEXT: break
        s -= 1
    if len(lines) > maxlines or max(widths) > maxw: issue(ob, "TEXT_OVERFLOW", f'"{" ".join(w for w, _ in words if w != chr(10))}" does not fit in {maxw}px on {maxlines} line(s)')
    lh = s * 1.18
    for i, ln in enumerate(lines):
        x = cx - widths[i] / 2
        for wd, c in ln:
            d.text((x, y + i * lh), wd, font=f, fill=A(col(c), a)); x += f.getlength(wd) + sp
    return (cx - max(widths) / 2, y, cx + max(widths) / 2, y + len(lines) * lh), s

def rr(d, b, fill=None, outline=None, width=2, radius=18, dashed=False):
    if dashed and outline is not None:
        d.rounded_rectangle(b, radius=radius, fill=fill)
        x0, y0, x1, y1 = b
        def seg(p0, p1, c, horiz):
            p = p0
            while p < p1:
                q = min(p + 14, p1)
                d.line([(p, c), (q, c)] if horiz else [(c, p), (c, q)], fill=outline, width=width); p += 24
        seg(x0 + radius, x1 - radius, y0, True); seg(x0 + radius, x1 - radius, y1, True)
        seg(y0 + radius, y1 - radius, x0, False); seg(y0 + radius, y1 - radius, x1, False)
    else:
        d.rounded_rectangle(b, radius=radius, fill=fill, outline=outline, width=width)

def bezier(p0, p1, p2, n=24):
    return [((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0], (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1]) for t in [i / n for i in range(n + 1)]]

def arrow_head(d, p_from, p_to, c, size=18):
    ang = math.atan2(p_to[1] - p_from[1], p_to[0] - p_from[0]); x1, y1 = p_to
    d.polygon([(x1, y1), (x1 - size * math.cos(ang - 0.45), y1 - size * math.sin(ang - 0.45)), (x1 - size * math.cos(ang + 0.45), y1 - size * math.sin(ang + 0.45))], fill=c)

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
    elif name == "app":
        d.rounded_rectangle([L + s * 0.04, T + s * 0.12, L + s * 0.96, T + s * 0.88], radius=int(s * 0.1), outline=c, width=w)
        d.line([L + s * 0.04, T + s * 0.3, L + s * 0.96, T + s * 0.3], fill=c, width=w)
        for k, ln in enumerate((0.55, 0.7, 0.45)): d.line([L + s * 0.18, T + s * (0.45 + 0.13 * k), L + s * (0.18 + ln * 0.7), T + s * (0.45 + 0.13 * k)], fill=c, width=w)
    elif name == "play":
        d.ellipse([L, T, L + s, T + s], fill=c); d.polygon([(L + s * 0.4, T + s * 0.28), (L + s * 0.4, T + s * 0.72), (L + s * 0.74, T + s * 0.5)], fill=A((15, 17, 25), a))
    elif name == "stop":
        d.ellipse([L, T, L + s, T + s], fill=c); d.rectangle([L + s * 0.33, T + s * 0.33, L + s * 0.67, T + s * 0.67], fill=A((15, 17, 25), a))
    elif name == "router":
        pts = [(0.15, 0.5), (0.5, 0.2), (0.85, 0.5), (0.5, 0.8)]
        for i in range(4):
            p, q = pts[i], pts[(i + 1) % 4]; d.line([L + s * p[0], T + s * p[1], L + s * q[0], T + s * q[1]], fill=c, width=w)
        for p in pts: d.ellipse([L + s * (p[0] - 0.09), T + s * (p[1] - 0.09), L + s * (p[0] + 0.09), T + s * (p[1] + 0.09)], outline=c, width=w, fill=A((15, 17, 25), a))
    elif name == "shield":
        d.polygon([(L + s * 0.5, T + s * 0.04), (L + s * 0.9, T + s * 0.2), (L + s * 0.84, T + s * 0.62), (L + s * 0.5, T + s * 0.96), (L + s * 0.16, T + s * 0.62), (L + s * 0.1, T + s * 0.2)], outline=c, fill=A(c[:3], a * 0.2))
        d.line([L + s * 0.32, T + s * 0.5, L + s * 0.46, T + s * 0.64, L + s * 0.7, T + s * 0.36], fill=c, width=w + 1)
    elif name == "clock":
        d.ellipse([L + s * 0.06, T + s * 0.06, L + s * 0.94, T + s * 0.94], outline=c, width=w); d.line([x, y, x, T + s * 0.24], fill=c, width=w + 1); d.line([x, y, L + s * 0.72, y], fill=c, width=w + 1)



# ----------------------------------------------------------------------------- timing
def resolve_t(spec, si, t):
    """Seconds after the voice starts scene si's line; 'wN' = start of the N-th word of that line."""
    if isinstance(t, str) and t.startswith("w"):
        return (int(t[1:]) - 1) / spec.get("pace_wps", 3.2)
    return float(t)

TEXT_KEYS = {"panel": ("label",), "label": ("text",), "pill": ("text",), "chip": ("text",), "text": ("text",), "packet": ("text",),
             "server": ("label",), "store": ("label",), "browser": ("url",), "bar": ("label", "right"), "meter": ("label", "right"),
             "grid": ("label",), "seq": ("left", "right"), "follow": ("text",), "endcard": ("text",)}
HEADLINE_KINDS = ("title", "brush", "question", "note", "callout")

def obj_strings(o):
    """On-screen strings of one object as (key, text). key 'headline' = titles/questions/notes (stranger test applies);
    key 'object' = short object labels inside the diagram; key 'code' = terminal/table text."""
    k = o.get("kind"); out = []
    if k in HEADLINE_KINDS:
        if o.get("parts"): out.append(("headline", "".join(p[0] for p in o["parts"])))
        elif o.get("text"): out.append(("headline", o["text"]))
    for key in TEXT_KEYS.get(k, ()):
        if isinstance(o.get(key), str) and o[key]: out.append(("object", o[key]))
    if k == "panel" and isinstance(o.get("value"), str): out.append(("object", o["value"]))
    if k == "panel" and isinstance(o.get("bar"), dict) and o["bar"].get("label"): out.append(("object", o["bar"]["label"]))
    if k == "terminal":
        if o.get("title"): out.append(("object", o["title"]))
        for ln in o.get("lines", []): out.append(("code", ln["text"] if isinstance(ln, dict) else ln))
    if k == "table":
        out.append(("code", " ".join(o.get("cols", []))))
        for r in o.get("rows", []): out.append(("code", " ".join(str(c) for c in r)))
    if k == "store":
        for r in o.get("rows", []): out.append(("code", " ".join(str(c) for c in r)))
    if k == "seq":
        for m in o.get("msgs", []): out.append(("object", m["text"]))
    if k == "dots":
        for l in o.get("labels", []): out.append(("object", l))
        if o.get("caption"): out.append(("headline", o["caption"] if isinstance(o["caption"], str) else "".join(p[0] for p in o["caption"])))
    return out

def display_strings(sc):
    """All on-screen strings created by one stage scene (objects plus text switched in by its events)."""
    out = []
    for o in sc.get("objects", []): out += obj_strings(o)
    for e in sc.get("events", []):
        for key, v in e.get("set", {}).items():
            if key in ("text", "label", "right", "value", "url") and isinstance(v, str): out.append(("object", v))
            if key == "parts" and isinstance(v, list): out.append(("headline", "".join(p[0] for p in v)))
            if key == "rows":
                for r in v: out.append(("code", " ".join(str(c) for c in r)))
    return out

# ----------------------------------------------------------------------------- object model
class Obj:
    def __init__(self, spec, si, o, line_start):
        self.o = dict(o); self.kind = o["kind"]; self.id = o.get("id"); self.si = si
        self.t0 = line_start + resolve_t(spec, si, o.get("t", 0.0))
        self.t_out = line_start + resolve_t(spec, si, o["out"]) if "out" in o else None
        self.line_start = line_start; self.spec = spec
        self.events = []; self.fade_out = None; self.parent = None; self.children = []
        if self.kind == "terminal":                                     # per-line anchors
            for ln in self.o.get("lines", []):
                if isinstance(ln, dict) and "at" in ln: ln["_at"] = line_start + resolve_t(spec, si, ln["at"])
        if self.kind == "seq":
            for m in self.o.get("msgs", []):
                m["_at"] = line_start + resolve_t(spec, si, m.get("at", 0.0))
        # backwards compatibility with v1 specs
        if self.kind == "panel" and "title" in self.o and "label" not in self.o: self.o["label"] = self.o.pop("title")
        if self.kind == "question" and "parts" not in self.o: self.o["parts"] = [(self.o.get("text", ""), "white")]
    def add_event(self, t, dur, e): self.events.append((t, dur, e))
    def props(self, t):
        p = dict(self.o); p.setdefault("dim", 1.0)
        for t0, dur, e in sorted(self.events, key=lambda x: x[0]):
            if t < t0: break
            u = ease((t - t0) / dur) if dur > 0 else 1.0
            for k, v in {**e.get("set", {}), **e.get("move", {})}.items():
                if isinstance(v, (int, float)) and not isinstance(v, bool) and isinstance(p.get(k), (int, float)) and not isinstance(p.get(k), bool):
                    p[k] = lerp(p[k], v, u) if u < 1 else v
                else: p[k] = v
        return p
    def own_alpha(self, t):
        if t < self.t0: return 0.0
        a = ease((t - self.t0) / 0.35)
        end = self.t_out
        for t0, dur, e in self.events:
            if e.get("hide") and t >= t0: end = t0 if end is None else min(end, t0)
        fade = 0.3
        if self.fade_out is not None and (end is None or self.fade_out < end): end, fade = self.fade_out, 0.15
        if end is not None and t >= end: a *= 1 - clamp((t - end) / fade)
        return a
    def alpha(self, t):
        a = self.own_alpha(t)
        return a * (self.parent.alpha(t) if self.parent is not None else 1.0)
    def dim(self, t):
        dm = self.props(t).get("dim", 1.0)
        return dm * (self.parent.dim(t) if self.parent is not None else 1.0)
    def ancestors(self):
        p, out = self.parent, []
        while p is not None: out.append(p); p = p.parent
        return out

_CACHE = {}
def build(spec, line_starts):
    key = id(spec)
    if key in _CACHE and _CACHE[key][0] == tuple(line_starts): return _CACHE[key][1]
    objs, by_id = [], {}
    for si, sc in enumerate(spec["scenes"]):
        if sc.get("type") != "stage": continue
        ls = line_starts[si]
        clear = sc.get("clear")
        if isinstance(clear, list):
            unknown = [c for c in clear if c not in {ob.id for ob in objs}]
            if unknown: raise KeyError(f"scene {si + 1} clears unknown object ids {unknown} (typo or an object that was split/renamed)")
        for ob in objs:
            if ob.fade_out is None and (clear is True or (isinstance(clear, list) and ob.id in clear)): ob.fade_out = ls - 0.4
        if "focus" in sc:                                                   # dim everything alive except the focused ids (and their parents/children)
            foc = set(sc["focus"])
            for ob in objs:
                if ob.fade_out is not None and ob.fade_out <= ls: continue
                if ob.parent is not None: continue                        # children inherit from their top-level parent
                keep = (not foc) or ob.id in foc or any(c.id in foc for c in _descendants(ob))
                ob.add_event(ls - 0.2, 0.4, {"set": {"dim": 1.0 if keep else 0.3}})
        for o in sc.get("objects", []):
            ob = Obj(spec, si, o, ls); objs.append(ob)
            if o.get("in"):
                par = by_id.get(o["in"])
                if par is None: raise KeyError(f"object {ob.id!r} in scene {si + 1} is inside unknown parent {o['in']!r}")
                ob.parent = par; par.children.append(ob)
            if ob.id: by_id[ob.id] = ob
        for e in sc.get("events", []):
            ob = by_id.get(e["id"])
            if ob is None: raise KeyError(f"event for unknown object id {e['id']!r} in scene {si + 1}")
            ob.add_event(ls + resolve_t(spec, si, e.get("t", 0.0)), e.get("dur", 0.5 if ("set" in e or "move" in e) else 0), e)
    _CACHE[key] = (tuple(line_starts), objs)
    return objs

def _descendants(ob):
    out = []
    for c in ob.children: out.append(c); out += _descendants(c)
    return out

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


# ----------------------------------------------------------------------------- drawing
def _typed(t, t0, txt, cps):
    return int(clamp((t - t0) * cps / max(1, len(txt))) * len(txt))

def draw_obj(d, img, ob, t):
    vis = ob.alpha(t)
    if vis <= 0.003: return
    a = vis * ob.dim(t)
    p = ob.props(t); k = ob.kind
    slide = (1 - ease((t - ob.t0) / 0.35)) * 14 if (t - ob.t0 < 0.35 and ob.parent is None and k not in ("arrow", "packet", "endcard")) else 0
    x = p.get("x", 0); y = p.get("y", 0) + slide

    if k == "panel":
        w, h = p["w"], p["h"]; c = col(p.get("color", "gray")); lvl = int(p.get("level", 0))
        fill = SHADES[min(lvl, 2)]
        rr(d, [x, y, x + w, y + h], fill=A(fill, a * (0.6 if p.get("dashed") else 1)), outline=A(c if p.get("color") else EDGE, a * (1 if p.get("color") else 0.8)),
           width=3 if p.get("color") else 2, radius=22 if lvl == 0 else 16, dashed=p.get("dashed", False))
        if p.get("hl"): rr(d, [x - 7, y - 7, x + w + 7, y + h + 7], outline=A(COL["pink"], a), width=3, radius=26, dashed=True)
        hx, hy, right = x + 22, y + 18, x + w - 20
        if p.get("icon"):
            draw_icon(d, p["icon"], x + 42, y + 42, 34, c if p.get("color") else COL["gray"], a); hx = x + 74
        if p.get("status"):
            draw_icon(d, {"play": "play", "stop": "stop", "check": "check", "cross": "cross"}[p["status"]], right - 18, y + 42, 34,
                      {"play": COL["cyan"], "stop": COL["red"], "check": COL["green"], "cross": COL["red"]}[p["status"]], a); right -= 50
        if isinstance(p.get("value"), str) and p["value"]:
            f = MONOB(26); vw = f.getlength(p["value"]) + 28
            rr(d, [right - vw, y + 22, right, y + 62], fill=A((14, 16, 24), a), outline=A(col(p.get("value_color", c if p.get("color") else "gray")), a), width=2, radius=12)
            d.text((right - vw / 2, y + 42), p["value"], font=f, fill=A(COL["white"], a), anchor="mm"); right -= vw + 14
        if isinstance(p.get("bar"), dict):
            b = p["bar"]; bw = b.get("w", 260); bx = right - bw; segs = b.get("segs", 24); v = clamp(b.get("value", 0)); bc = col(b.get("color", "pink"))
            for i in range(segs):
                on = (i + 0.5) / segs <= v; sx = bx + i * bw / segs
                d.rounded_rectangle([sx + 1.5, y + 28, sx + bw / segs - 1.5, y + 56], radius=2, fill=A(bc, a) if on else A((52, 56, 72), a))
            right = bx - 14
        if p.get("label"):
            maxw = right - hx
            f, lines, lh, ok = fit(p["label"].upper(), LABEL, p.get("lsize", 30), maxw, maxh=None, maxlines=2)
            if not ok: issue(ob, "TEXT_OVERFLOW", f'panel label "{p["label"]}" does not fit in {int(maxw)}px on 2 lines')
            ty = y + 42 - (len(lines) * lh) / 2
            draw_lines(d, hx, ty, lines, f, lh, A(COL["white"], a))
            if len(lines) > 1 and h < 120: issue(ob, "TEXT_OVERFLOW", f'panel label "{p["label"]}" needs 2 lines but the panel is only {h}px tall')
        if p.get("body"):
            cy = y + 84 + (h - 84) / 2; s = min(w * 0.45, (h - 100) * 0.8)
            if s >= 40: draw_icon(d, p["body"], x + w / 2, cy, s, col(p.get("body_color", p.get("color", "white"))), a)
        box(ob, x, y, x + w, y + h)

    elif k in ("title", "brush"):
        bx = draw_parts(d, x, y, p["parts"], LABEL, p.get("size", 52), p.get("maxw", 960), a, ob)[0]
        if p.get("underline", True):
            uw = (bx[2] - bx[0]) * 0.55; d.line([x - uw / 2, bx[3] + 10, x + uw / 2, bx[3] + 10], fill=A(COL["white"], a * 0.85), width=4)
        box(ob, bx[0], bx[1], bx[2], bx[3] + 14)

    elif k == "question":
        maxw = p.get("maxw", 900) - 120
        f, lines, lh, ok = fit("".join(q[0] for q in p["parts"]), LABEL, p.get("size", 34), maxw, maxlines=2)
        if not ok: issue(ob, "TEXT_OVERFLOW", "question pill text does not fit on 2 lines")
        tw = max(f.getlength(l) for l in lines); hh = len(lines) * lh + 30
        x0, x1 = x - (tw + 110) / 2, x + (tw + 110) / 2
        rr(d, [x0, y - hh / 2, x1, y + hh / 2], fill=A((14, 16, 24), a), outline=A(EDGE, a), width=2, radius=int(min(hh / 2, 34)))
        draw_parts(d, x - 24, y - len(lines) * lh / 2 + 2, p["parts"], LABEL, f.size, tw + 2, a, ob)
        d.ellipse([x1 - 62, y - 22, x1 - 18, y + 22], fill=A(COL["pink"], a)); d.text((x1 - 40, y), "?", font=UIB(30), fill=A(COL["white"], a), anchor="mm")
        box(ob, x0, y - hh / 2, x1, y + hh / 2)

    elif k in ("note", "callout"):
        parts = p.get("parts") or [(p.get("text", ""), p.get("color", "white"))]
        bx, s = draw_parts(d, x, y, parts, LABEL, p.get("size", 32), p.get("maxw", 520), a, ob)
        if "tx" in p:
            ar = ease((t - ob.t0 - 0.15) / 0.5)
            sx, sy = x, (bx[1] - 8) if p["ty"] < y else (bx[3] + 8)
            ex, ey = p["tx"], p["ty"]; ctrl = (sx + (ex - sx) * 0.1 + p.get("curve", 60), (sy + ey) / 2)
            pts = bezier((sx, sy), ctrl, (ex, ey)); n = max(2, int(len(pts) * ar))
            d.line(pts[:n], fill=A(COL["white"], a), width=3, joint="curve")
            if ar > 0.97: arrow_head(d, pts[-3], pts[-1], A(COL["white"], a), 16)
        box(ob, bx[0], bx[1], bx[2], bx[3])

    elif k in ("label", "text"):
        fn = FONTS.get(p.get("font", "ui"), UI); size = p.get("size", 30)
        maxw = p.get("maxw", 900)
        f, lines, lh, ok = fit(p["text"], fn, size, maxw, maxlines=p.get("maxlines", 3))
        if not ok: issue(ob, "TEXT_OVERFLOW", f'text "{p["text"]}" does not fit in {maxw}px')
        al = p.get("align", "l"); draw_lines(d, x, y, lines, f, lh, A(col(p.get("color", "white")), a), al)
        tw = max(f.getlength(l) for l in lines); x0 = x - tw / 2 if al == "c" else (x - tw if al == "r" else x)
        box(ob, x0, y, x0 + tw, y + len(lines) * lh)

    elif k in ("pill", "chip"):
        fn = MONOB if p.get("mono") else UIB; size = p.get("size", 28); maxw = p.get("maxw", 900) - 40
        f, lines, lh, ok = fit(p["text"], fn, size, maxw, maxlines=2)
        if not ok: issue(ob, "TEXT_OVERFLOW", f'pill "{p["text"]}" does not fit')
        tw = max(f.getlength(l) for l in lines); hh = len(lines) * lh + 20; c = col(p.get("color", "cyan")); filled = p.get("filled", True)
        x0, x1 = x - tw / 2 - 20, x + tw / 2 + 20
        rr(d, [x0, y - hh / 2, x1, y + hh / 2], fill=A(c, a) if filled else A((14, 16, 24), a), outline=A(c, a), width=2, radius=int(min(hh / 2, 22)))
        draw_lines(d, x, y - len(lines) * lh / 2 + lh * 0.1, lines, f, lh, A(COL["dark"] if filled else c, a), "c")
        box(ob, x0, y - hh / 2, x1, y + hh / 2)

    elif k == "terminal":
        w, h = p["w"], p["h"]; fs = p.get("size", 27)
        rr(d, [x, y, x + w, y + h], fill=A((16, 18, 26), a), outline=A(EDGE, a), width=2, radius=18)
        for i, cc in enumerate(((255, 95, 86), (255, 189, 46), (39, 201, 63))): d.ellipse([x + 22 + i * 26, y + 18, x + 36 + i * 26, y + 32], fill=A(cc, a))
        if p.get("title"):
            f, lines, lh, ok = fit(p["title"], MONO, 22, w - 140, maxlines=1, min_size=20)
            d.text((x + w - 22, y + 25), lines[0], font=f, fill=A(COL["gray"], a), anchor="rm")
        cps = p.get("cps", 40); f = MONO(fs); lh = fs * 1.5; yy = y + 62; clock = ob.t0 + 0.4; maxw = w - 52
        for ln in p["lines"]:
            ln = ln if isinstance(ln, dict) else {"text": ln}; txt = ln["text"]
            typed = ln.get("type", txt.startswith("$"))
            start = max(clock, ln.get("_at", clock))
            if t < start: break
            # wrap with a hanging indent so long commands stay inside the terminal
            wl = []
            lead = len(txt) - len(txt.lstrip(" "))
            cur = " " * lead
            for wd in txt.lstrip(" ").split(" "):
                cand = (cur + " " + wd) if cur.strip() else cur + wd
                if f.getlength(cand) <= maxw - (0 if not wl else f.getlength("  ")): cur = cand
                else:
                    if cur: wl.append(cur)
                    cur = wd
            wl.append(cur)
            n = _typed(t, start, txt, cps) if typed else len(txt)
            if CHECK["on"]: CHECK["typed"][id(ob)] = CHECK["typed"].get(id(ob), 0) + n
            shown_total = n; ystart = yy
            if ln.get("hl"):
                rr(d, [x + 14, yy - 6, x + w - 14, yy + len(wl) * lh - 2], fill=A(col(ln.get("hlcolor", "pink")), 0.25 * a), outline=A(col(ln.get("hlcolor", "pink")), a), width=2, radius=8)
            for j, seg in enumerate(wl):
                if shown_total <= 0: break
                piece = seg[:shown_total]; shown_total -= len(seg) + 1
                xx = x + 26 + (f.getlength("  ") if j else 0)
                c = col(ln.get("color", "white" if typed else "gray"))
                fl = ln.get("flag")
                if fl and fl in piece:
                    pre, post = piece.split(fl, 1)
                    d.text((xx, yy), pre, font=f, fill=A(c, a)); fx = xx + f.getlength(pre); fw = f.getlength(fl)
                    fc = col(ln.get("flagcolor", "pink"))
                    rr(d, [fx - 4, yy - 3, fx + fw + 4, yy + fs + 7], fill=A(fc, a), radius=6)
                    d.text((fx, yy), fl, font=MONOB(fs), fill=A(COL["dark"], a)); d.text((fx + fw + 2, yy), post, font=f, fill=A(c, a))
                else:
                    d.text((xx, yy), piece, font=f, fill=A(c, a))
                if typed and 0 < n < len(txt) and shown_total < 0 and int(t * 3) % 2 == 0:
                    cx_ = xx + f.getlength(piece) + 3; d.rectangle([cx_, yy, cx_ + 13, yy + fs + 3], fill=A(COL["white"], a))
                yy += lh
            if ln.get("check") and n >= len(txt):
                lastw = f.getlength(wl[-1]) + (f.getlength("  ") if len(wl) > 1 else 0)
                draw_icon(d, "check", x + 26 + lastw + 26, yy - lh + fs * 0.55, fs * 0.95, COL["green"], a)
            if yy > y + h - 12: issue(ob, "TEXT_OVERFLOW", f'terminal "{p.get("title", ob.id)}" is too short for its lines (needs about {int(yy - y + 16)}px)')
            clock = start + ((len(txt) / cps) if typed else 0.12) + ln.get("pause", 0.25)
        box(ob, x, y, x + w, y + h)

    elif k == "table":
        w = p["w"]; fs = p.get("size", 24); f = MONO(fs); cols = p["cols"]; rows = p.get("rows", [])
        widths = [max(f.getlength(str(r[i])) for r in [cols] + rows) for i in range(len(cols))]
        need = sum(widths) + 26 * (len(cols) - 1)
        if need > w: issue(ob, "TEXT_OVERFLOW", f"table needs {int(need)}px but has {w}px")
        lh = fs * 1.55; yy = y; hl = p.get("hl")
        for ri, r in enumerate([cols] + rows):
            if hl is not None and ri - 1 == hl:
                rr(d, [x - 8, yy - 5, x + w + 8, yy + lh - 6], fill=A(col(p.get("hlcolor", "pink")), a), radius=6)
            xx = x
            for i, cell in enumerate(r):
                c = COL["dark"] if (hl is not None and ri - 1 == hl) else (COL["gray"] if ri == 0 else col(p.get("color", "white")))
                d.text((xx, yy), str(cell), font=f, fill=A(c, a)); xx += widths[i] + 26
            yy += lh
        box(ob, x, y, x + w, yy)

    elif k == "store":
        w, h = p["w"], p["h"]; c = col(p.get("color", "cyan"))
        rr(d, [x, y, x + w, y + h], fill=A(SHADES[1], a), outline=A(c, a), width=2, radius=16)
        hx = x + 20
        if p.get("icon", "database"): draw_icon(d, p.get("icon", "database"), x + 38, y + 36, 30, c, a); hx = x + 66
        if p.get("label"):
            f, lines, lh, ok = fit(p["label"].upper(), LABEL, 26, w - (hx - x) - 20, maxlines=1)
            if not ok: issue(ob, "TEXT_OVERFLOW", f'store label "{p["label"]}" does not fit')
            d.text((hx, y + 36), lines[0], font=f, fill=A(COL["white"], a), anchor="lm")
        fs = p.get("size", 26); f = MONO(fs); yy = y + 72; hl = p.get("hl")
        for ri, (kk, vv) in enumerate(p.get("rows", [])):
            if yy + fs * 1.6 > y + h: issue(ob, "TEXT_OVERFLOW", "store has more rows than fit"); break
            if hl is not None and ri == hl: rr(d, [x + 12, yy - 6, x + w - 12, yy + fs + 10], fill=A(c, 0.22 * a), outline=A(c, a), width=2, radius=8)
            kw = f.getlength(str(kk)); vw = f.getlength(str(vv))
            if kw + vw + 60 > w: issue(ob, "TEXT_OVERFLOW", f'store row "{kk} {vv}" is wider than the store')
            d.text((x + 24, yy), str(kk), font=f, fill=A(COL["gray"], a))
            rr(d, [x + w - 34 - vw, yy - 4, x + w - 20, yy + fs + 6], fill=A(col(p.get("value_color", "amber")), a), radius=8)
            d.text((x + w - 27 - vw, yy), str(vv), font=MONOB(fs), fill=A(COL["dark"], a))
            yy += fs * 1.75
        box(ob, x, y, x + w, y + h)

    elif k == "browser":
        w, h = p["w"], p["h"]
        rr(d, [x, y, x + w, y + h], fill=A((30, 33, 40), a), radius=16)
        tabw = min(240, w * 0.45); rr(d, [x + 14, y + 10, x + 14 + tabw, y + 50], fill=A((44, 48, 58), a), radius=10)
        d.text((x + 30, y + 30), p.get("tab", "New Tab"), font=UI(24), fill=A(COL["white"], a), anchor="lm")
        d.rectangle([x, y + 50, x + w, y + 112], fill=A((44, 48, 58), a))
        for i, ch in enumerate("<>"): d.text((x + 30 + i * 34, y + 81), "←→"[i], font=UI(26), fill=A(COL["gray"], a), anchor="mm")
        rr(d, [x + 100, y + 60, x + w - 16, y + 102], fill=A((22, 24, 30), a), radius=20)
        sch = p.get("scheme", ""); url = p.get("url", "")
        n = _typed(t, ob.t0 + 0.3, url, p.get("cps", 18)) if p.get("type", True) else len(url)
        if CHECK["on"]: CHECK["typed"][id(ob)] = n
        f = UI(26); xx = x + 120
        if sch: d.text((xx, y + 81), sch, font=f, fill=A(COL["amber"], a), anchor="lm"); xx += f.getlength(sch) + 6
        d.text((xx, y + 81), url[:n], font=f, fill=A(COL["white"], a), anchor="lm")
        if f.getlength(sch + url) + 40 > w - 116: issue(ob, "TEXT_OVERFLOW", "browser URL too long for the URL bar")
        box(ob, x, y, x + w, y + h)

    elif k == "server":
        w, h = p["w"], p["h"]; c = col(p.get("color", "cyan"))
        rr(d, [x, y, x + w, y + h], fill=A(SHADES[1], a), outline=A(c, a * 0.9), width=2, radius=16)
        n = 3; top = y + 66 if p.get("label") else y + 16; rh = (y + h - 16 - top) / n
        for i in range(n):
            ry = top + i * rh
            rr(d, [x + 18, ry + 4, x + w - 18, ry + rh - 6], fill=A((24, 26, 34), a), radius=8)
            for j in range(5): d.line([x + 36 + j * 12, ry + rh * 0.3, x + 36 + j * 12, ry + rh * 0.7], fill=A(COL["gray"], a * 0.6), width=3)
            d.ellipse([x + w - 56, ry + rh / 2 - 5, x + w - 46, ry + rh / 2 + 5], fill=A(COL["green"], a))
            d.ellipse([x + w - 40, ry + rh / 2 - 5, x + w - 30, ry + rh / 2 + 5], fill=A(COL["white"], a))
        if p.get("label"):
            f, lines, lh, ok = fit(p["label"].upper(), LABEL, 26, w - 36, maxlines=1)
            if not ok: issue(ob, "TEXT_OVERFLOW", f'server label "{p["label"]}" does not fit')
            d.text((x + 20, y + 34), lines[0], font=f, fill=A(COL["white"], a), anchor="lm")
        box(ob, x, y, x + w, y + h)

    elif k in ("bar", "meter"):
        w, h = p["w"], p.get("h", 34); segs = p.get("segs", 36); v = clamp(p.get("value", 0)); c = col(p.get("color", "pink"))
        top = y
        if p.get("label"):
            f, lines, lh, ok = fit(p["label"].upper(), LABEL, 24, w, maxlines=1)
            if not ok: issue(ob, "TEXT_OVERFLOW", f'bar label "{p["label"]}" does not fit')
            d.text((x, y), lines[0], font=f, fill=A(COL["white"], a)); top = y + 38
        for i in range(segs):
            on = (i + 0.5) / segs <= v; sx = x + i * w / segs
            d.rounded_rectangle([sx + 1.5, top, sx + w / segs - 1.5, top + h], radius=3, fill=A(c, a) if on else A((44, 48, 64), a))
        if p.get("right"):
            f = MONOB(24); tw = f.getlength(p["right"]) + 26; mid = x + w / 2
            rr(d, [mid - tw / 2, top + h / 2 - 19, mid + tw / 2, top + h / 2 + 19], fill=A((14, 16, 24), a), outline=A(c, a), width=2, radius=12)
            d.text((mid, top + h / 2), p["right"], font=f, fill=A(COL["white"], a), anchor="mm")
            if tw > w: issue(ob, "TEXT_OVERFLOW", "bar value pill wider than the bar")
        box(ob, x, y, x + w, top + h)

    elif k == "grid":
        w, h, cols, rows = p["w"], p["h"], p["cols"], p["rows"]; n = int(round(p.get("n", cols * rows))); c = col(p.get("color", "pink"))
        cw, ch = w / cols, h / rows; top = y
        if p.get("label"):
            f, lines, lh, ok = fit(p["label"].upper(), LABEL, 24, w, maxlines=1)
            if not ok: issue(ob, "TEXT_OVERFLOW", "grid label does not fit")
            d.text((x, y), lines[0], font=f, fill=A(COL["white"], a)); top = y + 38
        for i in range(cols * rows):
            cx, cy = x + (i % cols) * cw, top + (i // cols) * ch
            d.rounded_rectangle([cx + 2, cy + 2, cx + cw - 2, cy + ch - 2], radius=3, fill=A(c, a) if i < n else A((44, 48, 64), a))
        box(ob, x, y, x + w, top + h)

    elif k == "seq":
        w, h = p["w"], p["h"]; c = col(p.get("color", "cyan")); lx, rx = x + 70, x + w - 70
        for X, lab in ((lx, p.get("left", "")), (rx, p.get("right", ""))):
            f = LABEL(24); d.text((X, y), lab.upper(), font=f, fill=A(COL["white"], a), anchor="ma")
            yy = y + 40
            while yy < y + h: d.line([X, yy, X, min(yy + 12, y + h)], fill=A(c, a * 0.8), width=3); yy += 22
        my = y + 80; gap = p.get("gap", 70)
        for m in p.get("msgs", []):
            if t < m["_at"]: break
            u = ease((t - m["_at"]) / 0.5); mc = col(m.get("color", p.get("color", "cyan")))
            x0_, x1_ = (lx, rx) if m.get("dir", ">") == ">" else (rx, lx)
            ex = lerp(x0_, x1_, u)
            d.line([x0_, my, ex, my + 14 * u], fill=A(mc, a), width=4)
            if u > 0.97: arrow_head(d, (x0_, my), (x1_, my + 14), A(mc, a), 18)
            f, lines, lh, ok = fit(m["text"], MONOB, 24, (rx - lx) - 40, maxlines=1)
            if not ok: issue(ob, "TEXT_OVERFLOW", f'sequence message "{m["text"]}" too long')
            tw = f.getlength(lines[0]) + 26; mx = (lx + rx) / 2
            rr(d, [mx - tw / 2, my - 44, mx + tw / 2, my - 10], fill=A(mc, a * u), radius=10)
            d.text((mx, my - 27), lines[0], font=f, fill=A(COL["dark"], a * u), anchor="mm")
            my += gap
        if my - gap + 30 > y + h: issue(ob, "TEXT_OVERFLOW", "sequence diagram is too short for its messages")
        box(ob, x, y, x + w, y + h)

    elif k == "arrow":
        pts = [tuple(q) for q in p["points"]]; prog = ease((t - ob.t0) / p.get("dur", 0.6)); c = col(p.get("color", "gray"))
        if p.get("curve") and len(pts) == 2:
            (x0_, y0_), (x1_, y1_) = pts; pts = bezier(pts[0], ((x0_ + x1_) / 2 + p["curve"], (y0_ + y1_) / 2), pts[1])
        n = max(2, int(len(pts) * prog)) if len(pts) > 2 else 2
        if len(pts) == 2:
            e = (lerp(pts[0][0], pts[1][0], prog), lerp(pts[0][1], pts[1][1], prog)); seg = [pts[0], e]
        else: seg = pts[:n]
        if p.get("dashed"):
            for i in range(len(seg) - 1):
                (ax, ay), (bx_, by_) = seg[i], seg[i + 1]; L_ = math.dist(seg[i], seg[i + 1]); kk = 0.0
                while kk < L_:
                    u0, u1 = kk / L_, min(1, (kk + 12) / L_); d.line([lerp(ax, bx_, u0), lerp(ay, by_, u0), lerp(ax, bx_, u1), lerp(ay, by_, u1)], fill=A(c, a), width=p.get("width", 4)); kk += 22
        else: d.line(seg, fill=A(c, a), width=p.get("width", 4), joint="curve")
        if p.get("head", True) and prog > 0.97: arrow_head(d, pts[-2], pts[-1], A(c, a), 18)

    elif k == "packet":
        path = [tuple(q) for q in p["path"]]; prog = clamp((t - ob.t0) / p.get("dur", 1.0))
        total = sum(math.dist(path[i], path[i + 1]) for i in range(len(path) - 1)); goal = total * ease(prog); acc = 0; pos = path[-1]
        for i in range(len(path) - 1):
            sg = math.dist(path[i], path[i + 1])
            if acc + sg >= goal:
                u = (goal - acc) / sg if sg else 0; pos = (lerp(path[i][0], path[i + 1][0], u), lerp(path[i][1], path[i + 1][1], u)); break
            acc += sg
        if prog >= 1 and not p.get("hold", True): return
        f = MONOB(p.get("size", 24)); tw = max(p.get("w", 0), f.getlength(p.get("text", "")) + 30); hh = p.get("h", 44); c = col(p.get("color", "cyan"))
        rr(d, [pos[0] - tw / 2, pos[1] - hh / 2, pos[0] + tw / 2, pos[1] + hh / 2], fill=A(c, a), radius=12)
        if p.get("text"): d.text(pos, p["text"], font=f, fill=A(COL["dark"], a), anchor="mm")

    elif k == "dots":
        n = p.get("n", 4); act = p.get("active", 0); cs = [col(c) for c in p.get("colors", ["amber", "cyan", "pink", "purple", "mint"])]
        sp = p.get("spacing", 150); labels = p.get("labels", [])
        for i in range(n):
            cx = x + (i - (n - 1) / 2) * sp; on = i <= round(act); cur = i == round(act)
            if i < n - 1: d.line([(cx + 34, y), (cx + sp - 34, y)], fill=A(EDGE, a), width=4)
            r = 34 if cur else 28
            d.ellipse([cx - r, y - r, cx + r, y + r], fill=A(cs[i % len(cs)], a) if on else A((44, 48, 64), a))
            d.text((cx, y), str(i + 1), font=UIB(30), fill=A(COL["dark"] if on else COL["gray"], a), anchor="mm")
            if i < len(labels):
                f, lines, lh, ok = fit(labels[i].upper(), LABEL, 22, sp - 12, maxlines=2)
                if not ok: issue(ob, "TEXT_OVERFLOW", f'dot label "{labels[i]}" too long')
                draw_lines(d, cx, y + 48, lines, f, lh, A(cs[i % len(cs)] if on else COL["gray"], a), "c")
        if p.get("caption"):
            draw_parts(d, x, y + (110 if labels else 60), [(p["caption"], "white")] if isinstance(p["caption"], str) else p["caption"], LABEL, 32, 900, a, ob)
        nl = max([len(fit(l.upper(), LABEL, 22, sp - 12, maxlines=2)[1]) for l in labels] or [0])
        bottom = y + 48 + nl * 27.5 + 4 if labels else y + 36
        if p.get("caption"): bottom = y + (110 if labels else 60) + 46
        box(ob, x - (n - 1) / 2 * sp - 40, y - 36, x + (n - 1) / 2 * sp + 40, bottom)

    elif k == "icon":
        s = p.get("size", 80); draw_icon(d, p["name"], x, y, s, col(p.get("color", "white")), a); box(ob, x - s / 2, y - s / 2, x + s / 2, y + s / 2)

    elif k == "badge":
        s = p.get("size", 44); c = COL["green"] if p.get("name", "check") == "check" else COL["red"]
        d.ellipse([x - s / 2, y - s / 2, x + s / 2, y + s / 2], fill=A(c, a)); draw_icon(d, "check" if p.get("name", "check") == "check" else "cross", x, y, s * 0.62, COL["white"], a)
        box(ob, x - s / 2, y - s / 2, x + s / 2, y + s / 2)

    elif k in ("endcard", "follow"):
        u = ease((t - ob.t0) / 0.5)
        if u > 0.01:
            blurred = img.filter(ImageFilter.GaussianBlur(14 * u)); dark = Image.new("RGB", img.size, (6, 7, 12))
            img.paste(Image.blend(blurred, dark, 0.45 * u * vis))
        cx, cy = W / 2, p.get("y", 820)
        rr(d, [cx - 300, cy - 120, cx + 300, cy + 120], fill=A((24, 26, 34), a), outline=A(EDGE, a), width=2, radius=28)
        d.text((cx, cy - 52), p.get("text", "@techinabite"), font=UIB(40), fill=A(COL["white"], a), anchor="mm")
        press = clamp((t - ob.t0 - 1.5) / 0.25)
        rr(d, [cx - 150, cy + 10, cx + 150, cy + 76], fill=A(COL["amber"] if press > 0.5 else (0, 150, 255), a), radius=30)
        d.text((cx, cy + 43), "Following" if press > 0.5 else "+ Follow", font=UIB(32), fill=A(COL["dark"] if press > 0.5 else COL["white"], a), anchor="mm")
        mx = lerp(cx + 240, cx + 70, ease((t - ob.t0 - 0.6) / 0.8)); my = lerp(cy + 200, cy + 52, ease((t - ob.t0 - 0.6) / 0.8))
        d.polygon([(mx, my), (mx, my + 40), (mx + 10, my + 31), (mx + 20, my + 47), (mx + 27, my + 44), (mx + 17, my + 28), (mx + 30, my + 27)], fill=A(COL["white"], a), outline=A((0, 0, 0), a))
        box(ob, cx - 300, cy - 120, cx + 300, cy + 120)

def render(d, img, t, spec, line_starts):
    """Draw every alive stage object at absolute time t, in spec order (later = on top)."""
    if CHECK["on"]: CHECK["boxes"] = {}; CHECK["typed"] = {}
    for ob in build(spec, line_starts):
        draw_obj(d, img, ob, t)


# ----------------------------------------------------------------------------- layout check (used by check_spec.py)
OVERLAY_KINDS = ("arrow", "packet", "endcard", "follow")

def _inside(a, b, tol=2):
    return a[0] >= b[0] - tol and a[1] >= b[1] - tol and a[2] <= b[2] + tol and a[3] <= b[3] + tol

def _overlap(a, b, pad=4):
    return not (a[2] <= b[0] + pad or b[2] <= a[0] + pad or a[3] <= b[1] + pad or b[3] <= a[1] + pad)

def layout_check(spec, line_starts, dur, mascot_box=None, step=0.25, draw_cls=None):
    """Render the stage offscreen every `step` seconds and collect layout problems. Returns a list of (level, code, message)."""
    objs = build(spec, line_starts)
    out, seen = [], set()
    def add(level, code, msg, key=None):
        k = key or (code, msg)
        if k not in seen: seen.add(k); out.append((level, code, msg))
    CHECK["on"] = True
    try:
        img = Image.new("RGB", (W, H), (13, 16, 28))
        d = draw_cls(img) if draw_cls else ImageDraw.Draw(img, "RGBA")
        last_change, prev_sig = 0.0, None
        t = 0.0
        while t < dur:
            CHECK["issues"] = []
            render(d, img, t, spec, line_starts)
            for code, oid, msg in CHECK["issues"]: add("FAIL", code, f"{oid}: {msg} (at {t:.1f}s)", (code, oid, msg))
            vis = [ob for ob in objs if ob.own_alpha(t) > 0.9 and ob.alpha(t) > 0.9 and id(ob) in CHECK["boxes"]]
            for ob in vis:
                b = CHECK["boxes"][id(ob)]
                if ob.parent is not None and id(ob.parent) in CHECK["boxes"] and not _inside(b, CHECK["boxes"][id(ob.parent)]):
                    add("FAIL", "OUTSIDE_PARENT", f"{ob.id} sticks out of its box {ob.parent.id} at {t:.1f}s", ("OP", ob.id))
                if ob.kind not in OVERLAY_KINDS and not (b[0] >= ZONE[0] and b[1] >= ZONE[1] and b[2] <= ZONE[2] and b[3] <= ZONE[3]):
                    add("FAIL", "OUT_OF_ZONE", f"{ob.id} ({[int(v) for v in b]}) leaves the content zone {ZONE} at {t:.1f}s", ("OZ", ob.id))
                if mascot_box and ob.kind not in OVERLAY_KINDS and _overlap(b, mascot_box, 0):
                    add("FAIL", "MASCOT_OVERLAP", f"{ob.id} is under the mascot at {t:.1f}s", ("MO", ob.id))
            for i, a_ in enumerate(vis):
                if a_.kind in OVERLAY_KINDS or a_.o.get("overlay"): continue
                for b_ in vis[i + 1:]:
                    if b_.kind in OVERLAY_KINDS or b_.o.get("overlay"): continue
                    if a_ in b_.ancestors() or b_ in a_.ancestors(): continue
                    if _overlap(CHECK["boxes"][id(a_)], CHECK["boxes"][id(b_)]):
                        add("FAIL", "OVERLAP", f"{a_.id} and {b_.id} overlap at {t:.1f}s (nest one inside the other with \"in\", or move them apart)", ("OV", a_.id, b_.id))
            # visible change rhythm (reference: something changes every 2-3 s)
            def _motion(ob):
                if ob.kind == "packet": return round(clamp((t - ob.t0) / ob.o.get("dur", 1.0)), 1)
                if ob.kind in ("terminal", "browser"): return CHECK["typed"].get(id(ob), 0)
                if ob.kind == "seq": return sum(1 for m in ob.o.get("msgs", []) if t >= m["_at"])
                return 0
            sig = tuple((id(ob), round(ob.alpha(t), 1), round(ob.dim(t), 1), _motion(ob), str(sorted((k, str(v)) for k, v in ob.props(t).items() if k not in ("lines",)))) for ob in vis)
            if sig != prev_sig: last_change = t
            elif t - last_change > 4.0 and vis: add("WARN", "STATIC", f"nothing on the stage changes between {last_change:.1f}s and {t:.1f}s: add a visible state change", ("ST", round(last_change, 1)))
            prev_sig = sig
            t += step
    finally:
        CHECK["on"] = False
    # empty boxes and too much text (static properties)
    for ob in objs:
        o = ob.o
        if ob.kind == "panel" and not ob.children and not o.get("body") and not o.get("compact") and o.get("h", 0) > 100:
            add("FAIL", "EMPTY_BOX", f'panel {ob.id} ("{o.get("label", "")}") is {o.get("h")}px tall but has nothing inside: put objects in it ("in": "{ob.id}"), give it a "body" illustration, or make it a compact header strip')
        for key, txt in obj_strings(o):
            nw = len([w for w in txt.split() if any(ch.isalnum() for ch in w)])
            if key == "object" and nw > 6:
                add("FAIL", "TOO_MUCH_TEXT", f'{ob.id}: object label "{txt}" has {nw} words; labels are 1-4 words (the voice explains)')
            if key == "headline" and nw > 9:
                add("FAIL", "TOO_MUCH_TEXT", f'{ob.id}: headline "{txt}" has {nw} words; keep titles and questions short')
    return out

def visible_strings(spec, line_starts, si, bounds):
    """Strings of every stage object visible in the middle of scene si (persisting objects included) - the frame a viewer actually sees."""
    objs = build(spec, line_starts); t = (bounds[si][0] + bounds[si][1]) / 2; out = []
    for ob in objs:
        if ob.alpha(t) > 0.5 and ob.dim(t) > 0.5: out += obj_strings(ob.o)
    return out

