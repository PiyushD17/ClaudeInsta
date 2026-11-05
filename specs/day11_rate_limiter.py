LINES = [
    "What actually goes into your rate limiter? 1 Redis script, 1 formula, 1 HTTP header.",
    "A rate limiter stops a client from sending too many requests in a given amount of time.",
    "One way to build it: a counter, an atomic check, a smoother window, and a 429 response.",
    "First, the counter: in Redis, a fixed-window limiter keeps one string key per window and bumps it with INCR. If the key does not exist, INCR creates it at 1. The key includes the window number, so a new window starts a fresh count.",
    "But how does your limiter stop 2 requests from reading the same count at once?",
    "Second, the atomic check: that race comes from separate commands, so run INCR, EXPIRE and the limit check inside a single Lua EVAL call. Redis executes Lua scripts atomically, so no other command can interleave.",
    "Third, a smoother window: a fixed window has an edge problem. A client could send 10 requests at second 9 and 10 more at second 11. That is 20 requests in 2 seconds, within a limit of 10 per 10 seconds.",
    "Cloudflare extrapolates from the previous counter. With a limit of 50 requests per minute, 18 requests in the current minute, which started 15 seconds ago, and 42 in the previous minute, the rate is 49.5 requests.",
    "It is an approximation, yet across 400 million requests only 0.003% were wrongly allowed or rate limited.",
    "Fourth, the response: a blocked client gets HTTP 429 Too Many Requests, which may include a Retry-After header.",
    "Retry-After holds either a number of seconds to wait, or a date after which to retry.",
    "Another algorithm is the token bucket. Stripe gives every user a bucket: each request removes a token, more tokens slowly drip in, and an empty bucket rejects it.",
    "The catch: counting is not enough. Stripe also runs a concurrent requests limiter, for example 20 API requests in progress at the same time, and load shedders that look at the whole system.",
    "So when a rate limiter blocks you, you now know the script, the formula and the header behind it. Follow for one tech topic a day.",
]

def wi(line, token, k=1):
    """'wN' anchor: the k-th word of script line `line` (1-based) that starts with `token`."""
    ws = [w.strip(".,:?\"").lower() for w in LINES[line - 1].split()]
    hits = [i + 1 for i, w in enumerate(ws) if w.startswith(token.lower())]
    return "w%d" % hits[k - 1]

# ---- layout grid (1080 x 1920): title area y 290-510, diagram y 540-940, lower area (terminal) y 975-1375, mascot top-right next to the @tag
TITLE = lambda i, parts, size=44, y=440: {"kind": "title", "id": "t%d" % i, "t": -0.25, "x": 540, "y": y, "parts": parts, "size": size, "maxw": 820}
DY, DH = 540, 400
LOW = dict(x=40, y=975, w=1000, h=400)
CLIENT = (155, DY + 350); LIMIT_IN = (330, DY + 350); SERVER = (925, DY + 350)

def pkt(pid, t, color="mint", text="GET", to="server", out=None):
    path = [CLIENT, LIMIT_IN] if to == "limiter" else ([CLIENT, SERVER] if to == "server" else [LIMIT_IN, CLIENT])
    o = {"kind": "packet", "id": pid, "t": t, "path": path, "text": text, "color": color, "dur": 1.1 if to != "server" else 1.6, "hold": to == "limiter", "w": 96, "h": 44}
    if out is not None: o["out"] = out
    return o

def term(tid, title, lines, t=-0.2, size=29, h=None, cps=36):
    return {"kind": "terminal", "id": tid, "t": t, "x": LOW["x"], "y": LOW["y"], "w": LOW["w"], "h": h or LOW["h"], "title": title, "size": size, "cps": cps, "lines": lines}

