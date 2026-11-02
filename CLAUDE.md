# Work Tools reels: project rules

Goal: a faceless short-video page about AI and software tools for work, aimed at B2B sponsors.
One new 1080x1920, 30 fps video per day. The user generates the voiceover on elevenlabs.io (free credits only,
never spend the user's money without asking) and sends the audio back, or Claude generates it with the ElevenLabs
connector only after explicit approval.

## Daily routine
1. Read the shared topics log (the Claude Docs document "Tech in a Bite: Topics Log", https://claude.ai/artifact/CH7PJ2ycmR5RjzwSrnsvsw; fall back to `topics_log.md`). Never repeat a topic. Pick a popular, current work tool (use the backlog or search the web for
   what launched recently).
2. Research: every claim and number must be checked against at least one reliable source, fetched now.
   Never invent statistics. Say "illustration" on any visual that is not real data or a real UI.
3. Write the script: 5 lines, about 20-25 seconds spoken (max ~3 words per second), the last line is the call to action
   ("Follow for one work tool a day.").
4. Create `specs/dayNN_topic.py` (copy `specs/day02_chatgpt_work.py`). Line start times drive scene changes and captions.
5. `python build.py specs/dayNN_topic.py` gives a silent video plus music. Send the script, silent video and music to the user.
6. When the user sends the voice audio: measure the voice (silence/energy detection or a transcript), retime the `lines`
   start/end times in the spec to match, end the video when the voice ends, then
   `python build.py specs/dayNN_topic.py path/to/voice.mp3` (music is ducked under the voice). Render once, send the file.
7. Add a row to the shared topics log document (and `topics_log.md`) (date, topic, hook angle, sources).

## Hook rules (first 1.5 seconds decide retention)
- Open with the strongest claim or a question, big text on screen from frame 0.
- Something visibly changes within the first second. Voice starts immediately, no silent lead-in.
- Length 20-25 seconds, or about 45 seconds when asked. Burned-in captions only if the spec has "captions": True (default). The user adds subtitles in ElevenLabs, so for those videos set "captions": False. The final line is the call to action.

## Style
Dark background, amber and mint accents, Inter font (bundled in `fonts/`). Music is original and synthesised
(no copyright issues); vary `bpm`, `seed` and `variant` (0-2) per video in the spec's `music` block.

## Scene types in reel.py
`hook`, `flow` (sources to output chips), `pills` (app list plus progress bar), `approval` (confirmation card), `cta`.
Add new scene functions to the SCENES dict when a topic needs a new visual. Keep text inside 940 px width.

## Setup (once)
Python 3.10+, `pip install -r requirements.txt`, and ffmpeg on the PATH (macOS: `brew install ffmpeg`,
Windows: `winget install ffmpeg`).

## Brand
Page name: Tech in a Bite (handle @techinabite). Header tag on every video is "@TECHINABITE" and the hook kicker (first scene) always reads "TECH IN A BITE". Never use "Tech in 25 seconds" or any length in the name. Topics: AI for everyday people,
developers, engineers and managers, plus cloud, databases, solution architecture and system design. Profile picture: `python avatar.py "TECH IN A" "BITE" out/avatar.png ""`.

## Writing rule for ALL on-screen text and scripts (set by the user, non-negotiable)
Everything written in a video must be clean, complete and understandable on its own. No half measures:
- Use complete sentences or clear, self-explaining labels. Never clipped fragments ("One row. Ten million.").
- Spell numbers and units so they make sense alone ("1 row in 10 million records", not "One row. Ten million.").
- Titles must fit on screen (they wrap to two lines automatically); shorten wording instead of cutting words off.
- Before rendering, read every on-screen string aloud as a stranger would: if a viewer would ask "what does that mean?", rewrite it.
- Scripts tell a story (hook question, problem, fix, catch, takeaway), not a list of facts.
