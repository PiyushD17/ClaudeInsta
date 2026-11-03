#!/usr/bin/env python3
"""Score the REHOOK (the mid-video second hook) with the same five checks as hookscore.py, with a lower bar.

Opening hook (hookscore.py): STRONG = overall 70+, every component 55+, no flags.
Rehook (this script):        PASS   = overall 60+, every component 40+, no flags.  Far above WEAK (below 50), a little below the opening hook.

Usage: python3 rehookscore.py out/dayNN_rehooks.txt     (one candidate per line, ranked; exit 0 only if the best one passes)
       python3 rehookscore.py --hook "But what happens when the balancer itself breaks?"
"""
import argparse, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "skills", "ig-reel"))
import hookscore as hs

MIN_OVERALL, MIN_COMPONENT = 60, 40

def score(text):
    results, overall, _verdict, flags = hs.run(text)
    comps = {k: round(v[0]) for k, v in results.items()}
    ok = overall >= MIN_OVERALL and min(comps.values()) >= MIN_COMPONENT and not flags
    return round(overall, 1), comps, flags, ok

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("input", nargs="?")
    ap.add_argument("--hook")
    a = ap.parse_args()
    lines = [a.hook] if a.hook else [l.strip() for l in open(a.input, encoding="utf-8") if l.strip()]
    rows = sorted(((score(l), l) for l in lines), key=lambda r: -r[0][0])
    for (ov, comps, flags, ok), l in rows:
        weakest = min(comps, key=comps.get)
        print(f"{'PASS' if ok else 'BELOW'} {ov:5.1f}  weakest {weakest} {comps[weakest]:>3}  {l}" + (f"  FLAGS: {flags}" if flags else ""))
    sys.exit(0 if rows[0][0][3] else 1)
