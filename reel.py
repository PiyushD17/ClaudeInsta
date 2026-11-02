import sys, math, subprocess, os
import numpy as np
from PIL import Image, ImageDraw, ImageFont

W, H, FPS, DUR = 1080, 1920, 30, 25.0
F = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts") + os.sep
BOLD = lambda s: ImageFont.truetype(F + "InterDisplay-Bold.otf", s)
MED = lambda s: ImageFont.truetype(F + "Inter-Medium.otf", s)
REG = lambda s: ImageFont.truetype(F + "Inter-Regular.otf", s)

BG = (13, 16, 28)
PANEL = (25, 30, 50)
EDGE = (52, 60, 88)
TEXT = (240, 243, 248)
MUTED = (146, 156, 178)
AMBER = (255, 190, 60)
MINT = (95, 220, 190)

class SoftDraw:
    """ImageDraw wrapper: Pillow ignores fill alpha for text on RGB images, so text with alpha is
    drawn into a small mask and pasted; everything else passes through."""
    def __init__(self, img):
        self.img = img
        self.d = ImageDraw.Draw(img, "RGBA")
    def __getattr__(self, name):
        return getattr(self.d, name)
    def text(self, xy, text, font=None, fill=None, anchor=None, **kw):
        a = fill[3] / 255 if (fill is not None and len(fill) == 4) else 1.0
        if a <= 0: return
        rgb = tuple(fill[:3])
        if a >= 0.999:
            return self.d.text(xy, text, font=font, fill=rgb, anchor=anchor)
        x0, y0, x1, y1 = [int(v) for v in self.d.textbbox(xy, text, font=font, anchor=anchor)]
        x0 -= 6; y0 -= 6; x1 += 6; y1 += 6
        mask = Image.new("L", (x1 - x0, y1 - y0), 0)
        ImageDraw.Draw(mask).text((xy[0] - x0, xy[1] - y0), text, font=font, fill=int(255 * a), anchor=anchor)
        self.img.paste(rgb, (x0, y0, x1, y1), mask)

def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def ease(u): u = clamp(u); return 1 - (1 - u) ** 3
def fade(t, t0, t1): return clamp((t - t0) / (t1 - t0))
def sw(t, t0, t1, fi=0.3, fo=0.3): return clamp(min((t - t0) / fi, (t1 - t) / fo))
def mix(c0, c1, u): return tuple(int(c0[i] + (c1[i] - c0[i]) * u) for i in range(3))
def A(c, a): return tuple(c) + (int(255 * clamp(a)),)

def wrap(d, text, f, maxw):
    words, lines, cur = text.split(), [], ""
    for w in words:
        test = (cur + " " + w).strip()
        if d.textlength(test, font=f) <= maxw: cur = test
        else: lines.append(cur); cur = w
    lines.append(cur)
    return lines

def spaced(d, center, text, f, fill, track=8):
    ws = [d.textlength(c, font=f) for c in text]
    x = center[0] - (sum(ws) + track * (len(text) - 1)) / 2
    for c, w in zip(text, ws):
        d.text((x, center[1]), c, font=f, fill=fill, anchor="lm"); x += w + track

def captions(d, t):
    for text, t0, t1 in LINES:
        a = clamp(min((t - (t0 - 0.1)) / 0.15, (t1 + 0.35 - t) / 0.25))
        if a <= 0: continue
        f = BOLD(58)
        lines = wrap(d, text, f, 940)
        lh = 76
        cy = 1340 - (len(lines) - 1) * lh / 2
        total_w = max(d.textlength(l, font=f) for l in lines)
        d.rounded_rectangle([W / 2 - total_w / 2 - 36, cy - lh / 2 - 22, W / 2 + total_w / 2 + 36,
                             cy + (len(lines) - 1) * lh + lh / 2 + 22], radius=34, fill=(6, 8, 16, int(170 * a)))
        n_words = len(text.split())
        shown = int(math.ceil(n_words * clamp((t - t0) / (t1 - t0 - 0.2)))) if t >= t0 else 0
        idx = 0
        for li, line in enumerate(lines):
            ws = line.split()
            space = d.textlength(" ", font=f)
            widths = [d.textlength(w, font=f) for w in ws]
            x = W / 2 - (sum(widths) + space * (len(ws) - 1)) / 2
            for w, wd in zip(ws, widths):
                idx += 1
                if idx <= shown:
                    col = AMBER if idx == shown and t < t1 else TEXT
                    d.text((x, cy + li * lh), w, font=f, fill=A(col, a), anchor="lm")
                x += wd + space

