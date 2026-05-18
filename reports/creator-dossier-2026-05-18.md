# Creator Dossier — 2026-05-18

## Project
- **Name:** semble
- **Repo:** https://github.com/MinishLab/semble
- **One-liner:** Fast and accurate code search for AI agents. Uses ~98% fewer tokens than grep+read.
- **License:** MIT
- **Latest release:** v0.1.7 (2026-05-12)
- **Signal:** Show HN on 2026-05-17 — front page, 312 points, 107 comments inside 24h. Still climbing. ~1.8k stars.

## Creator (tag target)
- **Name:** Thomas van Dongen
- **X handle:** @TvDongen  (verified: https://x.com/TvDongen)
- **Org:** MinishLab — the two-person research lab behind Model2Vec
- **One-line bio:** Builder of fast, small NLP infrastructure. Co-creator of Model2Vec static embeddings.

## Co-creator (mention in Why-this-one, not the tag)
- **Name:** Stephan Tulkens
- **X handle:** @tulkenss  (https://x.com/tulkenss)
- **GitHub:** https://github.com/stephantul

## Prior work / lineage
- **Model2Vec** — static embeddings that make sentence-transformers roughly 50x smaller and 500x faster. Widely cited; Rust port (model2vec-rs) and HF model family (potion-retrieval-32M, M2V_base).
- **semhash** — fast multimodal semantic dedup/filtering.
- Pattern: MinishLab ships small, CPU-only, no-API tools that beat heavyweight transformer baselines on speed while holding quality.

## What they care about
- CPU-first, local-first inference. No GPU, no API keys, no embedding service to call.
- Quality you can verify with a benchmark, not vibes.
- Open source, MIT, shipped in public with the numbers attached.

## The metric that's trending
- Momentum signal: Show HN front page (312 pts / 107 comments in a day), still climbing — not a frontier-lab dump.
- Headline efficiency claim: **~98% fewer tokens than grep+read** for agent code exploration.
- Speed: indexes **218x faster** and queries **11x faster** than a transformer baseline (CodeRankEmbed) while holding **NDCG@10 0.854** retrieval quality.

## Angle split (no-repeat enforcement)
- **X caption owns:** the Hacker News momentum + "code search written for coding agents" + local / CPU-only / no-API + "retrieval layer your agent was missing".
- **Video owns:** the 98%-fewer-tokens-vs-grep-and-read number, the 11x query-speed number, the grep-to-retrieval so-what.
- **Why-this-one owns:** the Model2Vec lineage (50x smaller / 500x faster), NDCG@10 0.854, Stephan Tulkens co-authorship, MIT, two-person-lab build-in-public discipline.

## Why this one (pick defense)
Semble is the cleanest in-lane signal in the 24h window. It's a Show HN trending right now (312 points, 107 comments, posted 2026-05-17) with a fresh release, and it comes from MinishLab — the team behind Model2Vec, whose static-embedding work has real credibility. The novelty is concrete and not a wrapper: it ports static embeddings plus BM25 and reciprocal rank fusion into a code-search layer purpose-built for coding agents, cutting token spend ~98% versus grep+read while staying CPU-only with no API or GPU. It sits authentically in builder-tier agent infrastructure with two reachable, well-known creators and verifiable X handles. Momentum is still climbing rather than saturated, and it's a different creator and a different angle from anything in the last 14 days of the ledger.

## Dropped candidates (window 2026-05-17/18)
- **colbymchenry/codegraph** — strongest project by raw momentum (+857 stars/day) but no findable X handle (personal site and GitHub list email/LinkedIn/Medium only; the "x2x2x2" claim was unverifiable and contradicted by two direct fetches). Lane-filter hard rule: drop anything without a findable X handle.
- **gidellav/zerostack** — Unix-style Rust coding agent, strong HN score, but "another coding agent" novelty is lower and crates.io page yielded no creator X handle.
- **KeygraphHQ/shannon** — autonomous AI pentester, in-lane, but org-driven with no clear individual creator and 43k stars (saturated, not still-climbing).
- **rohitg00/skillkit** — creator covered 2026-05-09 (agentmemory), inside the 14-day window.
- **tinyhumansai/openhuman** — already in style-history (2026-05-12); project_url match.
