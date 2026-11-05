#!/usr/bin/env python3
"""Render an Instagram carousel post (5-7 slides, 1080x1350, 4:5 portrait) from a spec.

Usage: python3 carousel.py specs/postNN_slug.py out/postNN          -> out/postNN_s01.png ... plus out/postNN_contact.png and JPG copies
The spec is a Python file with SPEC = {"tag": "@TECHINABITE", "topic": "...", "slides": [ {...}, ... ]}. Slide types:
  cover     kicker, title: [(text, accent_bool), ...], sub, chips: [str, ...]
  text      label, title, bullets: [str with optional **bold**], callout
  cards     label, title, cards: [{"label","head","text"}] (2 to 4), highlight: index
  flow      label, title, nodes: [{"head","text"}] (2 to 4, drawn top to bottom with arrows), callout
  compare   label, title, left/right: {"head","points":[...]}, callout
  detail    label, title, code: [str lines, drawn in a monospace panel], notes: [str], callout
  takeaway  label, title, points: [str], share, closer (always "Follow for one tech topic a day.")
Every slide has "level": 1 (the big picture), 2 (how it works) or 3 (deep dive), shown as a pill so the post visibly goes from high level to deep dive.
Optional per slide: "mascot": {"x","y","size"} or False. Cover and takeaway show the mascot by default.
Every drawn text box is recorded; the renderer raises if text leaves the safe area, overflows the content area, or the mascot covers text.
"""
import os, sys, importlib.util
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1080, 1350
HERE = os.path.dirname(os.path.abspath(__file__))
F = os.path.join(HERE, "fonts") + os.sep
BOLD = lambda s: ImageFont.truetype(F + "InterDisplay-Bold.otf", s)
MED = lambda s: ImageFont.truetype(F + "Inter-Medium.otf", s)
REG = lambda s: ImageFont.truetype(F + "Inter-Regular.otf", s)
MONO = lambda s: ImageFont.truetype(F + "DejaVuSansMono.ttf", s)
MONOB = lambda s: ImageFont.truetype(F + "DejaVuSansMono-Bold.ttf", s)

BG, BG2 = (13, 16, 28), (20, 24, 42)
PANEL, PANEL2 = (25, 30, 50), (33, 39, 64)
EDGE = (52, 60, 88)
TEXT = (240, 243, 248)
MUTED = (146, 156, 178)
AMBER = (255, 190, 60)
MINT = (95, 220, 190)
LEVELS = {1: ("LEVEL 1  ·  THE BIG PICTURE", MINT), 2: ("LEVEL 2  ·  HOW IT WORKS", AMBER), 3: ("LEVEL 3  ·  DEEP DIVE", (255, 120, 110))}
CLOSER = "Follow for one tech topic a day."
X0, X1 = 80, 1000            # content columns (safe margins 80 px)
Y0, Y1 = 215, 1215           # content area (below the level pill, above the progress bar)

class Canvas:
    def __init__(self, n, total, slide):
        self.img = Image.new("RGB", (W, H), BG)
        px = self.img.load()
        for y in range(H):                        # soft vertical gradient
            c = tuple(int(BG[i] + (BG2[i] - BG[i]) * y / H) for i in range(3))
            for x in range(0, W): px[x, y] = c
        self.d = ImageDraw.Draw(self.img, "RGBA")
        self.n, self.total, self.slide = n, total, slide
        self.boxes = []                           # (x0, y0, x1, y1, text) of every text drawn in the content area
        self.errors = []
        self.ymax = Y0
    def text(self, xy, s, font, fill, anchor="la", record=True):
        self.d.text(xy, s, font=font, fill=fill, anchor=anchor)
        b = self.d.textbbox(xy, s, font=font, anchor=anchor)
        if record:
            self.boxes.append((*b, s))
            if b[0] < 60 or b[2] > W - 60: self.errors.append(f"text leaves the safe area: {s[:40]!r}")
            self.ymax = max(self.ymax, b[3])
        return b
    def wrap(self, s, font, maxw):
        words, lines, cur = s.split(), [], ""
        for w in words:
            t = (cur + " " + w).strip()
            if self.d.textlength(t, font=font) <= maxw: cur = t
            else: lines.append(cur); cur = w
        lines.append(cur)
        return lines
    def para(self, x, y, s, font, fill, maxw, lh=None):
        lh = lh or int(font.size * 1.3)
        for ln in self.wrap(s, font, maxw):
            self.text((x, y), ln, font, fill); y += lh
        return y
    def rich(self, x, y, s, size, maxw, fill=TEXT, bold_fill=AMBER, lh=None):
        """Paragraph with **bold** segments (bold + amber)."""
        lh = lh or int(size * 1.36)
        toks = []                                  # (word, bold, glued_to_previous)
        for i, part in enumerate(s.split("**")):
            ws = part.split()
            for j, w in enumerate(ws):
                glue = (j == 0 and i > 0 and not part.startswith(" ") and bool(toks))
                toks.append((w, i % 2 == 1, glue))
        lines, cur, curw = [], [], 0
        sp = self.d.textlength(" ", font=MED(size))
        for w, b, g in toks:
            f = BOLD(size) if b else MED(size)
            ww = self.d.textlength(w, font=f)
            gap = 0 if (g or not cur) else sp
            if cur and not g and curw + gap + ww > maxw: lines.append(cur); cur, curw, gap = [], 0, 0
            cur.append((w, b, ww, gap)); curw += ww + gap
        lines.append(cur)
        for ln in lines:
            cx = x
            for w, b, ww, gap in ln:
                cx += gap
                self.text((cx, y), w, BOLD(size) if b else MED(size), bold_fill if b else fill); cx += ww
            y += lh
        return y
    def box(self, x0, y0, x1, y1, fill=PANEL, outline=EDGE, width=3, radius=28):
        self.d.rounded_rectangle([x0, y0, x1, y1], radius=radius, fill=fill, outline=outline, width=width)
        self.ymax = max(self.ymax, y1)

