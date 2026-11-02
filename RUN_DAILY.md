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

## 3. Write the script (use ig-reel) with a mandatory hook gate
A video is only worth delivering if people stay past the first three seconds. The hook is judged by `hookscore.py` and must pass before anything is rendered.

**Hook gate (do not skip, do not shortcut):**
1. Read `skills/ig-reel/hooks.json` (26 formulas). Write at least 6 candidate opening lines, each from a DIFFERENT formula.
   Each must be 5 to 12 words (spoken in about 3 seconds), contain something concrete (a number, a named thing or a clear stake from
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

**Engagement gate (also mandatory):**
- Run `python3 skills/ig-reel/beats.py script.txt --target <seconds> --wpm 190` and fix every flag it raises (hook too long, a beat that drags,
  a stretch with nothing concrete, no loop). Re-run until clean.
- The line before the closing call to action must echo a key word or idea from the hook, so the video loops cleanly.
- Every scene must show something changing at least every 3 to 4 seconds (the scene types already animate in steps; use them, do not leave a
  static card on screen).
- Do not pad. Cut any sentence that does not move the explanation forward.

**Then write the script** on the winning hook: plain spoken language, contractions, short lines, run it through ig-human.
- Overrides: no on-camera advice, length 30-60 seconds, and the "six words per card" limit does NOT apply. Our rule is stricter: every on-screen
  string must be a clean, complete, self-explaining sentence or label. Never clipped fragments.
- Shape: hook, the problem, the fix, the catch, one takeaway, then exactly: "Follow for one tech topic a day."
- Length: 100 to 190 words (about 30 to 60 seconds at 3.2 words/second) and at most about 950 characters, because the voiceover
  uses limited free credits. No greeting, no "in this video".
- Explain one idea only. Use a concrete example or analogy. Say what it costs or where it breaks, not only why it is great.

Note: `hookscore.py` is a heuristic. It reliably catches weak, slow or vague hooks but cannot promise views. Use it as a floor, not a guarantee,
and never trade accuracy for a higher score.

## 4. Build the video
1. Copy `specs/_example_generic_scenes.py` to `specs/dayNN_<slug>.py` (NN = day number). Look at `specs/day04_database_index.py` for a
   richer example. Keep `"captions": False` and `"pace_wps": 3.2`.
2. Use exactly one scene per script line, in order. Scene types: hook, steps, versus, stat, bars, flow, pills, approval, lane, scan,
   lookup, tree, writes, cta. Choose the ones that show the idea (steps for a process, versus for a comparison, stat for one number,
   bars for a size comparison). Add a new scene function to `reel.py` if the idea needs a new visual.
3. The hook scene must have its big text on screen from the first frame and must read as a complete thought
   (for example "1 row in 10 million records", never "One row. Ten million.").
4. Vary the music: change `bpm` (100-124), `seed` and `variant` (0, 1 or 2).
5. Safe zone: keep everything between y=230 and y=1440 on the 1080x1920 frame (the template already does).
6. Render: `python3 build.py specs/dayNN_<slug>.py` creates `out/dayNN_<slug>.mp4` (with music), `_silent.mp4` and `_bgm.wav`.
7. Check: `ffprobe` duration must be 30 to 60 seconds. Render preview frames of every scene (for example with
   `reel.load_spec` and `reel.frame(t)` in a short script) and look at them. Fix any overflow, overlap or cut-off text.
   Read every on-screen string aloud as a stranger would; rewrite anything that raises "what does that mean?".

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
- `out/dayNN_hooks.txt`: every candidate hook with its score (final one marked)
- `out/dayNN_sources.md`: each source as a link with what it supports
Then send one SendUserMessage: topic, length in seconds, the final hook with its hookscore (and the runner-up scores), how many hook rounds it took, the script, the caption, the sources, and any doubts or unverified points.
The summary must be readable on its own.

## 7. Update the log
Add a row to the topics log document (Day, date, topic, pillar, hook, sources, status "Video made") using the Claude Docs tools if available.
Also append the topic to the "Covered so far" line in memory (/areas/social-media-page.md) if memory tools are available.
If neither works, say so in the summary and list the row to add by hand.

## Quality gates (do not deliver if any fails)
- Hook: final spoken hook and on-screen hook score STRONG (70+) on hookscore.py, or the summary starts with "HOOK BELOW TARGET" after 5 rounds.
- Engagement: beats.py clean; loop echo present; something changes on screen every 3-4 seconds.
- Every fact traced to an opened source.
- Duration 30-60 s; script 100-190 words; ends with the closing line.
- All on-screen text complete and fitting on screen; nothing in the top 230 px or bottom 480 px of the frame.
- Topic not already in the log. Brand text says "Tech in a Bite", never a length like "in 25 seconds".