# ---------- music ----------
def make_music(path, bpm=112, seed=3, variant=0):
    from scipy.io import wavfile
    sr = 44100
    N = int(DUR * sr)
    L = np.zeros(N); R = np.zeros(N)
    rng = np.random.default_rng(seed)
    beat = 60 / bpm

    def add(sig, start, gain=1.0, pan=0.0):
        i = int(start * sr)
        if i >= N: return
        n = min(len(sig), N - i)
        L[i:i + n] += sig[:n] * gain * (1 - max(0, pan))
        R[i:i + n] += sig[:n] * gain * (1 + min(0, pan))

    def tone(f, dur, decay, harm=(1, 0.0, 0.0)):
        tt = np.arange(int(dur * sr)) / sr
        s = sum(h * np.sin(2 * np.pi * f * (k + 1) * tt) for k, h in enumerate(harm))
        return s * np.exp(-tt * decay)

    # kick
    tt = np.arange(int(0.28 * sr)) / sr
    fk = 48 + 95 * np.exp(-tt * 30)
    kick = np.sin(2 * np.pi * np.cumsum(fk) / sr) * np.exp(-tt * 9)
    tt = np.arange(int(0.12 * sr)) / sr
    snare = np.diff(rng.standard_normal(len(tt) + 1)) * np.exp(-tt * 26)
    tt = np.arange(int(0.05 * sr)) / sr
    hat = np.diff(rng.standard_normal(len(tt) + 1)) * np.exp(-tt * 90)

    nb = int(DUR / beat) + 1
    for b in range(nb):
        add(kick, b * beat, 0.85)
        if b % 2 == 1: add(snare, b * beat, 0.16)
        add(hat, b * beat + beat / 2, 0.06, 0.3)
        if b >= 4: add(hat, b * beat + beat / 4, 0.025, -0.3)

    VARS = [
        ([55.0, 43.65, 65.41, 49.0], [[220.0, 261.63, 329.63], [174.61, 220.0, 261.63], [261.63, 329.63, 392.0], [196.0, 246.94, 293.66]]),
        ([49.0, 55.0, 43.65, 65.41], [[196.0, 233.08, 293.66], [220.0, 261.63, 329.63], [174.61, 220.0, 261.63], [261.63, 329.63, 392.0]]),
        ([41.2, 49.0, 55.0, 36.71], [[164.81, 196.0, 246.94], [196.0, 246.94, 293.66], [220.0, 261.63, 329.63], [146.83, 185.0, 220.0]]),
    ]
    roots, chords = VARS[variant % len(VARS)]
    bar = 4 * beat
    nbars = int(DUR / bar) + 1
    pat = [1, 0, 1, 1, 0, 1, 0, 1]
    for k in range(nbars):
        r = roots[k % 4]; ch = chords[k % 4]
        for j, on in enumerate(pat):
            if on: add(tone(r, 0.3, 6, (1, 0.5, 0.25)), k * bar + j * beat / 2, 0.22)
        # pad
        dur = bar + 0.4
        tt = np.arange(int(dur * sr)) / sr
        w = np.clip(tt / 0.5, 0, 1) * np.clip((dur - tt) / 0.4, 0, 1)
        pad = np.zeros(len(tt))
        for f in ch:
            for det in (1.0, 1.004):
                for h in range(1, 6):
                    pad += np.sin(2 * np.pi * f * det * h * tt) / h
        add(pad * w * 0.018, k * bar, 1.0)
        # arp from bar 1
        if k >= 1:
            seq = [0, 1, 2, 1, 0, 1, 2, 1]
            for j, s in enumerate(seq):
                add(tone(ch[s] * 2, 0.35, 9, (1, 0.3, 0.1)), k * bar + j * beat / 2, 0.07, 0.4 if j % 2 else -0.4)

    out = np.stack([L, R], axis=1)
    out = np.tanh(out * 1.3)
    out /= np.max(np.abs(out)) / 0.72
    fo = int(1.2 * sr)
    out[-fo:] *= np.linspace(1, 0, fo)[:, None]
    wavfile.write(path, sr, (out * 32767).astype(np.int16))


