# Daily post run: make today's Tech in a Bite carousel post (Instagram, 5-7 images)

You run unattended. The owner wakes up, downloads your files and posts manually. Your job: deliver one finished, fact-checked carousel post (5 to 7 slides)
plus caption. A post is NOT a reel: it is read, saved and sent, not watched. Read CLAUDE.md first (brand, writing rules, accuracy rules, mascot, reach signals).
This file only replaces the video-specific parts (voiceover, scenes, music, animation review). Everything else in CLAUDE.md and RUN_DAILY.md section 2 (research) and section 4b (reviewer) applies.

## The idea of the format
One topic, explained at a high level first and then deeper with every swipe, so a beginner understands slides 1-3 and an engineer still learns something on slides 5-6.
- Level 1 (slides 1-3): the big picture. What it is, why it exists, the main parts, in plain words.
- Level 2 (slide 4, optionally 5): how it works, step by step.
- Level 3 (slides 5-6): the deep dive. The concrete detail a practitioner needs: a real command, config, number, trade-off or failure mode, all from sources.
- Last slide: takeaway, one slide worth sending or saving, and exactly "Follow for one tech topic a day.".
Each slide adds exactly one new idea and makes the next slide worth swiping to. Never repeat the same point on two slides. Style: `carousel.py` (dark, amber and mint, Inter, mascot on cover and last slide).

## Depth rules (same standard as the story-format reels; see STYLE_GUIDE.md)
The audience is mature: it knows the basics and wants to know what goes into building or running the thing. So:
- Level 1 (slides 1-3) stays short and plain, but never opens with a debate or "Stop doing X". The cover promises the mechanism with a number or concrete payoff ("What actually goes into a rate limiter? 4 algorithms, one Redis script.").
- Levels 2-3 are real mechanism, not summary: every deep slide shows a real command, query, config, header, default value or worked number taken from an official source and quoted verbatim in the facts file (for example `Retry-After: 120`, `INCR` + `EXPIRE` in one Lua `EVAL`, `rate = 42 * ((60-15)/60) + 18 = 49.5`). Use a code block or a worked-calculation block, not a paraphrase.
- At least 3 sources opened now; one worked example, identical on every slide; invented values labelled "Example"; one true, sourced trade-off or failure mode on a deep slide.
- Use the same colour for the same thing on every slide, keep text inside its box and at least 24 px for code, plain bold lettering only (no wavy underlines), generic icons (no brand logos).
- The reviewer is asked whether a mature engineer learns something real on slides 4-6; if not, the post is rewritten, not shipped.

## 0. Setup
```bash
pip install --break-system-packages -q Pillow numpy scipy
mkdir -p ~/.claude/instagram && cp instagram/voice.md ~/.claude/instagram/voice.md
```

