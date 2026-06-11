# Creator Dossier — 2026-06-11

## Creator

- **Name:** Wes McKinney
- **X handle:** [@wesmckinn](https://x.com/wesmckinn)
- **Org:** Kenn Software ("Development and knowledge systems for the agentic era") — github.com/kenn-io, kenn.io
- **Project:** agentsview — https://github.com/kenn-io/agentsview

## One-line bio

The builder who created pandas and Ibis and co-created Apache Arrow, now building local-first developer tooling for the coding-agent era.

## Voice notes

Measured, technical, understated. Performance-obsessed and standards-first. Wes writes about foundational infrastructure (dataframes, columnar memory, query engines) with dry precision and zero hype. He cares about open source, local-first, no vendor lock-in, and developer ergonomics. Tribute copy should be quiet and exact, not loud. Let the contrast (the dataframe legend now indexing agent sessions) carry the admiration.

## Prior work

- **pandas** (2008) — the dataframe library that defined a generation of Python data work.
- **Apache Arrow** — co-creator. The columnar in-memory standard now under half the modern data stack.
- **Ibis** — portable dataframe expressions across engines.
- *Python for Data Analysis* (O'Reilly) — the book.
- Now: founder of **Kenn Software**, a small team (with Phillip Cloud and Marius van Niekerk) shipping agentic-era tools: agentsview, roborev (review for agent-written code), msgvault (offline message archive), kata (issue tracker for agents), middleman.

## What they care about

Local-first over cloud. Single-binary, no-accounts ergonomics. Open formats and full-text search you own. Columnar storage and speed (DuckDB, SQLite FTS). Giving builders the same observability for agent work that data engineers have always had for pipelines.

## Geography (shareable)

United States — Nashville, Tennessee. Wes is public about being based there.

## Latest release / commit date

**agentsview v0.32.1 — June 5, 2026.** Active release cadence (32 minor releases since launch in spring 2026).

## Trending metric

~1.4k GitHub stars and climbing roughly +98 a day (about 7% daily growth) on June 11, 2026 — fast velocity for a six-week-old infra tool. Sits alongside Kenn Software's roborev (1.4k) and msgvault (1.8k). MIT licensed.

## The thing agentsview actually does (verified from README)

A single Go binary, no accounts, no cloud. It watches your coding-agent session directories, parses the JSONL each agent writes (Claude Code, Codex, Gemini CLI, OpenHands, Cursor, 20+ others), and stores structured records in SQLite with full-text search indexes. The embedded web dashboard gives you cross-agent browse, search, token usage, cost analysis, and activity heatmaps. Optional PostgreSQL sync for teams and a DuckDB mirror. Billed as a "100x faster replacement for ccusage."

## Angles (for caption vs Why-this-one separation)

- **Caption angle:** star velocity + the novel claim (one local binary unifies session history across 20+ agents).
- **Why-this-one angle:** the career arc — the pandas / Arrow creator turning his infrastructure instincts on the agent era, local-first and no lock-in.
