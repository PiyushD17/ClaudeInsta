LINES = [
    "Stop retraining AI models on your documents. Try RAG first.",
    "A language model's training data is static, with a cut-off date.",
    "Say your refund policy is not in it. Ask the chatbot, and it can present false information.",
    "RAG, retrieval-augmented generation, goes through these steps: create external data, retrieve relevant information, augment the LLM prompt, and update external data.",
    "Step 1: split each document into chunks, so that each piece fits the embedding model. Example chunk sizes range from 128 to 1024 tokens.",
    "But how does RAG pick the 1 related chunk out of all your documents?",
    "Then an embedding model converts each chunk into an embedding, a vector: a list of floating point numbers. By default, text-embedding-3-small returns 1536 numbers per chunk.",
    "That answers the earlier question: the distance between two vectors measures their relatedness. Small distances suggest high relatedness and large distances suggest low relatedness.",
    "The vectors are stored in a vector database. In Postgres, the pgvector extension lets you create a vector column in a table.",
    "Step 2: the user query is converted to a vector and matched with the vector database. In pgvector, ORDER BY a distance operator with LIMIT returns the nearest neighbors.",
    "Step 3: the RAG model augments the user input by adding the relevant retrieved data in context. The LLM receives the question and the retrieved information together.",
    "Step 4: to maintain current information, update the documents and update their embedding representations, in real time or in periodic batches.",
    "The catch: finding the right context gets harder at scale, which lowers answer quality.",
    "So before you retrain an AI model on your documents, ask whether RAG can retrieve them instead. Follow for one tech topic a day.",
]

def wi(line, token, k=1):
    """'wN' anchor: the k-th word of script line `line` (1-based) that starts with `token`."""
    ws = [w.strip(".,:?").lower() for w in LINES[line - 1].split()]
    hits = [i + 1 for i, w in enumerate(ws) if w.startswith(token.lower())]
    return "w%d" % hits[k - 1]

DOTS = lambda act, t=-0.3: {"kind": "dots", "id": "steps", "x": 540, "y": 345, "n": 4, "active": act, "t": t}