SPEC = None

def captions(d, t):
    for text, t0, t1 in SPEC["lines"]:
        a = clamp(min((t - (t0 - 0.1)) / 0.15, (t1 + 0.35 - t) / 0.25))
        if a <= 0: continue
        f = BOLD(58)
        lines = wrap(d, text, f, 940)
        lh = 76
        cy = 1340 - (len(lines) - 1) * lh / 2
        total_w = max(d.textlength(l, font=f) for l in lines)
        d.rounded_rectangle([W / 2 - total_w / 2 - 36, cy - lh / 2 - 22, W / 2 + total_w / 2 + 36,
                             cy + (len(lines) - 1) * lh + lh / 2 + 22], radius=34, fill=(6, 8, 16, int(170 * a)))
        n_words = len(text.split())
        shown = int(math.ceil(n_words * clamp((t - t0) / (t1 - t0 - 0.2)))) if t >= t0 else 0
        idx = 0
        for li, line in enumerate(lines):
            ws = line.split()
            space = d.textlength(" ", font=f)
            widths = [d.textlength(w, font=f) for w in ws]
            x = W / 2 - (sum(widths) + space * (len(ws) - 1)) / 2
            for w, wd in zip(ws, widths):
                idx += 1
                if idx <= shown:
                    col = AMBER if idx == shown and t < t1 else TEXT
                    d.text((x, cy + li * lh), w, font=f, fill=A(col, a), anchor="lm")
                x += wd + space

def title(d, a, text):
    f = BOLD(64)
    lines = wrap(d, text, f, 900)
    y0 = 360 - (len(lines) - 1) * 38
    for i, ln in enumerate(lines):
        d.text((W / 2, y0 + i * 76), ln, font=f, fill=A(TEXT, a), anchor="mm")

# ----- scene renderers: each gets (d, u, a, sc) with u = seconds since scene start, a = scene alpha -----
def sc_hook(d, u, a, sc):
    spaced(d, (W / 2, 360), sc["kicker"], MED(34), A(AMBER, a), 9)
    k = ease(fade(u, 0.0, 0.35))
    d.text((W / 2, 640 + (1 - k) * 30), sc["big1"], font=BOLD(sc.get("size1", 140)), fill=A(TEXT, a * k), anchor="mm")
    g = ease(fade(u, 0.5, 1.0))
    d.text((W / 2, 800 + (1 - g) * 30), sc["big2"], font=BOLD(sc.get("size2", 150)), fill=A(AMBER, a * g), anchor="mm")
    s = ease(fade(u, 1.3, 1.8))
    for i, ln in enumerate(wrap(d, sc["sub"], MED(44), 880)):
        d.text((W / 2, 960 + i * 62), ln, font=MED(44), fill=A(MUTED, a * s), anchor="mm")

def sc_flow(d, u, a, sc):
    """sources on top -> arrow -> output chips"""
    title(d, a, sc["title"])
    for i, lab in enumerate(sc["sources"]):
        k = ease(fade(u, 0.3 + 0.3 * i, 0.8 + 0.3 * i)) * a
        cx = W / 2 + (i - (len(sc["sources"]) - 1) / 2) * 400
        d.rounded_rectangle([cx - 170, 450, cx + 170, 560], radius=30, fill=A(PANEL, k), outline=A(MINT, k), width=3)
        d.text((cx, 505), lab, font=BOLD(40), fill=A(MINT, k), anchor="mm")
    ar = ease(fade(u, 1.1, 1.6)) * a
    d.polygon([(W / 2 - 30, 610), (W / 2 + 30, 610), (W / 2 + 30, 690), (W / 2 + 60, 690), (W / 2, 740), (W / 2 - 60, 690), (W / 2 - 30, 690)], fill=A(AMBER, ar))
    for i, lab in enumerate(sc["outputs"]):
        t0 = 1.7 + 0.35 * i
        k = ease(fade(u, t0, t0 + 0.4)) * a
        col, row = i % 2, i // 2
        x0 = 90 + col * 470; y0 = 800 + row * 190 + (1 - ease(fade(u, t0, t0 + 0.4))) * 30
        d.rounded_rectangle([x0, y0, x0 + 430, y0 + 150], radius=28, fill=A(PANEL, k), outline=A(EDGE, k), width=3)
        d.text((x0 + 215, y0 + 75), lab, font=BOLD(40), fill=A(TEXT, k), anchor="mm")

