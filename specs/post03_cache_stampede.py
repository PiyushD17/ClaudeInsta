# Post 03 (v3 story carousel): cache stampede, what happens when many requests miss the same expired cache entry.
# One chapter per slide, each ends on a rehook that the next slide pays off. No code.
SPEC = {
    "tag": "@TECHINABITE",
    "topic": "Cache stampede",
    "slides": [
        {"type": "cover_story", "level": 1,
         "title": [("1 expired", True), ("cache entry can", False), ("still flood", True), ("your database", False)],
         "meta": ["CACHING", "SYSTEM DESIGN", "NO CODE"]},

        {"type": "story", "level": 1, "step": 1, "title": [("A cache ", False), ("shields", True), (" your database", False)],
         "bullets": ["A **cache** is often added when a **dependency**, such as a database, is too slow or too inefficient at a given request rate.",
                     "The most common rule gives each cached entry a **time to live (TTL)**: when it runs out, the entry **expires**.",
                     "The next request that finds nothing in the cache is a **cache miss**: it must **rebuild** the value, for example from the database."],
         "hook": "But when **1 entry** expires and many requests arrive, what happens to your **database**?"},

        {"type": "story", "level": 1, "step": 2, "title": [("Everyone ", False), ("misses", True), (" together", False)],
         "bullets": ["A **cache stampede** is a type of **cascading failure** in massively parallel computing systems. AWS describes it as the **thundering herd**.",
                     "Many clients need the **same uncached resource** at about the same time, and each one tries to rebuild it.",
                     "At a high request rate the **database can be overloaded**. The cache hit rate can drop to **zero**, leaving the system in **congestion collapse**."],
         "hook": "How can **only 1 request** rebuild your cached value while the rest wait?"},

        {"type": "story", "level": 2, "step": 3, "title": [("One request ", False), ("rebuilds", True), (" while the rest wait", False)],
         "bullets": ["With a **lock**, a process on a cache miss tries to take it, and **recomputes** the value only if it gets the lock.",
                     "The nginx cache lock does this: **only 1 request at a time** may fill a new cache entry. Others wait.",
                     "It is **off by default**. Waiting stops after **5 seconds** by default: the request then goes to the proxied server anyway, **uncached**."],
         "hook": "But must anyone wait? Your cache can serve the **old value** instead."},

        {"type": "story", "level": 3, "step": 4, "title": [("Serve the ", False), ("stale", True), (" copy", False)],
         "bullets": ["The cache can **keep a stale item** and serve it while a process recomputes the new value.",
                     "Switched on, nginx can serve a **stale cached response** while it is updated. That **minimizes accesses** to the proxied server.",
                     "Also opt-in: a **background request** refreshes the expired item meanwhile.",
                     "AWS: decide when clients should see **stale data versus errors**."],
         "hook": "But stale only starts **after** expiry. Can your requests refresh **before** it?"},

        {"type": "story", "level": 3, "step": 5, "title": [("Refresh ", False), ("before", True), (" it expires", False)],
         "bullets": ["With **probabilistic early expiration**, each process may **recompute the value before it expires**, using an independent probabilistic decision.",
                     "The **longer a rebuild takes**, the earlier requests may start it. The authors show a tuning value called beta, set to **1**, works well in practice.",
                     "The cost: each cache entry **takes more memory**, because the rebuild time is stored with the value."],
         "hook": "Want your cache's defences and what each costs on **1 slide**? **Swipe**."},

        {"type": "takeaway", "level": 3, "label": "RECAP", "title": "Cache stampede, recap",
         "points": ["**Stampede**: many requests miss the same expired entry and can overload the database.",
                    "**Lock**: 1 request rebuilds, the rest wait (nginx: up to 5 s). Cost: extra write. **Stale**: serve the old copy. Cost: old data.",
                    "**Early refresh**: recompute before expiry. Cost: extra memory per entry."],
         "share": "Send this to whoever runs your cache. nginx's lock is off by default."},
    ],
}
