# Post 02 (v3 story carousel): PostgreSQL transaction ID wraparound and freezing.
# One chapter per slide, each slide ends on a rehook ("hook") that the next slide pays off. No code: concepts explained in depth.
SPEC = {
    "tag": "@TECHINABITE",
    "topic": "PostgreSQL wraparound",
    "slides": [
        {"type": "cover_story", "level": 1,
         "title": [("Without VACUUM,", False), ("your PostgreSQL", True), ("rows can turn invisible", False), ("after 2 billion", False), ("transactions", True)],
         "meta": ["POSTGRESQL", "TRANSACTION IDS", "VACUUM"]},

        {"type": "story", "level": 1, "step": 1, "title": [("PostgreSQL ", False), ("keeps", True), (" old row versions", False)],
         "bullets": ["Updating or deleting a row in **PostgreSQL** does **not immediately remove the old version** of the row.",
                     "Each **row version** is stamped with the **transaction ID** of the transaction that inserted it, and of the one that deleted it (zero if never deleted).",
                     "**VACUUM** later removes **dead row versions** and marks their space available for reuse."],
         "hook": "But your database stamps rows from a **32-bit** counter. What happens when it **runs out**?"},

        {"type": "story", "level": 2, "step": 2, "title": [("A ", False), ("32-bit", True), (" counter wraps around", False)],
         "bullets": ["PostgreSQL transaction IDs have **32 bits**. After **more than 4 billion** transactions the counter **wraps around to zero**.",
                     "IDs are compared like points on a circle: for every normal ID, **two billion** IDs count as older and **two billion** as newer.",
                     "A row version looks **in the past** for the next two billion transactions, then **suddenly appears to be in the future**: its output becomes **invisible**."],
         "hook": "But PostgreSQL can **pin your rows in the past forever**. How?"},

        {"type": "story", "level": 2, "step": 3, "title": [("VACUUM ", False), ("freezes", True), (" rows", False)],
         "bullets": ["**VACUUM** marks old rows as **frozen**: inserted far enough in the past to be visible to every current and future transaction.",
                     "A frozen row stays valid **until it is deleted**, however long that is.",
                     "Every table must be vacuumed **at least once every two billion transactions**. By default, autovacuum is forced once a table's oldest unfrozen ID is **200 million** transactions old, **even if disabled**."],
         "hook": "But when autovacuum **fails**, your database starts a **countdown** to read-only. How many transactions are left?"},

        {"type": "story", "level": 3, "step": 4, "title": [("PostgreSQL's ", False), ("countdown", True), (" to read-only", False)],
         "bullets": ["PostgreSQL **warns** when the oldest transaction IDs are **forty million** transactions from the wraparound point.",
                     "Ignore the warnings and it **refuses to assign new transaction IDs** once **fewer than three million** are left.",
                     "Running transactions continue, but **only read-only transactions can start**. Writes fail."],
         "hook": "But before you run VACUUM, the docs say **clear 3 things first**. Which ones?"},

        {"type": "story", "level": 3, "step": 5, "title": [("Before VACUUM: ", False), ("clear", True), (" 3 things", False)],
         "bullets": ["PostgreSQL's recovery steps clear **3 things**, then run a database-wide VACUUM:",
                     "**Old prepared transactions**: commit them or roll them back.",
                     "**Long-running open transactions**: commit, roll back, or terminate the session.",
                     "**Old replication slots**, often for servers that no longer exist: drop them."],
         "hook": "Before your PostgreSQL **refuses writes**, save this 3-line recap. Swipe."},

        {"type": "takeaway", "level": 3, "label": "RECAP", "title": "PostgreSQL transaction ID wraparound, recap",
         "points": ["**32-bit** transaction IDs wrap around: unfrozen old rows can look like they are in the future.",
                    "**VACUUM freezes** old rows. Autovacuum is forced at **200 million** transactions of age by default.",
                    "Warning at **forty million** left, **writes refused** at fewer than **three million**."],
         "share": "Send this to whoever is on call for your Postgres."},
    ],
}
