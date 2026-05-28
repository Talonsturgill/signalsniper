# Creator dossier — 2026-05-28

## Subject
- Name: Alex Newman
- GitHub: [thedotmack](https://github.com/thedotmack)
- X (project handle, official): [@Claude_Memory](https://x.com/Claude_Memory)
- Org: member of @SurfSolana
- Followers (GitHub): 1.6k
- Public repos: 119
- Project page link in README explicitly names `@Claude_Memory` as the official X account and Alex Newman as the author.

## Project
- Repo: [thedotmack/claude-mem](https://github.com/thedotmack/claude-mem)
- One-liner: persistent memory compression for AI coding agents, captured via lifecycle hooks, stored in SQLite plus Chroma, served back through MCP.
- Stars: 79.3k total, +671 in the last 24 hours (HN/X-driven spike).
- Forks: 6.8k.
- License: Apache 2.0.
- Latest release: v13.3.0 on 2026-05-21 (do not reference the version in copy per the routine rule).
- Maturity: 13 majors in roughly seven months of public shipping.

## What it actually does
- Wires into Claude Code's 5 lifecycle hooks (pre/post tool call, session start, session end, etc.) and captures each tool-use observation as it happens.
- Generates semantic summaries via a worker process that exposes an HTTP API.
- Persists to SQLite (full-text search) and Chroma (vector search) so the next session can do hybrid keyword plus semantic retrieval.
- Injects relevant context back into the next session via 4 MCP tools that follow a 3-layer workflow for token efficiency.
- Cross-platform: Claude Code, Gemini CLI, OpenCode, OpenClaw gateways, Codex, Copilot. Same hook pattern, different harness.

## Voice notes for the writer
- Build-in-public solo. Ships often.
- Frames the work as fixing his own pain ("agents kept dropping the thread") rather than a grand vision.
- Lane: agent infrastructure, MCP, memory, the kind of plumbing that becomes invisible once it works.

## What's trending right now
- The metric to lead with is total stars (79k) plus star velocity (+671 / day). Avoid the v13.3.0 version number per the X caption rule.
- The novel angle: not a new model, not a new framework, just the right plumbing between two existing primitives (lifecycle hooks and MCP) plus a vector store, applied to the one thing agents are worst at — remembering.

## Geography
- Not publicly stated. Treat as anywhere.
