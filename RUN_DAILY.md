# Daily run: make today's Tech in a Bite video

You are running unattended at the start of the day. The owner will wake up, download your files, add the AI voiceover in
ElevenLabs and post manually. Your job: deliver one finished, fact-checked, 30-60 second animated video plus script and caption.
Read CLAUDE.md first (brand and writing rules). Where this file and CLAUDE.md differ, this file wins.

## 0. Setup (about 1 minute)
```bash
pip install --break-system-packages -q Pillow numpy scipy   # skip if already present
which ffmpeg                                                  # must exist
mkdir -p ~/.claude/instagram && cp instagram/voice.md ~/.claude/instagram/voice.md
```
Instagram skills live in `skills/ig-reel`, `ig-human`, `ig-caption`. Read their SKILL.md files and run their Python tools
(`hookscore.py`, `beats.py`, `humanize.py`, `caption.py`) from those folders. They need no network. Only the reel, human and caption skills are used.

## 1. Pick today's topic
1. Read the shared topics log (Claude Docs document "Tech in a Bite: Topics Log",
   https://claude.ai/artifact/CH7PJ2ycmR5RjzwSrnsvsw). If it cannot be opened, read the "Covered so far" line in memory
   (/areas/social-media-page.md), then `topics_log.md` in this repo. Combine what you can read. Never repeat a covered topic.
2. Pillars to rotate: AI for everyday people, AI for builders, databases, system design, cloud and architecture.
   Do not use the same pillar two days in a row. Prefer evergreen "how it works" explainers; use news only if a major launch
   happened in the last 7 days and you can confirm it from two sources.
3. Day number = highest day in the log + 1.

## 2. Research (facts must be real)
- Open at least two sources with WebFetch (official docs preferred). A search snippet is not a source.
- Every number, name and date in the video must appear in an opened source. If a site is blocked, find another reputable page or mirror.
- If the core claims cannot be verified, drop the topic and take the next one (up to 3 attempts). Never invent or "round up" a statistic.
- Keep a list of the sources you actually opened.
- Copy the source's own wording for the key terms (for example "load balancing algorithm", "health check"). The video must use those exact
  terms. Never swap in a look-alike word ("rules", "tricks", "modes") for a technical term, and never put different kinds of things in one numbered list
  (an algorithm and a health check are not "two algorithms").
- Only state a count ("two common algorithms") if a source states that count. Otherwise say "a common one" or "two popular ones, among others" and mean it.

## 3. Write the script (use ig-reel) with a mandatory hook gate
A video is only worth delivering if people stay past the first three seconds. The hook is judged by `hookscore.py` and must pass before anything is rendered.

**Hook gate (do not skip, do not shortcut):**
1. Read `skills/ig-reel/hooks.json` (26 formulas). Write at least 6 candidate opening lines, each from a DIFFERENT formula.
   Each must be 5 to 12 words (spoken in about 3 seconds), name its subject so a stranger knows what it is about (open with the thing, for example "Your API request ...", before the punch), contain something concrete (a number, a named thing or a clear stake from
   the verified sources), put the payload at the front, speak straight to the viewer, and be TRUE. No fabricated numbers, no fake
   "nobody knows" claims you cannot defend, no promises the video does not deliver.
2. Put the candidates in `out/dayNN_hooks.txt` (one per line) and run `python3 skills/ig-reel/hookscore.py out/dayNN_hooks.txt`.
3. Target: the best hook must be STRONG (overall 70 or more, every component 55 or more, no flags). The script exits with status 0 only when
   the best hook scores 70 or more.
4. If the best hook is below 70: do not render. Read the weakest component for each candidate, write a NEW batch of 6 using other formulas or a
   sharper angle (more specific number, clearer stake, payload first), and score again. Repeat up to 5 rounds. If three rounds in a row stay
   below 55, rethink the angle of the whole video, or pick a different topic.
5. If after 5 rounds the best is still below 70, deliver the best one anyway but start the summary with "HOOK BELOW TARGET" and show
   the scores, so the owner knows to check it.
6. After the script is written, score the FINAL first spoken sentence once more, and the on-screen hook text of the first scene
   (it must say the same thing as the spoken hook, as a complete thought). If either drops below 70, fix it and re-render. Never deliver a
   video whose final hook differs from the one that passed.

**Rehook gate (mandatory, same discipline as the hook gate):** the video has two hooks, an opening hook and one rehook in the middle that renews curiosity.
Structure: hook, delay #1 (problem and setup, answer withheld), REHOOK, delay #2 (building toward the answer), answer, takeaway, closing line.
1. Pick the rehook line: it starts 25% to 65% of the way through the script (by words) and raises a NEW open question, a surprise, or a higher stake
   ("But your 4 servers still fail if the balancer itself breaks."). It must be TRUE and backed by a source quote. No fake cliffhangers, no "you won't believe it".
2. Write at least 6 rehook candidates (5 to 14 words, concrete: a number or named thing from the sources, speaking to "you", tension up front).
   Put them in `out/dayNN_rehooks.txt` and run `python3 rehookscore.py out/dayNN_rehooks.txt`.
3. Target: PASS = overall 60 or more, every component 40 or more, no flags. (The opening hook needs 70/55; a rehook may be a little lower, but far above WEAK, which is under 50.)
   If the best is below the bar, write a NEW batch with a sharper angle and score again, up to 5 rounds. If still below after 5 rounds, deliver the best one but
   start the summary with "REHOOK BELOW TARGET" and show the scores.
4. The rehook must be paid off: a later script line (the payoff) answers exactly what the rehook raised, and the main answer arrives by about 80% of the script.
   Only one rehook per video; do not stall.
5. Give the rehook scene a visible change on screen (a new scene type, a highlighted word or a flip) so viewers notice the second hook.
6. Record it in the facts file: `"rehook": {"line": N, "payoff_line": M}` (1-based script lines). `check_spec.py` verifies position, payoff order and re-scores the line.

**Reach gates (mandatory; they target what Instagram rewards: finishing, replaying, sending). The chart the owner uses: skip in 3 s = red, watch then leave = blue,
finish / replay / send = green.**
1. *Send-or-save line.* Exactly one script line (not the hook, not the closing line) must be worth sending to a specific person or saving: a rule of thumb, a
   "this is the bug your team has" moment, a number to remember. Pick who would send it ("a dev whose API gets rate limited") and why. Record
   `"share": {"line": N, "who": "...", "why": "..."}` in the facts file. It must be true and sourced like everything else. The closing line stays exactly "Follow for one tech topic a day."
2. *Replay design.* The last line before the closing call to action must reuse a word from the hook AND change how the hook reads on a second watch (the answer to the
   hook, turned into the lesson). Record `"replay": {"echo": "<word>", "twist": "..."}`. check_spec.py fails if the echo word is missing from the first and last lines.
3. *Length target.* Aim for 35 to 45 seconds (about 105 to 135 words). check_spec.py warns above 150 words or 50 s. Over 50 s needs a one-line reason in the summary
   (for example "two sources needed to make the example clear"). Never pad to reach a length either.
4. The reviewer (section 4b) also checks: is there a clear send/save line, does the ending recontextualise the hook, is anything cuttable.

**Engagement gate (also mandatory):**
- Run `python3 skills/ig-reel/beats.py script.txt --target <seconds> --wpm 190` and fix every flag it raises (hook too long, a beat that drags,
  a stretch with nothing concrete, no loop). Re-run until clean.
- The line before the closing call to action must echo a key word or idea from the hook, so the video loops cleanly.
- Every scene must show something changing at least every 3 to 4 seconds (the scene types already animate in steps; use them, do not leave a
  static card on screen).
- Do not pad. Cut any sentence that does not move the explanation forward.

**Then write the script** on the winning hook: plain spoken language, contractions, short lines, run it through ig-human.
- Overrides: no on-camera advice, length 30-60 seconds, and the "six words per card" limit does NOT apply. Our rule: every on-screen
  string and spoken line must have complete CONTEXT, so a stranger knows what is being talked about (see CLAUDE.md writing rule). Punchy, fragmentary
  lines are allowed when the subject is named in the line or the line right before it (for example "Your API request costs 1 token. No tokens, no entry.").
  Never use fragments that name no subject or unit ("One row. Ten million.").
- Shape: hook, the problem (delay #1), rehook, the build-up (delay #2), the answer, one takeaway, then exactly: "Follow for one tech topic a day."
- Length: aim for 105 to 135 words (35 to 45 seconds); hard limits 100 to 190 words (30 to 60 s at 3.2 words/second) and at most about 950 characters, because the voiceover
  uses limited free credits. No greeting, no "in this video".
- Explain one idea only. Use a concrete example or analogy. Say what it costs or where it breaks, not only why it is great.

Note: `hookscore.py` is a heuristic. It reliably catches weak, slow or vague hooks but cannot promise views. Use it as a floor, not a guarantee,
and never trade accuracy for a higher score.

## 3b. Facts file and consistency gate (mandatory, before any rendering)
Write `specs/dayNN_facts.json` from the sources you opened (schema at the top of `check_spec.py`):
- `terms`: the source term for each key idea plus the look-alike words you must never use (`never_say`).
- `counts`: the size of any set the video mentions, as stated by a source.
- `illustrative_numbers`: numbers you made up for a worked example (for instance "4 servers"). Each must be labelled as an example on screen.
- `claims`: one entry for EVERY factual sentence in the script and every factual on-screen label: what the video says, the source URL, and a quote copied
  from the page you opened. If you cannot find a quote, cut or rewrite the sentence.
Worked examples must be correct and consistent: decide the example once (how many servers, which visitor goes where), walk through it step by step
in writing, and reuse exactly the same example in every scene and in the script.
Then run `python3 check_spec.py specs/dayNN_slug.py --facts specs/dayNN_facts.json`. Fix every FAIL (wrong term, unsourced number or count,
different example numbers in different scenes, script/scene mismatch). WARN lines (vague short labels, hook wording) must each be fixed or consciously accepted in the report.

## 4. Build the video
1. Copy `specs/_example_generic_scenes.py` to `specs/dayNN_<slug>.py` (NN = day number). Look at `specs/day04_database_index.py` for a
   richer example. Keep `"captions": False` and `"pace_wps": 3.2`.
2. Use exactly one scene per script line, in order. Scene types: hook, steps, versus, stat, bars, flow, pills, approval, lane, scan,
   lookup, tree, writes, cta. Choose the ones that show the idea (steps for a process, versus for a comparison, stat for one number,
   bars for a size comparison). Add a new scene function to `reel.py` if the idea needs a new visual.
3. The hook scene must have its big text on screen from the first frame and must read as a complete thought
   (for example "1 row in 10 million records", never "One row. Ten million.").
4. Vary the music: change `bpm` (100-124), `seed` and `variant` (0, 1 or 2).
   Mascot: every video shows the page mascot (`assets/mascot.png`, a smiling chat-bubble chip with a bite taken out). Keep `"mascot": {"x": 900, "y": 1270, "size": 230}`
   in the spec. It bobs, tilts and bumps on each new line; it has no mouth animation. Never edit or replace the image. A scene may move or shrink it
   (`"mascot": {"x": 985, "y": 700, "size": 150}`) or hide it (`"mascot": False`) when it would cover text or a diagram. Keep it inside x 0-1080, y 230-1440.
   `check_spec.py` fails on any overlap, so fix those by moving the mascot first and only hide it when no free spot exists.
5. Safe zone: keep everything between y=230 and y=1440 on the 1080x1920 frame (the template already does).
6. Render: `python3 build.py specs/dayNN_<slug>.py` creates `out/dayNN_<slug>.mp4` (with music), `_silent.mp4` and `_bgm.wav`.
7. Check: `ffprobe` duration must be 30 to 60 seconds. Render preview frames of every scene (for example with
   `reel.load_spec` and `reel.frame(t)` in a short script) and look at them. Fix any overflow, overlap or cut-off text.
   Read every on-screen string aloud as a stranger would; rewrite anything that raises "what does that mean?".
8. Check the rendered file itself, not only the spec:
   `python3 check_spec.py specs/dayNN_slug.py --facts specs/dayNN_facts.json --video out/dayNN_slug_silent.mp4 --sheet out/dayNN_sheet.png --report out/dayNN_check.md`
   It re-checks the script and every on-screen string, then inspects the video: duration, content outside the Instagram safe zone, and dead or blank
   screens (FAIL at 0.5 s or more, WARN at 0.2 s or more). Fix and re-render until there is no FAIL.

## 4b. Reviewer pass (mandatory, independent)
The person who wrote the video must not be the only one to check it. Start a fresh reviewer with the Agent tool (general-purpose). Give it ONLY:
the facts file, `out/dayNN_check.md` (which lists the script next to every on-screen string, scene by scene), and `out/dayNN_sheet.png` (frames of every scene).
Do not give it your drafting notes. Ask it to:
1. For every spoken sentence, find the claim and source quote that supports it. List any sentence with no support.
2. For every on-screen string, confirm it is true, uses the source term, and says the same thing as the spoken line of its scene.
3. Walk through every worked example step by step (for instance "visitor 4 with 3 servers goes to server 1") and write the result. Confirm the pictures
   in the contact sheet show the same example, and that counts match ("3 servers" shows exactly three).
4. Check technical accuracy against general knowledge and the quotes: is anything oversimplified until it is wrong, or presented as universal when it is only common?
5. Reach check: name the send-or-save line and who would send it, say how the last line changes the hook on a second watch, and name any sentence that could be cut without losing the story.
6. Reply PASS, or a numbered list of problems with the exact fix for each.
Apply every fix, re-run `check_spec.py`, re-render, and send it back to the reviewer. Up to 3 rounds. If the Agent tool is not available, do the same review yourself as a
separate written pass (a table of sentence, quote, verdict) and say in the summary that the review was not independent.
**Stop rule:** if problems remain after 3 rounds, or a fact cannot be supported by a quote, do NOT deliver a video. Send one message that lists the open problems and
the files so far, so the owner can decide. A late correct video beats an on-time wrong one.


## 5. Caption
Run ig-caption. First line = the hook (visible before "more"). Two or three short lines of value, then "Follow for one tech topic a day."
3-5 relevant hashtags. At most one emoji. No invented facts.

## 6. Deliver (the owner downloads these in the morning)
Write these files and send each with SendUserFile:
- `out/dayNN_<slug>.mp4` (video with music)
- `out/dayNN_<slug>_silent.mp4`
- `out/dayNN_<slug>_bgm.wav`
- `out/dayNN_script.txt`: the voiceover script exactly as it should be pasted into ElevenLabs, one paragraph per line
- `out/dayNN_caption.txt`
- `out/dayNN_hooks.txt`: every candidate hook with its score (final one marked); `out/dayNN_rehooks.txt` likewise for the rehook
- `out/dayNN_sources.md`: each source as a link with what it supports, plus the claim table (what the video says, source link, quote)
- `out/dayNN_check.md`: the checker report and the reviewer's verdict
Then send one SendUserMessage: topic, length in seconds (with a reason if over 50 s), the send-or-save line and who it is for, the replay twist, the final hook with its hookscore (and the runner-up scores), the rehook with its score, how many hook and rehook rounds it took, the script, the caption, the sources, the checker result (0 FAIL) and the reviewer verdict, and any doubts or unverified points.
The summary must be readable on its own.

## 7. Update the log
Add a row to the topics log document (Day, date, topic, pillar, hook, sources, status "Video made") using the Claude Docs tools if available.
Also append the topic to the "Covered so far" line in memory (/areas/social-media-page.md) if memory tools are available.
If neither works, say so in the summary and list the row to add by hand.

## 8. Results log (the owner fills it, the run reads it)
The topics log document has a "Results" table (Day, views, average watch time, finished %, replays, sends, saves, notes). The owner pastes numbers from Instagram Insights
a few days after posting. At the start of each run, read it (if any rows are filled) and say in the summary which hook formula, rehook pattern, length and send-line type
did best and worst so far (only with at least 3 rows; otherwise say there is not enough data). Bias the next hook formulas toward the winners but never skip the gates. Never invent numbers.
The repo copy is `results_log.md`.

## Quality gates (do not deliver if any fails)
- Hook: final spoken hook and on-screen hook score STRONG (70+) on hookscore.py, or the summary starts with "HOOK BELOW TARGET" after 5 rounds.
- Rehook: one rehook in the middle (25-65% of the script) that passes `rehookscore.py` (60+, every part 40+) or the summary starts with "REHOOK BELOW TARGET"; it is answered later and the answer arrives by about 80%.
- Engagement: beats.py clean; loop echo present; something changes on screen every 3-4 seconds.
- Every fact traced to an opened source, with a quote in the claim table. Key terms exactly as the sources write them; no look-alike words.
- `check_spec.py` (with the facts file and the rendered video) reports 0 FAIL, and the independent reviewer replied PASS. Otherwise nothing is delivered (see the stop rule).
- Mascot present and never covering text or diagrams (`check_spec.py` reports no MASCOT_ZONE or MASCOT_OVERLAP FAIL).
- One consistent worked example across all scenes; counts in text match what the pictures show.
- Reach: one send-or-save line and a replay twist recorded in the facts file; target 35-45 s (over 50 s needs a reason).
- Duration 30-60 s; script 100-190 words; ends with the closing line.
- All on-screen text complete and fitting on screen; nothing in the top 230 px or bottom 480 px of the frame.
- Topic not already in the log. Brand text says "Tech in a Bite", never a length like "in 25 seconds".
