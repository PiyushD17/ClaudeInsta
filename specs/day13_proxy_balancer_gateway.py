LINES = [
 "Your 1 proxy_pass can be a reverse proxy, but also a load balancer.",
 "Three jobs can sit in front of your servers: a reverse proxy, a load balancer and an API gateway. In our example, alice calls GET /orders/42 through NGINX, and each job asks that request a different question.",
 "The reverse proxy asks which server handles this path of the request. In NGINX, a location block with proxy_pass, as in the docs example, passes all requests processed in that location to the proxied server at the specified address.",
 "If srv1 fails, your 1-server proxy_pass has no other server to try. What do 3 servers add?",
 "Point proxy_pass at an upstream group with 3 servers, srv1, srv2 and srv3, and nginx applies HTTP load balancing. The default method is round-robin.",
 "What the group adds is skipping: when a response from a server fails, nginx marks it unavailable and tries to avoid it for a while. max_fails defaults to 1 and fail_timeout to 10 seconds.",
 "An AWS Application Load Balancer sends its own health checks: about every 30 seconds by default for instance and IP targets, and by default 2 consecutive failed checks mean unhealthy.",
 "The catch: if a target group contains only unhealthy targets, the load balancer routes requests to all of them, regardless of health.",
 "The API gateway asks who is calling and what they may do. Amazon API Gateway lists traffic management, authorization and access control among its tasks.",
 "NGINX has directives for such tasks too: auth_request allows alice on a 2xx subrequest and denies on 401 or 403, and limit_req_zone sets a rate of 1r/s, and rejected requests get 503 by default.",
 "Save this rule of thumb, since roles overlap: usually, the load balancer answers which server is healthy, the gateway who is calling, and the reverse proxy which path goes where.",
 "So proxy_pass at 1 server is a plain reverse proxy; at an upstream group of 3 it also load balances. The gateway adds who is calling. Follow for one tech topic a day.",
]

def wi(line, token, k=1):
    """'wN' anchor: the k-th word of script line `line` (1-based) that starts with `token`."""
    ws = [w.strip(".,:?\"").lower() for w in LINES[line - 1].split()]
    hits = [i + 1 for i, w in enumerate(ws) if w.startswith(token.lower())]
    return "w%d" % hits[k - 1]

# ---- layout grid (1080 x 1920): title area y 290-510, diagram y 540-940, lower area y 975-1375, mascot top-right next to the @tag
TITLE = lambda i, parts, size=44, y=440: {"kind": "title", "id": "t%d" % i, "t": -0.25, "x": 540, "y": y, "parts": parts, "size": size, "maxw": 820}
DY = 540
LOW = dict(x=40, y=975, w=1000, h=400)
SRV_Y = {1: DY + 100, 2: DY + 200, 3: DY + 300}          # server boxes (centres +40)
ALICE = (230, DY + 250)
NG_IN = (520, DY + 250)
GW = (505, DY + 350)
BACK = [GW, (505, DY + 418), (190, DY + 418)]   # return path under the panels, crosses no text

def route(i):
    return [ALICE, NG_IN, (820, SRV_Y[i] + 40)]

def pkt(pid, t, i=1, text="GET", color="mint", out=None, dur=1.5, path=None):
    o = {"kind": "packet", "id": pid, "t": t, "path": path or route(i), "text": text, "color": color, "dur": dur, "w": 96, "h": 36, "hold": False}
    if out is not None: o["out"] = out
    return o

def term(tid, title, lines, t=-0.2, size=28, h=None, cps=40):
    return {"kind": "terminal", "id": tid, "t": t, "x": LOW["x"], "y": LOW["y"], "w": LOW["w"], "h": h or LOW["h"], "title": title, "size": size, "cps": cps, "lines": lines}

def strip(sid, y, label, value, color):
    return {"kind": "panel", "id": sid, "in": "nginx", "t": -0.3, "x": 262, "y": y, "w": 510, "h": 90, "label": label, "color": color, "value": value, "compact": True, "lsize": 26}

