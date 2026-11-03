"""Regression test: check_spec.py must catch every mistake found in the faulty Day 05 trial video.
Run: python3 tests/test_check_spec.py"""
import subprocess, sys, os
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
r = subprocess.run([sys.executable, "check_spec.py", "tests/day05_regression/spec.py", "--facts", "tests/day05_regression/facts.json"],
                   cwd=root, capture_output=True, text=True)
need = ["WRONG_TERM", "COUNT_UNSOURCED", "ENUM_UNSOURCED", "ENTITY_SET", "SHORT_LABEL", "REHOOK_SCORE"]
missing = [c for c in need if c not in r.stdout]
assert r.returncode == 1, "checker should fail the faulty Day 05 spec"
assert not missing, f"checker missed: {missing}"
# legacy specs must still load and run without crashing
r2 = subprocess.run([sys.executable, "check_spec.py", "specs/day04_database_index.py", "--legacy"], cwd=root, capture_output=True, text=True)
assert "Traceback" not in r2.stderr, r2.stderr
print("OK: Day 05 mistakes are caught; legacy spec runs.")
