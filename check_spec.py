#!/usr/bin/env python3
"""Pre-delivery checker for a Tech in a Bite video.

Usage:
  python3 check_spec.py specs/dayNN_slug.py --facts specs/dayNN_facts.json \
         [--video out/dayNN_slug_silent.mp4] [--sheet out/dayNN_sheet.png] [--report out/dayNN_check.md]
  python3 check_spec.py specs/old_spec.py --legacy          # no facts file (old specs only)
  python3 check_spec.py --video some.mp4                    # video checks only

It checks the SCRIPT and every ON-SCREEN string together, and (with --video) the rendered file itself.
Exit code 0 = no FAIL. Exit code 1 = at least one FAIL: do not deliver until every FAIL is fixed.
Target is 0 FAIL and 0 WARN. A WARN means a frame, line or number is not good enough yet: fix it. INFO lines are only length notes covered by "length_reason".

Facts file (written by the daily run from the sources it actually opened), JSON:
{
  "terms":   [{"use": "load balancing algorithm", "never_say": ["rule", "rules"]}],
  "counts":  {"algorithm": 2},                    # sizes of sets that a source states ("two common algorithms")
  "rehook":  {"line": 4, "payoff_line": 6},      # script lines (1-based): the mid-video second hook and the line that answers it
  "share":   {"line": 5, "who": "a dev whose API gets rate limited", "why": "a rule of thumb or moment worth sending or saving"},
  "replay":  {"echo": "bucket", "twist": "how the last line makes the opening hook land differently on a second watch"},
  "topic_terms": ["API", "token bucket"],       # every scene must show at least one, so each frame ties back to the topic on its own
  "length_reason": "why the video is over 50 s",   # optional; turns the length WARNs into INFO
  "illustrative_numbers": ["4"],                  # numbers invented for a worked example (must be labelled as an example)
  "claims":  [{"say": "...", "source": "https://...", "quote": "text copied from the opened page"}]
}
"""
import argparse, importlib.util, json, os, re, subprocess, sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
NUMW = {"two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8,
        "nine": 9, "ten": 10, "eleven": 11, "twelve": 12}
UNITS = {"million", "billion", "thousand", "percent", "seconds", "second", "ms", "milliseconds", "minutes",
         "minute", "hours", "hour", "days", "day", "times", "x", "or", "and", "of", "in", "to", "at", "a", "the",
         "more", "less", "than", "per"}
STOP_BEFORE_NUM = {"of", "in", "to", "at", "by", "for", "about", "than", "over", "under", "with", "and", "or", "is",
                   "are", "from", "every", "each", "only", "just", "around", "nearly", "roughly", "up", "down",
                   "was", "were", "be", "has", "have", "had", "top", "last", "next", "first", "level", "levels"}
CTA = "Follow for one tech topic a day."

findings = []  # (level, code, message)
LENGTH_REASON = False

def add(level, code, msg):
    findings.append((level, code, msg))

def norm_noun(w):
    w = w.lower()
    return w[:-1] if w.endswith("s") and len(w) > 3 else w

# ----------------------------------------------------------------------------- loading
def load_spec(path):
    sp = importlib.util.spec_from_file_location("spec", path)
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    spec = m.SPEC
    lines = [(l if isinstance(l, str) else l[0]) for l in spec["lines"]]
    # timings: same rule as reel.load_spec
    starts, ends = [], []
    if spec.get("pace_wps"):
        t = 0.2
        for text in lines:
            dd = len(text.split()) / spec["pace_wps"]
            starts.append(round(t, 2)); t += dd + spec.get("gap", 0.4)
        dur = round(t + 0.6, 1)
    else:
        starts = [l[1] for l in spec["lines"]]
        dur = spec.get("dur", 25.0)
    bounds = []
    for i, s in enumerate(starts):
        s0 = max(0.0, s - 0.3) if i else 0.0
        s1 = max(0.0, starts[i + 1] - 0.3) if i + 1 < len(starts) else dur + 0.5
        bounds.append((s0, s1))
    return spec, lines, bounds, dur

