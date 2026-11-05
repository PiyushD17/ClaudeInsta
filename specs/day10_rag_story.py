SPEC = {
    "tag": "@TECHINABITE",
    "pace_wps": 3.2,
    "captions": False,
    "music": {"bpm": 108, "seed": 10, "variant": 2},
    "mascot": {"x": 900, "y": 1300, "size": 150},
    "lines": [
        ("Stop retraining AI models on your documents. Try RAG first."),
        ("A language model's training data is static, with a cut-off date."),
        ("Say your refund policy is not in it. Ask the chatbot, and it can present false information."),
        ("But how does the chatbot find the 1 relevant page in all your documents?"),
        ("RAG, retrieval-augmented generation, retrieves relevant information, then gives it to the model with your question."),
        ("Often, your documents are converted to numerical representations and stored in a vector database. Your question is converted too, then matched against them."),
        ("So to change what a RAG chatbot knows, don't retrain the model. Update its documents."),
        ("The catch: finding the right context gets harder at scale, which lowers answer quality."),
        ("So before you retrain an AI model on your documents, ask whether RAG can retrieve them instead. Follow for one tech topic a day."),
    ],
    "scenes": [
        {"type": "hook", "kicker": "TECH IN A BITE", "big1": "Stop retraining AI models", "big2": "on your documents.", "sub": "Try RAG first.", "size1": 84, "size2": 90},
        {"type": "stage", "objects": [
            {"kind": "brush", "id": "t1", "t": -0.3, "x": 540, "y": 380, "parts": [("Language models: ", "white"), ("static training data", "amber")], "size": 50},
            {"kind": "panel", "id": "llm", "x": 90, "y": 520, "w": 900, "h": 330, "title": "Large language model (LLM)", "icon": "database", "color": "purple", "t": "w1"},
            {"kind": "meter", "id": "train", "x": 130, "y": 640, "w": 820, "h": 34, "value": 0.0, "label": "Training data of an AI language model", "color": "mint", "t": "w4"},
            {"kind": "chip", "id": "cut", "x": 540, "y": 770, "text": "Cut-off date: no newer facts", "color": "amber", "t": "w10"}],
         "events": [{"id": "train", "t": "w4", "dur": 1.6, "set": {"value": 1.0}}]},
        {"type": "stage", "objects": [
            {"kind": "terminal", "id": "chat", "x": 90, "y": 900, "w": 900, "h": 240, "title": "Example: chatbot without RAG", "size": 25, "cps": 40, "t": 0.3,
             "lines": [{"text": "(Your refund policy is not in its training data.)", "color": "gray"},
                       {"text": "$ Ask: What is our refund policy?", "type": True, "color": "white"},
                       {"text": "Answer: Refunds are allowed at any time.", "color": "red", "hl": True}]},
            {"kind": "badge", "id": "bad", "x": 940, "y": 1070, "name": "cross", "size": 54, "t": "w16"}]},
        {"type": "stage", "objects": [
            {"kind": "question", "id": "q", "x": 540, "y": 330, "text": "How does the chatbot find the 1 relevant page in your documents?", "size": 26, "t": 0.2}],
         "clear": ["t1", "llm", "train", "cut", "chat", "bad"]},
        {"type": "stage", "objects": [
            {"kind": "brush", "id": "t2", "x": 540, "y": 440, "parts": [("RAG: ", "cyan"), ("retrieval-augmented generation", "white")], "size": 44},
            {"kind": "panel", "id": "docs", "x": 70, "y": 560, "w": 380, "h": 330, "title": "Example: 5 document files", "icon": "folder", "t": 0.3},
            {"kind": "grid", "id": "g", "x": 100, "y": 650, "w": 320, "h": 70, "cols": 5, "rows": 1, "n": 5, "color": "gray", "t": 0.4},
            {"kind": "packet", "id": "p1", "path": [(300, 790), (470, 790), (650, 790)], "text": "1 page", "color": "mint", "dur": 1.2, "hold": False, "t": "w4"},
            {"kind": "panel", "id": "llm2", "x": 520, "y": 560, "w": 490, "h": 330, "title": "AI language model", "icon": "chat", "color": "purple", "t": "w1"},
            {"kind": "text", "id": "pr", "x": 765, "y": 700, "text": "Question + 1 relevant page", "size": 28, "align": "c", "maxw": 420, "color": "white", "t": "w13"},
            {"kind": "arrow", "id": "a1", "points": [(450, 720), (520, 720)], "color": "mint", "t": "w3"}]},
        {"type": "stage", "objects": [
            {"kind": "panel", "id": "vec", "x": 70, "y": 975, "w": 940, "h": 150, "title": "Vector database for your documents", "icon": "database", "color": "cyan", "t": "w5"},
            {"kind": "chip", "id": "c1", "x": 375, "y": 1070, "text": "Documents → numerical representations", "color": "cyan", "t": "w5"},
            {"kind": "chip", "id": "c2", "x": 540, "y": 932, "text": "Your question → numerical representation", "color": "amber", "t": "w16"},
            {"kind": "callout", "id": "m", "x": 540, "y": 1165, "text": "Question matched against documents", "size": 24, "t": "w21"}]},
        {"type": "stage", "objects": [
            {"kind": "callout", "id": "no", "x": 760, "y": 985, "text": "Don't retrain the model", "color": "pink", "size": 30, "tx": 760, "ty": 895, "t": "w9"},
            {"kind": "callout", "id": "yes", "x": 270, "y": 1065, "text": "Update its documents", "color": "mint", "size": 30, "tx": 270, "ty": 895, "t": "w13"}],
         "clear": ["vec", "c1", "c2", "m"]},
        {"type": "stage", "objects": [
            {"kind": "meter", "id": "qual", "x": 130, "y": 940, "w": 820, "h": 34, "value": 1.0, "label": "Illustration: RAG chatbot answer quality", "color": "green", "t": 0.2},
            {"kind": "grid", "id": "scale", "x": 130, "y": 1030, "w": 820, "h": 90, "cols": 30, "rows": 3, "n": 6, "color": "amber", "label": "Illustration: documents the chatbot must search", "t": 0.3}],
         "clear": ["no", "yes"],
         "events": [{"id": "qual", "t": "w12", "dur": 2.0, "set": {"value": 0.4, "color": "red"}}, {"id": "scale", "t": "w9", "dur": 2.0, "set": {"n": 80}}]},
        {"type": "cta", "big": "Retrain an AI model on your documents?", "sub": "Ask if RAG can retrieve them instead.", "size": 76, "line": "for one tech topic a day.", "follow_first": True, "follow_at": 4.9, "sub_at": 1.8},
    ],
}
