# Daily post run: make today's Tech in a Bite carousel post (Instagram, 5-7 images)

You run unattended. The owner wakes up, downloads your files and posts manually. Your job: deliver one finished, fact-checked carousel post (5 to 7 slides)
plus caption. A post is NOT a reel: it is read, saved and sent, not watched. Read CLAUDE.md first (brand, writing rules, accuracy rules, mascot, reach signals).
This file only replaces the video-specific parts (voiceover, scenes, music, animation review). Everything else in CLAUDE.md and RUN_DAILY.md section 2 (research) and section 4b (reviewer) applies.

## The idea of the format (v3 story carousel, owner feedback Nov 2026)
People on Instagram are not looking for code. A post is a STORY that unfolds as they swipe: every slide is one chapter that explains one technical concept
in depth, in words, and ends on a rehook that makes the next swipe necessary. Concepts and mechanisms, never syntax. Model post: `specs/post01_kubernetes_probes.py` (v3).
- Slide 1 cover (`cover_story`): a huge stacked headline that promises the mechanism with a number or concrete stake, plus a short meta row.
- Slides 2-6 (`story`): STEP 01, 02, ... One chapter each. Level 1 (the big picture, plain words) -> level 2 (how it works, the numbers) -> level 3 (the deep dive: the failure mode, trade-off or rule a practitioner needs).
- Every content slide ends with a `hook` box: a question or tension that the NEXT slide pays off ("But what if your app needs 2 minutes just to start?").
- Last slide: `takeaway` recap (2-3 points), a `share` line, and "Follow for one tech topic a day." (drawn automatically).
Never repeat the same point on two slides.

## Depth rules (same standard as the story-format reels, explained in words)
The audience is mature: it knows the basics and wants to know how the thing really behaves. So:
- The cover never opens with a debate or "Stop doing X". It promises the mechanism ("Why your liveness probe can kill your slow app within 30 seconds").
- Levels 2-3 are real mechanism, explained in plain words: default values, worked numbers, what the system does step by step, the failure mode and why. All from official sources, quoted verbatim in the facts file.
- NO CODE: no commands, YAML, JSON, field names in camelCase, terminals or tables on a slide (checker FAIL CODE, WARN CODE_TERM). Say what a setting means ("3 failed checks in a row"), not its name (`failureThreshold: 3`).
- At least 3 sources opened now; one worked example, identical on every slide; invented values labelled "Example"; one true, sourced trade-off or failure mode on a deep slide.
- Every claim must be true as written: "within about 30 s" if the arithmetic is approximate; "the docs example allows 5 minutes", not "the startup probe gives 5 minutes". Hooks must be true too.
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
The cover `title` is that headline split into 3-5 stacked lines as `[(text, accent), ...]` (accent 1-2 key lines); `meta` is 2-3 short tags (topic name, "3 PROBES", "NO CODE").
Then write every content slide's rehook (`hook`) and score each with `rehookscore.score()` (the checker does it): PASS is 60+ overall and 40+ per component, at most 18 words, true, paid off by the next slide.

## 4. Write the slides (specs/postNN_<slug>.py) - v3 story format
COPY THE STRUCTURE OF `specs/post01_kubernetes_probes.py` (the model post). Rules (enforced by `carousel_check.py` and `carousel.py`):
- 5 to 7 slides. Slide 1 `cover_story`, last slide `takeaway`, every slide in between is a `"type": "story"` slide (stage, text, cards, flow, compare and detail templates are retired for posts; the checker FAILS them).
  Levels 1, 1, 1, 2, 3, 3, 3 for 7 slides (never decreasing; slides 1-2 level 1; at least one level 3 slide before the takeaway). `step` numbers the chapters 1, 2, 3 ...
- A story slide = `title` as parts `[(text, accent), ...]` (the accent word is drawn in amber italic; at most 9 words), 1-4 `bullets` (rich text, `**bold**` for the key fact; one idea per bullet, up to ~25 words),
  optional `cards` (2 side-by-side cards: `label`, `head`, `text`, `color` pink/mint/amber/cyan, `highlight`) for a contrast, and the `hook`.
- No code anywhere (see Depth rules). Explain what the system does, with the numbers.
- Layout: the renderer FAILS if content runs into the hook box or a card's text does not fit. Fix the wording, never the checker.
- Writing rules (CLAUDE.md): every slide names the topic (topic_terms) and is understandable alone; exact source terms; invented values labelled "Example"; computed numbers go in `derived_numbers` with how they were computed.
- Send-or-save slide: exactly one slide (not the cover) carries a true, sourced rule of thumb or number to remember. The takeaway has 2-3 short `points` and a `share` line.
- Mascot: cover and takeaway only; the renderer fails if it covers text or a box.

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
(5) judge the story: is each slide's hook TRUE and actually paid off by the next slide (check every pair), is there any code or config syntax (must be none); judge the climb: does slide 1-3 work for a beginner, does 5-6 teach something an engineer did not know, is any slide repeating another or cuttable, is there a clear send-or-save slide;
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
- 5-7 slides, climbing level 1 to level 3, story slides only, every content slide ending on a true rehook (60+) that the next slide pays off, no code; cover headline STRONG (70+) or the summary starts with "HOOK BELOW TARGET".
- `carousel_check.py` 0 FAIL, 0 WARN; `tests/test_carousel.py` passes; every slide image viewed.
- Every slide stands alone and names the topic; every fact has a source quote; exact source terms; one consistent example; counts stated by sources.
- One send-or-save slide; the takeaway ends with "Follow for one tech topic a day."; mascot never covers text.
- Independent reviewer PASS. Never post anywhere, never spend money, never call ElevenLabs.
