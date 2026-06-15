# Creator dossier 2026-06-15

## Project
- **Name:** obsidian-wiki
- **URL:** https://github.com/Ar9av/obsidian-wiki
- **One-liner:** Framework for AI agents to build and maintain a digital brain through an Obsidian wiki, implementing Karpathy's LLM Wiki pattern.
- **Latest release:** v2026.06.5, shipped June 14, 2026 (true last-24h signal).
- **Language:** Python (63%).

## Creator
- **Name:** Arnav
- **X handle:** @_ar9av
- **Site:** ar9av.in
- **GitHub:** https://github.com/Ar9av
- **Bio:** `renice -n -20 $$` (a Unix in-joke: bump my own process to top priority). Reads as a terminal-native builder with a dry sense of humor.
- **Geography:** Not publicly stated on the profile. Left out of all copy.

## Voice notes
- Terminal-native, understated, build-in-public. The bio is a shell command, not a tagline.
- Ships small and ships often (release tags like `v2026.06.5` show a date-versioned cadence).
- Frames his own work against named prior art (Karpathy's LLM Wiki, Google's paper-authoring) rather than overclaiming originality. Tribute copy should match: credit the pattern, spotlight the execution.

## Prior work
- **PaperOrchestra** (579 stars) - automated AI research-paper authoring, inspired by Google's approach.
- **AgentTower** - real-time monitoring UI for Claude Code sessions.
- **agent-manual** - docs covering AI coding-agent configuration across platforms.
- **fast-is-english-word** - perf experiment, ~42M ops/sec English-word validation.
- **transformer-nmt-chatbot** (41 stars) - earlier NMT chatbot.

Pattern: Arnav lives in the AI-coding-agent ecosystem. He builds the meta-tooling - watching agents, configuring agents, and now giving agents a memory. obsidian-wiki (2.1k stars) is clearly his breakout relative to everything else on the profile.

## What he cares about
- Persistent, structured knowledge over repeated LLM round-trips.
- Working across agents, not locking to one. obsidian-wiki targets Claude Code, Cursor, Windsurf, Pi, and mines history from Claude, Codex, Hermes, Pi, OpenClaw.
- Incremental, delta-based work (a manifest so the system updates rather than reprocesses).

## The novel angle (feeds the Why-this-one)
Most "agent memory" projects bolt a vector store onto a chat loop. obsidian-wiki instead makes the *agent* the librarian: it ingests source material, extracts concepts and relationships, merges them into existing markdown pages while tracking contradictions, and maintains schema coherence over time. The knowledge lives in human-readable Obsidian notes you own, not an opaque embedding blob. A manifest tracks what's already ingested so updates are deltas, and it can mine past coding-agent sessions for what you already learned.

## The trending metric (feeds the X caption)
- **Stars:** ~2.1k total, **+135 in the last 24h** on GitHub trending (Python, daily).
- Still early and climbing - high daily velocity relative to a small base, not a saturated headline number.
- Use "crossed 2k stars and climbing" as the growth hook. **No version number in the caption.**

## Four-stage loop (feeds the diagram scene)
1. **ingest** - pull in documents, PDFs, chat exports, images.
2. **extract** - lift concepts and relationships.
3. **merge** - fold into existing pages, flag contradictions.
4. **maintain** - keep schema coherence; a manifest enables delta updates.

Skills shipped: `/wiki-query` (cross-project retrieval) and `/wiki-update` (sync learnings across codebases).
