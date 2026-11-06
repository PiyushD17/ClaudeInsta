# Content strategy for @techinabite (from the owner's performance analysis, 6 Nov 2026)

Every daily job (reel and carousel) reads this file first. It is a standing instruction. Where it is stricter than another procedure file, this file wins; where it
conflicts with an owner rule in CLAUDE.md (accuracy, writing rule, no code in carousels, story format depth), the CLAUDE.md rule wins and the run says so in its summary.

## 1. What the data says (state of the account, 6 Nov 2026, day 4 after launch)
- 8 reels, 1,751 total views, mean 219, **median 149**, mean without the best reel 147. Likes 17 (about 1 per 100 views), shares/sends 3, comments 0, reposts 0.
- Per reel (views / likes / shares): database index "10 million rows" 719/7/1; Redis 191/7/1; load balancer algorithms 171/0/0; availability zones 163/0/0;
  AI context window 135/1/0; database transactions 133/0/1; AI agents / bigger models 126/2/0; API rate limiting 113/0/0.
- Account Status: reach limits Green, removed content Green, features Green; monetisation Orange (separate from reach). **Never assume a shadowban or penalty without evidence.**
- Facts, not conclusions: one outlier (719), a flat baseline of about 150 for the rest, very low engagement (likes, saves, shares, comments). The sample is far too small to name a winning topic,
  duration, time of day or style. Treat every hypothesis below as a test, never as proven.
- Reference point (descriptive, not a platform benchmark): about 150 views per reel. Aspiration for the next 10-14 reels: typical reel 250-400 views (a target, not a forecast).

## 2. Hypotheses to test (label every run with the experiment it belongs to)
| Experiment tag | Example | Question |
|---|---|---|
| NUMBER | "10 million rows. One query." | do concrete numbers attract more viewers? |
| FAILURE | "Why your API keeps returning 429" | do relatable problems improve retention? |
| COUNTER | "More cache can make things slower" | do surprising (but true) facts increase shares? |
| EVERYDAY-AI | "Why ChatGPT forgets what you told it" | does broad, familiar framing widen the audience? |
| VISUAL | "SQL scan vs index lookup" | do side-by-side visuals improve completion? |
| COMPARE | "Nginx vs load balancer vs API gateway: which one answers which problem?" | do open-loop comparisons (a set of options the viewer wants to see ranked or resolved) raise retention, saves and shares? |
Rules: put the tag in the topics log "Hook angle" cell and the results log "Hook formula" cell. Do not declare a winner from one or two examples. Compare medians (not only means) once 10-15 more reels exist.
Prefer concrete technical problems, counterintuitive outcomes and practical engineering questions over abstract topic titles ("Understanding X"). AI topics need a familiar user problem
("Why can giving AI more information make its answer worse?"), but never state a system-dependent behaviour as universal ("can", "often", "in this setup").

## 3. Hook and opening rules (first two seconds)
Never open with "Today we will learn...", "Understanding the basics of...", "An introduction to...", a long logo animation or a generic branding sequence.
Use one of: problem ("Your API works fine until traffic spikes"), curiosity ("Why is Redis so fast?"), contradiction ("More servers do not always mean more speed"),
consequence ("One wrong Kubernetes probe can restart a healthy app"). The opening must make the viewer curious about the explanation and must be TRUE and answered by the video (no clickbait the content does not pay off).
The existing gates stay: at least 6 candidates from different formulas, best STRONG (70+) on hookscore.py, rehook 60+. In addition, **deliver the three best candidates** with a one-line rationale each and say which is recommended.
**Deliver the surprise in the first 2 seconds (owner, 6 Nov 2026).** The opening line must already contain the surprising fact or contradiction, not just a question about it. Model: "Your database said COMMIT succeeded. So why isn't your data in the table file yet?" Test every hook: if the surprise only arrives after second 2, rewrite it. Still true, still answered by the video.
Engineers are the core audience: the hook promises the mechanism or the surprising outcome with a number or concrete stake, never a debate ("Stop doing X").