def sc_pills(d, u, a, sc):
    """row of app pills + a long-running progress bar"""
    title(d, a, sc["title"])
    for i, lab in enumerate(sc["pills"]):
        t0 = 0.3 + 0.35 * i
        k = ease(fade(u, t0, t0 + 0.4)) * a
        y = 470 + i * 130 + (1 - ease(fade(u, t0, t0 + 0.4))) * 24
        d.rounded_rectangle([160, y, 920, y + 100], radius=50, fill=A(PANEL, k), outline=A(MINT, k), width=3)
        d.ellipse([195, y + 32, 231, y + 68], fill=A(MINT, k))
        d.text((270, y + 50), lab, font=BOLD(42), fill=A(TEXT, k), anchor="lm")
    p = ease(fade(u, 2.2, 2.6)) * a
    d.text((W / 2, 1090), sc["bar_label"], font=MED(38), fill=A(MUTED, p), anchor="mm")
    d.rounded_rectangle([160, 1140, 920, 1166], radius=13, fill=A(EDGE, p))
    prog = clamp((u - 2.6) / 3.2)
    d.rounded_rectangle([160, 1140, 160 + 760 * prog, 1166], radius=13, fill=A(AMBER, p))

def sc_approval(d, u, a, sc):
    title(d, a, sc["title"])
    k = ease(fade(u, 0.3, 0.9)) * a
    d.rounded_rectangle([110, 470, 970, 1010], radius=34, fill=A(PANEL, k), outline=A(AMBER, k), width=4)
    d.text((160, 540), sc["badge"], font=BOLD(30), fill=A(AMBER, k), anchor="lm")
    for i, ln in enumerate(wrap(d, sc["ask"], BOLD(52), 740)):
        d.text((160, 640 + i * 70), ln, font=BOLD(52), fill=A(TEXT, k), anchor="lm")
    b = ease(fade(u, 1.2, 1.7)) * a
    press = clamp((u - 2.6) / 0.3)
    d.rounded_rectangle([160, 860, 520, 960], radius=30, fill=A(MINT if press > 0 else EDGE, b))
    d.text((340, 910), sc["yes"], font=BOLD(40), fill=A((10, 14, 24) if press > 0 else TEXT, b), anchor="mm")
    d.rounded_rectangle([560, 860, 920, 960], radius=30, outline=A(EDGE, b), width=3)
    d.text((740, 910), sc["no"], font=BOLD(40), fill=A(MUTED, b), anchor="mm")
    d.text((W / 2, 1090), "Illustration", font=REG(26), fill=A(MUTED, a), anchor="mm")

def sc_cta(d, u, a, sc):
    v = ease(fade(u, 0.2, 0.8))
    d.text((W / 2, 600), sc["big"], font=BOLD(sc.get("size", 120)), fill=A(AMBER, a * v), anchor="mm")
    d.text((W / 2, 720), sc["sub"], font=MED(44), fill=A(MUTED, a * v), anchor="mm")
    c = ease(fade(u, 3.4, 4.0)) * a
    d.text((W / 2, 930 + (1 - c) * 24), sc.get("line", "One work tool a day."), font=BOLD(70), fill=A(TEXT, c), anchor="mm")
    d.text((W / 2, 1060 + (1 - c) * 24), "Follow.", font=BOLD(112), fill=A(AMBER, c), anchor="mm")


def sc_bars(d, u, a, sc):
    """horizontal bars. item: (label, frac 0-1, colour, value_text) or with 'num' to count up."""
    title(d, a, sc["title"])
    for i, it in enumerate(sc["items"]):
        t0 = 0.4 + 0.9 * i
        k = ease(fade(u, t0, t0 + 0.4)) * a
        y = 520 + i * 270
        d.text((110, y), it["label"], font=MED(42), fill=A(MUTED, k), anchor="lm")
        g = ease(fade(u, t0 + 0.2, t0 + 1.2))
        bw = max(10, 860 * it["frac"] * g)
        d.rounded_rectangle([110, y + 40, 110 + 860, y + 120], radius=20, fill=A(PANEL, k))
        d.rounded_rectangle([110, y + 40, 110 + bw, y + 120], radius=20, fill=A(it["color"], k))
        txt = it["value"] if "num" not in it else f"{int(it['num'] * g):,}" + it.get("unit", "")
        d.text((110, y + 160), txt, font=BOLD(54), fill=A(it["color"], k), anchor="lm")
    d.text((W / 2, 520 + len(sc["items"]) * 270 + 20), sc.get("note", ""), font=REG(28), fill=A(MUTED, a), anchor="mm")

