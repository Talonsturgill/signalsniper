# Creator Dossier — 2026-05-23

## Subject
**Can Bölük** (handle: **@_can1357**)
GitHub: https://github.com/can1357
X profile: https://x.com/_can1357
Project: **oh-my-pi** (`omp`) — https://github.com/can1357/oh-my-pi

## One-line bio
Reverse engineer and low-level systems researcher (VMProtect devirtualizer, VTIL project) who's turned the same harness-building instincts onto AI coding agents.

## Voice notes
Terse, technical, low-key. Doesn't market — drops releases. Background in offensive security research (Secret Club blog) leaves a clear fingerprint on his agent design: determinism, content addressing, debugger primitives over heuristics. He doesn't pitch the agent as a product. He pitches it as a tool harness with the rough edges filed off.

## Prior work
- **VTIL** — Virtual-machine Translation Intermediate Language; an analysis framework for devirtualizing obfuscated binaries.
- **VMProtect devirtualizer (3.x)** — static devirtualizer for VMProtect-protected x64 binaries, GPL-3 released.
- **Hex-Rays microcode plugins** — automated simplification of Windows kernel decompilation.
- Active author at Secret Club (secret.club) — a collective of reverse engineers and exploit developers.

## What he cares about
Determinism. Content addressing over positional addressing. Real debuggers over heuristic prompt engineering. A small, fast core (Rust) with a thin orchestration surface (TypeScript/Bun) — the same separation he applied to VTIL years before agents existed.

## Latest move
**v15.2.4** of `oh-my-pi` shipped 2026-05-22, the day before today. The project is a fork-and-rewrite of Mario Zechner's pi-mono (we covered the original on 2026-05-09), but the angle is completely different: Can rebuilt the agent surface around **hash-anchored edits** (the model points at content hashes, not line numbers — eliminating the "string not found" loops that plague every coding agent) plus a Rust core with first-class LSP and DAP integration.

## Stack (verifiable from repo)
- TypeScript front-end on Bun runtime
- Rust core, ~27,000 lines
- 40+ LLM providers wired through one router
- 32 built-in tools, 13 LSP operations, 27 DAP operations
- Real debugger integration: lldb, dlv, debugpy
- First-class subagent orchestration across isolated worktrees
- License: MIT

## Trending metric
- **6,500+ stars total**
- **+457 stars in the last 24 hours**
- v15.2.4 release on 2026-05-22 (the day before this tribute)
- TypeScript trending lane today

## Geography
Not publicly stated. Active in offensive-security community circles internationally.

## Why-this-one angle (Gmail)
The pivot story: a reverse engineer who built devirtualizers for years is now pushing the harness layer of coding agents forward — with the same instincts that made VTIL work. Not a hype play. A craftsman shifting domains.

## The novel technical claim
**Hash-anchored edits.** Existing agents tell the model "edit line 42." Files shift, line 42 isn't what it was, the edit fails, the model loops. oh-my-pi has the model point at a content hash of the anchor region instead. Files can shift freely. The edit lands or it errors loudly — no silent corruption, no whitespace battles.

## Risk / lane-adjacency check
- Already in `style-history.json`? **No** — different `project_url`, different creator from the 2026-05-09 pi-mono coverage (Mario Zechner / badlogic).
- Findable X handle? **Yes** — @_can1357, verified across multiple sources.
- Frontier lab? **No** — solo builder.
- Big company team? **No** — individual.

## Sources
- Repo: https://github.com/can1357/oh-my-pi
- Creator GitHub: https://github.com/can1357
- Creator X: https://x.com/_can1357
- Secret Club author page: https://secret.club/author/can1357.html
- VMProtect devirtualizer announcement: https://x.com/_can1357/status/1295103431145922562
- Independent write-up: https://dudarik.com/en/blog/oh-my-pi/
