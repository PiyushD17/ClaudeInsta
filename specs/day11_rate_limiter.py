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
    ws = [w.strip(".,:?").lower() for w in LINES[line - 1].split()]
    hits = [i + 1 for i, w in enumerate(ws) if w.startswith(token.lower())]
    return "w%d" % hits[k - 1]

DOTS = lambda act, t=-0.3: {"kind": "dots", "id": "steps", "x": 540, "y": 345, "n": 4, "active": act, "t": t}
DLABEL = {"kind": "text", "id": "dl", "x": 540, "y": 392, "text": "Rate limiter building blocks", "size": 22, "color": "gray", "align": "c", "font": "med", "t": -0.3}
TITLE = lambda i, parts, size=42, y=458: {"kind": "brush", "id": "t%d" % i, "t": -0.2, "x": 540, "y": y, "parts": parts, "size": size}

SPEC = {
    "tag": "@TECHINABITE",
    "pace_wps": 3.2,
    "captions": False,
    "format": "story",
    "music": {"bpm": 104, "seed": 11, "variant": 1},
    "mascot": {"x": 900, "y": 1300, "size": 150},
    "lines": LINES,
    "scenes": [
        # 1 hook + base diagram
        {"type": "stage", "objects": [
            {"kind": "text", "id": "k", "t": -0.5, "x": 540, "y": 285, "text": "TECH IN A BITE", "size": 30, "color": "amber", "align": "c", "font": "med"},
            {"kind": "text", "id": "h1", "t": -0.5, "x": 540, "y": 330, "text": "What actually goes into your rate limiter?", "size": 64, "color": "white", "align": "c", "maxw": 900},
            {"kind": "text", "id": "h2", "t": wi(1, "1"), "x": 540, "y": 500, "text": "1 Redis script, 1 formula, 1 HTTP header.", "size": 46, "color": "amber", "align": "c", "maxw": 900},
            {"kind": "panel", "id": "cl", "t": 0.0, "x": 70, "y": 700, "w": 260, "h": 230, "title": "API client sending requests", "icon": "user"},
            {"kind": "panel", "id": "rl", "t": 0.0, "x": 400, "y": 700, "w": 290, "h": 230, "title": "Rate limiter for API requests", "icon": "gear", "color": "amber"},
            {"kind": "panel", "id": "api", "t": 0.0, "x": 760, "y": 700, "w": 250, "h": 230, "title": "Your API gets requests", "icon": "server", "color": "cyan"},
            {"kind": "arrow", "id": "a1", "t": 0.6, "points": [(330, 815), (400, 815)], "color": "mint"},
            {"kind": "arrow", "id": "a2", "t": 0.8, "points": [(690, 815), (760, 815)], "color": "mint"}]},
        # 2 what a rate limiter does
        {"type": "stage", "objects": [
            TITLE(2, [("Rate limiting: ", "white"), ("too many requests", "pink")], 44),
            {"kind": "meter", "id": "load", "x": 90, "y": 560, "w": 900, "h": 30, "value": 0.1, "segs": 30, "label": "Requests from one client in a given amount of time", "color": "mint", "t": wi(2, "sending")},
            {"kind": "chip", "id": "lim", "x": 540, "y": 1010, "text": "Rate limiter: too many requests are blocked", "color": "pink", "t": wi(2, "many"), "filled": False}],
         "clear": ["k", "h1", "h2"],
         "events": [{"id": "load", "t": wi(2, "sending"), "dur": 2.0, "set": {"value": 0.95, "color": "pink"}}]},
        # 3 four parts
        {"type": "stage", "objects": [
            TITLE(3, [("Rate limiter: ", "cyan"), ("its parts", "white")], 44, 400),
            {"kind": "panel", "id": "p1", "x": 90, "y": 500, "w": 900, "h": 100, "title": "Counter for requests", "color": "amber", "t": wi(3, "counter"), "tsize": 32},
            {"kind": "panel", "id": "p2", "x": 90, "y": 630, "w": 900, "h": 100, "title": "Atomic check of requests", "color": "cyan", "t": wi(3, "atomic"), "tsize": 32},
            {"kind": "panel", "id": "p3", "x": 90, "y": 760, "w": 900, "h": 100, "title": "Smoother window for requests", "color": "pink", "t": wi(3, "smoother"), "tsize": 32},
            {"kind": "panel", "id": "p4", "x": 90, "y": 890, "w": 900, "h": 100, "title": "429 response to requests", "color": "mint", "t": wi(3, "429"), "tsize": 32}],
         "clear": ["t2", "load", "lim", "cl", "rl", "api", "a1", "a2"]},
        # 4 part 1: counter
        {"type": "stage", "objects": [
            DOTS(0),
            DLABEL,
            TITLE(4, [("Counter: ", "amber"), ("count requests with INCR", "white")], 40),
            {"kind": "terminal", "id": "r4", "x": 90, "y": 520, "w": 900, "h": 170, "title": "Example: Redis counter key", "size": 26, "cps": 30, "t": wi(4, "incr"),
             "lines": [{"text": "INCR ratelimit:user123:7", "type": True, "color": "white", "pause": 1.8},
                       {"text": "(integer) 1", "color": "mint"}]},
            {"kind": "terminal", "id": "r4b", "x": 90, "y": 720, "w": 900, "h": 110, "title": "Example: key of the next window", "size": 26, "t": wi(4, "includes"),
             "lines": [{"text": "ratelimit:user123:8", "color": "amber"}]},
            {"kind": "chip", "id": "k4", "x": 540, "y": 880, "text": "The window number is part of the key", "color": "amber", "t": wi(4, "includes")},
            {"kind": "chip", "id": "f4", "x": 540, "y": 950, "text": "A new window starts a fresh count", "color": "mint", "t": wi(4, "fresh"), "filled": False}],
         "clear": ["t3", "p1", "p2", "p3", "p4"]},
        # 5 rehook
        {"type": "stage", "objects": [
            {"kind": "question", "id": "q5", "x": 540, "y": 440, "text": "Can 2 requests read the same count at once?", "size": 30, "t": -0.2},
            {"kind": "terminal", "id": "r5", "x": 90, "y": 540, "w": 900, "h": 250, "title": "Example: separate read and write steps, limit 10", "size": 26, "t": wi(5, "2"),
             "lines": [{"text": "Request A reads count: 9 -> allowed", "color": "mint"},
                       {"text": "Request B reads count: 9 -> allowed", "color": "mint"},
                       {"text": "Both write back 10: the limit is bypassed", "color": "red", "hl": True}]}],
         "clear": ["t4", "r4", "r4b", "k4", "f4"]},
        # 6 part 2: atomic
        {"type": "stage", "objects": [
            TITLE(6, [("Atomic check: ", "cyan"), ("one Lua EVAL call", "white")], 40),
            {"kind": "terminal", "id": "r6", "x": 90, "y": 520, "w": 900, "h": 270, "title": "Example: Lua script run by EVAL (simplified)", "size": 24, "cps": 34, "t": wi(6, "inside"),
             "lines": [{"text": "count = INCR key", "type": True, "color": "white"},
                       {"text": "if count == 1 then EXPIRE key window end", "type": True, "color": "white"},
                       {"text": "return count <= limit  -- allowed?", "type": True, "color": "mint"}]},
            {"kind": "chip", "id": "at", "x": 540, "y": 880, "text": "Redis executes Lua scripts atomically", "color": "cyan", "t": wi(6, "atomically")},
            {"kind": "chip", "id": "il", "x": 540, "y": 955, "text": "No other command can interleave", "color": "cyan", "t": wi(6, "interleave"), "filled": False}],
         "clear": ["q5", "r5"],
         "events": [{"id": "steps", "t": 0.0, "dur": 0.5, "set": {"active": 1}}]},
        # 7 part 3: window edge
        {"type": "stage", "objects": [
            TITLE(7, [("Smoother window: ", "pink"), ("fixed-window edge problem", "white")], 38),
            {"kind": "panel", "id": "w1", "x": 70, "y": 520, "w": 450, "h": 230, "title": "Window before the edge", "color": "gray", "t": wi(7, "edge")},
            {"kind": "panel", "id": "w2", "x": 560, "y": 520, "w": 450, "h": 230, "title": "Window after the edge", "color": "gray", "t": wi(7, "edge")},
            {"kind": "chip", "id": "b1", "x": 295, "y": 650, "text": "10 requests at second 9", "color": "amber", "t": wi(7, "second", 1)},
            {"kind": "chip", "id": "b2", "x": 785, "y": 650, "text": "10 requests at second 11", "color": "amber", "t": wi(7, "second", 2)},
            {"kind": "chip", "id": "b3", "x": 540, "y": 850, "text": "20 requests in 2 seconds", "color": "pink", "t": wi(7, "20")},
            {"kind": "chip", "id": "b4", "x": 540, "y": 930, "text": "Limit: 10 requests per 10 seconds", "color": "gray", "t": wi(7, "limit"), "filled": False}],
         "clear": ["t6", "r6", "at", "il"],
         "events": [{"id": "steps", "t": 0.0, "dur": 0.5, "set": {"active": 2}}]},
        # 8 previous-counter extrapolation (Cloudflare)
        {"type": "stage", "objects": [
            TITLE(8, [("Cloudflare: ", "pink"), ("rate limit from the previous counter", "white")], 36),
            {"kind": "terminal", "id": "r8a", "x": 90, "y": 520, "w": 900, "h": 190, "title": "Example: 50 requests per minute is the limit", "size": 25, "t": wi(8, "with"),
             "lines": [{"text": "current minute: 18 requests (started 15 s ago)", "color": "gray", "pause": 1.0},
                       {"text": "previous minute: 42 requests", "color": "gray"}]},
            {"kind": "terminal", "id": "r8b", "x": 90, "y": 740, "w": 900, "h": 215, "title": "Rate approximation for requests", "size": 25, "cps": 40, "t": wi(8, "rate"),
             "lines": [{"text": "rate = 42 * ((60-15)/60) + 18", "type": True, "color": "white"},
                       {"text": "     = 42 * 0.75 + 18", "type": True, "color": "white"},
                       {"text": "     = 49.5 requests", "type": True, "color": "mint", "hl": True}]}],
         "clear": ["t7", "w1", "w2", "b1", "b2", "b3", "b4"]},
        # 9 accuracy
        {"type": "stage", "objects": [
            {"kind": "meter", "id": "acc", "x": 90, "y": 1030, "w": 900, "h": 30, "value": 0.0, "segs": 100, "label": "Requests wrongly allowed or rate limited", "right": "0.003% of 400 million requests", "color": "pink", "t": wi(9, "only")},
            {"kind": "chip", "id": "ap", "x": 540, "y": 1115, "text": "Cloudflare's estimate is an approximation", "color": "amber", "t": wi(9, "approximation"), "filled": False}]},
        # 10 part 4: 429
        {"type": "stage", "objects": [
            TITLE(10, [("Response: ", "mint"), ("HTTP 429 Too Many Requests", "white")], 38),
            {"kind": "terminal", "id": "r10", "x": 90, "y": 520, "w": 900, "h": 220, "title": "Example response to a blocked client", "size": 26, "cps": 36, "t": wi(10, "blocked"),
             "lines": [{"text": "HTTP/1.1 429 Too Many Requests", "type": True, "color": "red", "pause": 1.3},
                                              {"text": "Retry-After: 3600", "type": True, "color": "mint"}]},
            {"kind": "chip", "id": "ra", "x": 540, "y": 830, "text": "Retry-After: how long to wait before retrying", "color": "mint", "t": wi(10, "retry-after"), "filled": False}],
         "clear": ["acc", "ap", "t8", "r8a", "r8b"],
         "events": [{"id": "steps", "t": 0.0, "dur": 0.5, "set": {"active": 3}}]},
        # 11 Retry-After formats
        {"type": "stage", "objects": [
            {"kind": "terminal", "id": "r11a", "x": 90, "y": 880, "w": 900, "h": 100, "title": "Retry-After: seconds to wait", "size": 26, "t": wi(11, "number"),
             "lines": [{"text": "Retry-After: 120", "color": "mint"}]},
            {"kind": "terminal", "id": "r11b", "x": 90, "y": 1000, "w": 900, "h": 105, "title": "Retry-After: date to retry after", "size": 26, "t": wi(11, "date"),
             "lines": [{"text": "Retry-After: Wed, 21 Oct 2015 07:28:00 GMT", "color": "cyan"}]}]},
        # 12 token bucket
        {"type": "stage", "objects": [
            TITLE(12, [("Token bucket ", "amber"), ("(Stripe)", "white")], 42),
            {"kind": "panel", "id": "bk", "x": 90, "y": 520, "w": 900, "h": 230, "title": "Rate limiter: one bucket per user", "icon": "database", "color": "amber", "t": wi(12, "bucket")},
            {"kind": "meter", "id": "tok", "x": 130, "y": 650, "w": 820, "h": 34, "value": 0.7, "segs": 20, "label": "Tokens in the bucket", "color": "amber", "t": wi(12, "bucket")},
            {"kind": "chip", "id": "e12", "x": 540, "y": 840, "text": "Empty bucket: the request is rejected", "color": "pink", "t": wi(12, "empty")}],
         "clear": ["t10", "r10", "ra", "r11a", "r11b", "steps", "dl"],
         "events": [{"id": "tok", "t": wi(12, "removes"), "dur": 0.8, "set": {"value": 0.45}},
                    {"id": "tok", "t": wi(12, "slowly"), "dur": 1.2, "set": {"value": 0.6}},
                    {"id": "tok", "t": wi(12, "empty"), "dur": 0.8, "set": {"value": 0.0, "color": "pink"}}]},
        # 13 catch: other limiter types
        {"type": "stage", "objects": [
            TITLE(13, [("Stripe: ", "white"), ("more than request counts", "pink")], 40),
            {"kind": "panel", "id": "s1", "x": 90, "y": 520, "w": 900, "h": 130, "title": "Request rate limiter", "color": "amber", "t": wi(13, "counting"), "icon": "gear"},
            {"kind": "text", "id": "s1t", "x": 130, "y": 585, "text": "Restricts each user to N requests per second", "size": 26, "color": "gray", "t": wi(13, "counting"), "maxw": 820},
            {"kind": "panel", "id": "s2", "x": 90, "y": 680, "w": 900, "h": 130, "title": "Concurrent requests limiter", "color": "cyan", "t": wi(13, "concurrent"), "icon": "gear"},
            {"kind": "text", "id": "s2t", "x": 130, "y": 745, "text": "Example: 20 API requests in progress at the same time", "size": 26, "color": "gray", "t": wi(13, "example"), "maxw": 820},
            {"kind": "panel", "id": "s3", "x": 90, "y": 840, "w": 900, "h": 130, "title": "Load shedders for API requests", "color": "pink", "t": wi(13, "load"), "icon": "gear"},
            {"kind": "text", "id": "s3t", "x": 130, "y": 905, "text": "Decide on the whole state of the system", "size": 26, "color": "gray", "t": wi(13, "whole"), "maxw": 820}],
         "clear": ["t12", "bk", "tok", "e12"]},
        {"type": "cta", "big": "Rate limiter: script, formula, header", "sub": "Redis Lua script. Cloudflare formula. Retry-After header.", "size": 70, "line": "for one tech topic a day.", "follow_first": True, "follow_at": 4.9, "sub_at": 1.8},
    ],
}
