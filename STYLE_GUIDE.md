# Style guide: technical story reels (v2, measured frame by frame from the two reference videos)

The owner's references are two ~2:40 explainers with thousands of views ("what happens when you open google.com" and "why deleting a Docker
container doesn't free your disk"). They were sampled every 3 seconds. This guide writes down what they do, as rules our renderer
(`stage.py`) and checker (`check_spec.py`) enforce. The model spec is `specs/day11_rate_limiter.py`.

## 1. The screen shows objects and state. The voice explains.
- Reference frames contain almost no sentences. They show **things**: a browser window with a URL bar, a server, a disk bar reading "100 GB used",
  a folder tab "/var/lib/postgresql", a terminal with real output, packets with `GET / HTTP/1.1`, status pills "ESTABLISHED", "SYN", "ACK".
- Every explanation lives in the narration; the screen proves it with an object changing state (a counter goes 9 -> 10, a bar fills, a row is
  highlighted, a packet bounces back with 429).
- Rule: object labels are 1-4 words (checker FAIL above 6); titles/questions/notes at most 9 words; never a sentence inside a box.

## 2. Every box has contents, and boxes nest.
- Reference B: BUILD SERVER DISK > TEST PIPELINE > CONTAINER > WRITABLE LAYER / POSTGRES IMAGE, next to VOLUME > DATA FOLDER > "orders".
- Rule: a panel taller than 100 px must contain objects (`"in": "<panel id>"`) or a `body` illustration; header-only strips are `compact`
  (checker EMPTY_BOX). Children must stay inside their parent (OUTSIDE_PARENT). Inner boxes use a lighter shade (`level` 1-2).
- Reuse the same objects all video long. The diagram is built in the first seconds and then only changes state; it is never thrown away
  without a reason (a new chapter that needs a different picture).

## 3. Text never leaves its box.
- The engine wraps every text onto new lines inside its box (panel labels up to 2 lines, pills 2 lines, terminal lines with a hanging indent).
  It shrinks only down to 24 px; if it still does not fit, the checker FAILS (TEXT_OVERFLOW). Fix by shortening the words or making the box bigger.
- Nothing overlaps unless nested (OVERLAP). Packets and arrows are the only overlays.

## 4. Typography and colour
- Labels, titles, notes: heavy italic caps (Inter Display Black Italic; drop an OFL brush font such as Permanent Marker into `fonts/brush.ttf`
  to get the hand-lettered look - the engine uses it automatically). Values and code: mono. UI text: Inter SemiBold.
- Sizes at 1080 px width: titles 44-54, panel labels 30, terminal 27-29, pills 26-28, never below 24.
- One colour per concept for the whole video (reference A: TCP cyan, HTTP amber, TLS pink, IP purple). Pink = problem/over limit,
  mint = OK/result, amber = the data being counted, cyan = storage/infra, purple = second actor.
- Titles: a short straight underline. No wavy lines, no wobble.

## 5. Layout grid (1080 x 1920)
- y 262: @TECHINABITE tag; mascot small at the top-right (x 1000, y 300, size 90), like the reference logo.
- y 290-510: title area: step dots (y 335) and the chapter title (y 440) or the question pill (y ~466).
- y 540-940: the main diagram (persistent).
- y 975-1375: the lower area: a terminal with real commands/output, or a second diagram (e.g. two time windows).
- Below 1420: empty on purpose (Instagram caption and buttons cover it). Checker OUT_OF_ZONE outside x 30-1050, y 290-1420.

## 6. Motion: something changes every 2-3 seconds, exactly on its word.
- Every object and every terminal line is anchored to the word that introduces it (`wi(line, "word")`, terminal lines `"at"`).
- Focus: when the story is about one part, the rest dims (`"focus": ["limiter", "steps"]`); `"focus": []` brings everything back.
- Highlight the thing being talked about: dashed pink outline (`hl`), highlighted terminal row (`hl`), highlighted flag (`flag`).
- Checker WARN STATIC if nothing visible changes for more than 4 s.

## 7. Story structure (both references)
- Open on the topic's real setting: the diagram is on screen at frame 0 together with the hook (no title card).
- Name the steps once with numbered dots and walk them in order; the active dot moves.
- A question pill in the middle (the rehook) that the next scene answers on the diagram.
- Real artefacts in the terminal: commands and their real output from official docs (e.g. `> INCR mykey` / `(integer) 11`), with the
  important row or flag highlighted; worked numbers exactly as the source gives them.
- End: recap dots, then a blurred background with a follow card that gets clicked.

## 8. Mascot and brand
- Header tag "@TECHINABITE", first scene shows "TECH IN A BITE". Mascot `assets/mascot.png`, small, top-right, never over content.
- No third-party logos (the references use Google/Docker/Postgres logos; we use generic icons).

## 9. What failed before (do not repeat)
- Empty panels with a long title squeezed into the header; text running out of the box (Nov 2026 owner feedback).
- Walls of chips and sentences on screen; titles that explain instead of label.
- Wavy underlines/wobbly letters; a separate hook card that did not belong to the story.
- Visuals ahead of the voice; stale objects left on screen after their scene.
