# Tech in a Bite: topics covered (one per day)
Update this table every time a video is made. Never repeat a topic. Memory also keeps a short copy.
Mix: AI for everyday people, developers, engineers and managers, plus cloud, databases, system design and architecture.

| Day | Date | Topic | Hook angle | Sources checked |
|---|---|---|---|---|
| 01 | 2026-11-01 | Gemini Notebook (ex NotebookLM) | New name, cloud computer per notebook | Google announcement coverage |
| 02 | 2026-11-01 | ChatGPT Work (OpenAI, launched 9 Jul 2026) | Agent that builds sheets/decks, asks approval | SiliconANGLE, Fox Business |
| 04 | 2026-11-02 | What a database index does (45 s, no burned-in subtitles) | "How can a database find one row out of ten million without looking at the rest?" | PostgreSQL docs (postgrespro mirror), Use The Index, Luke |
| 03 | 2026-11-01 | Why Redis is fast (RAM, single thread, pipelining) | "Why is Redis so fast? Three reasons." | Redis benchmark docs (via redict.io mirror), AlgoMaster |

## Backlog
AI: Claude Cowork, Microsoft Copilot Cowork, Perplexity, Cursor, Notion AI, Canva AI
Databases: what an index does, Postgres vs MySQL, caching strategies, SQL vs NoSQL
System design: load balancers, CAP theorem, message queues, rate limiting, CDN
Cloud: serverless vs containers, what Kubernetes does, regions and availability zones
| 10 | 2026-11-05 | What RAG (retrieval-augmented generation) does | "Stop retraining AI models on your documents. Try RAG first." (hook score 87.0) | AWS "What is RAG?", Lewis et al. RAG paper (arXiv 2005.11401) |
| 11 | 2026-11-05 | Rate limiter deep dive (story format, test run) | "What actually goes into your rate limiter? 1 Redis script, 1 formula, 1 HTTP header." (73.0) | Redis tutorial, Redis eval-intro, Cloudflare blog, Stripe blog, MDN, RFC 6585 |
| P01 | 2026-11-05 | [POST] Kubernetes liveness, readiness and startup probes (v3 story) | "Why your liveness probe can kill your slow app within 30 seconds" (76.4) | kubernetes/website: probes task page, pod lifecycle, probes concept |
| 12 | 2026-11-06 | PostgreSQL write-ahead log: why COMMIT flushes 1 file, not your table (story, COUNTER+NUMBER) | "Why does a PostgreSQL COMMIT flush 1 file, not your table?" (77.8) | PostgreSQL 18 docs: wal-intro, wal-configuration, wal-internals, runtime-config-wal, wal-async-commit, sql-checkpoint, functions-admin |
