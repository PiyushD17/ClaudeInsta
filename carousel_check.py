#!/usr/bin/env python3
"""Pre-delivery checker for a Tech in a Bite carousel post.

Usage: python3 carousel_check.py specs/postNN_slug.py --facts specs/postNN_facts.json [--report out/postNN_check.md] [--render out/postNN]
Exit code 0 = no FAIL. Target: 0 FAIL and 0 WARN. A WARN means a slide is not good enough yet: fix it.

Facts file (JSON), written from sources the run actually opened:
{
  "topic_terms": ["RAG", "retrieval"],                  # every slide must show at least one, so each slide stands alone
  "terms": [{"use": "vector database", "never_say": ["vector store rule"]}],
  "illustrative_numbers": ["3"],                        # numbers invented for an example (must be labelled "Example" on the slide)
  "derived_numbers": {"30": "0 + 3 * 10 from the sourced defaults"},   # numbers computed from sourced numbers (say how; the reviewer checks it)
  "claims": [{"say": "...", "source": "https://...", "quote": "copied from the opened page", "slides": [2, 3]}],
  "share": {"slide": 5, "who": "a dev who ...", "why": "..."},     # exactly one slide worth sending or saving (not the cover)
  "saves": "why someone would save it"                  # optional note
}
"""
import argparse, json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "skills", "ig-reel"))
import carousel, hookscore as hs, rehookscore

findings = []
NUMWORDS = {"1": "one", "2": "two", "3": "three", "4": "four", "5": "five", "6": "six", "7": "seven", "8": "eight", "9": "nine", "10": "ten"}
def add(level, code, msg): findings.append((level, code, msg))
SKIP = {"type", "level", "highlight", "mascot", "_tag", "_topic", "color", "step"}

def strings(slide):
    if slide.get("type") in ("story", "cover_story") and not slide.get("objects"):
        out = [("headline", "".join(p[0] for p in slide["title"]).strip())]
        return out + strings_plain({k: v for k, v in slide.items() if k != "title"})
    if slide.get("objects") or slide.get("type") == "stage":
        import stage
        out = []
        if slide.get("title") and slide["type"] == "stage": out.append(("headline", "".join(p[0] for p in slide["title"])))
        for o in slide.get("objects", []): out += stage.obj_strings(o)
        rest = {k: v for k, v in slide.items() if k != "objects" and not (slide["type"] == "stage" and k == "title")}
        return out + strings_plain(rest)
    return strings_plain(slide)