NON_DISPLAY = {"type", "mode", "mascot", "follow_first"}   # spec keys that are settings, never shown on screen

def collect(obj, key=""):
    """All on-screen strings in a scene dict as (key, text)."""
    out = []
    if isinstance(obj, str):
        if key not in NON_DISPLAY:
            out.append((key, obj))
    elif isinstance(obj, dict):
        for k, v in obj.items():
            out += collect(v, k)
    elif isinstance(obj, (list, tuple)):
        for v in obj:
            out += collect(v, key)
    return out

def scene_strings(sc):
    if sc.get("type") == "stage":
        import stage
        return stage.display_strings(sc)
    return collect(sc)

# ----------------------------------------------------------------------------- text patterns
RE_NUM = re.compile(r"(?<![\w.])(\d+(?:[.,]\d+)*)(?:\s+(million|billion|thousand|percent))?|\b(two|three|four|five|six|seven|eight|nine|ten|eleven|twelve)\b", re.I)
RE_LABEL = re.compile(r"\b([A-Za-z]+)\s+(\d{1,3})\b")
RE_COUNT = re.compile(r"(?<![\d.])\b(\d{1,2}|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve)\s+([A-Za-z]+)", re.I)

def numbers_in(text):
    """Number tokens in text, excluding 'Noun 3' entity labels. Returns normalised strings."""
    labels = {m.span(2) for m in RE_LABEL.finditer(text) if m.group(1).lower() not in STOP_BEFORE_NUM}
    out = []
    for m in RE_NUM.finditer(text):
        if m.group(1) and any(m.start(1) == a and m.end(1) == b for a, b in labels):
            continue
        tok = m.group(0).lower().strip()
        out.append(tok)
    return out

def entity_labels(text):
    res = []
    for m in RE_LABEL.finditer(text):
        w = m.group(1)
        if w.lower() in STOP_BEFORE_NUM or w.lower() in UNITS:
            continue
        res.append((norm_noun(w), int(m.group(2))))
    return res

def count_claims(text):
    res = []
    labels = {m.span(2) for m in RE_LABEL.finditer(text) if m.group(1).lower() not in STOP_BEFORE_NUM}
    for m in RE_COUNT.finditer(text):
        if m.span(1) in labels:        # "Visitor 2 goes ..." is a label, not a count of goes
            continue
        n = m.group(1).lower()
        n = NUMW.get(n, None) if n in NUMW else int(n)
        noun = m.group(2).lower()
        if n is None or n < 2 or n > 12 or noun in UNITS or noun in NUMW:
            continue
        res.append((norm_noun(noun), n))
    return res