def sc_lane(d, u, a, sc):
    """requests queue up and are handled one at a time"""
    title(d, a, sc["title"])
    d.text((W / 2, 440), sc["sub"], font=MED(38), fill=A(MUTED, a), anchor="mm")
    box = ease(fade(u, 0.2, 0.7)) * a
    d.rounded_rectangle([640, 560, 990, 860], radius=34, fill=A(PANEL, box), outline=A(MINT, box), width=4)
    d.text((815, 610), sc["worker"], font=BOLD(34), fill=A(MINT, box), anchor="mm")
    d.line([90, 710, 620, 710], fill=A(EDGE, a), width=4)
    p = (u - 0.9) / 0.9
    n = sc["blocks"]
    for k in range(n):
        r = k - p
        if r > 0:
            x = 580 - (r - 1) * 110 if r > 1 else 580 - (r - 1) * 110
            x = 580 - (r - 1) * 110 - 40 * (1 - clamp(r - 1)) * 0
            al = a * ease(fade(u, 0.3 + 0.15 * k, 0.6 + 0.15 * k))
            col = AMBER
            cx = 560 - (r - 1) * 110
        elif r > -1:
            cx = 815; al = a * (1 + r) ; col = MINT
        else:
            continue
        if cx < 90: continue
        d.rounded_rectangle([cx - 40, 670, cx + 40, 750], radius=16, fill=A(col, al))
        d.text((cx, 710), str(k + 1), font=BOLD(34), fill=A((10, 14, 24), al), anchor="mm")
    done = int(clamp(p + 1, 0, n))
    d.text((815, 790), f"done: {done}", font=MED(34), fill=A(TEXT, box), anchor="mm")
    d.text((W / 2, 1000), sc["note"], font=MED(40), fill=A(MUTED, a), anchor="mm")

def sc_scan(d, u, a, sc):
    """grid of rows scanned one by one, accelerating, until the target row is found"""
    title(d, a, sc["title"])
    cols, rows, cell, x0, y0 = 10, 12, 70, 190, 470
    n = cols * rows; target = sc.get("target", n - 3)
    t0, t1 = 0.8, sc["scan_secs"]
    p = clamp((u - t0) / (t1 - t0))
    idx = int((target + 1) * p * p)
    found = p >= 1
    for i in range(n):
        r, c = divmod(i, cols)
        x, y = x0 + c * cell, y0 + r * cell
        if i == target:
            col = AMBER if found else MUTED
            d.rounded_rectangle([x, y, x + 58, y + 58], radius=12, fill=A(col, a * (1 if found else 0.5)))
        elif i < idx:
            d.rounded_rectangle([x, y, x + 58, y + 58], radius=12, fill=A(MINT, a * 0.35))
        elif i == idx and not found:
            d.rounded_rectangle([x - 4, y - 4, x + 62, y + 62], radius=14, fill=A(AMBER, a))
        else:
            d.rounded_rectangle([x, y, x + 58, y + 58], radius=12, fill=A(PANEL, a))
    count = target + 1 if found else idx + 1
    d.text((W / 2, 1340), f"Rows checked: {count}", font=BOLD(60), fill=A(AMBER if found else TEXT, a), anchor="mm")
    if found:
        k = ease(fade(u, t1, t1 + 0.4)) * a
        d.text((W / 2, 1398), sc["found"], font=MED(38), fill=A(MINT, k), anchor="mm")
    d.text((W / 2, 1434), sc.get("note", ""), font=REG(24), fill=A(MUTED, a), anchor="mm")