## 1. Pick today's post topic
1. Read the shared topics log (Claude Docs document "Tech in a Bite: Topics Log", https://claude.ai/artifact/CH7PJ2ycmR5RjzwSrnsvsw), memory (/areas/social-media-page.md "Covered so far") and `topics_log.md`.
   Never repeat a topic that already has a reel or a post, and never pick the topic of today's reel. Prefer a different pillar from today's reel
   (pillars: AI for everyday people, AI for builders, databases, system design, cloud and architecture).
2. Pick a topic that has real depth: something with a simple idea on the surface and a genuinely useful detail underneath (a mechanism, a trade-off, a number you can verify).
3. Post number: highest "P" number in the log plus 1 (Day column "P01", "P02", ...). Files: `specs/postNN_<slug>.py`, `specs/postNN_facts.json`, `out/postNN_*`.

## 2. Research (facts must be real)
Same as RUN_DAILY.md section 2: open at least two sources (official docs preferred), a search snippet is not a source, every number, name and term must appear in an opened source, use the sources' exact terms,
only state counts a source states. For the deep-dive slides open the primary documentation page, not a blog summary. If the core claims cannot be verified after 3 attempts, pick another topic; after 3 topics, send a message instead of a post.

## 3. Cover hook gate (the cover decides whether anyone swipes)
Write at least 6 cover headlines from different formulas in `skills/ig-reel/hooks.json`, 5 to 12 words, naming the subject, with a number or named thing, true. Put them in `out/postNN_hooks.txt`
and score with `python3 skills/ig-reel/hookscore.py out/postNN_hooks.txt`. The best must be STRONG (70+). Otherwise write a new batch, up to 5 rounds; then deliver the best one but start the summary with "HOOK BELOW TARGET".
The cover `title` is that headline split into 2-4 lines (accent the key line); `sub` completes the thought in one sentence; `chips` say how many slides and "BIG PICTURE TO DEEP DIVE".
Also write a one-line curiosity gap into slide 2 or 3 that the deep-dive slides pay off.

## 4. Write the slides (specs/postNN_<slug>.py, schema in carousel.py)
- 5 to 7 slides. Slide 1 `cover`, last slide `takeaway`. Set `"level"` 1, 1, 1, 2, 3, 3 (or similar; never decreasing; slides 1-2 level 1; at least one level 3 slide before the takeaway).
- Slide types: `text` (3 bullets and a callout), `cards` (2-4 parts), `flow` (2-4 ordered steps), `compare` (two options), `detail` (a monospace panel with a real command, config, formula or table + notes), `takeaway`.
  Use a different type on neighbouring slides. The deep dive should use `detail` or `compare` with real specifics.
- Writing rules (CLAUDE.md): complete CONTEXT on every slide; every slide must name the topic in its own words (EVERY SLIDE STANDS ALONE, `topic_terms` in the facts file); no vague slogans; spell out numbers and units; one worked example, identical on every slide; write `**bold**` around the 1-2 words per bullet that matter.
  Keep each slide under about 60 words: a slide is read in seconds. Short punchy lines are fine when the subject is named.
- Send-or-save slide: exactly one slide (not the cover) carries a true, sourced rule of thumb, a number to remember or a "this is the bug your team has" moment. Put it in a `callout`, and say in the takeaway `share` line who to send it to.
- Last slide: `points` (2-3 takeaways that mirror the cover's promise) and `share`. The closing "Follow for one tech topic a day." is drawn automatically.
- Mascot: shown by default on the cover and the takeaway; the renderer fails if it covers text.

## 5. Facts file (mandatory, before rendering)
`specs/postNN_facts.json` (schema at the top of `carousel_check.py`): `topic_terms`, `terms` (+ `never_say`), `illustrative_numbers` (every invented number, each labelled "Example" on its slide), `claims` (one per factual sentence and label, each with `source` URL, a `quote` copied from the opened page, and `slides`: the slide numbers it supports) and `share`.
Every slide except the cover needs at least one claim. Every number on a slide must appear in a claim quote on that slide or in `illustrative_numbers`.

## 6. Render and check
```bash
python3 carousel.py specs/postNN_<slug>.py out/postNN
python3 carousel_check.py specs/postNN_<slug>.py --facts specs/postNN_facts.json --render out/postNN --report out/postNN_check.md
python3 tests/test_carousel.py
```
Target 0 FAIL and 0 WARN (a warning means a slide is not good enough yet; fix it). Then LOOK at every slide image (Read tool on `out/postNN_s01.png` ... one at a time and the contact sheet `out/postNN_contact.png`):
text must fit, nothing cut off, nothing overlapping, each slide understandable alone, the order of slides must climb from simple to deep. Read every string aloud as a stranger would.

## 7. Independent reviewer (mandatory)
Start a fresh agent (Agent tool, general-purpose) and give it ONLY: `specs/postNN_facts.json`, `out/postNN_check.md`, the slide images `out/postNN_s01.png ...` and the contact sheet.
Ask it to: (1) for every sentence on every slide find the claim and quote that supports it and list unsupported ones; (2) confirm every string is true, uses the source term and matches the worked example;
(3) check technical accuracy against general knowledge (oversimplified until wrong? presented as universal when only common?); (4) judge each slide alone (does it name the topic, is it understandable without the others?);
(5) judge the climb: does slide 1-3 work for a beginner, does 5-6 teach something an engineer did not know, is any slide repeating another or cuttable, is there a clear send-or-save slide;
(6) reply PASS or a numbered list of problems with exact fixes. "Complete" means complete context, not full grammatical sentences. Apply fixes, re-run the checks, re-render, send it back. Up to 3 rounds.
**Stop rule:** if problems remain after 3 rounds or a fact has no source quote, do NOT deliver a post; send one message listing the open problems.

## 8. Caption (ig-caption skill)
First line = the cover hook. Then 3-6 short lines that recap the climb (what slide 1 promises, what slide 6 reveals) without repeating the slides word for word. One line that asks the viewer to save it or send it to the person named in `share`.
End with "Follow for one tech topic a day." and 3-5 hashtags. At most one emoji. No invented facts. Write `out/postNN_caption.txt`.

## 9. Deliver
SendUserFile each: the slide PNGs in order (`out/postNN_s01.png` ... these are the files to upload to Instagram as a carousel, in this order), `out/postNN_caption.txt`, `out/postNN_hooks.txt` (candidates with scores, final marked),
`out/postNN_sources.md` (links with what each supports plus the claim table), `out/postNN_check.md` (checker report plus reviewer verdict). Then ONE SendUserMessage: topic, number of slides, the climb (one line per slide with its level),
the cover headline and score (and runner-ups, rounds), the send-or-save slide and who it is for, the checker result, the reviewer verdict, the caption, the sources, and any doubts. If the owner might want a different cover, say what the second-best was.

## 10. Update the logs
Add a row to the topics log document (Day "PNN", date, "[POST] topic", pillar, cover hook, sources, status "Post made") with the Claude Docs tools, and append the topic to "Covered so far" in memory (/areas/social-media-page.md), also to `topics_log.md`.
Add a row (numbers blank) to the Results table in the topics log document and `results_log.md` (Day "PNN"; Hook formula; "send-or-save" type) so the owner can fill saves, sends and shares later.
Read the Results table first: with at least 3 filled post rows say which cover formulas and slide types did best and worst, otherwise say there is not enough data. Never invent numbers.
Commit your spec and facts files to a new branch `postNN-<slug>` and push it (never to main); if pushing fails, say so.

## Quality gates (do not deliver if any fails)
- 5-7 slides, climbing level 1 to level 3; cover headline STRONG (70+) or the summary starts with "HOOK BELOW TARGET".
- `carousel_check.py` 0 FAIL, 0 WARN; `tests/test_carousel.py` passes; every slide image viewed.
- Every slide stands alone and names the topic; every fact has a source quote; exact source terms; one consistent example; counts stated by sources.
- One send-or-save slide; the takeaway ends with "Follow for one tech topic a day."; mascot never covers text.
- Independent reviewer PASS. Never post anywhere, never spend money, never call ElevenLabs.
