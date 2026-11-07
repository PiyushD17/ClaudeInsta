# Day 13 brief: reverse proxy vs load balancer vs API gateway (COMPARE)

## 1. Topic and audience
Engineers and learners who mix up three roles in front of servers. One thing to remember: the roles answer different questions (which path / which server is healthy / who is calling), and one NGINX proxy_pass can play the first two. Value outcome: a reason to save (a rule of thumb) and to send to a teammate.

## 2. Hooks
Recommended (72.1 STRONG, true, answered): "Your 1 proxy_pass can be a reverse proxy, but also a load balancer." (a concrete contradiction that promises the mechanism). Alternatives (hookscore): "Not 3 boxes: 1 NGINX proxy_pass can proxy and balance your traffic." (81.6, higher score, but "not 3 boxes" overstates it because the API gateway is a separate role); "Your load balancer is not a new box: NGINX uses proxy_pass for both." (40.9, weak); "Your NGINX proxy and load balancer use the same proxy_pass line." (26.8, weak). The recommended hook was chosen because it is STRONG and strictly true. Rehook (line 4, PASS 75.0): "If srv1 fails, your 1-server proxy_pass has no other server to try. What do 3 servers add?" Answered in line 6.

## 3. Storyboard (about 110 s, one persistent diagram: alice -> NGINX with 3 role strips -> servers)
1. 0-4 s Hook: diagram on screen at frame 0, reverse proxy strip lights, then load balancer.
2. 4-16 s Three jobs, one request: tracker 1-2-3, /orders/42 chip, each job asks a different question.
3. 16-29 s Reverse proxy: terminal shows location block and proxy_pass.
4. 29-34 s Rehook: "proxy_pass: 1 SERVER", "srv1 FAILED" pills, question bar.
5. 34-42 s Load balancer: upstream group of 3, round-robin packets.
6. 42-52 s Payoff: srv1 crossed, marked unavailable, tries to avoid it; max_fails=1, fail_timeout=10s defaults.
7. 52-62 s AWS ALB health checks: 30 s, 2 consecutive failed checks (NGINX dimmed, servers shown as ALB targets).
8. 62-69 s The catch: only unhealthy targets, requests go to all.
9. 69-77 s API gateway: traffic management, authorization and access control.
10. 77-88 s NGINX directives for such tasks: auth_request (2xx allow, 401/403 deny), limit_req_zone rate 1r/s, 503 default.
11. 88-98 s Rule of thumb (share line): three question/answer strips.
12. 98-110 s Recap and "Follow for one tech topic a day."
Exact on-screen text: see out/day13_check.md (SHOWN lines per scene).

## 4. Technical accuracy
Every factual sentence has a verbatim source quote in specs/day13_facts.json (NGINX docs, AWS ALB and API Gateway docs, MDN); table in out/day13_sources.md. Caveats: the roles overlap, hence "usually" in the rule of thumb; max_fails and fail_timeout values are NGINX defaults; ALB numbers are defaults for instance and IP targets and approximate; NGINX auth_request and limit_req are examples that NGINX can cover such tasks, not a claim that it replaces a managed gateway. The 3 servers, alice and GET /orders/42 are an illustrative example. Independent reviewer: PASS in round 5 (rounds 1-4 found and fixed issues).

## 5. Cover headline
"Proxy vs balancer vs gateway" (4 words)

## 6. Caption
See out/day13_caption.txt.

## 7. Audio
Original synthesised music (bpm 108, seed 13, variant 0). Lower it under your voice (about 20-25% of voice volume), no lyrics. Voiceover script is out/day13_script.txt (1949 characters, within the 2000 free-credit limit).

## 8. Performance hypothesis
The COMPARE pattern with a visible tracker and a saveable rule of thumb should beat the baseline median (about 150 views) on saves and sends. Validating metric: saves plus sends per 100 views (and average watch time as the second signal). Length (110 s) is a risk: if skip rate is high, shorten next COMPARE. Do not conclude from one reel.

## 9. Experiment tag
COMPARE (also NUMBER/VISUAL traits; the single tag is COMPARE).