### Open-loop comparison pattern (owner idea, 6 Nov 2026; experiment tag COMPARE)
Viewers want to see how each option in a set turns out, so a comparison opens a loop that stays open until every option has been resolved. Use it for "X vs Y (vs Z)" topics, as a reel or a carousel: API gateway vs load balancer, CDN vs API gateway, Nginx vs load balancer, PostgreSQL vs MySQL, Python vs Rust, and similar.
- Hook: name the set and promise the resolution ("3 tiers of caching: only 1 fits your read-heavy API"). Tease the options in order and keep a visible tracker (basic / medium / premium style tiers, or option A, B, C) so the viewer knows which are still unresolved.
- Resolve the options one by one on screen with the same criteria for each (the same worked example, the same 2-3 dimensions), and answer the loop at the end with a decision rule ("choose X when ..., Y when ...").
- Fairness and accuracy come first: compare on dimensions the sources state, name the trade-offs of every option, no "X is better" verdict without its condition, no invented benchmarks, scores or rankings, and no tiers or ratings that the sources do not support. A tier label is a presentation device only when it follows a real documented difference.
- The practical takeaway (section 5) is the decision rule or a configuration warning for the winning case. Carousel: one option per slide with a rehook, then a decision-rule slide.
- Pick comparisons where the options are often confused or used together in real stacks; avoid language or vendor flame wars. Still label the run COMPARE and compare medians only after enough rows.

## 4. Story shape (every reel)
Hook (0-2 s) -> context with a concrete visual (problem in plain words) -> explanation that shows the mechanism with animation -> payoff (practical lesson, consequence or fix) -> short CTA.
The video must deliver its promised answer even if the viewer ignores the CTA. One principal idea per scene. If the idea cannot be explained accurately in the time budget, narrow its scope or make it a carousel.
Length (owner decision, 6 Nov 2026): the STORY FORMAT stays the default, up to 150 s hard maximum, and must be high quality and engaging as described in this file. Only if the idea can really be explained in about 30 s, make it a short reel (RUN_DAILY.md) instead. Do not pad a short idea into a long reel and do not squeeze a multi-step mechanism into 30 s.
Never add filler scenes to reach a length. Animation: simple diagrams and animated data flows, visual comparisons, clear cause and effect, large readable text, consistent colours, no decoration; never captions that repeat the voice without showing the mechanism.

**Give viewers a reason to save (owner, 6 Nov 2026).** Every piece ends with one practical takeaway a viewer can reuse: a configuration warning, a debugging tip, or a simple architecture rule, stated concretely (setting name, command or rule of thumb, with its default or condition). It comes before the CTA, and it is also the first thing the caption's extra-value line repeats as "Save this for ...". A recap of the mechanism alone is not a takeaway.

## 5. Value test: what the viewer walks away with
Each piece must leave at least one of: "I finally understand that" / "I did not know that" / "this could help me solve a problem" / "I should save this" / "my colleague would find this useful".
Name which one in the brief (section 8). The send-or-save line (existing "share" gate) is the delivery mechanism; make it concrete (who would send it and why).

## 6. Technical accuracy (non-negotiable, trust is the product)
Distinguish typical behaviour from guarantees ("by default", "in PostgreSQL 18", "in this docs example"). No invented benchmarks or statistics. No universal claims ("every indexed query is faster", "Redis is always faster than a database").
Name trade-offs. Use the sources' exact terms. Simplify without distorting. The facts file, checker and independent reviewer gates stay. Write the caveats down in the brief (section 8, item 4).

## 7. Instagram SEO and discoverability (captions)
- Put the main technical keyword naturally in the first caption line (that line is what shows before "more").
- Add related technical terms only where they add meaning (rate limiting: HTTP 429, Retry-After, exponential backoff, API reliability, backend engineering; Kubernetes: liveness probe, readiness probe, startup probe, kubelet, container restarts).
- Readable, engaging sentences, never a keyword list. 3-5 relevant hashtags, no hashtag stuffing, no hidden or unrelated keywords, never claim a keyword, hashtag or sound is trending without current evidence.
- Caption structure: compelling first line; why it matters in practice; one or two lines of extra value that do not just repeat the video; a relevant CTA (save or send to the person named in "share"); then "Follow for one tech topic a day." and the hashtags.
- Audio: subtle instrumental or electronic music, no lyrics, supports the animation and never competes with the voice. No assumption that trending audio or hashtags guarantee reach.

