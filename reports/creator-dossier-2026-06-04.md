# Creator dossier — 2026-06-04

## Subject

- **Name:** Tejas Chopra
- **X handle:** [@chopra_tejas](https://x.com/chopra_tejas)
- **GitHub:** [chopratejas](https://github.com/chopratejas)
- **Project:** headroom — https://github.com/chopratejas/headroom
- **One-line bio:** Senior Software Engineer on Netflix's Data Storage Platform
  team (Los Gatos, CMU grad), international speaker, and the creator of
  headroom, the context-compression layer that sits between an app and its LLM.

## What the project is

headroom is a context-compression layer for AI agents. It compresses the
material an agent feeds into the model (tool outputs, logs, files, RAG chunks,
conversation history) *before* that material reaches the LLM, cutting token
usage by a stated 60-95% while preserving answer quality.

It ships in three forms, all on the same pipeline:
- **Library** — call `compress(messages)` from Python or TypeScript.
- **Proxy** — `headroom proxy --port 8787`, a drop-in for any OpenAI-compatible
  client, zero code change.
- **MCP server** — exposes `headroom_compress`, `headroom_retrieve`,
  `headroom_stats` as MCP tools.

The technical heart is six specialized compressors feeding a reversible store:
- **SmartCrusher** — structural JSON compression.
- **CodeCompressor** — AST-aware compression for Python, JS, Go, Rust, Java, C++.
- **Kompress-base** — a HuggingFace model trained on agentic traces for text.
- **CacheAligner** — stabilizes prefixes so Anthropic/OpenAI KV caches still hit.
- **Image compression** — a trained ML router, 40-90% reduction.
- **CCR (Compress-Cache-Retrieve)** — keeps originals locally so compression is
  reversible; the LLM can pull the full original back via a tool whenever it
  needs it. This is the differentiator: lossy on the wire, lossless on demand.

## Benchmarks (for fact-checking the spec)

- Code search: 92% token reduction (17,765 -> 1,408).
- SRE debugging: 92% reduction (65,694 -> 5,118).
- GitHub triage: 73% reduction.
- Accuracy preserved: GSM8K math held at the 0.870 baseline; TruthfulQA +0.030.
- Aggregate (creator's public claim): ~$700,000 saved across users, ~200B
  tokens freed.

## Prior work

- Netflix Data Storage Platform — architecting petabyte-scale storage for
  Netflix Studios and Streaming. Before that, storage infrastructure at Box.
- Frequent international keynote speaker (microservices, cloud, storage, NFTs);
  Carnegie Mellon ECE master's, computer-systems specialization.
- The throughline: a storage/efficiency engineer's instinct applied to the new
  scarce resource, the context window.

## Voice notes

Engineer-to-engineer, practical, cost-aware. The framing in the press coverage
("Netflix engineer open-sources AI cost-cutting tool") is efficiency-first, not
hype. The right tribute register is peer respect for the systems instinct, not
fan noise. No superlatives.

## What he cares about

- Treating tokens like a storage/bandwidth budget to be engineered down.
- Reversibility and correctness: compress aggressively, lose nothing, because
  the original is one tool call away.
- Meeting people where they are: library, proxy, and MCP so adoption costs
  nothing.

## Geography

Los Gatos, California (Netflix HQ region). Treat Netflix as employer context;
headroom ships under headroomlabs.ai as its own thing.

## Trending metric (feeds the X caption)

- **Stars:** ~11,000 on `chopratejas/headroom`, up roughly 3,500 in a single
  day (read 2026-06-04). Star velocity is the live story.
- **Why it's hot now:** v0.22.4 shipped June 1, 2026; widely picked up after a
  HN front-page run and a round of press ("Netflix engineer open-sources AI
  cost-cutting tool"). Adoption tracks the universal agent pain of context bloat.

## Angle split (keep the two surfaces from overlapping)

- **X caption angle:** star velocity + what it does (compresses agent reads to
  cut up to 95% of the token bill, reversible).
- **Why-this-one angle:** the creator arc — a Netflix storage engineer applying
  the storage-efficiency instinct to the context window, built to fix his own
  bills, then open sourced; six compressors, proxy, MCP, ~$700k saved.