# ----------------------------------------------------------------------------- text checks
def text_checks(spec, lines, bounds, facts, legacy):
    scenes = spec["scenes"]
    onscreen = [scene_strings(sc) for sc in scenes]
    all_texts = [("script line %d" % (i + 1), l) for i, l in enumerate(lines)]
    for i, items in enumerate(onscreen):
        all_texts += [("scene %d %s" % (i + 1, k or "text"), t) for k, t in items]

    # scene/line pairing
    if len(scenes) != len(lines):
        add("FAIL", "SCENE_COUNT", f"{len(lines)} script lines but {len(scenes)} scenes: use exactly one scene per line.")

    # script rules
    words = len(" ".join(lines).split())
    chars = len(" ".join(lines))
    if not lines[-1].strip().endswith(CTA):
        add("FAIL", "CTA", f'The last script line must end with exactly: "{CTA}"')
    global STORY
    story = STORY = spec.get("format") == "story"          # technical deep dive: up to ~150 s, 2000 characters of voiceover credits
    lo, hi, cmax = (200, 460, 2000) if story else (100, 190, 1000)
    if not lo <= words <= hi:
        add("FAIL", "WORDS", f"Script has {words} words (needs {lo} to {hi}).")
    if chars > cmax:
        add("FAIL", "CHARS", f"Script has {chars} characters (limit about {cmax - 50}).")
    brand = " ".join(t for _, t in all_texts)
    if re.search(r"tech in (\d+|a) (second|minute)", brand, re.I):
        add("FAIL", "BRAND", 'Brand text must say "Tech in a Bite", never a length.')
    if scenes and scenes[0].get("type") == "hook":
        hook = " ".join(t for k, t in onscreen[0] if k in ("big1", "big2"))
        spoken = lines[0]
        hw = {w for w in re.findall(r"[a-z0-9]+", hook.lower()) if len(w) > 2}
        sw_ = set(re.findall(r"[a-z0-9]+", spoken.lower()))
        miss = [w for w in hw if w not in sw_]
        if hw and len(miss) / len(hw) > 0.5:
            add("WARN", "HOOK_MISMATCH", f'On-screen hook "{hook}" shares few words with the spoken hook "{spoken}". They must say the same thing.')

    # facts
    if facts is None:
        if not legacy:
            add("FAIL", "NO_FACTS", "No facts file. Write specs/dayNN_facts.json (terms, counts, illustrative_numbers, claims with quotes) before checking.")
        return
    quotes = " ".join(c.get("quote", "") for c in facts.get("claims", [])).lower()
    for c in facts.get("claims", []):
        if not (c.get("source", "").startswith("http") and len(c.get("quote", "").strip()) >= 15):
            add("FAIL", "CLAIM_INCOMPLETE", f'Claim "{c.get("say", "?")}" needs a source URL and a real quote (15+ characters).')
    if not facts.get("claims"):
        add("FAIL", "NO_CLAIMS", "The facts file has no claims. Every factual sentence needs a source quote.")

    # banned look-alike terms
    for term in facts.get("terms", []):
        for bad in term.get("never_say", []):
            rx = re.compile(r"\b%s\b" % re.escape(bad), re.I)
            for where, text in all_texts:
                if rx.search(text):
                    add("FAIL", "WRONG_TERM", f'"{bad}" used in {where}: "{text}". The source term is "{term["use"]}".')
        if term["use"].lower() not in brand.lower() and not any(w in brand.lower() for w in term["use"].lower().split()[-1:]):
            add("WARN", "TERM_UNUSED", f'The source term "{term["use"]}" never appears in the video.')

    # every number must be backed by a quote or declared illustrative
    illus = {x.lower() for x in facts.get("illustrative_numbers", [])}
    for where, text in all_texts:
        for tok in numbers_in(text):
            n = tok.split()[0]
            if tok in illus or n in illus or NUMW.get(n) and str(NUMW[n]) in illus:
                continue
            variants = {tok, tok.replace(" ", ""), n}
            if n in NUMW:
                variants.add(str(NUMW[n]))
            if n.isdigit():
                variants |= {k for k, v in NUMW.items() if str(v) == n}
            if not any(re.search(r"(?<![\w.])%s(?![\w])" % re.escape(v), quotes) for v in variants):
                add("FAIL", "NUMBER_UNSOURCED", f'"{tok}" in {where} ("{text}") is not in any claim quote and not listed as illustrative.')

    # counts of sets ("3 rules") must be sourced
    counts = {norm_noun(k): v for k, v in facts.get("counts", {}).items()}
    seen = defaultdict(set)
    for where, text in all_texts:
        for noun, n in count_claims(text):
            if str(n) in illus:
                continue
            seen[noun].add(n)
            if counts.get(noun) != n:
                add("FAIL", "COUNT_UNSOURCED", f'"{n} {noun}s" in {where} ("{text}"): no source states that count (facts.counts has {counts.get(noun, "nothing")} for "{noun}"). Use the source term and a sourced count, or reword without a count.')
    # numbered titles across scenes (Rule 1, Rule 2, ...)
    enum = defaultdict(dict)
    for i, items in enumerate(onscreen):
        for k, t in items:
            if k == "title":
                for noun, n in entity_labels(t):
                    enum[noun].setdefault(n, set()).add(i)
    for noun, idx in enum.items():
        if len(idx) >= 2 and counts.get(noun) != max(idx):
            add("FAIL", "ENUM_UNSOURCED", f'Titles number "{noun}" 1 to {max(idx)} but no source says there are {max(idx)} of them (facts.counts: {counts.get(noun, "nothing")}). Items in one list must be the same kind of thing.')

    # one example world: the same set of entities in every scene
    per_scene = defaultdict(lambda: defaultdict(set))
    for i, items in enumerate(onscreen):
        for _, t in items:
            for noun, n in entity_labels(t):
                per_scene[noun][i].add(n)
    for noun, sc in per_scene.items():
        rich = {i: s for i, s in sc.items() if len(s) >= 2}
        sets = {tuple(sorted(s)) for s in rich.values()}
        if len(sets) > 1:
            detail = "; ".join(f"scene {i + 1} uses {sorted(s)}" for i, s in sorted(rich.items()))
            add("FAIL", "ENTITY_SET", f'"{noun}" numbers differ between scenes ({detail}). Use the same set everywhere so the example does not contradict itself.')
        stated = seen.get(noun, set()) | ({counts[noun]} if noun in counts else set())
        top = max((max(s) for s in sc.values()), default=0)
        if stated and top > max(stated):
            add("FAIL", "ENTITY_COUNT", f'A scene shows "{noun} {top}" but the text only counts {sorted(stated)} {noun}s.')

    # rehook: a second hook in the middle that the video pays off later
    rh = facts.get("rehook")
    if not rh:
        add("FAIL", "REHOOK_MISSING", 'The facts file needs "rehook": {"line": N, "payoff_line": M} (1-based script lines).')
    else:
        n, m = rh.get("line"), rh.get("payoff_line")
        wc = [len(l.split()) for l in lines]
        total = sum(wc)
        if not (isinstance(n, int) and isinstance(m, int) and 1 < n <= len(lines) and n < m <= len(lines)):
            add("FAIL", "REHOOK_LINES", f"rehook line {n} / payoff_line {m} are not valid script lines (payoff must come after the rehook).")
        else:
            frac = sum(wc[:n - 1]) / total
            if not 0.25 <= frac <= 0.65:
                add("FAIL", "REHOOK_POSITION", f"The rehook (line {n}) starts {frac:.0%} into the script. It belongs in the middle (25% to 65%).")
            pay = sum(wc[:m - 1]) / total
            if pay > 0.85:
                add("WARN", "ANSWER_LATE", f"The payoff (line {m}) arrives {pay:.0%} into the script. Deliver the answer by about 80%.")
            sys.path.insert(0, HERE)
            import rehookscore
            first = re.split(r"(?<=[.?!])\s", lines[n - 1].strip())[0]
            ov, comps, flags, ok = rehookscore.score(first)
            if not ok:
                weakest = min(comps, key=comps.get)
                add("FAIL", "REHOOK_SCORE", f'Rehook "{first}" scores {ov} (needs 60+, every part 40+, no flags; weakest: {weakest} {comps[weakest]}). Write sharper candidates.')
    # reach signals (Instagram: send/save, replay, finish): one send-worthy line and a replay design are mandatory
    sh = facts.get("share")
    if not sh:
        add("FAIL", "SHARE_MISSING", 'The facts file needs "share": {"line": N, "who": "...", "why": "..."}: one script line worth sending to a specific person or saving.')
    else:
        n = sh.get("line")
        if not (isinstance(n, int) and 1 < n < len(lines)) or not sh.get("who") or not sh.get("why"):
            add("FAIL", "SHARE_LINES", 'share needs a valid script line (not the hook or the closing line) plus "who" it is for and "why" they would send or save it.')
    rp = facts.get("replay")
    if not rp or not rp.get("echo") or not rp.get("twist"):
        add("FAIL", "REPLAY_MISSING", 'The facts file needs "replay": {"echo": "<word from the hook>", "twist": "<how the last line changes how the hook reads on a second watch>"}.')
    else:
        last_before_cta = " ".join(lines[-1:]).lower()
        hook_text = lines[0].lower()
        if rp["echo"].lower() not in hook_text or rp["echo"].lower() not in last_before_cta:
            add("FAIL", "REPLAY_ECHO", f'The echo word "{rp["echo"]}" must appear in the first line (the hook) and in the last line.')
    total_words = sum(len(l.split()) for l in lines)
    if total_words > 150:
        add("INFO" if facts.get("length_reason") else "WARN", "LENGTH_LONG", f"Script has {total_words} words (about {total_words / 3.2 + 0.4 * len(lines):.0f} s). Finish rate falls with length: aim for 35 to 45 s (about 105 to 135 words) and cut anything that does not move the story.")
    # every frame must tie back to the topic AND stand on its own
    terms_ok = [t.lower() for t in facts.get("topic_terms", [])]
    if not terms_ok:
        add("FAIL", "TOPIC_TERMS_MISSING", 'The facts file needs "topic_terms": ["API", "token bucket", ...]: words that tie a frame to the topic. Every scene must show at least one.')
    else:
        vis = stage_visible(spec, lines, bounds)
        for i, items in enumerate(onscreen):
            if vis and spec["scenes"][i].get("type") == "stage": items = vis[i]
            shown = " ".join(t for k, t in items if k != "kicker").lower()
            if not any(t in shown for t in terms_ok):
                add("FAIL", "FRAME_STANDALONE", f"Scene {i + 1} shows nothing that names the topic (needs one of {terms_ok}). A viewer who sees only this frame must know what the video is about.")
    # short labels: stranger test
    for i, items in enumerate(onscreen):
        for k, t in items:
            if k in ("big1", "big2", "kicker", "big", "object", "code"):
                continue
            nw = len(t.split())
            short = nw <= 2 or (nw == 3 and re.match(r"(a|an|the|one|some)\b", t, re.I))
            if short and not re.search(r"[\d.?!]", t):
                add("FAIL", "SHORT_LABEL", f'Scene {i + 1} {k}: "{t}". A frame must be understood on its own. Spell out what it is, in words that tie it to the topic.')

    # side-by-side listing for the reviewer
    return onscreen

