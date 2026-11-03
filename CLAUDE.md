# Tech in a Bite: project rules

Goal: a faceless short-video page (@techinabite) about tech topics (AI, databases, cloud, system design), aimed at growing an audience and attracting B2B sponsors.
One new 1080x1920, 30 fps video per day. The user generates the voiceover on elevenlabs.io (free credits only,
never spend the user's money without asking) and sends the audio back, or Claude generates it with the ElevenLabs
connector only after explicit approval.

## Daily routine
The automated procedure is in `RUN_DAILY.md` and takes precedence over anything below. In short: read the shared topics log
(Claude Docs document "Tech in a Bite: Topics Log", https://claude.ai/artifact/CH7PJ2ycmR5RjzwSrnsvsw; fall back to `topics_log.md`),
pick a new topic, verify every fact from sources opened now, write a story-style 100-190 word script (30-60 seconds) ending with
"Follow for one tech topic a day.", build the video with `python3 build.py specs/dayNN_topic.py`, write the caption, deliver the files, update the log.
When the user sends a voice recording later: measure it, retime the spec, then `python3 build.py specs/dayNN_topic.py voice.mp3`
(music is ducked under the voice) and render once.

## Hook rules (first 1.5 seconds decide retention)
- Open with the strongest claim or a question, big text on screen from frame 0, written as a complete thought.
- Something visibly changes within the first second. The voice starts immediately.
- Length 30-60 seconds. No burned-in captions: the user adds subtitles in ElevenLabs (specs use "captions": False).
- The final line is always the call to action: "Follow for one tech topic a day."

## Rehook (mid-video second hook)
Every video has one rehook 25-65% of the way in that renews curiosity and is answered later (answer by about 80%). It must be true and sourced.
Score it with `python3 rehookscore.py`: PASS is overall 60+ and every component 40+ (the opening hook needs 70/55). See RUN_DAILY.md section 3.

## Hook quality is mandatory
Every video's hook must score STRONG (70+) on `skills/ig-reel/hookscore.py` before rendering. If the first batch of hooks scores lower, write new hooks
and score again (up to 5 rounds) instead of rendering a weak opening. See RUN_DAILY.md section 3. Engagement matters as much as accuracy.

## Style
Dark background, amber and mint accents, Inter font (bundled in `fonts/`). Music is original and synthesised
(no copyright issues); vary `bpm`, `seed` and `variant` (0-2) per video in the spec's `music` block.

## Scene types in reel.py
`hook`, `steps`, `versus`, `stat`, `bars`, `flow`, `pills`, `approval`, `lane`, `scan`, `lookup`, `tree`, `writes`, `cta`.
Add new scene functions to the SCENES dict when a topic needs a new visual. Keep text inside 940 px width and everything between y=230 and y=1440 (Instagram safe zone).

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

## Accuracy rules (set by the owner after the Day 05 mistakes)
- Use the exact technical terms the sources use. Never replace a term with a look-alike ("3 rules" for algorithms is wrong).
- Numbered lists hold one kind of thing, and any count must be stated by a source.
- One worked example, identical in every scene and in the script (same number of servers, same visitors).
- Every factual sentence needs a source quote in `specs/dayNN_facts.json`; run `python3 check_spec.py` (with `--video`) and get an independent reviewer PASS before delivering.
- If a check cannot be satisfied, deliver a list of problems instead of a video.
