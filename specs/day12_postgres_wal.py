LINES = [
    "PostgreSQL survives a crash without writing your table at COMMIT, and replays 1 log instead.",
    "PostgreSQL uses a write-ahead log, WAL: changes to data files must be written only after those changes have been logged.",
    "The path has a WAL record, a flush at COMMIT, a checkpoint, and REDO after a crash.",
    "First, the WAL record. Each change is appended to the WAL at an insert position called the Log Sequence Number, a byte offset that only increases. WAL files live in pg_wal, normally 16 MB each, named in ever-increasing numbers.",
    "Only 1 file is flushed at COMMIT. Which one, the WAL or your data files?",
    "Second, the flush. At COMMIT, only the WAL file has to be flushed. Changed data pages can be redone from the WAL records after a crash: roll-forward recovery, also known as REDO.",
    "Third, the checkpoint. At checkpoint time, all dirty data pages are flushed to disk and a checkpoint record is written to the WAL. The CHECKPOINT command forces one.",
    "A checkpoint begins every checkpoint_timeout, 5 minutes by default, or when max_wal_size, 1 GB by default, is about to be exceeded.",
    "Fourth, REDO. After a crash, PostgreSQL reads the latest checkpoint record to find the redo record, and starts REDO from that point in the WAL.",
    "Shorter checkpoint intervals mean faster crash recovery, but dirty data pages are flushed more often.",
    "The catch: with synchronous_commit off, COMMIT does not wait for the flush. A crash can lose recent transactions, for up to three times wal_writer_delay, 200 ms by default. The database stays consistent.",
    "So when your COMMIT survives a crash, you know why: the WAL flush, the checkpoint and the replay. Follow for one tech topic a day.",
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
WB_OUT = [(450, 893), (640, 893)]       # WAL buffers -> pg_wal
PG_OUT = [(450, 733), (640, 733)]       # shared buffers -> data files
REDO_OUT = [(640, 893), (450, 733)]     # pg_wal -> shared buffers

def pkt(pid, t, path, text, color="mint", dur=0.9, out=None):
    o = {"kind": "packet", "id": pid, "t": t, "path": path, "text": text, "color": color, "dur": dur, "w": 110, "h": 44}
    if out is not None: o["out"] = out
    return o

def term(tid, title, lines, t=-0.2, size=29, h=None, cps=36):
    return {"kind": "terminal", "id": tid, "t": t, "x": LOW["x"], "y": LOW["y"], "w": LOW["w"], "h": h or LOW["h"], "title": title, "size": size, "cps": cps, "lines": lines}

SPEC = {
    "tag": "@TECHINABITE",
    "pace_wps": 3.2,
    "captions": False,
    "format": "story",
    "music": {"bpm": 98, "seed": 12, "variant": 2},
    "mascot": {"x": 1000, "y": 300, "size": 90},
    "lines": LINES,
    "scenes": [
        # 1 hook: the diagram the whole story runs on is there from frame 0
        {"type": "stage", "objects": [
            {"kind": "label", "id": "k", "t": -0.5, "x": 540, "y": 292, "text": "TECH IN A BITE", "size": 28, "color": "amber", "align": "c", "font": "med"},
            {"kind": "title", "id": "h1", "t": -0.5, "x": 540, "y": 326, "parts": [("PostgreSQL survives a crash\nwithout writing your ", "white"), ("table", "amber")], "size": 54, "maxw": 820, "underline": False},
            {"kind": "title", "id": "h2", "t": wi(1, "commit"), "x": 540, "y": 482, "parts": [("at COMMIT · replays 1 log instead", "mint")], "size": 34, "underline": False, "maxw": 820},
            {"kind": "panel", "id": "mem", "t": -0.4, "x": 40, "y": DY, "w": 490, "h": 400, "label": "Memory", "icon": "server", "color": "cyan"},
            {"kind": "panel", "id": "sb", "in": "mem", "t": -0.35, "x": 60, "y": DY + 82, "w": 450, "h": 150, "label": "Shared buffers", "level": 1},
            {"kind": "grid", "id": "sbg", "in": "sb", "t": -0.35, "x": 82, "y": DY + 170, "w": 406, "h": 46, "cols": 8, "rows": 1, "n": 0, "color": "amber"},
            {"kind": "panel", "id": "wb", "in": "mem", "t": -0.3, "x": 60, "y": DY + 242, "w": 450, "h": 150, "label": "WAL buffers", "level": 1},
            {"kind": "grid", "id": "wbg", "in": "wb", "t": -0.3, "x": 82, "y": DY + 330, "w": 406, "h": 46, "cols": 8, "rows": 1, "n": 0, "color": "mint"},
            {"kind": "panel", "id": "disk", "t": -0.4, "x": 550, "y": DY, "w": 490, "h": 400, "label": "Disk", "icon": "database", "color": "amber"},
            {"kind": "panel", "id": "df", "in": "disk", "t": -0.35, "x": 570, "y": DY + 82, "w": 450, "h": 150, "label": "Data files", "level": 1},
            {"kind": "grid", "id": "dfg", "in": "df", "t": -0.35, "x": 592, "y": DY + 170, "w": 406, "h": 46, "cols": 8, "rows": 1, "n": 0, "color": "amber"},
            {"kind": "panel", "id": "pw", "in": "disk", "t": -0.3, "x": 570, "y": DY + 242, "w": 450, "h": 150, "label": "pg_wal", "level": 1},
            {"kind": "grid", "id": "pwg", "in": "pw", "t": -0.3, "x": 592, "y": DY + 330, "w": 406, "h": 46, "cols": 8, "rows": 1, "n": 0, "color": "mint"},
            pkt("p1", wi(1, "commit"), WB_OUT, "WAL")],
         "events": [{"id": "sbg", "t": wi(1, "table"), "dur": 0.3, "set": {"n": 1}},
                    {"id": "wbg", "t": wi(1, "commit"), "dur": 0.3, "set": {"n": 1}},
                    {"id": "wbg", "t": wi(1, "replays"), "dur": 0.3, "set": {"n": 0}},
                    {"id": "pwg", "t": wi(1, "replays"), "dur": 0.3, "set": {"n": 1}},
                    {"id": "pw", "t": wi(1, "log"), "dur": 0.0, "set": {"hl": True}}]},
        # 2 why: write-ahead log
        {"type": "stage", "objects": [
            TITLE(2, [("Write-ahead log: ", "mint"), ("log first", "white")]),
            pkt("p2", wi(2, "have"), WB_OUT, "WAL")],
         "clear": ["k", "h1", "h2"],
         "events": [{"id": "pw", "t": 0.0, "dur": 0.0, "set": {"hl": False}},
                    {"id": "sbg", "t": 0.0, "dur": 0.0, "set": {"n": 0}},
                    {"id": "pwg", "t": 0.0, "dur": 0.0, "set": {"n": 0}},
                    {"id": "sbg", "t": wi(2, "changes"), "dur": 0.3, "set": {"n": 2}},
                    {"id": "df", "t": wi(2, "data"), "dur": 0.0, "set": {"hl": True}},
                    {"id": "df", "t": wi(2, "after"), "dur": 0.0, "set": {"hl": False}},
                    {"id": "wbg", "t": wi(2, "after"), "dur": 0.3, "set": {"n": 2}},
                    {"id": "wbg", "t": wi(2, "logged"), "dur": 0.3, "set": {"n": 0}},
                    {"id": "pwg", "t": wi(2, "logged"), "dur": 0.3, "set": {"n": 2}},
                    {"id": "pw", "t": wi(2, "logged"), "dur": 0.0, "set": {"hl": True}}]},
        # 3 the path
        {"type": "stage", "objects": [
            {"kind": "dots", "id": "steps", "t": -0.2, "x": 540, "y": 335, "n": 4, "active": -1, "spacing": 235,
             "labels": ["WAL record", "Flush at COMMIT", "Checkpoint", "REDO"]}],
         "clear": ["t2", "p2"],
         "events": [{"id": "pw", "t": 0.0, "dur": 0.0, "set": {"hl": False}},
                    {"id": "steps", "t": wi(3, "wal"), "dur": 0.0, "set": {"active": 0}},
                    {"id": "steps", "t": wi(3, "flush"), "dur": 0.0, "set": {"active": 1}},
                    {"id": "steps", "t": wi(3, "checkpoint"), "dur": 0.0, "set": {"active": 2}},
                    {"id": "steps", "t": wi(3, "redo"), "dur": 0.0, "set": {"active": 3}}]},
        # 4 WAL record: LSN, pg_wal, 16 MB segments
        {"type": "stage", "objects": [
            TITLE(4, [("WAL record: ", "mint"), ("appended at an LSN", "white")]),
            term("r4", "PostgreSQL docs: WAL files", [
                {"text": "insert position: LSN", "color": "white", "at": wi(4, "log")},
                {"text": "LSN is a:        byte offset", "color": "gray", "at": wi(4, "byte")},
                {"text": "directory:       pg_wal", "color": "white", "at": wi(4, "pg_wal")},
                {"text": "segment size:    16 MB", "color": "amber", "hl": True, "hlcolor": "amber", "at": wi(4, "16")},
                {"text": "first segment:", "color": "gray", "at": wi(4, "named")},
                {"text": "000000010000000000000001", "color": "mint", "at": wi(4, "ever-increasing")}], size=29, cps=60)],
         "clear": [], "focus": ["wb", "pw", "steps"],
         "events": [{"id": "steps", "t": -0.2, "dur": 0.0, "set": {"active": 0}},
                    {"id": "sbg", "t": 0.0, "dur": 0.0, "set": {"n": 2}},
                    {"id": "pwg", "t": 0.0, "dur": 0.0, "set": {"n": 0}},
                    {"id": "wbg", "t": wi(4, "change"), "dur": 0.3, "set": {"n": 1}},
                    {"id": "wbg", "t": wi(4, "appended"), "dur": 0.3, "set": {"n": 2}},
                    {"id": "wb", "t": wi(4, "wal"), "dur": 0.0, "set": {"hl": True}},
                    {"id": "wb", "t": wi(4, "pg_wal"), "dur": 0.0, "set": {"hl": False}},
                    {"id": "pw", "t": wi(4, "pg_wal"), "dur": 0.0, "set": {"hl": True}}]},
        # 5 rehook: which file does COMMIT flush?
        {"type": "stage", "objects": [
            {"kind": "question", "id": "q5", "t": -0.25, "x": 540, "y": 466, "parts": [("Only 1 file is flushed at COMMIT. ", "white"), ("Which one?", "amber")], "size": 34},
            {"kind": "pill", "id": "a5", "t": wi(5, "wal"), "x": 300, "y": 1130, "text": "WAL file?", "color": "mint", "size": 44, "maxw": 440},
            {"kind": "pill", "id": "b5", "t": wi(5, "data"), "x": 780, "y": 1130, "text": "Data files?", "color": "amber", "size": 44, "maxw": 440}],
         "clear": ["t4", "r4"], "focus": ["df", "pw", "steps"],
         "events": [{"id": "pw", "t": 0.0, "dur": 0.0, "set": {"hl": False}},
                    {"id": "wbg", "t": 0.0, "dur": 0.0, "set": {"n": 2}},
                    {"id": "wb", "t": 0.0, "dur": 0.0, "set": {"hl": False}},
                    {"id": "pw", "t": wi(5, "wal"), "dur": 0.0, "set": {"hl": True}},
                    {"id": "pw", "t": wi(5, "data"), "dur": 0.0, "set": {"hl": False}},
                    {"id": "df", "t": wi(5, "data"), "dur": 0.0, "set": {"hl": True}}]},
        # 6 flush: only the WAL is flushed at COMMIT
        {"type": "stage", "objects": [
            TITLE(6, [("COMMIT: ", "mint"), ("flush the WAL only", "white")]),
            pkt("p6", wi(6, "flushed"), WB_OUT, "WAL"),
            term("r6", "PostgreSQL docs: settings and functions", [
                {"text": "synchronous_commit = on   -- default", "color": "white", "at": wi(6, "commit")},
                {"text": "> SELECT pg_current_wal_flush_lsn();", "type": True, "color": "white", "at": wi(6, "flushed")},
                {"text": "-- last location known to be", "color": "gray", "at": wi(6, "flushed")},
                {"text": "-- written to durable storage", "color": "gray", "at": wi(6, "changed")},
                {"text": "REDO = roll-forward recovery", "color": "mint", "hl": True, "hlcolor": "mint", "at": wi(6, "roll-forward")}], size=29, cps=45)],
         "clear": ["q5", "a5", "b5"], "focus": [],
         "events": [{"id": "steps", "t": -0.2, "dur": 0.0, "set": {"active": 1}},
                    {"id": "df", "t": 0.0, "dur": 0.0, "set": {"hl": False}},
                    {"id": "pw", "t": 0.0, "dur": 0.0, "set": {"hl": False}},
                    {"id": "wbg", "t": wi(6, "flushed"), "dur": 0.3, "set": {"n": 0}},
                    {"id": "pwg", "t": wi(6, "changed"), "dur": 0.3, "set": {"n": 2}},
                    {"id": "sb", "t": wi(6, "changed"), "dur": 0.0, "set": {"hl": True}},
                    {"id": "sb", "t": wi(6, "roll-forward"), "dur": 0.0, "set": {"hl": False}}]},
        # 7 checkpoint
        {"type": "stage", "objects": [
            TITLE(7, [("Checkpoint: ", "amber"), ("dirty pages to disk", "white")]),
            pkt("p7", wi(7, "flushed"), PG_OUT, "PAGE", color="amber"),
            term("r7", "PostgreSQL docs: CHECKPOINT command", [
                {"text": "> CHECKPOINT;", "type": True, "color": "white", "at": wi(7, "checkpoint", 4)},
                {"text": "-- forces an immediate checkpoint", "color": "gray", "at": wi(7, "forces")}], size=29, h=200, cps=40)],
         "clear": ["t6", "r6", "p6"], "focus": [],
         "events": [{"id": "steps", "t": -0.2, "dur": 0.0, "set": {"active": 2}},
                    {"id": "sb", "t": 0.0, "dur": 0.0, "set": {"hl": False}},
                    {"id": "sb", "t": wi(7, "dirty"), "dur": 0.0, "set": {"hl": True}},
                    {"id": "sbg", "t": wi(7, "flushed"), "dur": 0.3, "set": {"n": 0}},
                    {"id": "sb", "t": wi(7, "flushed"), "dur": 0.0, "set": {"hl": False}},
                    {"id": "dfg", "t": wi(7, "disk"), "dur": 0.3, "set": {"n": 2}},
                    {"id": "pwg", "t": wi(7, "record"), "dur": 0.3, "set": {"n": 3}},
                    {"id": "pw", "t": wi(7, "record"), "dur": 0.0, "set": {"hl": True}}]},
        # 8 when a checkpoint begins
        {"type": "stage", "objects": [
            TITLE(8, [("When a checkpoint ", "amber"), ("begins", "white")]),
            {"kind": "panel", "id": "c1", "t": wi(8, "checkpoint_timeout"), "x": 40, "y": 1010, "w": 1000, "h": 90, "label": "checkpoint_timeout", "icon": "clock", "color": "amber", "value": "5min", "compact": True},
            {"kind": "panel", "id": "c2", "t": wi(8, "max_wal_size"), "x": 40, "y": 1130, "w": 1000, "h": 90, "label": "max_wal_size", "icon": "document", "color": "cyan", "value": "1GB", "compact": True}],
         "clear": ["t7", "r7", "p7"], "focus": [],
         "events": [{"id": "pw", "t": 0.0, "dur": 0.0, "set": {"hl": False}},
                    {"id": "c1", "t": wi(8, "5"), "dur": 0.0, "set": {"hl": True}},
                    {"id": "c1", "t": wi(8, "or"), "dur": 0.0, "set": {"hl": False}},
                    {"id": "c2", "t": wi(8, "1"), "dur": 0.0, "set": {"hl": True}},
                    {"id": "pwg", "t": wi(8, "exceeded"), "dur": 0.8, "set": {"n": 8, "color": "pink"}},
                    {"id": "c2", "t": wi(8, "exceeded"), "dur": 0.0, "set": {"value_color": "pink"}}]},
        # 9 REDO after a crash
        {"type": "stage", "objects": [
            TITLE(9, [("Crash recovery: ", "pink"), ("REDO from the checkpoint", "white")]),
            pkt("p9", wi(9, "starts"), REDO_OUT, "REDO", color="mint", dur=1.0),
            term("r9", "PostgreSQL docs: crash recovery", [
                {"text": "latest checkpoint record", "color": "white", "at": wi(9, "reads")},
                {"text": "-> redo record", "color": "amber", "at": wi(9, "redo")},
                {"text": "-> REDO from that point", "color": "mint", "hl": True, "hlcolor": "mint", "at": wi(9, "starts")}], size=29, h=260, cps=40)],
         "clear": ["t8", "c1", "c2"], "focus": [],
         "events": [{"id": "steps", "t": -0.2, "dur": 0.0, "set": {"active": 3}},
                    {"id": "pw", "t": 0.0, "dur": 0.0, "set": {"hl": False}},
                    {"id": "sbg", "t": 0.0, "dur": 0.0, "set": {"n": 3}},
                    {"id": "pwg", "t": 0.0, "dur": 0.0, "set": {"n": 8, "color": "mint"}},
                    {"id": "mem", "t": wi(9, "crash"), "dur": 0.0, "set": {"status": "cross", "color": "pink"}},
                    {"id": "sbg", "t": wi(9, "crash"), "dur": 0.3, "set": {"n": 0}},
                    {"id": "pw", "t": wi(9, "reads"), "dur": 0.0, "set": {"hl": True}},
                    {"id": "sbg", "t": wi(9, "starts"), "dur": 0.8, "set": {"n": 3}},
                    {"id": "mem", "t": wi(9, "starts"), "dur": 0.0, "set": {"status": "check", "color": "cyan"}}]},
        # 10 the trade-off (send-or-save)
        {"type": "stage", "objects": [
            TITLE(10, [("Shorter interval: ", "mint"), ("faster recovery", "white")]),
            {"kind": "bar", "id": "b1", "t": -0.2, "x": 60, "y": 1040, "w": 960, "h": 60, "value": 0.9, "segs": 24, "color": "cyan", "label": "Redo work after a crash"},
            {"kind": "bar", "id": "b2", "t": -0.2, "x": 60, "y": 1190, "w": 960, "h": 60, "value": 0.3, "segs": 24, "color": "amber", "label": "Dirty page flushes"},
            {"kind": "label", "id": "n10", "t": -0.2, "x": 540, "y": 1310, "text": "Illustration, not measured", "size": 26, "color": "gray", "align": "c", "font": "ui"}],
         "clear": ["t9", "r9", "p9"], "focus": [],
         "events": [{"id": "pw", "t": 0.0, "dur": 0.0, "set": {"hl": False}},
                    {"id": "b1", "t": wi(10, "faster"), "dur": 0.8, "set": {"value": 0.3}},
                    {"id": "b2", "t": wi(10, "flushed"), "dur": 0.8, "set": {"value": 0.9, "color": "pink"}}]},
        # 11 the catch: synchronous_commit = off
        {"type": "stage", "objects": [
            TITLE(11, [("Catch: ", "pink"), ("synchronous_commit off", "white")]),
            term("r11", "PostgreSQL docs: asynchronous commit", [
                {"text": "synchronous_commit = off", "color": "white", "hl": True, "hlcolor": "pink", "at": wi(11, "synchronous_commit")},
                {"text": "wal_writer_delay = 200ms   -- default", "color": "white", "at": wi(11, "200")},
                {"text": "risk window: 3 x 200ms = 600ms", "color": "pink", "at": wi(11, "three")},
                {"text": "risk: data loss, not corruption", "color": "mint", "at": wi(11, "database")}], size=29, h=300, cps=40)],
         "clear": ["t10", "b1", "b2", "n10"], "focus": [],
         "events": [{"id": "sbg", "t": 0.0, "dur": 0.0, "set": {"n": 0}},
                    {"id": "mem", "t": 0.0, "dur": 0.0, "set": {"status": None}},
                    {"id": "pwg", "t": 0.0, "dur": 0.0, "set": {"n": 5, "color": "mint"}},
                    {"id": "wbg", "t": wi(11, "does"), "dur": 0.3, "set": {"n": 2, "color": "pink"}},
                    {"id": "mem", "t": wi(11, "crash"), "dur": 0.0, "set": {"status": "cross", "color": "pink"}},
                    {"id": "wbg", "t": wi(11, "lose"), "dur": 0.3, "set": {"n": 0}},
                    {"id": "df", "t": wi(11, "consistent"), "dur": 0.0, "set": {"status": "check"}}]},
        # 12 recap and follow
        {"type": "stage", "objects": [
            {"kind": "dots", "id": "recap", "t": -0.2, "x": 540, "y": 640, "n": 3, "active": -1, "spacing": 300, "labels": ["WAL flush", "Checkpoint", "Replay"],
             "colors": ["mint", "amber", "cyan"], "caption": [("Inside a PostgreSQL ", "white"), ("COMMIT", "amber")]},
            {"kind": "endcard", "id": "end", "t": wi(12, "follow"), "y": 1020, "text": "@techinabite"},
            {"kind": "title", "id": "endl", "t": wi(12, "follow"), "x": 540, "y": 1180, "parts": [("Follow for one tech topic a day.", "white")], "size": 36, "underline": False}],
         "events": [{"id": "recap", "t": wi(12, "wal"), "dur": 0.0, "set": {"active": 0}}, {"id": "recap", "t": wi(12, "checkpoint"), "dur": 0.0, "set": {"active": 1}}, {"id": "recap", "t": wi(12, "replay"), "dur": 0.0, "set": {"active": 2}}],
         "clear": True},
    ],
}