def mascot_overlap_checks(path):
    """FAIL when the mascot sits on top of scene content. Renders each scene without the mascot and looks inside its box."""
    import numpy as np
    sys.path.insert(0, HERE)
    import reel
    reel.load_spec(path)
    if not reel.SPEC.get("mascot"):
        return
    saved = reel.SPEC["mascot"]
    for i, (sc, (s0, s1)) in enumerate(zip(reel.SPEC["scenes"], reel.scene_bounds())):
        cfg = reel.mascot_cfg(sc)
        if not cfg:
            continue
        x0, y0, x1, y1 = [int(v) for v in (cfg["x"] - cfg["size"] * 0.62, cfg["y"] - cfg["size"] * 0.62 - 12,
                                           cfg["x"] + cfg["size"] * 0.62, cfg["y"] + cfg["size"] * 0.62 + 12)]
        if x0 < 0 or x1 > reel.W or y0 < 230 or y1 > 1440:
            add("FAIL", "MASCOT_ZONE", f"Scene {i + 1}: mascot box {x0},{y0}-{x1},{y1} leaves the safe zone (x 0-1080, y 230-1440).")
        reel.SPEC["mascot"] = None
        try:
            for t in np.linspace(s0 + 0.6, max(s0 + 0.7, s1 - 0.5), 5):
                fr = np.asarray(reel.frame(float(t)).convert("L"), dtype=np.int16)
                box = fr[max(0, y0):y1, max(0, x0):x1]
                if (np.abs(box - np.median(fr[:, :8], axis=1)[max(0, y0):y1, None]) > 30).sum() > 150:
                    add("FAIL", "MASCOT_OVERLAP", f"Scene {i + 1}: the mascot covers scene content around t={t:.1f}s. Move or shrink it with a per-scene \"mascot\" setting, or hide it with \"mascot\": False.")
                    break
        finally:
            reel.SPEC["mascot"] = saved