def strings_plain(slide):
    out = []
    def walk(o, key=""):
        if isinstance(o, dict):
            for k, v in o.items():
                if k not in SKIP: walk(v, k)
        elif isinstance(o, list):
            for v in o: walk(v, key)
        elif isinstance(o, tuple):
            walk(o[0], key)
        elif isinstance(o, str): out.append((key, o.replace("**", "")))
    walk(slide)
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("spec"); ap.add_argument("--facts", required=True); ap.add_argument("--report"); ap.add_argument("--render")
    a = ap.parse_args()
    spec = carousel.load_spec(a.spec); facts = json.load(open(a.facts))
    slides = spec["slides"]; n = len(slides)
    texts = [strings(s) for s in slides]
    # structure
    if not 5 <= n <= 7: add("FAIL", "SLIDE_COUNT", f"{n} slides; a post has 5 to 7.")
    if slides[0]["type"] not in ("cover", "cover_story"): add("FAIL", "COVER", "Slide 1 must be the cover (cover_story).")
    if slides[-1]["type"] != "takeaway": add("FAIL", "TAKEAWAY", "The last slide must be the takeaway (it carries the closing call to action).")
    for i, s in enumerate(slides[1:-1], start=2):
        if s["type"] != "story":
            add("FAIL", "SLIDE_TYPE", f'Slide {i} is a "{s["type"]}" slide. Content slides are "story" slides (v3: one chapter per slide, ending on a rehook); the stage and old text/cards/flow/compare/detail templates are retired for posts.')
            continue
        hook = s.get("hook", "").replace("**", "")
        if not hook: add("FAIL", "NO_REHOOK", f"Slide {i} has no hook: every content slide ends on a rehook that the next slide pays off."); continue
        if len(hook.split()) > 18: add("WARN", "REHOOK_LONG", f'Slide {i} hook has {len(hook.split())} words (keep it under 18).')
        sc, comps, _fl, ok = rehookscore.score(hook)
        if not ok: add("FAIL", "REHOOK_SCORE", f'Slide {i} hook "{hook}" scores {sc} {comps} (need 60+ overall, 40+ each).')
        else: add("INFO", "REHOOK_SCORE", f'Slide {i} hook scores {sc}.')
    # no code on a carousel (owner rule, Nov 2026): concepts, not syntax
    for i, s in enumerate(slides, start=1):
        for o in s.get("objects", []):
            if o.get("kind") in ("terminal", "table"): add("FAIL", "CODE", f'Slide {i} has a {o["kind"]} object: posts explain concepts, no code or config.')
        for k, t in strings(s):
            if re.search(r"`|[{}]|^\$ |^> |\w+\(\)|:\s*\S+\s*$" if k == "code" else r"`|[{}]|^\$ |^> |\w+\(\)", t):
                add("FAIL", "CODE", f'Slide {i}: "{t[:50]}" looks like code; explain the concept in words.')
            for w in re.findall(r"\b[a-z]+[A-Z][A-Za-z]*\b", t):
                add("WARN", "CODE_TERM", f'Slide {i}: "{w}" is a config field name; say what it means in words.')
    lv = [s.get("level", 1) for s in slides]
    if lv != sorted(lv): add("FAIL", "LEVELS", f"Levels must never go back down: {lv}.")
    if lv[0] != 1 or lv[1] != 1: add("FAIL", "LEVELS", "Slides 1 and 2 must be level 1 (the high-level picture).")
    if not any(l == 3 and s["type"] != "takeaway" for l, s in zip(lv, slides)): add("FAIL", "DEEP_DIVE", "At least one non-takeaway slide must be level 3 (the deep dive).")
    if n >= 6 and 2 not in lv: add("WARN", "LEVELS", "No level 2 slide: add a how-it-works slide between the overview and the deep dive.")
    # cover hook
    cover = " ".join(t for t, _ in slides[0]["title"])
    _r, overall, _v, flags = hs.run(cover + ".")
    if overall < 70: add("FAIL", "COVER_SCORE", f'Cover headline "{cover}" scores {overall:.1f} on hookscore (need 70+). Write a stronger cover.')
    else: add("INFO", "COVER_SCORE", f'Cover headline "{cover}" scores {overall:.1f}.')
    # topic terms, never_say, short labels, numbers, word counts
    tt = [t.lower() for t in facts.get("topic_terms", [])]
    if not tt: add("FAIL", "TOPIC_TERMS", "facts file needs topic_terms.")
    ill = {str(x) for x in facts.get("illustrative_numbers", [])}
    claims = facts.get("claims", [])
    for i, items in enumerate(texts):
        shown = " ".join(t for _, t in items).lower()
        if tt and not any(t in shown for t in tt): add("FAIL", "FRAME_STANDALONE", f"Slide {i + 1} shows nothing that names the topic (needs one of {tt}).")
        words = sum(len(t.split()) for k, t in items if k not in ("label", "chips", "meta"))
        if words > 85: add("WARN", "TOO_MUCH_TEXT", f"Slide {i + 1} has {words} words; a slide must be readable in a few seconds (cut below 85).")
        for k, t in items:
            for term in facts.get("terms", []):
                for bad in term.get("never_say", []):
                    if bad.lower() in t.lower(): add("FAIL", "WRONG_TERM", f'Slide {i + 1}: "{bad}" must be "{term["use"]}".')
            nw = len(t.split())
            if k in ("title", "headline") and slides[i]["type"] in ("cover", "cover_story"): continue      # cover title lines are one headline split over lines
            if k not in ("label", "chips", "meta", "head", "kicker", "code", "object") and (nw <= 2 and not re.search(r"[\d.?!]", t)):
                add("FAIL", "SHORT_LABEL", f'Slide {i + 1} {k}: "{t}" is too short to stand alone; say what it is.')
        own = [c for c in claims if i + 1 in c.get("slides", [])]
        quotes = " ".join(c.get("quote", "") for c in own)
        qwords = set(re.findall(r"[a-z]+", quotes.lower()))
        derived = {str(x) for x in facts.get("derived_numbers", {})}
        for k, t in items:
            if k in ("chips", "meta") and re.fullmatch(r"\d+ SLIDES", t): continue
            for num in re.findall(r"\d[\d,.]*", t):
                num = num.rstrip(".,")
                if num in NUMWORDS and NUMWORDS[num] in qwords: continue      # "four ways" in the quote backs a "4" on the slide
                if num and num not in quotes and num not in ill and num not in derived:
                    add("FAIL", "UNSOURCED_NUMBER", f'Slide {i + 1}: "{num}" (in "{t[:50]}") is in no claim quote of that slide and not in illustrative_numbers.')
        if i > 0 and not own:
            add("FAIL", "NO_CLAIM", f"Slide {i + 1} has no claim (list it in a claim's \"slides\" with source URL and quote).")
    for c in claims:
        if not str(c.get("source", "")).startswith("http") or len(str(c.get("quote", ""))) < 15:
            add("FAIL", "BAD_CLAIM", f'Claim "{c.get("say", "")[:50]}" needs an http source and a quote copied from the page.')
    sh = facts.get("share")
    if not sh or not sh.get("who") or not sh.get("why") or not (2 <= sh.get("slide", 0) <= n): add("FAIL", "SHARE", 'facts need "share": {"slide": N (2..last), "who": "...", "why": "..."} (one slide worth sending or saving).')
    # rendering
    paths, errs = carousel.render(spec, a.render or os.path.join(HERE, "out", "check_tmp"))
    for e in errs: add("FAIL", "LAYOUT", e)
    fails = [f for f in findings if f[0] == "FAIL"]; warns = [f for f in findings if f[0] == "WARN"]
    lines = [f"# Carousel check: {spec.get('topic', '')}", ""]
    for i, items in enumerate(texts):
        lines.append(f"### Slide {i + 1} [{slides[i]['type']}, level {slides[i].get('level', 1)}]")
        lines += [f"SHOWN [{k}]: {t}" for k, t in items]; lines.append("")
    lines.append("## Findings")
    lines += [f"- {l} {c}: {m}" for l, c, m in findings] or ["- none"]
    lines.append(f"\nResult: {len(fails)} FAIL, {len(warns)} WARN. " + ("Reviewer pass still required." if not fails else "Do not deliver."))
    out = "\n".join(lines)
    if a.report: os.makedirs(os.path.dirname(a.report) or ".", exist_ok=True); open(a.report, "w").write(out)
    print("\n".join(l for l in lines if l.startswith("- ") or l.startswith("Result")))
    sys.exit(1 if fails else 0)
main()
