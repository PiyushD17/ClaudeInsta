SPEC = {
    "tag": "@TECHINABITE",
    "dur": 25.0,
    "music": {"bpm": 116, "seed": 11, "variant": 1},
    "lines": [
        ("OpenAI just gave ChatGPT a new job. It's called ChatGPT Work.", 0.2, 3.6),
        ("Connect your apps and files, and it builds the sheets, decks and reports.", 3.9, 8.6),
        ("It links to Slack, Teams, Google Drive and SharePoint, and can keep working for hours.", 8.9, 14.8),
        ("It asks for your approval before any sensitive action.", 15.1, 18.6),
        ("OpenAI launched it in July. Follow for one work tool a day.", 18.9, 24.5),
    ],
    "scenes": [
        {"type": "hook", "kicker": "TECH IN A BITE", "big1": "ChatGPT", "big2": "Work", "sub": "From chatting to getting it done"},
        {"type": "flow", "title": "Connect. Then it builds.", "sources": ["Your apps", "Your files"],
         "outputs": ["Spreadsheets", "Slide decks", "Documents", "Dashboards"]},
        {"type": "pills", "title": "Plugs into your tools", "pills": ["Slack", "Microsoft Teams", "Google Drive", "SharePoint"],
         "bar_label": "Keeps working on a task for hours"},
        {"type": "approval", "title": "You stay in control", "badge": "SENSITIVE ACTION", "ask": "Send this report to the whole team?", "yes": "Approve", "no": "Review"},
        {"type": "cta", "big": "July 2026", "sub": "when OpenAI launched ChatGPT Work", "size": 130},
    ],
}