def stage_visible(spec, lines, bounds):
    """For stage scenes: the strings actually visible mid-scene (persisting objects included)."""
    if not any(sc.get("type") == "stage" for sc in spec["scenes"]):
        return None
    sys.path.insert(0, HERE)
    import stage
    starts = _starts(spec, lines)
    return [stage.visible_strings(spec, starts, i, bounds) if sc.get("type") == "stage" else None for i, sc in enumerate(spec["scenes"])]

def _starts(spec, lines):
    if spec.get("pace_wps"):
        t, out = 0.2, []
        for text in lines:
            out.append(round(t, 2)); t += len(text.split()) / spec["pace_wps"] + spec.get("gap", 0.4)
        return out
    return [l[1] for l in spec["lines"]]

def stage_layout_checks(path):
    """Layout of stage scenes: text inside its box, nesting, no overlaps, no empty boxes, content zone, mascot, short labels, visible change."""
    sys.path.insert(0, HERE)
    import reel, stage
    reel.load_spec(path)
    if not any(sc.get("type") == "stage" for sc in reel.SPEC["scenes"]):
        return
    mb = reel.mascot_boxes()[0] if reel.SPEC.get("mascot") and reel.mascot_boxes() else None
    for level, code, msg in stage.layout_check(reel.SPEC, [l[1] for l in reel.SPEC["lines"]], reel.DUR, mb, draw_cls=reel.SoftDraw):
        add(level, code, msg)

