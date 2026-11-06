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

## Carousel posts (second daily job)
Besides the reel, a separate daily job makes an Instagram carousel post: 5-7 slides (1080x1350) that climb from the big picture to a deep dive. Procedure: `RUN_DAILY_POST.md`; tools: `carousel.py`, `carousel_check.py`, `specs/postNN_*`. The same brand, writing, accuracy and reviewer rules apply (every slide stands alone, every fact has a source quote, exact source terms, mascot never covers text). Format v3 (owner, Nov 2026): a STORY carousel, no code. Each slide is one chapter explaining a concept in depth in words and ends on a rehook the next slide pays off; model `specs/post01_kubernetes_probes.py`. A post never repeats a topic that already has a reel or a post.

## Content strategy (owner analysis, 6 Nov 2026): read `CONTENT_STRATEGY.md` before every run
Baseline after 8 reels: median about 149 views, very few saves, shares and comments, one 719-view outlier (the database index reel), no evidence of any reach penalty. Hence: hooks are concrete problems, numbers, contradictions or consequences (never "Understanding X" or a generic intro), every piece leaves the viewer something worth saving or sending, every run is tagged with one experiment (NUMBER, FAILURE, COUNTER, EVERYDAY-AI, VISUAL, COMPARE) and delivers `out/<id>_brief.md` (three hooks with rationale, storyboard, accuracy caveats, cover headline, SEO-aware caption, audio note, performance hypothesis). Captions put the main technical keyword in the first line and use 3-5 relevant hashtags. No clickbait, no universal claims, no invented numbers. Never conclude a winner from one or two examples; compare medians once 10-15 more reels exist.

## Story format (technical deep dives): the default for new reels
Reference style measured frame by frame from two long explainers with thousands of views: `STYLE_GUIDE.md` (v2). Procedure: `RUN_DAILY_STORY.md` (takes precedence over the short-reel parts of `RUN_DAILY.md`). Model spec: `specs/day11_rate_limiter.py`.
The screen shows OBJECTS and STATE (nested boxes with contents, key-value stores, servers, packets, a terminal with real commands and output); the voice explains. Labels 1-4 words, never sentences in boxes, text always wrapped inside its box (never below 24 px), nothing overlapping, something changing every 2-3 s on its word. The stage layout check in `check_spec.py` FAILS on overflow, overlap, empty boxes and out-of-zone objects. Mature audience, real mechanism from official docs, hook promises the mechanism, 50 s when it fits, hard maximum 150 s, voiceover script at most 2000 characters (free ElevenLabs credits). All other gates still apply.

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

## Reach signals (what Instagram rewards)
Skipping in the first 3 seconds hurts; finishing, replaying and sending help. So every video has: a hook that names its subject and scores 70+, a rehook, one line worth
sending or saving, a last line that makes the hook land differently on a second watch, and a target length of 35 to 45 seconds. See RUN_DAILY.md section 3 (reach gates)
and section 8 (results log). Nobody can guarantee reach; the results log is how we learn what works.

## Mascot
The page mascot is `assets/mascot.png` (owner-approved; a smiling chat-bubble chip with a bite taken out). Every video shows it via the spec's `"mascot"` key (see RUN_DAILY.md section 4). It never moves its mouth, never covers text, and stays inside the safe zone.

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
Everything written in a video must be clean, complete and understandable on its own. "Complete" means the CONTEXT is complete: a stranger must always know what is being talked about. It does NOT mean every line must be a grammatical sentence. No half measures:
- Short, punchy, even fragmentary lines are allowed (and good for hooks) when the context is complete, for example "Your API request costs 1 token. No tokens, no entry." or "1 row in 10 million records". The subject must be named in the line itself or in the line directly before it.
- Never use clipped fragments that name no subject or unit ("One row. Ten million." says nothing: one row of what?). Fix those by adding the missing context, not by padding into a long sentence.
- Spell numbers and units so they make sense alone ("1 row in 10 million records", not "One row. Ten million.").
- EVERY FRAME STANDS ALONE (owner rule): a viewer who sees only one frame must know what the video is about and understand what the frame says. Each scene must show words that name the topic (the facts file lists `topic_terms`; check_spec.py fails a scene with none) and no label may be a vague headline by itself ("Slow down" says nothing: slow down what?). Write "Too many requests" with a label saying what happens to an API, not a bare slogan.
- Titles must fit on screen (they wrap to two lines automatically); shorten wording instead of cutting words off.
- Before rendering, read every on-screen string aloud as a stranger would: if a viewer would ask "what does that mean?" or "what are we talking about?", add the missing context. Do not rewrite a punchy line into a long sentence if the context is already clear.
- Scripts tell a story (hook question, problem, fix, catch, takeaway), not a list of facts.

## Animations must be correct
Every moving scene is reviewed as a filmstrip (`animsheet.py`, RUN_DAILY.md section 4a), not only as one still frame: the right object must react, counters must equal what is drawn, and the order on screen must equal the order of the words. New animated scenes get a regression test in `tests/`.

## Zero warnings
A video ships only with `check_spec.py` reporting 0 FAIL and 0 WARN (INFO length notes covered by a `length_reason` are fine). A warning means a frame, line or number is not good enough yet: fix it instead of accepting it.

## Accuracy rules (set by the owner after the Day 05 mistakes)
- Use the exact technical terms the sources use. Never replace a term with a look-alike ("3 rules" for algorithms is wrong).
- Numbered lists hold one kind of thing, and any count must be stated by a source.
- One worked example, identical in every scene and in the script (same number of servers, same visitors).
- Every factual sentence needs a source quote in `specs/dayNN_facts.json`; run `python3 check_spec.py` (with `--video`) and get an independent reviewer PASS before delivering.
- If a check cannot be satisfied, deliver a list of problems instead of a video.