def title_block(c, s, y=None, size=70, maxw=920):
    y = y or Y0 + 70
    f = BOLD(size)
    lines = c.wrap(s, f, maxw)
    while len(lines) > 3 and size > 52:
        size -= 4; f = BOLD(size); lines = c.wrap(s, f, maxw)
    for ln in lines:
        c.text((X0, y), ln, f, TEXT); y += int(size * 1.12)
    c.d.rounded_rectangle([X0, y + 12, X0 + 90, y + 17], radius=3, fill=AMBER)
    return y + 56

def label(c, s, y=Y0 + 6):
    x = X0
    for ch in s:                                  # letter-spaced mono label
        c.text((x, y), ch, MONOB(26), AMBER); x += c.d.textlength(ch, font=MONOB(26)) + 7

def callout(c, y, s, size=34):
    lines = c.wrap(s, BOLD(size), 820)
    h = 40 + int(size * 1.36) * len(lines)
    c.box(X0, y, X1, y + h, fill=(60, 44, 36), outline=AMBER, width=3, radius=24)
    c.d.rounded_rectangle([X0, y, X0 + 8, y + h], radius=4, fill=AMBER)
    yy = y + 20
    for ln in lines:
        c.text((X0 + 36, yy), ln, BOLD(size), TEXT); yy += int(size * 1.36)
    return y + h + 24

