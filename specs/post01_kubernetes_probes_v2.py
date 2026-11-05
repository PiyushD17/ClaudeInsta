# Post 01: Kubernetes liveness, readiness and startup probes (carousel v2: stage slides, STYLE_GUIDE.md)
# Slide 1080 x 1350; content zone x 60-1020, y 200-1240; title at y 232.
POD = dict(x=60, y=420, w=960, h=330)

SPEC = {
    "tag": "@TECHINABITE",
    "topic": "Kubernetes probes",
    "slides": [
        # 1 cover
        {"type": "cover", "level": 1,
         "title": [("What actually goes into", False), ("your Kubernetes", False), ("probes?", True)],
         "sub": "3 probes, 4 mechanisms, 1 trap: from the big picture to the real YAML.",
         "chips": ["7 SLIDES", "BIG PICTURE TO DEEP DIVE"]},

        # 2 three probes, three questions
        {"type": "stage", "level": 1, "title": [("3 Kubernetes probes, ", "white"), ("3 questions", "amber")],
         "objects": [
            {"kind": "panel", "id": "pod", "x": 60, "y": 400, "w": 960, "h": 800, "label": "Pod", "icon": "container", "color": "cyan"},
            {"kind": "panel", "id": "c", "in": "pod", "x": 90, "y": 490, "w": 900, "h": 680, "label": "Container", "icon": "app", "level": 1},
            {"kind": "panel", "id": "sp", "in": "c", "x": 120, "y": 580, "w": 840, "h": 170, "label": "Startup probe", "icon": "clock", "color": "purple", "level": 2},
            {"kind": "pill", "id": "spq", "in": "sp", "x": 540, "y": 690, "text": "Is the app started?", "color": "purple", "filled": False},
            {"kind": "panel", "id": "lp", "in": "c", "x": 120, "y": 770, "w": 840, "h": 170, "label": "Liveness probe", "icon": "gear", "color": "pink", "level": 2},
            {"kind": "pill", "id": "lpq", "in": "lp", "x": 540, "y": 880, "text": "Restart the container?", "color": "pink", "filled": False},
            {"kind": "panel", "id": "rp", "in": "c", "x": 120, "y": 960, "w": 840, "h": 170, "label": "Readiness probe", "icon": "check", "color": "mint", "level": 2},
            {"kind": "pill", "id": "rpq", "in": "rp", "x": 540, "y": 1070, "text": "Ready for traffic?", "color": "mint", "filled": False}]},

        # 3 what each failure does
        {"type": "stage", "level": 1, "title": [("When a probe ", "white"), ("fails", "pink")],
         "objects": [
            {"kind": "pill", "id": "thr", "x": 540, "y": 336, "text": "after failureThreshold failures in a row", "color": "gray", "filled": False, "size": 26},
            {"kind": "panel", "id": "lv", "x": 60, "y": 390, "w": 470, "h": 420, "label": "Liveness fails", "icon": "gear", "color": "pink"},
            {"kind": "store", "id": "ctr", "in": "lv", "x": 90, "y": 490, "w": 410, "h": 220, "label": "Container (example)", "icon": "app", "color": "pink",
             "rows": [["liveness", "failed", "pink"], ["restarts", "0 -> 1", "amber"]], "hl": 0},
            {"kind": "pill", "id": "lvr", "in": "lv", "x": 295, "y": 755, "text": "killed; restartPolicy restarts", "color": "pink", "size": 24},
            {"kind": "panel", "id": "rd", "x": 550, "y": 390, "w": 470, "h": 420, "label": "Readiness fails", "icon": "check", "color": "mint"},
            {"kind": "store", "id": "eps", "in": "rd", "x": 580, "y": 490, "w": 410, "h": 220, "label": "EndpointSlice", "icon": "folder", "color": "mint",
             "rows": [["pod A IP", "ready", "mint"], ["pod B IP", "removed", "pink"]], "hl": 1},
            {"kind": "pill", "id": "rdr", "in": "rd", "x": 785, "y": 755, "text": "no Service traffic", "color": "mint"},
            {"kind": "panel", "id": "st", "x": 60, "y": 840, "w": 960, "h": 370, "label": "Startup probe first", "icon": "clock", "color": "purple"},
            {"kind": "terminal", "id": "gate", "in": "st", "x": 90, "y": 930, "w": 900, "h": 250, "title": "Kubernetes docs",
             "lines": [{"text": "liveness / readiness: not run", "color": "gray"},
                       {"text": "...until the startup probe succeeds", "color": "white"},
                       {"text": "startup fails -> killed, then restartPolicy", "color": "pink", "hl": True}]}]},

        # 4 four ways to check
        {"type": "stage", "level": 2, "title": [("4 ways ", "amber"), ("a probe checks", "white")],
         "objects": [
            {"kind": "panel", "id": "m", "x": 60, "y": 440, "w": 960, "h": 520, "label": "Probe mechanisms", "icon": "magnifier", "color": "amber"},
            {"kind": "table", "id": "tbl", "in": "m", "x": 100, "y": 540, "w": 880, "size": 28, "hl": 2, "hlcolor": "amber",
             "cols": ["MECHANISM", "SUCCESS WHEN"],
             "rows": [["exec", "command exits 0"], ["grpc", "status is SERVING"], ["httpGet", "200 <= code < 400"], ["tcpSocket", "port is open"]]},
            {"kind": "pill", "id": "one", "in": "m", "x": 540, "y": 900, "text": "1 mechanism per probe", "color": "amber", "filled": False},
            {"kind": "terminal", "id": "res", "x": 60, "y": 1000, "w": 960, "h": 160, "title": "3 results",
             "lines": [{"text": "Success   Failure   Unknown (check again)", "color": "white"}]}]},

        # 5 deep dive: the real startup probe YAML and its time budget
        {"type": "stage", "level": 3, "title": [("Startup probe: ", "purple"), ("the real YAML", "white")],
         "objects": [
            {"kind": "terminal", "id": "yaml", "x": 60, "y": 380, "w": 960, "h": 480, "title": "Kubernetes docs example", "size": 28,
             "lines": [{"text": "livenessProbe:", "color": "pink"},
                       {"text": "  httpGet: {path: /healthz, port: liveness-port}", "color": "white"},
                       {"text": "  failureThreshold: 1", "color": "white"},
                       {"text": "  periodSeconds: 10", "color": "white"},
                       {"text": "startupProbe:", "color": "purple"},
                       {"text": "  httpGet: {path: /healthz, port: liveness-port}", "color": "white"},
                       {"text": "  failureThreshold: 30", "color": "white", "flag": "30", "flagcolor": "purple"},
                       {"text": "  periodSeconds: 10", "color": "white", "flag": "10", "flagcolor": "purple"}]},
            {"kind": "panel", "id": "bud", "x": 60, "y": 900, "w": 960, "h": 310, "label": "Startup time budget", "icon": "clock", "color": "purple"},
            {"kind": "label", "id": "calc", "in": "bud", "x": 540, "y": 990, "text": "failureThreshold 30 * periodSeconds 10", "font": "mono", "size": 30, "color": "gray", "align": "c"},
            {"kind": "label", "id": "calc2", "in": "bud", "x": 540, "y": 1040, "text": "= 300 s = 5 minutes max", "font": "mono", "size": 36, "color": "white", "align": "c"},
            {"kind": "pill", "id": "kill", "in": "bud", "x": 540, "y": 1140, "text": "no success? killed at 300 s", "color": "pink", "filled": False}]},

        # 6 deep dive: the trap and the rule of thumb (send-or-save slide)
        {"type": "stage", "level": 3, "title": [("The liveness ", "pink"), ("trap", "white")],
         "objects": [
            {"kind": "panel", "id": "tr", "x": 60, "y": 380, "w": 960, "h": 330, "label": "Wrong liveness probe", "icon": "cross", "color": "pink"},
            {"kind": "grid", "id": "pods", "in": "tr", "x": 100, "y": 480, "w": 880, "h": 70, "cols": 8, "rows": 1, "n": 3, "color": "pink", "label": "Containers restarting under load (example)"},
            {"kind": "pill", "id": "casc", "in": "tr", "x": 290, "y": 640, "text": "cascading failures", "color": "pink"},
            {"kind": "pill", "id": "tmo", "in": "tr", "x": 760, "y": 640, "text": "timeoutSeconds default: 1 s", "color": "pink", "filled": False},
            {"kind": "panel", "id": "rule", "x": 60, "y": 740, "w": 960, "h": 470, "label": "Liveness restart window", "icon": "check", "color": "mint"},
            {"kind": "label", "id": "f1", "in": "rule", "x": 540, "y": 840, "text": "initialDelaySeconds + failureThreshold * periodSeconds", "font": "mono", "size": 26, "color": "white", "align": "c", "maxw": 880},
            {"kind": "label", "id": "f2", "in": "rule", "x": 540, "y": 900, "text": "defaults: 0 + 3 * 10 = 30 s", "font": "mono", "size": 40, "color": "amber", "align": "c"},
            {"kind": "pill", "id": "rot", "in": "rule", "x": 540, "y": 1020, "text": "container starts slower? add startup probe", "color": "mint"},
            {"kind": "pill", "id": "rot2", "in": "rule", "x": 540, "y": 1130, "text": "liveness threshold > readiness", "color": "mint", "filled": False}]},

        # 7 takeaway
        {"type": "takeaway", "level": 3, "label": "RECAP", "title": "Kubernetes probes, recap",
         "points": ["**Startup** probe: is the app started? Gates the other two.",
                    "**Liveness** fails: container killed, restartPolicy restarts it. **Readiness** fails: no Service traffic.",
                    "Liveness window on defaults: **0 + 3 * 10 = 30 s**. Slower start? Add a startup probe."],
         "share": "Send this to whoever owns your probe YAML."},
    ],
}
