# Post 01 (v3 story carousel): Kubernetes liveness, readiness and startup probes.
# One chapter per slide, each slide ends on a rehook ("hook") that the next slide pays off. No code: concepts explained in depth.
SPEC = {
    "tag": "@TECHINABITE",
    "topic": "Kubernetes probes",
    "slides": [
        {"type": "cover_story", "level": 1,
         "title": [("Why your", False), ("liveness probe", True), ("can kill your", False), ("slow app within", False), ("30 seconds", True)],
         "meta": ["KUBERNETES", "3 PROBES", "NO CODE"]},

        {"type": "story", "level": 1, "step": 1, "title": [("Kubernetes keeps ", False), ("asking", True)],
         "bullets": ["A **probe** is a check the **kubelet** runs periodically on a container. Kubernetes acts on the result.",
                     "**Startup**: has the app started?",
                     "**Liveness**: should the container be restarted?",
                     "**Readiness**: can it take traffic?"],
         "hook": "But fail the wrong one, and Kubernetes **restarts your container**. Which one?"},

        {"type": "story", "level": 1, "step": 2, "title": [("Two ways a probe ", False), ("fails", True)],
         "bullets": ["A probe only fails after **3 failed checks in a row** (the default)."],
         "cards": [{"label": "Liveness fails", "head": "Restarted", "text": "Kubelet kills the container; restart policy applies. Same for startup probes.", "color": "pink", "highlight": True},
                   {"label": "Readiness fails", "head": "Cut off", "text": "Not killed, but the Pod gets no traffic from matching Services.", "color": "mint", "highlight": True}],
         "hook": "But what if your app needs **2 minutes** just to start?"},

        {"type": "story", "level": 2, "step": 3, "title": [("The ", False), ("30-second", True), (" trap", False)],
         "bullets": ["Default timing: first check at **0 s**, then **every 10 s**, failed after **3 misses** in a row.",
                     "So a liveness probe on default timing gives up **within about 30 seconds** (0 + 3 x 10).",
                     "Example: an app that needs **2 minutes** to start is **killed and restarted** before it ever finishes."],
         "hook": "But **1 extra probe** can give your slow app **minutes** to start. Which one?"},

        {"type": "story", "level": 3, "step": 4, "title": [("The ", False), ("startup", True), (" probe buys time", False)],
         "bullets": ["It runs **first**: liveness and readiness checks wait until it succeeds.",
                     "The Kubernetes docs example allows **30 checks, 10 s apart**: up to **5 minutes** to start.",
                     "Still not started after that? The container is **killed**, then its restart policy applies."],
         "hook": "But a badly set liveness probe can **pile load onto your healthy pods**. How?"},

        {"type": "story", "level": 3, "step": 5, "title": [("When liveness ", False), ("cascades", True)],
         "bullets": ["A liveness probe must signal **unrecoverable application failure**, for example a deadlock.",
                     "Get it wrong and containers **restart under high load**: failed requests and **more load** on the pods still running.",
                     "Common pattern: the same cheap check as readiness, but liveness **allows more failures**."],
         "hook": "Before your next outage: **all 3 Kubernetes probes on 1 slide**. Swipe."},

        {"type": "takeaway", "level": 3, "label": "RECAP", "title": "Kubernetes probes, recap",
         "points": ["**Startup**: has the app started? Liveness and readiness wait for it.",
                    "**Liveness** fails: restarted. **Readiness** fails: no Service traffic.",
                    "Default liveness timing: **up to 30 s** (0 + 3 x 10). Slower start? Add a startup probe."],
         "share": "Send this to whoever sets your probes."},
    ],
}