def chrome(c):
    d, s = c.d, c.slide
    tag = c.slide.get("_tag", "@TECHINABITE")
    x = 80
    for ch in tag:
        c.text((x, 84), ch, MED(24), MUTED, record=False); x += d.textlength(ch, font=MED(24)) + 6
    c.text((W - 80, 84), f"{c.n:02d} / {c.total:02d}", MONOB(26), MUTED, anchor="ra", record=False)
    lab, col = LEVELS[s.get("level", 1)]
    w = d.textlength(lab, font=MONOB(22)) + 44
    d.rounded_rectangle([80, 130, 80 + w, 174], radius=22, fill=(col[0] // 6, col[1] // 6, col[2] // 6), outline=col, width=2)
    c.text((102, 152), lab, MONOB(22), col, anchor="lm", record=False)
    # progress bar + swipe hint
    d.rounded_rectangle([80, 1262, 1000, 1268], radius=3, fill=EDGE)
    d.rounded_rectangle([80, 1262, 80 + 920 * c.n / c.total, 1268], radius=3, fill=AMBER)
    c.text((80, 1300), c.slide.get("_topic", "").upper()[:48], MONOB(20), MUTED, record=False)
    hint = "SAVE  ·  SHARE" if c.n == c.total else "SWIPE  >"
    c.text((W - 80, 1300), hint, MONOB(20), AMBER, anchor="ra", record=False)

# ----- slide types -----
def s_cover(c, s):
    y = 300
    c.text((X0, y), "TECH IN A BITE  ·  POST", MONOB(28), AMBER); y += 90
    parts = s["title"]
    size = 150
    while size > 70 and max(c.d.textlength(t, font=BOLD(size)) for t, _ in parts) > 920: size -= 6
    for t, acc in parts:
        c.text((X0, y), t, BOLD(size), AMBER if acc else TEXT); y += int(size * 1.04)
    y += 48
    for ln in c.wrap(s["sub"], MED(40), 880):
        c.text((X0, y), ln, MED(40), MUTED); y += 54
    y += 36
    x = X0
    for chip in s.get("chips", []):
        w = c.d.textlength(chip, font=MONOB(24)) + 40
        c.d.rounded_rectangle([x, y, x + w, y + 54], radius=27, outline=AMBER, width=2)
        c.text((x + 20, y + 27), chip, MONOB(24), AMBER, anchor="lm"); x += w + 16
    c.ymax = max(c.ymax, y + 54)

def s_text(c, s):
    label(c, s["label"]); y = title_block(c, s["title"])
    for b in s["bullets"]:
        c.d.ellipse([X0, y + 14, X0 + 16, y + 30], fill=AMBER)
        y = c.rich(X0 + 44, y, b, 38, 840) + 22
    if s.get("callout"): callout(c, max(y + 10, 930 if len(s["bullets"]) < 4 else y + 10), s["callout"])

def s_cards(c, s):
    label(c, s["label"]); y = title_block(c, s["title"], size=64)
    cards = s["cards"]; hl = s.get("highlight", -1)
    cols = 2; cw = (X1 - X0 - 24) // 2
    rows = (len(cards) + 1) // 2
    ch = 300 if rows == 2 else 400
    for i, cd in enumerate(cards):
        cx = X0 + (i % cols) * (cw + 24); cy = y + (i // cols) * (ch + 24)
        c.box(cx, cy, cx + cw, cy + ch, fill=PANEL2 if i == hl else PANEL, outline=AMBER if i == hl else EDGE, width=4 if i == hl else 3)
        c.text((cx + 28, cy + 26), cd["label"], MONOB(22), AMBER if i == hl else MUTED)
        yy = c.para(cx + 28, cy + 70, cd["head"], BOLD(40), TEXT, cw - 56, 48)
        c.para(cx + 28, yy + 6, cd["text"], MED(28), MUTED, cw - 56, 38)
    y += rows * (ch + 24)
    if s.get("callout"): callout(c, y, s["callout"])

def s_flow(c, s):
    label(c, s["label"]); y = title_block(c, s["title"], size=64)
    nodes = s["nodes"]; hl = s.get("highlight", -1)
    nh = 150 if len(nodes) <= 3 else 130
    for i, nd in enumerate(nodes):
        c.box(X0, y, X1, y + nh, fill=PANEL2 if i == hl else PANEL, outline=MINT if i == hl else EDGE, width=4 if i == hl else 3)
        c.d.ellipse([X0 + 26, y + nh / 2 - 30, X0 + 86, y + nh / 2 + 30], fill=MINT if i == hl else EDGE)
        c.text((X0 + 56, y + nh / 2), str(i + 1), BOLD(34), (10, 14, 24) if i == hl else TEXT, anchor="mm", record=False)
        c.text((X0 + 110, y + 30), nd["head"], BOLD(36), TEXT)
        c.para(X0 + 110, y + 30 + 46, nd["text"], MED(27), MUTED, 800, 36)
        y += nh
        if i < len(nodes) - 1:
            c.d.polygon([(W / 2 - 18, y + 4), (W / 2 + 18, y + 4), (W / 2, y + 28)], fill=AMBER); y += 34
    y += 24
    if s.get("callout"): callout(c, y, s["callout"])

def s_compare(c, s):
    label(c, s["label"]); y = title_block(c, s["title"], size=64)
    cw = (X1 - X0 - 24) // 2
    bottoms = []
    for side, (x, col) in enumerate(((X0, MUTED), (X0 + cw + 24, MINT))):
        card = s["left"] if side == 0 else s["right"]
        yy = y + 26
        h = 96 + sum(len(c.wrap(p, MED(30), cw - 56)) * 40 + 20 for p in card["points"])
        c.box(x, y, x + cw, y + h + 30, fill=PANEL, outline=col, width=4)
        for ln in c.wrap(card["head"], BOLD(38), cw - 56):
            c.text((x + 28, yy), ln, BOLD(38), col); yy += 46
        yy += 14
        for p in card["points"]:
            yy = c.para(x + 28, yy, p, MED(30), TEXT, cw - 56, 40) + 20
        bottoms.append(y + h + 30)
    y = max(bottoms) + 30
    if s.get("callout"): callout(c, y, s["callout"])

def s_detail(c, s):
    label(c, s["label"]); y = title_block(c, s["title"], size=62)
    lines = s["code"]; lh = 44
    h = 40 + lh * len(lines)
    c.box(X0, y, X1, y + h, fill=(10, 12, 22), outline=EDGE, width=3, radius=22)
    for i, ln in enumerate(lines):
        col = MUTED if ln.strip().startswith(("#", "//", "--")) else (MINT if ln.strip().startswith(("-", ">")) else TEXT)
        c.text((X0 + 30, y + 24 + i * lh), ln, MONO(28), col)
    y += h + 26
    for nt in s.get("notes", []):
        c.d.ellipse([X0, y + 12, X0 + 14, y + 26], fill=AMBER)
        y = c.rich(X0 + 40, y, nt, 32, 860) + 14
    if s.get("callout"): callout(c, y + 10, s["callout"])

def s_takeaway(c, s):
    label(c, s["label"]); y = title_block(c, s["title"], size=66)
    for p in s["points"]:
        c.d.ellipse([X0, y + 14, X0 + 16, y + 30], fill=MINT)
        y = c.rich(X0 + 44, y, p, 36, 800, bold_fill=MINT) + 18
    y += 14
    if s.get("share"): y = callout(c, y, s["share"], size=32)
    y += 10
    c.text((X0, y + 70), "Follow", BOLD(96), AMBER); c.text((X0, y + 170), "for one tech topic a day.", BOLD(48), TEXT)

TYPES = {"cover": s_cover, "text": s_text, "cards": s_cards, "flow": s_flow, "compare": s_compare, "detail": s_detail, "takeaway": s_takeaway}

def mascot(c, cfg):
    m = Image.open(os.path.join(HERE, "assets", "mascot.png")).convert("RGBA")
    size = cfg["size"]; m = m.resize((size, size), Image.LANCZOS)
    glow = Image.new("RGBA", (int(size * 1.6),) * 2, (0, 0, 0, 0))
    ImageDraw.Draw(glow).ellipse((size * 0.2, size * 0.2, size * 1.4, size * 1.4), fill=(110, 90, 255, 60))
    glow = glow.filter(ImageFilter.GaussianBlur(size * 0.12))
    c.img.paste(glow, (int(cfg["x"] - glow.width / 2), int(cfg["y"] - glow.height / 2)), glow)
    c.img.paste(m, (int(cfg["x"] - size / 2), int(cfg["y"] - size / 2)), m)
    r = size / 2
    box = (cfg["x"] - r, cfg["y"] - r, cfg["x"] + r, cfg["y"] + r)
    for b in c.boxes:
        if b[0] < box[2] and b[2] > box[0] and b[1] < box[3] and b[3] > box[1]:
            c.errors.append(f"mascot covers text {b[4][:40]!r}")
    if box[0] < 40 or box[2] > W - 40 or box[1] < 190 or box[3] > 1250: c.errors.append("mascot outside the safe area")

def load_spec(path):
    sp = importlib.util.spec_from_file_location("postspec", path)
    m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m)
    return m.SPEC

def render_slide(spec, i):
    s = dict(spec["slides"][i]); n, total = i + 1, len(spec["slides"])
    s["_tag"], s["_topic"] = spec.get("tag", "@TECHINABITE"), spec.get("topic", "")
    c = Canvas(n, total, s)
    chrome(c)
    TYPES[s["type"]](c, s)
    if c.ymax > Y1 + (300 if s["type"] in ("cover", "takeaway") else 0): c.errors.append(f"content runs to y={int(c.ymax)} (limit {Y1})")
    cfg = s.get("mascot", None)
    if cfg is None and s["type"] in ("cover", "takeaway"): cfg = {"x": 890, "y": 1110, "size": 190} if s["type"] == "cover" else {"x": 900, "y": 1130, "size": 170}
    if cfg: mascot(c, cfg)
    return c

def render(spec, outprefix):
    os.makedirs(os.path.dirname(outprefix) or ".", exist_ok=True)
    errors, paths = [], []
    for i in range(len(spec["slides"])):
        c = render_slide(spec, i)
        errors += [f"slide {i + 1}: {e}" for e in c.errors]
        p = f"{outprefix}_s{i + 1:02d}.png"; c.img.save(p); c.img.convert("RGB").save(p.replace(".png", ".jpg"), quality=95)
        paths.append(p)
    ims = [Image.open(p).resize((360, 450)) for p in paths]
    sheet = Image.new("RGB", (360 * len(ims), 450))
    for i, im in enumerate(ims): sheet.paste(im, (360 * i, 0))
    sheet.save(f"{outprefix}_contact.png")
    return paths, errors

if __name__ == "__main__":
    spec = load_spec(sys.argv[1])
    paths, errors = render(spec, sys.argv[2])
    print("\n".join(paths))
    if errors:
        print("LAYOUT PROBLEMS:\n" + "\n".join(errors)); sys.exit(1)
    print("ok: layout clean")