def sc_lookup(d, u, a, sc):
    """book-index lookup: step down a sorted list, then jump to the page"""
    title(d, a, sc["title"])
    d.rounded_rectangle([90, 450, 540, 1150], radius=30, fill=A(PANEL, a), outline=A(EDGE, a), width=3)
    d.text((130, 505), sc["list_label"], font=BOLD(28), fill=A(AMBER, a), anchor="lm")
    items, tg = sc["items"], sc["target"]
    cur = min(tg, int(max(0, u - 0.8) / 0.55)) if u > 0.8 else -1
    for i, (term, pg) in enumerate(items):
        y = 600 + i * 100
        hot = (i == cur)
        if hot:
            d.rounded_rectangle([110, y - 38, 520, y + 38], radius=18, fill=A(AMBER, a * 0.22), outline=A(AMBER, a), width=3)
        d.text((140, y), term, font=BOLD(40), fill=A(TEXT if hot else MUTED, a), anchor="lm")
        d.text((500, y), str(pg), font=MED(36), fill=A(AMBER if hot else MUTED, a), anchor="rm")
    ar = ease(fade(u, 0.8 + 0.55 * tg + 0.3, 0.8 + 0.55 * tg + 0.8)) * a
    d.polygon([(560, 790), (610, 790), (610, 765), (660, 810), (610, 855), (610, 830), (560, 830)], fill=A(MINT, ar))
    pc = ease(fade(u, 0.8 + 0.55 * tg + 0.7, 0.8 + 0.55 * tg + 1.2)) * a
    d.rounded_rectangle([690, 560, 990, 1050], radius=26, fill=A(PANEL, pc), outline=A(MINT, pc), width=4)
    d.text((840, 620), sc["page_label"], font=BOLD(40), fill=A(MINT, pc), anchor="mm")
    for j in range(7):
        d.rounded_rectangle([730, 690 + j * 46, 950 - (j % 3) * 50, 702 + j * 46], radius=6, fill=A(EDGE, pc))
    d.text((W / 2, 1260), sc["note"], font=MED(40), fill=A(MUTED, a), anchor="mm")

def sc_tree(d, u, a, sc):
    """balanced tree with a highlighted root-to-row path"""
    title(d, a, sc["title"])
    root = (540, 520)
    mids = [(230, 740), (540, 740), (850, 740)]
    leaves = [(105 + i * 108, 960) for i in range(9)]
    row = (leaves[4][0], 1200)
    steps = [1.2, 2.2, 3.2, 4.2]
    def on(k): return u >= steps[k]
    for i, m in enumerate(mids):
        d.line([root, m], fill=A(AMBER if (i == 1 and on(1)) else EDGE, a), width=6 if (i == 1 and on(1)) else 4)
        for j in range(3):
            l = leaves[i * 3 + j]
            hot = (i == 1 and j == 1 and on(2))
            d.line([m, l], fill=A(AMBER if hot else EDGE, a), width=6 if hot else 4)
    d.line([leaves[4], row], fill=A(AMBER if on(3) else EDGE, a), width=6 if on(3) else 4)
    def node(c, w, h, label, hot):
        d.rounded_rectangle([c[0] - w / 2, c[1] - h / 2, c[0] + w / 2, c[1] + h / 2], radius=18,
                            fill=A(AMBER if hot else PANEL, a), outline=A(AMBER if hot else EDGE, a), width=3)
        d.text(c, label, font=MED(28), fill=A((10, 14, 24) if hot else MUTED, a), anchor="mm")
    node(root, 180, 76, "A – Z", on(0))
    for i, (m, lab) in enumerate(zip(mids, ["A – H", "I – Q", "R – Z"])):
        node(m, 150, 70, lab, i == 1 and on(1))
    labs = ["···"] * 9; labs[3], labs[4], labs[5] = "I–K", "L–N", "O–Q"
    for i, l in enumerate(leaves):
        node(l, 92, 62, labs[i], i == 4 and on(2))
    rk = ease(fade(u, steps[3], steps[3] + 0.4)) * a
    d.rounded_rectangle([row[0] - 110, row[1] - 40, row[0] + 110, row[1] + 40], radius=20, fill=A(MINT, rk))
    d.text(row, "Your row", font=BOLD(36), fill=A((10, 14, 24), rk), anchor="mm")
    nk = ease(fade(u, 5.2, 5.7)) * a
    for i, ln in enumerate(wrap(d, sc["note"], MED(38), 860)):
        d.text((W / 2, 1330 + i * 56), ln, font=MED(38), fill=A(TEXT, nk), anchor="mm")