SPEC = {
    "tag": "@TECHINABITE",
    "pace_wps": 3.2,
    "captions": False,
    "format": "story",
    "music": {"bpm": 104, "seed": 11, "variant": 1},
    "mascot": {"x": 1000, "y": 300, "size": 90},
    "lines": LINES,
    "scenes": [
        # 1 hook: the diagram the whole story runs on is there from frame 0
        {"type": "stage", "objects": [
            {"kind": "label", "id": "k", "t": -0.5, "x": 540, "y": 292, "text": "TECH IN A BITE", "size": 28, "color": "amber", "align": "c", "font": "med"},
            {"kind": "title", "id": "h1", "t": -0.5, "x": 540, "y": 326, "parts": [("What actually goes into\nyour ", "white"), ("rate limiter?", "amber")], "size": 54, "maxw": 820, "underline": False},
            {"kind": "title", "id": "h2", "t": wi(1, "1"), "x": 540, "y": 482, "parts": [("1 Redis script · 1 formula · 1 HTTP header", "mint")], "size": 34, "underline": False, "maxw": 820},
            {"kind": "panel", "id": "client", "t": -0.4, "x": 40, "y": DY, "w": 230, "h": DH, "label": "Client", "icon": "user", "body": "user", "body_color": "gray"},
            {"kind": "panel", "id": "limiter", "t": -0.3, "x": 300, "y": DY, "w": 480, "h": DH, "label": "Rate limiter", "icon": "gear", "color": "amber", "value": "0/10"},
            {"kind": "grid", "id": "win", "in": "limiter", "t": -0.3, "x": 330, "y": DY + 130, "w": 420, "h": 80, "cols": 10, "rows": 1, "n": 0, "color": "mint", "label": "Requests in this window"},
            {"kind": "server", "id": "server", "t": -0.2, "x": 810, "y": DY, "w": 230, "h": DH, "label": "API server", "color": "cyan"},
            pkt("p1", wi(1, "redis"), "mint"), pkt("p2", wi(1, "formula"), "mint"), pkt("p3", wi(1, "http"), "mint")],
         "events": [{"id": "win", "t": wi(1, "formula"), "dur": 0.3, "set": {"n": 1}}, {"id": "win", "t": wi(1, "http"), "dur": 0.3, "set": {"n": 2}}, {"id": "win", "t": wi(1, "header"), "dur": 0.3, "set": {"n": 3}},
                    {"id": "limiter", "t": wi(1, "formula"), "dur": 0.0, "set": {"value": "1/10"}}, {"id": "limiter", "t": wi(1, "http"), "dur": 0.0, "set": {"value": "2/10"}}, {"id": "limiter", "t": wi(1, "header"), "dur": 0.0, "set": {"value": "3/10"}}]},
        # 2 what it does: requests pass, then too many are stopped
        {"type": "stage", "objects": [
            TITLE(2, [("Rate limiting: ", "white"), ("too many requests", "pink")]),
            pkt("p4", wi(2, "stops"), "mint"), pkt("p5", wi(2, "client"), "mint"),
            pkt("p6", wi(2, "too"), "pink", "GET", "limiter", out=4.6), pkt("p7", wi(2, "many"), "pink", "GET", "limiter", out=4.6)],
         "clear": ["k", "h1", "h2"],
         "events": [{"id": "limiter", "t": wi(2, "sending"), "dur": 0.0, "set": {"value": "10/10", "value_color": "pink"}},
                    {"id": "win", "t": wi(2, "stops"), "dur": 2.4, "set": {"n": 10}}, {"id": "win", "t": wi(2, "too"), "dur": 0.0, "set": {"color": "pink"}}]},
        # 3 the four building blocks
        {"type": "stage", "objects": [
            {"kind": "dots", "id": "steps", "t": -0.2, "x": 540, "y": 335, "n": 4, "active": -1, "spacing": 220,
             "labels": ["Counter", "Atomic check", "Window", "429"]}],
         "clear": ["t2", "p6", "p7"],
         "events": [{"id": "steps", "t": wi(3, "counter"), "dur": 0.0, "set": {"active": 0}},
                    {"id": "steps", "t": wi(3, "atomic"), "dur": 0.0, "set": {"active": 1}},
                    {"id": "steps", "t": wi(3, "smoother"), "dur": 0.0, "set": {"active": 2}},
                    {"id": "steps", "t": wi(3, "429"), "dur": 0.0, "set": {"active": 3}},
                    ]},
        # 4 counter: one Redis key per window
        {"type": "stage", "objects": [
            TITLE(4, [("Counter: ", "amber"), ("one key per window", "white")]),
            {"kind": "store", "id": "redis", "in": "limiter", "t": wi(4, "redis"), "x": 320, "y": DY + 100, "w": 440, "h": 280, "label": "Redis (example)", "rows": []},
            term("r4", "Example: redis-cli", [
                {"text": "> INCR ratelimit:user123:7", "type": True, "color": "white", "at": wi(4, "incr")},
                {"text": "(integer) 1", "color": "mint", "at": wi(4, "creates")},
                {"text": "> INCR ratelimit:user123:8", "type": True, "color": "white", "at": wi(4, "window", 2)},
                {"text": "(integer) 1", "color": "mint", "at": wi(4, "fresh")}], t=wi(4, "incr"))],
         "events": [{"id": "steps", "t": -0.2, "dur": 0.0, "set": {"active": 0}},
                    {"id": "limiter", "t": -0.2, "dur": 0.0, "set": {"value": "", "value_color": "amber"}},
                    {"id": "redis", "t": wi(4, "key"), "dur": 0.0, "set": {"rows": [["ratelimit:user123:7", "-"]], "hl": 0}},
                    {"id": "redis", "t": wi(4, "if"), "dur": 0.0, "set": {"rows": [], "hl": None}},
                                        {"id": "redis", "t": wi(4, "creates"), "dur": 0.0, "set": {"rows": [["ratelimit:user123:7", "1"]], "hl": 0}},
                    {"id": "redis", "t": wi(4, "window", 2), "dur": 0.0, "set": {"rows": [["ratelimit:user123:7", "1"], ["ratelimit:user123:8", "1"]], "hl": 1}}],
         "clear": ["win"]},
        # 5 rehook: two requests read the same count
        {"type": "stage", "objects": [
            {"kind": "question", "id": "q5", "t": -0.25, "x": 540, "y": 466, "parts": [("2 requests read the same ", "white"), ("count", "amber"), (" at once?", "white")], "size": 34},
            dict(pkt("pa", wi(5, "2"), "cyan", "A", "limiter", out=4.8), path=[(155, DY + 290), (330, DY + 290)]), pkt("pb", wi(5, "requests"), "purple", "B", "limiter", out=4.8),
            term("r5", "Example: separate GET and SET commands", [
                {"text": "A > GET ratelimit:user123:7   -> \"9\"", "color": "cyan", "at": wi(5, "reading")},
                {"text": "B > GET ratelimit:user123:7   -> \"9\"", "color": "purple", "at": wi(5, "same")},
                {"text": "A > SET ratelimit:user123:7 10", "color": "cyan", "at": wi(5, "count")},
                {"text": "B > SET ratelimit:user123:7 10   both allowed", "color": "red", "hl": True, "at": wi(5, "once")}])],
         "clear": ["t4", "r4"], "focus": ["limiter", "steps"],
         "events": [{"id": "redis", "t": 0.0, "dur": 0.0, "set": {"rows": [["ratelimit:user123:7", "9"]], "hl": 0}},
                    {"id": "redis", "t": wi(5, "once"), "dur": 0.0, "set": {"rows": [["ratelimit:user123:7", "10"]], "value_color": "pink"}}]},
        # 6 atomic check: one Lua EVAL call
        {"type": "stage", "objects": [
            TITLE(6, [("Atomic check: ", "cyan"), ("one Lua EVAL call", "white")]),
            term("r6", "Example: EVAL Lua script (simplified)", [
                {"text": "count = INCR key", "type": True, "color": "white", "at": wi(6, "incr")},
                {"text": "if count == 1 then EXPIRE key window end", "type": True, "color": "white", "at": wi(6, "expire")},
                {"text": "return count <= limit", "type": True, "color": "mint", "at": wi(6, "limit")},
                {"text": "-- one atomic step: no other command can interleave", "color": "gray", "at": wi(6, "atomically")}], cps=40)],
         "clear": ["q5", "pa", "pb", "r5"], "focus": [],
         "events": [{"id": "steps", "t": -0.2, "dur": 0.0, "set": {"active": 1}},
                    {"id": "redis", "t": 0.0, "dur": 0.0, "set": {"rows": [["ratelimit:user123:7", "9"]], "value_color": "amber", "hl": 0}},
                    {"id": "limiter", "t": wi(6, "single"), "dur": 0.0, "set": {"hl": True}},
                    {"id": "redis", "t": wi(6, "executes"), "dur": 0.0, "set": {"rows": [["ratelimit:user123:7", "10"]]}}]},
        # 7 smoother window: the fixed-window edge
        {"type": "stage", "objects": [
            TITLE(7, [("Fixed window: ", "pink"), ("the edge problem", "white")]),
            {"kind": "panel", "id": "w1", "t": wi(7, "fixed"), "x": 40, "y": 975, "w": 490, "h": 400, "label": "Window: seconds 0-10", "icon": "clock", "level": 0},
            {"kind": "panel", "id": "w2", "t": wi(7, "fixed"), "x": 550, "y": 975, "w": 490, "h": 400, "label": "Window: seconds 10-20", "icon": "clock", "level": 0},
            {"kind": "grid", "id": "g1", "in": "w1", "t": wi(7, "fixed"), "x": 70, "y": 1110, "w": 430, "h": 70, "cols": 10, "rows": 1, "n": 0, "color": "amber"},
            {"kind": "grid", "id": "g2", "in": "w2", "t": wi(7, "fixed"), "x": 580, "y": 1110, "w": 430, "h": 70, "cols": 10, "rows": 1, "n": 0, "color": "amber"},
            {"kind": "pill", "id": "s9", "in": "w1", "t": wi(7, "second"), "x": 285, "y": 1270, "text": "at second 9", "color": "amber", "mono": True},
            {"kind": "pill", "id": "s11", "in": "w2", "t": wi(7, "second", 2), "x": 795, "y": 1270, "text": "at second 11", "color": "amber", "mono": True}],
         "clear": ["t6", "r6"], "focus": ["limiter", "steps"],
         "events": [{"id": "steps", "t": -0.2, "dur": 0.0, "set": {"active": 2}},
                    {"id": "limiter", "t": 0.0, "dur": 0.0, "set": {"hl": False, "value": "10/10s"}},
                    {"id": "g1", "t": wi(7, "second"), "dur": 0.6, "set": {"n": 10}},
                    {"id": "g2", "t": wi(7, "second", 2), "dur": 0.6, "set": {"n": 10}},
                    {"id": "redis", "t": 0.0, "dur": 0.0, "set": {"rows": [["ratelimit:user123:0", "0"], ["ratelimit:user123:1", "0"]], "hl": None}},
                    {"id": "redis", "t": wi(7, "second"), "dur": 0.0, "set": {"rows": [["ratelimit:user123:0", "10"], ["ratelimit:user123:1", "0"]], "hl": 0}},
                    {"id": "redis", "t": wi(7, "second", 2), "dur": 0.0, "set": {"rows": [["ratelimit:user123:0", "10"], ["ratelimit:user123:1", "10"]], "hl": 1}},
                    {"id": "t7", "t": wi(7, "20"), "dur": 0.0, "set": {"parts": [("20 requests ", "pink"), ("in 2 seconds", "white")]}},
                    {"id": "w1", "t": wi(7, "20"), "dur": 0.0, "set": {"hl": True}},
                    {"id": "w2", "t": wi(7, "20"), "dur": 0.0, "set": {"hl": True}}]},
        # 8 Cloudflare's previous-counter estimate
        {"type": "stage", "objects": [
            TITLE(8, [("Cloudflare: ", "pink"), ("previous counter", "white")]),
            term("r8", "Cloudflare's example", [
                {"text": "limit:           50 requests per minute", "color": "gray", "at": wi(8, "limit")},
                {"text": "current minute:  18 requests, started 15 s ago", "color": "gray", "at": wi(8, "18")},
                {"text": "previous minute: 42 requests", "color": "gray", "at": wi(8, "42")},
                {"text": "rate = 42 * ((60-15)/60) + 18", "type": True, "color": "white", "at": wi(8, "minute", 3), "pause": 0.1},
                {"text": "     = 42 * 0.75 + 18", "type": True, "color": "white", "pause": 0.1},
                {"text": "     = 49.5 requests", "type": True, "color": "mint", "hl": True, "hlcolor": "mint"}], cps=75)],
         "clear": ["t7", "w1", "w2", "g1", "g2", "s9", "s11"], "focus": ["limiter", "steps"],
         "events": [{"id": "limiter", "t": wi(8, "limit"), "dur": 0.0, "set": {"value": "50 / min"}},
                    {"id": "redis", "t": 0.0, "dur": 0.0, "set": {"rows": [], "hl": None}},
                    {"id": "redis", "t": wi(8, "18"), "dur": 0.0, "set": {"rows": [["current minute", "18"]], "hl": 0}},
                    {"id": "redis", "t": wi(8, "42"), "dur": 0.0, "set": {"rows": [["current minute", "18"], ["previous minute", "42"]], "hl": 1}}]},
        # 9 how accurate the estimate is
        {"type": "stage", "objects": [
            TITLE(9, [("400 million requests: ", "white"), ("0.003% wrong", "mint")])],
         "clear": ["t8"],
         "events": [{"id": "redis", "t": wi(9, "approximation"), "dur": 0.0, "set": {"rows": [["current minute", "18"], ["previous minute", "42"], ["estimated rate", "49.5"]], "hl": 2}}]},
        # 10 the response: 429 with Retry-After
        {"type": "stage", "objects": [
            TITLE(10, [("Response: ", "mint"), ("HTTP 429", "pink")]),
            pkt("p429", wi(10, "gets"), "pink", "429", "back", out=6.5),
            term("r10", "Example response (RFC 6585)", [
                {"text": "HTTP/1.1 429 Too Many Requests", "type": True, "color": "red", "at": wi(10, "http")},
                {"text": "Content-Type: text/html", "color": "gray", "at": wi(10, "requests")},
                {"text": "Retry-After: 3600", "color": "white", "flag": "Retry-After", "flagcolor": "mint", "at": wi(10, "retry-after")}])],
         "clear": ["t9", "r8"], "focus": ["limiter", "steps", "client"],
         "events": [{"id": "steps", "t": -0.2, "dur": 0.0, "set": {"active": 3}},
                    {"id": "limiter", "t": 0.0, "dur": 0.0, "set": {"value": "10/10", "value_color": "pink"}},
                    {"id": "redis", "t": 0.0, "dur": 0.0, "set": {"rows": [["ratelimit:user123:7", "11"]], "hl": 0, "value_color": "pink"}}]},
        # 11 Retry-After: seconds or a date
        {"type": "stage", "objects": [
            TITLE(11, [("Retry-After: ", "mint"), ("seconds or a date", "white")]),
            term("r11", "Retry-After: two formats (MDN examples)", [
                {"text": "Retry-After: 120", "color": "white", "flag": "120", "flagcolor": "mint", "at": wi(11, "number")},
                {"text": "# seconds to wait", "color": "gray", "at": wi(11, "seconds")},
                {"text": "Retry-After: Wed, 21 Oct 2015 07:28:00 GMT", "color": "white", "flag": "Wed, 21 Oct 2015 07:28:00 GMT", "flagcolor": "cyan", "at": wi(11, "date")},
                {"text": "# date after which to retry", "color": "gray", "at": wi(11, "retry", 2)}])],
         "clear": ["t10", "r10", "p429"]},
        # 12 token bucket
        {"type": "stage", "objects": [
            TITLE(12, [("Token bucket ", "amber"), ("(Stripe)", "white")]),
            {"kind": "grid", "id": "tokens", "in": "limiter", "t": -0.2, "x": 330, "y": DY + 130, "w": 420, "h": 80, "cols": 10, "rows": 1, "n": 7, "color": "amber", "label": "Tokens: one bucket per user"},
            pkt("pt1", wi(12, "request"), "mint", "GET", "server"),
            pkt("pt2", wi(12, "rejects"), "pink", "GET", "limiter", out=3.0)],
         "clear": ["t11", "r11", "redis", "steps"],
         "events": [{"id": "limiter", "t": 0.0, "dur": 0.0, "set": {"label": "Token bucket", "value": "", "value_color": "amber"}},
                    {"id": "tokens", "t": wi(12, "removes"), "dur": 0.4, "set": {"n": 6}},
                    {"id": "tokens", "t": wi(12, "drip"), "dur": 1.0, "set": {"n": 8}},
                    {"id": "tokens", "t": wi(12, "empty"), "dur": 0.8, "set": {"n": 0, "color": "pink"}},
                    {"id": "limiter", "t": wi(12, "rejects"), "dur": 0.0, "set": {"value": "0 tokens", "value_color": "pink"}}]},
        # 13 the catch: Stripe runs more than request counting
        {"type": "stage", "objects": [
            TITLE(13, [("Stripe: ", "white"), ("more than counting", "pink")]),
            {"kind": "panel", "id": "c1", "t": wi(13, "counting"), "x": 40, "y": 985, "w": 1000, "h": 110, "label": "Request rate limiter", "icon": "gear", "color": "amber", "value": "N requests/s per user", "compact": True},
            {"kind": "panel", "id": "c2", "t": wi(13, "concurrent"), "x": 40, "y": 1120, "w": 1000, "h": 110, "label": "Concurrent requests limiter", "icon": "gear", "color": "cyan", "value": "20 in progress", "compact": True},
            {"kind": "panel", "id": "c3", "t": wi(13, "load"), "x": 40, "y": 1255, "w": 1000, "h": 110, "label": "Load shedder", "icon": "shield", "color": "pink", "value": "whole system", "compact": True}],
         "clear": ["t12", "tokens", "pt1", "pt2"], "focus": ["c1", "c2", "c3"],
         "events": [{"id": "c2", "t": wi(13, "20"), "dur": 0.0, "set": {"hl": True}}, {"id": "c2", "t": wi(13, "load"), "dur": 0.0, "set": {"hl": False}}, {"id": "c3", "t": wi(13, "whole"), "dur": 0.0, "set": {"hl": True}}]},
        # 14 recap and follow
        {"type": "stage", "objects": [
            {"kind": "dots", "id": "recap", "t": -0.2, "x": 540, "y": 640, "n": 3, "active": -1, "spacing": 300, "labels": ["Redis script", "Formula", "HTTP header"],
             "colors": ["cyan", "pink", "mint"], "caption": [("Inside your ", "white"), ("rate limiter", "amber")]},
            {"kind": "endcard", "id": "end", "t": wi(14, "follow"), "y": 1020, "text": "@techinabite"},
            {"kind": "title", "id": "endl", "t": wi(14, "follow"), "x": 540, "y": 1180, "parts": [("Follow for one tech topic a day.", "white")], "size": 36, "underline": False}],
         "events": [{"id": "recap", "t": wi(14, "script"), "dur": 0.0, "set": {"active": 0}}, {"id": "recap", "t": wi(14, "formula"), "dur": 0.0, "set": {"active": 1}}, {"id": "recap", "t": wi(14, "header"), "dur": 0.0, "set": {"active": 2}}],
         "clear": True},
    ],
}
