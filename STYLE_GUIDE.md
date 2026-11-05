# Style guide: technical story videos (set from two reference explainers with thousands of views)

The reference videos are long narrated diagram explainers. What made them work, and how our pipeline reproduces it:

1. **One persistent canvas.** A single diagram builds up over the whole video and keeps its state (a bar filled in chapter 2 is still there in chapter 5). Use `"type": "stage"` scenes (`stage.py`). Objects live until a scene `clear`s them. Never reset the whole screen between lines unless the chapter really changes.
2. **Real mechanism, not a summary.** Every step shows the thing an engineer would actually see: a real command, query, config key, API field, default value or number, taken from the official docs and quoted in the facts file. "Converted to numerical representations" is a summary; `text-embedding-3-small returns 1536 numbers` and the `SELECT ... ORDER BY embedding <-> '[3,1,2]' LIMIT 5;` query are the mechanism.
3. **Audience: mature, knows the basics.** Do not spend the opening on "why does this exist" or on a debate they already settled. The hook promises what goes into building or running the thing ("What actually goes into building a RAG system? 4 steps, with real code."). At most one short line of problem setup.
4. **A skeleton, then depth.** Name the steps/components once (numbered dots stay at the top, the active dot moves), then go deep on each in order. The order on screen equals the order of the words.
5. **Questions as second hooks.** A question pill appears 25-65% in and is answered by a later line (the rehook gate).
6. **Concrete example, labelled.** One worked example, identical everywhere. Invented values are labelled "Example" or "Illustration". Real values carry their source.
7. **Terminal blocks for code.** Typed commands, highlighted result lines. Text in mono, large enough for a phone (>= 24 px), always inside its box (stage.py shrinks text to fit; still check).
8. **Colour has meaning.** Amber = the data/input being worked on, cyan = storage/infra, mint = good/result, pink = problem/step 3, purple = model/compute. Keep the same colour for the same thing in every scene.
9. **Clean lettering.** Plain bold titles, no wavy underlines, no wobble. Titles that name the topic. Nothing decorative that makes text harder to read.
10. **Frame 0 is the story.** The first frame already shows the hook text plus the diagram the story builds on, not a separate title card.
11. **Voice only.** Music is optional and kept very low (the owner mixes the voice in). Never burn in captions.
12. **No dead screens.** Every scene has something on screen from its first moment (objects start at t = -0.2/-0.3 relative to the line); old objects fade out before new ones appear (stage.py does this for `clear`).
13. **Trade-off or failure mode before the end.** One true, sourced "catch" (limit, cost, failure case), then a recap of the steps and the closing line "Follow for one tech topic a day."
14. **Generic icons only.** No brand logos or trademarked marks.

Layout: content between y=300 and y=1250, x within 70-1010; mascot (size ~150, x 900, y 1300) never overlaps content; the lower third stays calm.

Length: as short as the mechanism allows. 50 s when one mechanism fits; otherwise up to 150 s (hard maximum). Voiceover characters are limited by the owner's free ElevenLabs credits, so keep the script <= 2000 characters and always state the character count in the delivery summary.