def sc_writes(d, u, a, sc):
    """every write touches the table AND the index; then keep only indexes you use"""
    title(d, a, sc["title"])
    for px, lab in ((90, "TABLE"), (570, "INDEX")):
        d.rounded_rectangle([px, 440, px + 420, 900], radius=28, fill=A(PANEL, a), outline=A(EDGE, a), width=3)
        d.text((px + 36, 490), lab, font=BOLD(28), fill=A(MUTED, a), anchor="lm")
        for j in range(4):
            d.rounded_rectangle([px + 36, 540 + j * 56, px + 384 - (j % 2) * 60, 560 + j * 56], radius=8, fill=A(EDGE, a))
    k1 = ease(fade(u, 1.0, 1.5)) * a
    d.rounded_rectangle([126, 780, 474, 830], radius=14, fill=A(AMBER, k1))
    k2 = ease(fade(u, 1.7, 2.2)) * a
    d.rounded_rectangle([606, 780, 954, 830], radius=14, fill=A(AMBER, k2))
    d.polygon([(500, 790), (555, 790), (555, 770), (590, 805), (555, 840), (555, 820), (500, 820)], fill=A(MINT, k2))
    nt = ease(fade(u, 2.4, 2.9)) * a
    d.text((W / 2, 980), sc["note1"], font=BOLD(46), fill=A(TEXT, nt), anchor="mm")
    c = ease(fade(u, 4.2, 4.7)) * a
    chips = sc["chips"]
    for i, (lab, sub, good) in enumerate(chips):
        y = 1110 + i * 150
        col = MINT if good else MUTED
        d.rounded_rectangle([110, y, 970, y + 110], radius=30, fill=A(PANEL, c), outline=A(col, c), width=3)
        d.text((150, y + 55), lab, font=BOLD(40), fill=A(col, c), anchor="lm")
        d.text((930, y + 55), sub, font=MED(34), fill=A(col, c), anchor="rm")
        if not good:
            d.line([140, y + 55, 140 + d.textlength(lab, font=BOLD(40)) + 20, y + 55], fill=A(AMBER, c), width=5)

def sc_steps(d, u, a, sc):
    """numbered steps revealed one by one; the newest is highlighted"""
    title(d, a, sc["title"])
    items = sc["items"]; gap = sc.get("gap", 1.3)
    cur = min(len(items) - 1, int(max(0, u - 0.5) / gap))
    lines_per = [wrap(d, t, MED(40), 700) for t in items]
    y = 470
    for i, (t, lns) in enumerate(zip(items, lines_per)):
        k = ease(fade(u, 0.5 + gap * i, 0.9 + gap * i)) * a
        if k <= 0: break
        h = 40 + 52 * len(lns)
        hot = (i == cur)
        d.rounded_rectangle([90, y, 990, y + h], radius=28, fill=A(PANEL, k), outline=A(AMBER if hot else EDGE, k), width=5 if hot else 3)
        d.ellipse([125, y + h / 2 - 34, 193, y + h / 2 + 34], fill=A(AMBER if hot else EDGE, k))
        d.text((159, y + h / 2), str(i + 1), font=BOLD(38), fill=A((10, 14, 24) if hot else TEXT, k), anchor="mm")
        for j, ln in enumerate(lns):
            d.text((225, y + h / 2 - (len(lns) - 1) * 26 + j * 52), ln, font=MED(40), fill=A(TEXT if hot else MUTED, k), anchor="lm")
        y += h + 26
    if sc.get("note"):
        d.text((W / 2, min(y + 40, 1400)), sc["note"], font=REG(28), fill=A(MUTED, a), anchor="mm")

def sc_versus(d, u, a, sc):
    """two cards side by side, each with up to 3 short complete lines"""
    title(d, a, sc["title"])
    for side, (x0, col) in enumerate(((70, MUTED), (550, MINT))):
        k = ease(fade(u, 0.4 + 1.0 * side, 0.9 + 1.0 * side)) * a
        card = sc["left"] if side == 0 else sc["right"]
        d.rounded_rectangle([x0, 470, x0 + 460, 1190], radius=30, fill=A(PANEL, k), outline=A(col, k), width=4)
        for i, ln in enumerate(wrap(d, card["head"], BOLD(44), 380)):
            d.text((x0 + 40, 540 + i * 56), ln, font=BOLD(44), fill=A(col, k), anchor="lm")
        y = 700
        for j, b in enumerate(card["points"]):
            bk = ease(fade(u, 1.0 + 1.0 * side + 0.5 * j, 1.4 + 1.0 * side + 0.5 * j)) * a
            for i, ln in enumerate(wrap(d, b, MED(34), 380)):
                d.text((x0 + 40, y + i * 46), ln, font=MED(34), fill=A(TEXT, bk), anchor="lm")
            y += 46 * len(wrap(d, b, MED(34), 380)) + 36
    if sc.get("note"):
        d.text((W / 2, 1290), sc["note"], font=MED(38), fill=A(MUTED, a), anchor="mm")

