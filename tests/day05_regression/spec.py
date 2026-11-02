# Text-only reconstruction of the faulty Day 05 trial video (wording copied from the rendered frames; script lines approximated).
# Used only to prove that check_spec.py catches the mistakes the owner reported.
SPEC = {
    "tag": "@TECHINABITE", "pace_wps": 3.2, "captions": False,
    "lines": [
        "Three rules decide which server answers you. One failure can take the whole site down.",
        "A load balancer picks the server for each visitor.",
        "Rule one: round robin takes turns in order.",
        "Rule two: least connections picks the least busy server.",
        "Rule three: it avoids broken servers.",
        "The catch: the balancer can fail too. So there is a pair.",
        "Three rules, one backup plan. Follow for one tech topic a day.",
    ],
    "scenes": [
        {"type": "hook", "kicker": "TECH IN A BITE", "big1": "3 rules decide which", "big2": "server answers you", "sub": "One failure can take the whole site down."},
        {"type": "flow", "title": "A load balancer picks the server for each visitor", "top": "Visitors", "servers": ["Server 1", "Server 2", "Server 3", "Server 4"]},
        {"type": "steps", "title": "Rule 1: round robin takes turns in order",
         "items": ["Visitor 1 goes to server 1.", "Visitor 2 goes to server 2.", "Visitor 3 goes to server 3.", "Visitor 4 goes to server 1 again."]},
        {"type": "versus", "title": "Rule 2: least connections picks the least busy server",
         "left": ("Round robin", ["Takes turns in order.", "Ignores how busy each server is."]),
         "right": ("Least connections", ["Looks at active connections.", "Picks the least busy server."])},
        {"type": "steps", "title": "Rule 3: avoid broken servers", "items": ["It notices a server is failing.", "It stops sending visitors there.", "It tries that server again later."]},
        {"type": "versus", "title": "The catch: the balancer can fail too",
         "left": ("One balancer", ["If it fails,", "nothing gets through."]), "right": ("A pair", ["One is active.", "A standby takes over."])},
        {"type": "cta", "big": "3 rules, 1 backup plan", "sub": "That is a load balancer."},
    ],
}