def side_by_side(spec, lines, bounds, onscreen):
    out = ["", "## Script next to on-screen text (reviewer reads this)"]
    for i, sc in enumerate(spec["scenes"]):
        out.append(f"\n### Scene {i + 1} [{sc.get('type')}] {bounds[i][0]:.1f}-{bounds[i][1]:.1f}s")
        out.append(f"SAID : {lines[i] if i < len(lines) else '(no line)'}")
        for k, t in (onscreen[i] if i < len(onscreen) else []):
            out.append(f"SHOWN [{k or 'text'}]: {t}")
    return "\n".join(out)

# ----------------------------------------------------------------------------- video checks
STORY = False

def video_checks(path, bounds, sheet_path, ignore_boxes=()):
    import numpy as np
    probe = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
                           capture_output=True, text=True)
    dur = float(probe.stdout.strip() or 0)
    lo, hi = (60, 150) if STORY else (30, 60)
    if not lo <= dur <= hi:
        add("FAIL", "DURATION", f"Video is {dur:.1f} s (needs {lo} to {hi}).")
    elif dur > 50 and not STORY:
        add("INFO" if LENGTH_REASON else "WARN", "DURATION_LONG", f"Video is {dur:.1f} s. Target 35 to 45 s; over 50 s needs a stated reason in the summary.")
    fps = 10
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", path, "-vf", f"fps={fps},scale=270:480", "-f", "rawvideo",
                          "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
    frames = np.frombuffer(raw, np.uint8).reshape(-1, 480, 270, 3)
    gray = frames.astype(np.int16).mean(axis=3)
    # true background per row, taken from the empty left margin (text never goes there)
    bg = np.median(gray[:, :, :8], axis=(0, 2))[None, :, None]
    mask = np.abs(gray - bg) > 30
    for bx0, by0, bx1, by1 in ignore_boxes:          # the mascot is always on screen: do not count it as content
        mask[:, max(0, int(by0 / 4)):int(by1 / 4) + 1, max(0, int(bx0 / 4)):int(bx1 / 4) + 1] = False
    # Instagram safe zone: nothing in the top 230 px (rows < 57) or below y=1440 (rows > 360)
    bad = [i / fps for i in range(len(mask)) if mask[i, :57].sum() > 25 or mask[i, 360:].sum() > 25]
    if bad:
        add("FAIL", "SAFE_ZONE", f"Content outside the Instagram safe zone (above y=230 or below y=1440) at {bad[0]:.1f} to {bad[-1]:.1f} s.")
    # dead screens: content area (y 300-1440) nearly empty
    empty = [int(mask[i, 75:360].sum()) < 60 for i in range(len(mask))]
    runs, start = [], None
    for i, e in enumerate(empty + [False]):
        if e and start is None:
            start = i
        if not e and start is not None:
            runs.append((start / fps, (i - start) / fps)); start = None
    for s, length in runs:
        if length >= 0.5:
            add("FAIL", "DEAD_SCREEN", f"Nothing on screen for {length:.1f} s starting at {s:.1f} s. Viewers swipe on empty screens.")
        elif length >= 0.2:
            add("WARN", "BLANK_FLASH", f"Content area empty for about {length:.2f} s at {s:.1f} s (scene change). Make the next scene's first text appear sooner.")
    # contact sheet for the reviewer
    if sheet_path:
        from PIL import Image, ImageDraw
        if bounds:
            times = [max(0.0, min(dur - 0.3, b1 - 0.7)) for _, b1 in bounds]
        else:
            times = [t for t in np.arange(1.0, dur, 3.0)]
        cols = min(6, len(times)); rows = (len(times) + cols - 1) // cols
        sheet = Image.new("RGB", (cols * 270, rows * 500), (20, 20, 20))
        d = ImageDraw.Draw(sheet)
        for k, t in enumerate(times):
            im = Image.fromarray(frames[min(len(frames) - 1, int(t * fps))])
            x, y = (k % cols) * 270, (k // cols) * 500
            sheet.paste(im, (x, y + 20)); d.text((x + 6, y + 4), f"scene {k + 1}  t={t:.1f}s", fill=(255, 200, 80))
        sheet.save(sheet_path)
    return dur

# ----------------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("spec", nargs="?")
    ap.add_argument("--facts")
    ap.add_argument("--video")
    ap.add_argument("--sheet")
    ap.add_argument("--report")
    ap.add_argument("--legacy", action="store_true", help="old specs without a facts file")
    a = ap.parse_args()
    if not a.spec and not a.video:
        ap.error("give a spec and/or --video")
    facts = json.load(open(a.facts)) if a.facts else None
    global LENGTH_REASON
    LENGTH_REASON = bool(facts and facts.get("length_reason"))
    spec = lines = bounds = onscreen = None
    extra = ""
    if a.spec:
        spec, lines, bounds, dur = load_spec(a.spec)
        onscreen = text_checks(spec, lines, bounds, facts, a.legacy) or [scene_strings(sc) for sc in spec["scenes"]]
        extra = side_by_side(spec, lines, bounds, onscreen)
        mascot_overlap_checks(a.spec)
        stage_layout_checks(a.spec)
    if a.video:
        boxes = []
        if a.spec:
            sys.path.insert(0, HERE)
            import reel
            reel.load_spec(a.spec)
            boxes = reel.mascot_boxes() if reel.SPEC.get("mascot") else []
        video_checks(a.video, bounds, a.sheet, boxes)
    report = ["# Check report"]
    for level in ("FAIL", "WARN", "INFO"):
        for lv, code, msg in findings:
            if lv == level:
                report.append(f"- {lv} {code}: {msg}")
    nfail = sum(1 for f in findings if f[0] == "FAIL")
    nwarn = sum(1 for f in findings if f[0] == "WARN")
    report.append(f"\nResult: {nfail} FAIL, {nwarn} WARN." + (" Do not deliver." if nfail else " Reviewer pass still required."))
    text = "\n".join(report) + extra
    print(text)
    if a.report:
        open(a.report, "w").write(text + "\n")
    sys.exit(1 if nfail else 0)

if __name__ == "__main__":
    main()