SPEC = {
    "tag": "@TECHINABITE",
    "pace_wps": 3.2,
    "captions": False,
    "format": "story",
    "music": {"bpm": 100, "seed": 10, "variant": 2},
    "mascot": {"x": 900, "y": 1300, "size": 150},
    "lines": LINES,
    "scenes": [
        # 1 hook: the story canvas from frame 0
        {"type": "stage", "objects": [
            {"kind": "text", "id": "k", "t": -0.5, "x": 540, "y": 285, "text": "TECH IN A BITE", "size": 30, "color": "amber", "align": "c", "font": "med"},
            {"kind": "text", "id": "h1", "t": -0.5, "x": 540, "y": 330, "text": "Stop retraining AI models on your documents.", "size": 66, "color": "white", "align": "c", "maxw": 900},
            {"kind": "text", "id": "h2", "t": wi(1, "try"), "x": 540, "y": 520, "text": "Try RAG first.", "size": 72, "color": "amber", "align": "c"},
            {"kind": "panel", "id": "docs", "t": 0.0, "x": 70, "y": 660, "w": 380, "h": 250, "title": "Example: 5 document files", "icon": "folder"},
            {"kind": "grid", "id": "g", "t": 0.1, "x": 100, "y": 750, "w": 320, "h": 70, "cols": 5, "rows": 1, "n": 5, "color": "gray"},
            {"kind": "panel", "id": "llm2", "t": 0.0, "x": 520, "y": 660, "w": 490, "h": 250, "title": "AI language model", "icon": "chat", "color": "purple"},
            {"kind": "arrow", "id": "a1", "t": 0.8, "points": [(450, 790), (520, 790)], "color": "mint"}]},
        # 2 static training data
        {"type": "stage", "objects": [
            {"kind": "brush", "id": "t1", "t": -0.3, "x": 540, "y": 420, "parts": [("Language models: ", "white"), ("static training data", "amber")], "size": 46},
            {"kind": "meter", "id": "train", "x": 548, "y": 770, "w": 440, "h": 34, "value": 0.0, "label": "Its training data", "color": "mint", "t": wi(2, "training")},
            {"kind": "chip", "id": "cut", "x": 765, "y": 860, "text": "Cut-off date: no newer facts", "color": "amber", "t": wi(2, "cut-off")}],
         "clear": ["k", "h1", "h2", "docs", "g", "a1"],
         "events": [{"id": "train", "t": wi(2, "training"), "dur": 1.6, "set": {"value": 1.0}}]},
        # 3 chatbot example
        {"type": "stage", "objects": [
            {"kind": "terminal", "id": "chat", "x": 90, "y": 950, "w": 900, "h": 210, "title": "Example: chatbot without RAG", "size": 25, "cps": 28, "t": wi(3, "not"),
             "lines": [{"text": "(Your refund policy is not in its training data.)", "color": "gray"},
                       {"text": "$ Ask: What is our refund policy?", "type": True, "color": "white", "pause": 0.8},
                       {"text": "Answer: Refunds are allowed at any time.", "color": "red", "hl": True}]},
            {"kind": "badge", "id": "bad", "x": 1030, "y": 1060, "name": "cross", "size": 54, "t": wi(3, "false")}]},
        # 4 RAG in 4 steps
        {"type": "stage", "objects": [
            {"kind": "brush", "id": "t4", "t": -0.2, "x": 540, "y": 400, "parts": [("RAG: ", "cyan"), ("retrieval-augmented generation", "white")], "size": 44},
            {"kind": "panel", "id": "r1", "x": 90, "y": 500, "w": 900, "h": 100, "title": "Step 1: Create external data", "color": "amber", "t": wi(4, "create"), "tsize": 32},
            {"kind": "panel", "id": "r2", "x": 90, "y": 630, "w": 900, "h": 100, "title": "Step 2: Retrieve relevant information", "color": "cyan", "t": wi(4, "retrieve"), "tsize": 32},
            {"kind": "panel", "id": "r3", "x": 90, "y": 760, "w": 900, "h": 100, "title": "Step 3: Augment the LLM prompt", "color": "pink", "t": wi(4, "augment"), "tsize": 32},
            {"kind": "panel", "id": "r4", "x": 90, "y": 890, "w": 900, "h": 100, "title": "Step 4: Update external data", "color": "mint", "t": wi(4, "update"), "tsize": 32}],
         "clear": ["t1", "llm2", "train", "cut", "chat", "bad"]},
        # 6 step 1: chunking
        {"type": "stage", "objects": [
            DOTS(0),
            {"kind": "brush", "id": "t6", "t": -0.2, "x": 540, "y": 430, "parts": [("Step 1: ", "amber"), ("split documents into chunks", "white")], "size": 40},
            {"kind": "panel", "id": "d6", "x": 70, "y": 540, "w": 380, "h": 400, "title": "Example: 1 document", "icon": "document", "t": wi(5, "split")},
            {"kind": "grid", "id": "gd", "x": 110, "y": 620, "w": 300, "h": 280, "cols": 1, "rows": 8, "n": 8, "color": "gray", "t": wi(5, "split")},
            {"kind": "arrow", "id": "a6", "points": [(450, 740), (520, 740)], "color": "amber", "t": wi(5, "into")},
            {"kind": "panel", "id": "c6", "x": 520, "y": 540, "w": 490, "h": 400, "title": "Example: document chunks for RAG", "icon": "folder", "color": "amber", "t": wi(5, "into")},
            {"kind": "grid", "id": "gc", "x": 550, "y": 620, "w": 430, "h": 280, "cols": 4, "rows": 3, "n": 0, "color": "amber", "t": wi(5, "into")},
            {"kind": "chip", "id": "sz", "x": 540, "y": 1030, "text": "Example chunk sizes: 128 to 1024 tokens", "color": "amber", "t": wi(5, "example")}],
         "clear": ["t4", "r1", "r2", "r3", "r4"],
         "events": [{"id": "gc", "t": wi(5, "chunks"), "dur": 1.8, "set": {"n": 12}}]},
        # 6 rehook
        {"type": "stage", "objects": [
            {"kind": "question", "id": "q", "x": 540, "y": 440, "text": "How does RAG pick the 1 related chunk?", "size": 28, "t": -0.2},
            {"kind": "grid", "id": "qa", "x": 90, "y": 580, "w": 900, "h": 300, "cols": 9, "rows": 4, "n": 36, "color": "amber", "label": "Example: chunks of your documents", "t": wi(6, "chunk")},
            {"kind": "chip", "id": "rel", "x": 540, "y": 960, "text": "Your question: which 1 chunk is related?", "color": "pink", "t": wi(6, "related")}],
         "clear": ["t6", "d6", "gd", "a6", "c6", "gc", "sz"]},
        # 7 embedding
        {"type": "stage", "objects": [
            {"kind": "brush", "id": "t7", "t": -0.2, "x": 540, "y": 430, "parts": [("Chunk → ", "white"), ("embedding", "cyan")], "size": 44},
            {"kind": "chip", "id": "ch", "x": 540, "y": 540, "text": "One chunk of text", "color": "amber", "t": wi(7, "chunk")},
            {"kind": "arrow", "id": "a71", "points": [(540, 575), (540, 640)], "color": "gray", "t": wi(7, "chunk")},
            {"kind": "panel", "id": "em", "x": 190, "y": 650, "w": 700, "h": 110, "title": "Text embedding model for RAG", "icon": "gear", "color": "purple", "t": wi(7, "embedding")},
            {"kind": "arrow", "id": "a72", "points": [(540, 765), (540, 830)], "color": "gray", "t": wi(7, "vector")},
            {"kind": "terminal", "id": "vec", "x": 90, "y": 840, "w": 900, "h": 130, "title": "Example (shortened): a vector (list) of floating point numbers", "size": 30, "t": wi(7, "floating"),
             "lines": [{"text": "[0.0123, -0.0345, 0.1012, ...]", "color": "mint"}]},
            {"kind": "chip", "id": "dim", "x": 540, "y": 1050, "text": "text-embedding-3-small: 1536 numbers per chunk", "color": "cyan", "t": wi(7, "text-")}],
         "clear": ["q", "qa", "rel"]},
        # 8 payoff of the rehook
        {"type": "stage", "objects": [
            {"kind": "brush", "id": "t8", "t": -0.2, "x": 540, "y": 430, "parts": [("Distance = ", "white"), ("relatedness", "mint")], "size": 44},
            {"kind": "panel", "id": "map", "x": 70, "y": 520, "w": 940, "h": 460, "title": "Vectors compared (simplified illustration)", "icon": "magnifier", "color": "gray", "t": wi(8, "distance")},
            {"kind": "chip", "id": "mq", "x": 520, "y": 760, "text": "Your question as a vector", "color": "amber", "t": wi(8, "distance")},
            {"kind": "chip", "id": "mr", "x": 690, "y": 830, "text": "Refund policy chunk", "color": "mint", "t": wi(8, "small")},
            {"kind": "text", "id": "ms", "x": 700, "y": 880, "text": "small distance: high relatedness", "size": 26, "color": "mint", "align": "c", "t": wi(8, "small")},
            {"kind": "chip", "id": "mh", "x": 290, "y": 610, "text": "Holiday list chunk", "color": "gray", "t": wi(8, "large"), "filled": False},
            {"kind": "text", "id": "ml", "x": 290, "y": 655, "text": "large distance: low relatedness", "size": 26, "color": "gray", "align": "c", "t": wi(8, "large")}],
         "clear": ["t7", "ch", "a71", "em", "a72", "vec", "dim"]},
        # 9 vector database table
        {"type": "stage", "objects": [
            {"kind": "brush", "id": "t9", "t": -0.2, "x": 540, "y": 430, "parts": [("Store vectors: ", "white"), ("pgvector", "cyan")], "size": 44},
            {"kind": "terminal", "id": "sql", "x": 90, "y": 540, "w": 900, "h": 270, "title": "Postgres + pgvector", "size": 26, "cps": 40, "t": wi(9, "postgres"),
             "lines": [{"text": "CREATE EXTENSION vector;", "type": True, "color": "white"},
                       {"text": "CREATE TABLE items (id bigserial PRIMARY KEY,", "type": True, "color": "white"},
                       {"text": "  embedding vector(3));", "type": True, "color": "mint"}]},
            {"kind": "chip", "id": "v3", "x": 540, "y": 900, "text": "vector(3): 3 dimensions, only to keep the example small", "color": "cyan", "t": wi(9, "create"), "filled": False},
            {"kind": "chip", "id": "v1536", "x": 540, "y": 975, "text": "A real text-embedding-3-small vector: 1536 numbers", "color": "gray", "t": wi(9, "create"), "filled": False}],
         "clear": ["t8", "map", "mq", "mr", "ms", "mh", "ml"]},
        # 10 step 2: retrieval
        {"type": "stage", "objects": [
            {"kind": "brush", "id": "t10", "t": -0.2, "x": 540, "y": 430, "parts": [("Step 2: ", "cyan"), ("find the nearest vectors", "white")], "size": 40},
            {"kind": "terminal", "id": "q10", "x": 90, "y": 540, "w": 900, "h": 260, "title": "Query: your question as a vector", "size": 28, "cps": 45, "t": wi(10, "pgvector"),
             "lines": [{"text": "SELECT * FROM items", "type": True, "color": "white"},
                       {"text": "ORDER BY embedding <-> '[3,1,2]'", "type": True, "color": "mint"},
                       {"text": "LIMIT 5;", "type": True, "color": "white"}]},
            {"kind": "chip", "id": "l2", "x": 540, "y": 870, "text": "<->  L2 distance", "color": "cyan", "t": wi(10, "distance")},
            {"kind": "chip", "id": "cos", "x": 540, "y": 945, "text": "<=>  cosine distance", "color": "amber", "t": wi(10, "distance")}],
         "clear": ["t9", "sql", "v3", "v1536"],
         "events": [{"id": "steps", "t": 0.0, "dur": 0.5, "set": {"active": 1}}]},
        # 11 step 3: augment
        {"type": "stage", "objects": [
            {"kind": "brush", "id": "t11", "t": -0.2, "x": 540, "y": 430, "parts": [("Step 3: ", "pink"), ("augment the prompt", "white")], "size": 40},
            {"kind": "terminal", "id": "pr", "x": 90, "y": 540, "w": 900, "h": 190, "title": "Example: prompt sent to the LLM", "size": 26, "t": wi(11, "augments"),
             "lines": [{"text": "Context: <retrieved chunk about refunds>", "color": "mint"},
                       {"text": "Question: What is our refund policy?", "color": "amber"}]},
            {"kind": "arrow", "id": "a11", "points": [(540, 735), (540, 800)], "color": "gray", "t": wi(11, "receives")},
            {"kind": "panel", "id": "m11", "x": 190, "y": 810, "w": 700, "h": 120, "title": "AI language model (LLM)", "icon": "chat", "color": "purple", "t": wi(11, "receives")},
            {"kind": "chip", "id": "ans", "x": 540, "y": 1000, "text": "Question + retrieved information go to the LLM", "color": "mint", "t": wi(11, "together")}],
         "clear": ["t10", "q10", "l2", "cos"],
         "events": [{"id": "steps", "t": 0.0, "dur": 0.5, "set": {"active": 2}}]},
        # 12 step 4: update
        {"type": "stage", "objects": [
            {"kind": "brush", "id": "t12", "t": -0.2, "x": 540, "y": 430, "parts": [("Step 4: ", "mint"), ("keep the data current", "white")], "size": 40},
            {"kind": "panel", "id": "d12", "x": 70, "y": 540, "w": 380, "h": 170, "title": "Your documents for RAG", "icon": "document", "color": "mint", "t": wi(12, "update")},
            {"kind": "arrow", "id": "a12", "points": [(450, 625), (520, 625)], "color": "mint", "t": wi(12, "embedding")},
            {"kind": "panel", "id": "v12", "x": 520, "y": 540, "w": 490, "h": 170, "title": "Vector database for RAG", "icon": "database", "color": "cyan", "t": wi(12, "embedding")},
            {"kind": "chip", "id": "u1", "x": 260, "y": 780, "text": "Update the documents", "color": "mint", "t": wi(12, "update")},
            {"kind": "chip", "id": "u2", "x": 765, "y": 780, "text": "Update their embeddings", "color": "cyan", "t": wi(12, "embedding")},
            {"kind": "chip", "id": "rt", "x": 540, "y": 880, "text": "Real-time process: update embeddings", "color": "amber", "t": wi(12, "real"), "filled": False},
            {"kind": "chip", "id": "pb", "x": 540, "y": 960, "text": "Periodic batch: update embeddings", "color": "amber", "t": wi(12, "periodic"), "filled": False}],
         "clear": ["t11", "pr", "a11", "m11", "ans"],
         "events": [{"id": "steps", "t": 0.0, "dur": 0.5, "set": {"active": 3}}]},
        # 13 the catch
        {"type": "stage", "objects": [
            {"kind": "brush", "id": "t13", "t": -0.2, "x": 540, "y": 430, "parts": [("The catch with ", "white"), ("RAG at scale", "pink")], "size": 44},
            {"kind": "meter", "id": "qual", "x": 130, "y": 620, "w": 820, "h": 34, "value": 1.0, "label": "Illustration: RAG chatbot answer quality", "color": "green", "t": -0.1},
            {"kind": "grid", "id": "scale", "x": 130, "y": 740, "w": 820, "h": 110, "cols": 30, "rows": 3, "n": 6, "color": "amber", "label": "Illustration: documents the chatbot must search", "t": -0.1}],
         "clear": ["t12", "d12", "a12", "v12", "u1", "u2", "rt", "pb", "steps"],
         "events": [{"id": "qual", "t": wi(13, "lowers"), "dur": 2.0, "set": {"value": 0.4, "color": "red"}},
                    {"id": "scale", "t": wi(13, "at"), "dur": 2.0, "set": {"n": 80}}]},
        {"type": "cta", "big": "Retrain an AI model on your documents?", "sub": "Ask if RAG can retrieve them instead.", "size": 76, "line": "for one tech topic a day.", "follow_first": True, "follow_at": 4.9, "sub_at": 1.8},
    ],
}
