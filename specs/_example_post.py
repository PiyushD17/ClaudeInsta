# TEMPLATE for a carousel post (layout demo only: placeholder text, not facts, never post it).
# Copy to specs/postNN_<slug>.py. 5-7 slides: slides 1-2 high level (level 1), middle slides how it works (level 2), last content slides deep dive (level 3), then the takeaway.
SPEC = {
    "tag": "@TECHINABITE",
    "topic": "Your topic name",
    "slides": [
        {"type": "cover", "level": 1, "title": [("What", False), ("YOUR TOPIC", True), ("really is", False)], "sub": "One sentence that says what the post explains and why it matters.", "chips": ["6 SLIDES", "BIG PICTURE TO DEEP DIVE"]},
        {"type": "text", "level": 1, "label": "THE BIG PICTURE", "title": "What your topic is, in plain words",
         "bullets": ["First plain statement with the **key term** in bold.", "Second statement, what problem it solves.", "Third statement, where you meet it every day."],
         "callout": "One sentence worth remembering."},
        {"type": "cards", "level": 1, "label": "THE PARTS", "title": "The four parts of your topic", "highlight": 1,
         "cards": [{"label": "PART 1", "head": "First part", "text": "What it does."}, {"label": "PART 2", "head": "Second part", "text": "What it does."},
                   {"label": "PART 3", "head": "Third part", "text": "What it does."}, {"label": "PART 4", "head": "Fourth part", "text": "What it does."}]},
        {"type": "flow", "level": 2, "label": "HOW IT WORKS", "title": "What happens, step by step",
         "nodes": [{"head": "Step one", "text": "What happens first."}, {"head": "Step two", "text": "What happens next."}, {"head": "Step three", "text": "What happens last."}],
         "highlight": 1, "callout": "The step where most people go wrong."},
        {"type": "detail", "level": 3, "label": "DEEP DIVE", "title": "The detail that matters in practice",
         "code": ["# a real command, config or formula", "key = value", "> result"], "notes": ["What the first line means.", "What to watch for in **production**."],
         "callout": "A rule of thumb worth saving."},
        {"type": "takeaway", "level": 3, "label": "RECAP", "title": "What to remember",
         "points": ["The **one idea** of the post.", "The **catch** and when it breaks."], "share": "Send this to someone who keeps asking about it."},
    ],
}