## 8. Brief delivered with every reel and post: `out/<id>_brief.md`
Written from the run's real artefacts (do not invent anything), one file with these sections:
1. Topic and audience: what it teaches and why the audience cares; the one thing to remember; which value outcome of section 5 it targets.
2. Three alternative hooks (best three scored candidates, scores shown) and the recommended one with a one-line rationale.
3. Production storyboard: scene by scene with approximate timing, exact on-screen text, visuals and animation behaviour, transitions, and the educational purpose of each scene (for carousels: slide by slide).
4. Technical accuracy review: caveats, assumptions and misleading readings to avoid (typical vs guaranteed).
5. Cover headline: a concise, attention-grabbing title that reads on a small thumbnail (truthful, 3-7 words).
6. Instagram caption (also written to its own file).
7. Audio recommendation (the generated music follows section 7; say if the owner should lower it under the voice).
8. Performance hypothesis: why this piece might beat the baseline (median about 150 views) and the single metric that would validate it (for example saves per 100 views, average watch time, shares).
9. Experiment tag (section 2).

## 9. Topic pipeline (priority experiments; always check the topics log first and never repeat a covered topic)
Comparison topics (tag COMPARE; owner delegated the choice, 6 Nov 2026): the examples the owner gave (API gateway vs load balancer, CDN vs API gateway, Nginx vs load balancer, PostgreSQL vs MySQL, Python vs Rust) were illustrations, not a to-do list. The run decides which comparison is best for the audience, as if the page's livelihood depended on it, and must verify every fact itself. Choose a comparison only if (1) engineers genuinely confuse or combine the options, (2) official docs of each option state the differences in quotable words, (3) the options can be judged on the same 2-3 criteria without a "which is better" verdict, (4) a decision rule is accurate and testable. Prefer infrastructure and architecture roles (gateway, proxy, load balancer, CDN, queue vs stream, cache patterns) where docs define the role precisely; broad language or vendor comparisons (Python vs Rust, PostgreSQL vs MySQL) are allowed only with a narrow, documented angle and otherwise skipped. If no comparison passes these tests, make a normal topic instead of forcing the pattern. Do not run COMPARE two days in a row.
Candidates from the analysis: what actually happens on a cache miss; why AI hallucinations happen; why a Kubernetes Pod keeps restarting (CrashLoopBackOff; only if it adds an insight beyond the covered probes post);
what happens when two users update the same database record; why microservices sometimes create more problems; what an AI agent does differently from a chatbot; how a message queue absorbs traffic spikes; why caching can make an application slower; why distributed systems return stale data.
Already covered (do not repeat without a genuinely new insight): database indexes, load balancer algorithms, 429 and rate limiting, availability zones, context window, transactions, RAG, Kubernetes probes, Redis speed.
Choose by audience benefit, technical relevance, novelty and visual storytelling potential. Balance pillars; do not run the same pillar two days in a row.

## 10. Metrics (what the owner records; what the run reads)
Per reel: views at 24 h and 72 h, accounts reached, average watch time, duration, retention/completion, likes, saves, shares/sends, comments, follows attributed (and follower vs non-follower split where Instagram shows it).
Record a missing metric as "n/a", never an estimate. The run reads `results_log.md` and the Results table in the topics log, reports median (not only mean) views once at least 10 filled rows exist, and says which experiment tags and formulas did best and worst only with at least 3 filled rows per tag; otherwise "not enough data yet".

## 11. Non-negotiable production rules
No clickbait the content does not answer. No inaccurate technical claims. No invented benchmarks, statistics or facts. No filler scenes. No unexplained jargon. No keyword stuffing. No copying other creators' scripts.
No generic motivational messaging. No assumption that longer videos perform better, or that hashtags and trending audio guarantee reach. Guiding principle: do not just explain what a technology is; show why it matters, what surprising problem it solves, or what can go wrong without understanding it.
