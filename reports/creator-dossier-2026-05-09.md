# Creator dossier · 2026-05-09 · second run

> First run today shipped a tribute to Mario Zechner (`pi-mono`, mono-terminal, SCHEMATIC). This second run rotates project, framework, and aesthetic.

## Project

`rohitg00/agentmemory` — "Your coding agent remembers everything. No more re-explaining."

- URL: https://github.com/rohitg00/agentmemory
- Stars: 3,332 (≈ 518 added in the last 24h)
- License: Apache-2.0
- Latest tag: 0.9.5 (May 9, 2026)

## Creator

- Name: Rohit Ghumare
- X: @ghumare64  (https://x.com/ghumare64)
- GitHub: @rohitg00  (https://github.com/rohitg00)
- Geography: London, UK (shareable)
- One-line: Principal Product Evangelist, Google Cloud GDE, CNCF Ambassador, Docker Captain, AWS Community Builder. Spent the last few years shipping Kubernetes and DevOps tooling; pivoted into the agent stack this spring.

## Voice notes

Reads as DevRel-trained but earns it. Posts numbers, not vibes. Will quote a benchmark before he quotes himself. Comfortable on stage, comfortable in the terminal. Build-in-public cadence on X is steady, not loud.

## What this project is

A persistent-memory layer for coding agents that survives across sessions. Solves the "first ten minutes of every chat is re-explaining the codebase" problem. Sits behind any MCP-compatible client (Claude Code, Cursor, Gemini CLI, others) plus a REST API.

The proof is in the receipts:

- 95.2% retrieval accuracy on the LongMemEval-S benchmark.
- 92% fewer tokens than the built-in memory in Claude / Cursor / friends.
- ~$10 per developer per year in token cost vs ~$500 for an LLM-summarized approach.
- 51 MCP tools exposed.
- Four memory tiers consolidated on a sleep-cycle metaphor: working, episodic, semantic, procedural.
- Triple-stream retrieval: BM25 keyword + dense vector + knowledge graph, fused with Reciprocal Rank Fusion (k=60).
- Zero external database. SQLite plus an in-house engine called `iii`.
- Real-time memory viewer at `localhost:3113`.

## Trending metric

Star velocity is the loudest signal. ~518 stars added in the last 24h, repo cleared 3.3k. v0.9.5 cut today; that release is forbidden in copy per the routine rules. Lead with stars.

## Notes for the writer

- Numbers do the work. RECEIPT is the framework.
- The 95.2% / 92% / $10 numbers are the heroes. Don't bury them.
- The sleep-cycle memory tiers metaphor is interesting but tangential. Save it for a future run.
- Don't repeat any number from the X caption inside the scenes.
- Contractions where natural. He's a writer; he uses them.

## Lane fit (defense)

- Lane: agent infrastructure + MCP tooling + builder-tier memory layer.
- Momentum: still climbing this week, not saturated. Released today.
- Novelty: hybrid triple-stream search with RRF for *agent memory specifically* is genuinely new packaging.
- Resonance: anyone who's lost two hours of context to a closed Cursor tab will read this and nod.

## Geography note

London. Optional to call out in the Gmail's Why-this-one. Not in the X caption.

## Anti-repeat snapshot

- Today's prior pick: project=pi-mono, brand=null, aesthetic=mono-terminal, framework=SCHEMATIC.
- Today's second pick: project=agentmemory, brand=null, aesthetic=subway-chrome, framework=RECEIPT.
- Both axes rotated. Anti-repeat passes.
