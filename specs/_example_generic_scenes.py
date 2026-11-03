# Example showing the generic scene types (hook, steps, versus, stat, bars, cta) for any topic.
# Copy this file to specs/dayNN_topic.py and replace the content. Lines are timed automatically (pace_wps).
SPEC = {
    "tag": "@TECHINABITE",
    "pace_wps": 3.2,
    "captions": False,
    "mascot": {"x": 900, "y": 1270, "size": 230},   # the page mascot; per scene use "mascot": {...} to move it or "mascot": False to hide it
    "music": {"bpm": 112, "seed": 8, "variant": 1},
    "lines": [
        "Every app you use is quietly asking other apps for help. How does that work?",
        "It sends a request to an API, which is a menu of things another program is willing to do for you.",
        "You ask, the server checks who you are, does the work, and sends back an answer.",
        "An API call is like ordering at a restaurant. The kitchen stays hidden, and you only deal with the menu.",
        "That is why one app can show another app's data without ever touching its database.",
        "That's an API. Follow for one tech topic a day.",
    ],
    "scenes": [
        {"type": "hook", "kicker": "TECH IN A BITE", "big1": "How do apps", "big2": "talk to each other?", "sub": "The answer is an API.", "size1": 110, "size2": 96},
        {"type": "stat", "title": "A menu of requests", "value": "1 request", "label": "One request goes out and one answer comes back.", "size": 120},
        {"type": "steps", "title": "What happens on every request", "items": ["Your app sends a request.", "The server checks who you are.", "It does the work.", "It sends the answer back."], "gap": 1.5},
        {"type": "versus", "mascot": False, "title": "An API works like a restaurant", "left": {"head": "Restaurant", "points": ["You read the menu.", "You order.", "The kitchen stays hidden."]}, "right": {"head": "API", "points": ["You read the docs.", "You send a request.", "The database stays hidden."]}},
        {"type": "bars", "title": "Why this matters", "items": [{"label": "Without an API", "frac": 1.0, "color": (255, 190, 60), "value": "Every app builds everything itself"}, {"label": "With an API", "frac": 0.25, "color": (95, 220, 190), "value": "Apps reuse each other's work"}], "note": "Illustration, not to scale."},
        {"type": "cta", "big": "That is an API.", "sub": "A menu of requests another program will answer.", "size": 90, "line": "One tech topic a day."},
    ],
}