def sc_stat(d, u, a, sc):
    """one big number (optionally counting up) with a full sentence explaining it"""
    title(d, a, sc["title"])
    g = ease(fade(u, 0.3, 1.8))
    val = f"{int(sc['num'] * g):,}{sc.get('unit', '')}" if "num" in sc else sc["value"]
    d.text((W / 2, 760), val, font=BOLD(sc.get("size", 150)), fill=A(AMBER, a), anchor="mm")
    k = ease(fade(u, 1.5, 2.1)) * a
    for i, ln in enumerate(wrap(d, sc["label"], MED(46), 860)):
        d.text((W / 2, 930 + i * 64), ln, font=MED(46), fill=A(TEXT, k), anchor="mm")
    if sc.get("note"):
        d.text((W / 2, 1300), sc["note"], font=REG(28), fill=A(MUTED, k), anchor="mm")

SCENES = {"hook": sc_hook, "flow": sc_flow, "pills": sc_pills, "approval": sc_approval, "cta": sc_cta, "bars": sc_bars, "lane": sc_lane, "scan": sc_scan, "lookup": sc_lookup, "tree": sc_tree, "writes": sc_writes, "steps": sc_steps, "versus": sc_versus, "stat": sc_stat}

def scene_bounds():
    starts = [max(0.0, l[1] - 0.3) if i else 0.0 for i, l in enumerate(SPEC["lines"])]
    ends = starts[1:] + [DUR + 0.5]
    return list(zip(starts, ends))

def frame(t):
    img = Image.new("RGB", (W, H), BG)
    d = SoftDraw(img)
    spaced(d, (W / 2, 262), SPEC["tag"], MED(26), A(MUTED, 1), 8)
    for sc, (s0, s1) in zip(SPEC["scenes"], scene_bounds()):
        a = sw(t, s0, s1, 0.3, 0.3 if s1 < DUR else 0.1)
        if a > 0:
            SCENES[sc["type"]](d, t - s0, a, sc)
    if SPEC.get("captions", True):
        captions(d, t)
    return img

def load_spec(path):
    global SPEC, DUR
    import importlib.util
    sp = importlib.util.spec_from_file_location("spec", path)
    m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m)
    SPEC = m.SPEC
    if SPEC.get("pace_wps"):               # auto-time lines from word counts (user's measured ElevenLabs pace ~3.2 words/s)
        t, new = 0.2, []
        for item in SPEC["lines"]:
            text = item if isinstance(item, str) else item[0]
            dd = len(text.split()) / SPEC["pace_wps"]
            new.append((text, round(t, 2), round(t + dd, 2))); t += dd + SPEC.get("gap", 0.4)
        SPEC["lines"] = new; SPEC["dur"] = round(t + 0.6, 1)
    DUR = SPEC.get("dur", 25.0)

if __name__ == "__main__":
    mode, specpath, out = sys.argv[1], sys.argv[2], sys.argv[3]
    load_spec(specpath)
    if mode == "preview":
        times = [s0 + 2.2 for s0, _ in scene_bounds()]
        sheet = Image.new("RGB", (360 * len(times), 640))
        for i, t in enumerate(times): sheet.paste(frame(t).resize((360, 640)), (360 * i, 0))
        sheet.save(out)
    elif mode == "music":
        m = SPEC.get("music", {})
        make_music(out, m.get("bpm", 112), m.get("seed", 3), m.get("variant", 0))
    else:
        tmp = out.replace(".mp4", "_tmp.mp4")
        p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                              "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "veryfast",
                              "-crf", "20", "-pix_fmt", "yuv420p", "-movflags", "+faststart", tmp], stdin=subprocess.PIPE)
        for i in range(int(DUR * FPS)):
            p.stdin.write(frame(i / FPS).tobytes())
        p.stdin.close()
        if p.wait() == 0: os.rename(tmp, out)
        else: sys.exit("ffmpeg failed")
