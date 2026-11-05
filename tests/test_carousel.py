"""Tests for carousel.py and carousel_check.py: the template renders clean, text overflow is caught, and the checker catches the mistakes it is for.
Run: python3 tests/test_carousel.py"""
import os, sys, json, subprocess, tempfile, copy
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, root)
import carousel
spec = carousel.load_spec(os.path.join(root, "specs", "_example_post.py"))
tmp = tempfile.mkdtemp()
paths, errs = carousel.render(spec, os.path.join(tmp, "t"))
assert not errs, errs                                          # template layout is clean
assert len(paths) == 6 and all(os.path.getsize(p) > 10000 for p in paths)
bad = copy.deepcopy(spec)
bad["slides"][1]["bullets"] = ["word " * 40] * 6                # far too much text
_, errs = carousel.render(bad, os.path.join(tmp, "b"))
assert any("runs to" in e for e in errs), errs                  # overflow is detected
def check(specmod, facts):
    sp = os.path.join(tmp, "s.py"); open(sp, "w").write("SPEC = " + repr(specmod))
    fp = os.path.join(tmp, "f.json"); json.dump(facts, open(fp, "w"))
    r = subprocess.run([sys.executable, os.path.join(root, "carousel_check.py"), sp, "--facts", fp, "--render", os.path.join(tmp, "c")], capture_output=True, text=True)
    return r.returncode, r.stdout
facts = {"topic_terms": ["your topic"], "claims": [{"say": "x", "source": "https://example.com", "quote": "quote copied from the page text", "slides": [2, 3, 4, 5, 6]}],
         "share": {"slide": 5, "who": "someone", "why": "because"}, "illustrative_numbers": []}
rc, out = check(spec, facts)
assert "NO_CLAIM" not in out and "SHARE" not in out and "SLIDE_COUNT" not in out, out
rc, out = check(spec, dict(facts, claims=[]))
assert rc == 1 and "NO_CLAIM" in out, out                      # slides without a claim fail
rc, out = check(spec, {k: v for k, v in facts.items() if k != "share"})
assert "SHARE" in out, out                                      # missing send-or-save slide fails
few = copy.deepcopy(spec); few["slides"] = few["slides"][:3]
rc, out = check(few, facts)
assert "SLIDE_COUNT" in out, out                                # fewer than 5 slides fails
flat = copy.deepcopy(spec)
for s in flat["slides"]: s["level"] = 1
rc, out = check(flat, facts)
assert "DEEP_DIVE" in out, out                                  # no deep dive fails
num = copy.deepcopy(spec); num["slides"][1]["bullets"] = ["It makes 37 requests per second."]
rc, out = check(num, facts)
assert "UNSOURCED_NUMBER" in out, out                           # numbers must come from a quote
print("OK: carousel renders clean; overflow, missing claims, share, slide count, levels and unsourced numbers are caught.")