def server(n, t):
    return {"kind": "panel", "id": "s%d" % n, "in": "servers", "t": t, "x": 820, "y": SRV_Y[n], "w": 205, "h": 80, "label": "srv%d" % n, "color": "cyan", "level": 1, "compact": True}

SPEC = {
    "tag": "@TECHINABITE",
    "pace_wps": 3.2,
    "captions": False,
    "format": "story",
    "music": {"bpm": 108, "seed": 13, "variant": 0},
    "mascot": {"x": 1000, "y": 300, "size": 90},
    "lines": LINES,
    "scenes": [
        # 1 hook: the diagram the whole story runs on is on screen from frame 0
        {"type": "stage", "objects": [
            {"kind": "label", "id": "k", "t": -0.5, "x": 540, "y": 292, "text": "TECH IN A BITE", "size": 28, "color": "amber", "align": "c", "font": "med"},
            {"kind": "title", "id": "h1", "t": -0.5, "x": 540, "y": 326, "parts": [("Your 1 ", "white"), ("proxy_pass", "amber"), (":\nreverse proxy or load balancer", "white")], "size": 40, "maxw": 760, "underline": False},
            {"kind": "title", "id": "h2", "t": -0.3, "x": 540, "y": 492, "parts": [("NGINX · reverse proxy · load balancer", "mint")], "size": 30, "underline": False, "maxw": 860},
            {"kind": "panel", "id": "client", "t": -0.4, "x": 40, "y": DY, "w": 190, "h": 400, "label": "alice", "icon": "user", "body": "user", "body_color": "gray"},
            {"kind": "pill", "id": "ex", "in": "client", "t": -0.35, "x": 135, "y": DY + 360, "text": "Example", "color": "gray", "size": 24, "maxw": 160},
            {"kind": "panel", "id": "nginx", "t": -0.3, "x": 245, "y": DY, "w": 545, "h": 400, "label": "NGINX", "icon": "gear", "color": "amber"},
            strip("rp", DY + 85, "Reverse proxy", "proxy_pass", "cyan"),
            strip("lb", DY + 195, "Load balancer", "proxy_pass", "mint"),
            strip("gw", DY + 305, "API gateway", "auth_request", "purple"),
            {"kind": "panel", "id": "servers", "t": -0.2, "x": 805, "y": DY, "w": 235, "h": 400, "label": "Servers", "icon": "server", "color": "cyan"},
            server(1, -0.2),
            pkt("p1", wi(1, "reverse"), 1)],
         "events": [{"id": "rp", "t": wi(1, "reverse"), "dur": 0.0, "set": {"hl": True}},
                    {"id": "rp", "t": wi(1, "but"), "dur": 0.0, "set": {"hl": False}},
                    {"id": "lb", "t": wi(1, "load"), "dur": 0.0, "set": {"hl": True}}]},
        # 2 three jobs, one request
        {"type": "stage", "objects": [
            {"kind": "dots", "id": "steps", "t": -0.2, "x": 540, "y": 335, "n": 3, "active": -1, "spacing": 215,
             "labels": ["Reverse proxy", "Load balancer", "API gateway"]},
            dict(TITLE(2, [("Same request, ", "white"), ("3 questions", "amber")]), t=wi(2, "each")),
            {"kind": "pill", "id": "req", "in": "client", "t": wi(2, "alice"), "x": 135, "y": DY + 300, "text": "/orders/42", "color": "amber", "mono": True, "size": 24, "maxw": 215},
            pkt("p2", wi(2, "calls"), 1)],
         "clear": ["k", "h1", "h2"], "focus": [],
         "events": [{"id": "lb", "t": 0.0, "dur": 0.0, "set": {"hl": False}},
                    {"id": "steps", "t": wi(2, "reverse"), "dur": 0.0, "set": {"active": 0}},
                    {"id": "rp", "t": wi(2, "reverse"), "dur": 0.0, "set": {"hl": True}},
                    {"id": "steps", "t": wi(2, "load"), "dur": 0.0, "set": {"active": 1}},
                    {"id": "rp", "t": wi(2, "load"), "dur": 0.0, "set": {"hl": False}},
                    {"id": "lb", "t": wi(2, "load"), "dur": 0.0, "set": {"hl": True}},
                    {"id": "steps", "t": wi(2, "api"), "dur": 0.0, "set": {"active": 2}},
                    {"id": "lb", "t": wi(2, "api"), "dur": 0.0, "set": {"hl": False}},
                    {"id": "gw", "t": wi(2, "api"), "dur": 0.0, "set": {"hl": True}},
                    {"id": "rp", "t": wi(2, "each"), "dur": 0.0, "set": {"hl": True}},
                    {"id": "lb", "t": wi(2, "each"), "dur": 0.0, "set": {"hl": True}}]},
        # 3 reverse proxy
        {"type": "stage", "objects": [
            TITLE(3, [("Reverse proxy: ", "cyan"), ("which server?", "white")]),
            pkt("p3a", wi(3, "handles"), 1), pkt("p3", wi(3, "passes"), 1),
            term("r3", "Example: NGINX config", [
                {"text": "location /orders/ {", "type": True, "color": "white", "at": wi(3, "location")},
                {"text": "    proxy_pass http://srv1.example.com;", "type": True, "color": "white", "hl": True, "hlcolor": "cyan", "at": wi(3, "proxy_pass")},
                {"text": "}", "type": True, "color": "white", "pause": 0.05}], cps=45, h=240)],
         "clear": ["t2", "req", "p2"], "focus": ["client", "nginx", "rp", "servers", "s1", "steps"],
         "events": [{"id": "gw", "t": 0.0, "dur": 0.0, "set": {"hl": False}},
                    {"id": "lb", "t": 0.0, "dur": 0.0, "set": {"hl": False}},
                    {"id": "steps", "t": -0.2, "dur": 0.0, "set": {"active": 0}},
                    {"id": "rp", "t": 0.0, "dur": 0.0, "set": {"hl": True}},
                    {"id": "s1", "t": wi(3, "server"), "dur": 0.0, "set": {"hl": True}},
                    {"id": "s1", "t": wi(3, "path"), "dur": 0.0, "set": {"hl": False}},
                    {"id": "client", "t": wi(3, "path"), "dur": 0.0, "set": {"hl": True}},
                    {"id": "client", "t": wi(3, "in"), "dur": 0.0, "set": {"hl": False}},
                    {"id": "s1", "t": wi(3, "proxied"), "dur": 0.0, "set": {"hl": True}}]},
        # 4 rehook
        {"type": "stage", "objects": [
            {"kind": "question", "id": "q4", "t": wi(4, "what"), "x": 540, "y": 466, "parts": [("Failed server. ", "white"), ("What do 3 servers add?", "amber")], "size": 30, "maxw": 960},
            {"kind": "pill", "id": "a4", "t": wi(4, "1"), "x": 540, "y": 1090, "text": "proxy_pass: 1 SERVER", "color": "cyan", "size": 40, "maxw": 900},
            {"kind": "pill", "id": "b4", "t": wi(4, "fails"), "x": 540, "y": 1210, "text": "srv1 FAILED", "color": "pink", "size": 44, "maxw": 700}],
         "clear": ["t3", "r3", "p3", "p3a"], "focus": ["nginx", "servers", "s1", "steps"],
         "events": [{"id": "s1", "t": 0.0, "dur": 0.0, "set": {"hl": False}},
                    {"id": "s1", "t": wi(4, "fails"), "dur": 0.0, "set": {"status": "cross", "color": "pink"}}]},
        # 5 load balancer: upstream group of 3
        {"type": "stage", "objects": [
            TITLE(5, [("Load balancer: ", "mint"), ("upstream group", "white")]),
            server(2, wi(5, "srv2")), server(3, wi(5, "srv3")),
            pkt("p5a", wi(5, "default"), 1, dur=1.0), pkt("p5b", wi(5, "method"), 2, dur=1.0), pkt("p5c", wi(5, "round-robin"), 3, dur=1.0),
            term("r5", "NGINX docs: default load balancing configuration", [
                {"text": "upstream myapp1 {", "type": True, "color": "white", "at": wi(5, "upstream")},
                {"text": "    server srv1.example.com;", "type": True, "color": "white", "at": wi(5, "srv1")},
                {"text": "    server srv2.example.com;", "type": True, "color": "white", "at": wi(5, "srv2")},
                {"text": "    server srv3.example.com;", "type": True, "color": "white", "at": wi(5, "srv3")},
                {"text": "}", "type": True, "color": "white", "pause": 0.05},
                {"text": "proxy_pass http://myapp1;", "type": True, "color": "white", "hl": True, "hlcolor": "mint", "at": wi(5, "and", 2)},
                {"text": "-- default method: round-robin", "color": "mint", "at": wi(5, "round-robin")}], size=27, cps=45)],
         "clear": ["q4", "a4", "b4"], "focus": [],
         "events": [{"id": "s1", "t": 0.0, "dur": 0.0, "set": {"status": None, "color": "cyan"}},
                    {"id": "rp", "t": 0.0, "dur": 0.0, "set": {"hl": False}},
                    {"id": "steps", "t": -0.2, "dur": 0.0, "set": {"active": 1}},
                    {"id": "lb", "t": wi(5, "point"), "dur": 0.0, "set": {"hl": True}}]},
        # 6 failover: the payoff of the rehook (the same srv1 that failed in scene 4)
        {"type": "stage", "objects": [
            TITLE(6, [("Group: ", "mint"), ("skips failed servers", "white")]),
            pkt("p6a", wi(6, "avoid"), 2), pkt("p6b", wi(6, "while"), 3),
            term("r6", "NGINX docs: server parameters", [
                {"text": "-> srv1 marked unavailable", "color": "pink", "hl": True, "hlcolor": "pink", "at": wi(6, "unavailable")},
                {"text": "-> tries to avoid it for a while", "color": "mint", "at": wi(6, "avoid")},
                {"text": "max_fails=1        -- default", "color": "white", "at": wi(6, "max_fails")},
                {"text": "fail_timeout=10s   -- default", "color": "white", "at": wi(6, "fail_timeout")}], size=28, cps=45, h=300)],
         "clear": ["t5", "r5", "p5a", "p5b", "p5c"], "focus": [],
         "events": [{"id": "lb", "t": 0.0, "dur": 0.0, "set": {"hl": True}},
                    {"id": "s1", "t": wi(6, "fails"), "dur": 0.0, "set": {"status": "cross", "color": "pink"}},
                    {"id": "s1", "t": wi(6, "unavailable"), "dur": 0.0, "set": {"hl": True}}]},
        # 7 AWS ALB defaults
        {"type": "stage", "objects": [
            TITLE(7, [("AWS load balancer: ", "mint"), ("health checks", "white")]),
            term("r7", "AWS docs: health check defaults", [
                {"text": "Application Load Balancer", "color": "gray", "at": wi(7, "aws")},
                {"text": "HealthCheckIntervalSeconds  30", "color": "white", "hl": True, "hlcolor": "mint", "at": wi(7, "30")},
                {"text": "UnhealthyThresholdCount     2", "color": "white", "hl": True, "hlcolor": "amber", "at": wi(7, "2")},
                {"text": "-- defaults; 2 consecutive failed checks", "color": "gray", "at": wi(7, "consecutive")}], size=28, h=300, cps=45)],
         "clear": ["t6", "r6", "p6a", "p6b"], "focus": ["servers", "s1", "s2", "s3", "steps"],
         "events": [{"id": "s1", "t": 0.0, "dur": 0.0, "set": {"status": None, "color": "cyan", "hl": False}},
                    {"id": "steps", "t": -0.2, "dur": 0.0, "set": {"active": 1}},
                    {"id": "lb", "t": 0.0, "dur": 0.0, "set": {"hl": False}},
                    {"id": "servers", "t": wi(7, "targets"), "dur": 0.0, "set": {"label": "ALB targets"}},
                    {"id": "s1", "t": wi(7, "unhealthy"), "dur": 0.0, "set": {"status": "cross", "color": "pink"}}]},
        # 8 the catch: only unhealthy targets
        {"type": "stage", "objects": [
            TITLE(8, [("Catch: ", "pink"), ("only unhealthy targets", "white")]),
            term("r8", "Example: 3 AWS targets", [
                {"text": "healthy targets:   0 of 3", "color": "pink", "at": wi(8, "only")},
                {"text": "-> requests go to ALL targets", "color": "red", "hl": True, "hlcolor": "pink", "at": wi(8, "routes")},
                {"text": "-- regardless of health", "color": "gray", "at": wi(8, "regardless")}], size=28, h=260, cps=45)],
         "clear": ["t7", "r7"], "focus": ["servers", "s1", "s2", "s3", "steps"],
         "events": [{"id": "s2", "t": wi(8, "unhealthy"), "dur": 0.0, "set": {"status": "cross", "color": "pink"}},
                    {"id": "s3", "t": wi(8, "unhealthy"), "dur": 0.0, "set": {"status": "cross", "color": "pink"}},
                    {"id": "s1", "t": wi(8, "all"), "dur": 0.0, "set": {"hl": True}},
                    {"id": "s2", "t": wi(8, "all"), "dur": 0.0, "set": {"hl": True}},
                    {"id": "s3", "t": wi(8, "all"), "dur": 0.0, "set": {"hl": True}}]},
        # 9 API gateway: who is calling and what they may do
        {"type": "stage", "objects": [
            TITLE(9, [("API gateway: ", "purple"), ("who may call?", "white")]),
            term("r9", "AWS docs: what API Gateway handles", [
                {"text": "traffic management", "color": "purple", "at": wi(9, "traffic")},
                {"text": "authorization and access control", "color": "purple", "hl": True, "hlcolor": "purple", "at": wi(9, "authorization")}], size=28, cps=45, h=220)],
         "clear": ["t8", "r8"], "focus": ["client", "steps"],
         "events": [{"id": "s1", "t": 0.0, "dur": 0.0, "set": {"status": None, "color": "cyan", "hl": False}},
                    {"id": "s2", "t": 0.0, "dur": 0.0, "set": {"status": None, "color": "cyan", "hl": False}},
                    {"id": "s3", "t": 0.0, "dur": 0.0, "set": {"status": None, "color": "cyan", "hl": False}},
                    {"id": "servers", "t": 0.0, "dur": 0.0, "set": {"label": "Servers"}},
                    {"id": "steps", "t": -0.2, "dur": 0.0, "set": {"active": 2}},
                    {"id": "client", "t": wi(9, "who"), "dur": 0.0, "set": {"hl": True}},
                    {"id": "client", "t": wi(9, "and"), "dur": 0.0, "set": {"hl": False}},
                    {"id": "client", "t": wi(9, "what"), "dur": 0.0, "set": {"hl": True}},
                    {"id": "client", "t": wi(9, "amazon"), "dur": 0.0, "set": {"hl": False}},
                    {"id": "lb", "t": 0.0, "dur": 0.0, "set": {"hl": False}}]},
        # 10 NGINX asks the same questions
        {"type": "stage", "objects": [
            TITLE(10, [("NGINX: ", "amber"), ("auth_request, limit_req", "white")]),
            pkt("p10a", wi(10, "allows"), 1, "GET", "mint", path=[ALICE, GW, (820, SRV_Y[1] + 40)]),
            pkt("p10b", wi(10, "denies"), 1, "401", "pink", path=BACK),
            pkt("p10c", wi(10, "rejected"), 1, "503", "pink", path=BACK),
            term("r10", "NGINX docs: access and rate limits", [
                {"text": "auth_request /auth;", "color": "white", "hl": True, "hlcolor": "purple", "at": wi(10, "auth_request")},
                {"text": "-- 2xx: allowed, 401 or 403: denied", "color": "gray", "at": wi(10, "allows")},
                {"text": "limit_req_zone $binary_remote_addr zone=one:10m rate=1r/s;", "color": "white", "at": wi(10, "limit_req_zone")},
                {"text": "limit_req zone=one burst=5;", "color": "white", "at": wi(10, "1r/s")},
                {"text": "-- rejected requests: status 503 (default)", "color": "pink", "at": wi(10, "rejected")}], size=27, cps=50)],
         "clear": ["t9", "r9"], "focus": [],
         "events": [{"id": "gw", "t": 0.0, "dur": 0.0, "set": {"hl": True}}, {"id": "steps", "t": -0.2, "dur": 0.0, "set": {"active": 2}},
                    {"id": "nginx", "t": 0.0, "dur": 0.0, "set": {"hl": True}},
                    {"id": "nginx", "t": wi(10, "auth_request"), "dur": 0.0, "set": {"hl": False}},
                    {"id": "client", "t": wi(10, "alice"), "dur": 0.0, "set": {"hl": True}},
                    {"id": "client", "t": wi(10, "on"), "dur": 0.0, "set": {"hl": False}}]},
        # 11 rule of thumb (send-or-save)
        {"type": "stage", "objects": [
            TITLE(11, [("Which question, ", "white"), ("which job?", "amber")]),
            {"kind": "panel", "id": "c1", "t": wi(11, "healthy"), "x": 40, "y": 1010, "w": 1000, "h": 90, "label": "Which server is healthy?", "icon": "gear", "color": "mint", "value": "Load balancer", "compact": True},
            {"kind": "panel", "id": "c2", "t": wi(11, "calling"), "x": 40, "y": 1130, "w": 1000, "h": 90, "label": "Who is calling?", "icon": "gear", "color": "purple", "value": "API gateway", "compact": True},
            {"kind": "panel", "id": "c3", "t": wi(11, "path"), "x": 40, "y": 1250, "w": 1000, "h": 90, "label": "Which path goes where?", "icon": "gear", "color": "cyan", "value": "Reverse proxy", "compact": True}],
         "clear": ["t10", "r10", "p10a", "p10b", "p10c", "steps"], "focus": [],
         "events": [{"id": "gw", "t": 0.0, "dur": 0.0, "set": {"hl": False}},
                    {"id": "lb", "t": wi(11, "load"), "dur": 0.0, "set": {"hl": True}},
                    {"id": "gw", "t": wi(11, "gateway"), "dur": 0.0, "set": {"hl": True}},
                    {"id": "lb", "t": wi(11, "gateway"), "dur": 0.0, "set": {"hl": False}},
                    {"id": "rp", "t": wi(11, "reverse"), "dur": 0.0, "set": {"hl": True}},
                    {"id": "gw", "t": wi(11, "reverse"), "dur": 0.0, "set": {"hl": False}}]},
        # 12 recap and follow
        {"type": "stage", "objects": [
            {"kind": "dots", "id": "recap", "t": -0.2, "x": 540, "y": 640, "n": 3, "active": -1, "spacing": 300, "labels": ["Reverse proxy", "Load balancer", "API gateway"],
             "colors": ["cyan", "mint", "purple"], "caption": [("proxy_pass: ", "amber"), ("2 jobs, plus the gateway", "white")]},
            {"kind": "endcard", "id": "end", "t": wi(12, "follow"), "y": 1020, "text": "@techinabite"},
            {"kind": "title", "id": "endl", "t": wi(12, "follow"), "x": 540, "y": 1180, "parts": [("Follow for one tech topic a day.", "white")], "size": 36, "underline": False}],
         "events": [{"id": "recap", "t": wi(12, "reverse"), "dur": 0.0, "set": {"active": 0}}, {"id": "recap", "t": wi(12, "load"), "dur": 0.0, "set": {"active": 1}}, {"id": "recap", "t": wi(12, "gateway"), "dur": 0.0, "set": {"active": 2}}],
         "clear": True},
    ],
}
