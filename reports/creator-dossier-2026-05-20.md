# Creator Dossier — Tirth Kanani · 2026-05-20

## Identity

- **Name**: Tirth Kanani
- **GitHub**: [tirth8205](https://github.com/tirth8205)
- **X / Twitter**: [@tirth_8205](https://x.com/tirth_8205)
- **LinkedIn**: in/tirthkanani
- **Site**: tirthkanani.com
- **Location**: London, United Kingdom

## One-line bio

AI/ML engineer and technical founder out of London who builds production-grade developer tools — most visibly code-review-graph, an open-source knowledge graph layer that lets AI coding agents read only the files an edit actually touches.

## Voice notes

Tirth posts as an individual builder, not a startup voice. Technical but plain — comments like "100% recall, conservative on precision" instead of marketing-spin. He shares benchmark CSVs, not screenshots of CEO-style threads. The tone to match is engineer-to-engineer: state the numbers, name the tradeoff, get out of the way.

## Prior work

- **CrumbleUX** — a real-time visual language model product for design critique. The same instinct that drove code-review-graph — let the model focus on a small structural slice rather than the whole interface — shows up there first.
- **GraphMinds** — earlier project on graph-based algorithms and AI exploration. Code-review-graph is the production-grade extension of that thread.
- **SupplyMinds** — first place at the Epiminds Multi-Agent Hackathon 2025.
- Earlier work at the University of Birmingham HCI and AI Lab on Graph Neural Networks.

## What he cares about

- **Context efficiency for agents.** The core thesis of code-review-graph is that AI coding tools waste tokens re-reading entire codebases on every task. The fix is structural, not statistical.
- **Conservative recall.** The benchmark headline isn't "97% accurate" — it's "100% recall, 0.54 F1" with an explicit note that the system over-includes rather than miss anything affected.
- **Real benchmarks.** The repo ships measurements across fastapi, flask, gin, httpx, nextjs, and one full Next.js monorepo, not synthetic toys.
- **MCP as the integration surface.** Rather than asking users to switch tools, the project ships as an MCP server that drops into Claude Code, Cursor, Codex, Windsurf, Zed, Continue, OpenCode, Antigravity, Gemini CLI, Qwen, Qoder, Kiro, and Copilot.

## Latest release

The repo is on v0.x with 24 releases and 442 commits on main. Tirth has been shipping incrementally — Tree-sitter language support, blast-radius traversal, MCP tools, the wiki generation module — through May 2026. The 17k-star mark crossed earlier this week and the project is now climbing roughly +120 stars/day on GitHub trending.

## The metric trending

- **17,000+ GitHub stars** total, +123 today on the trending board.
- **8.2× average token reduction** across six real repositories (range 6.9× to 16.4×).
- **49× reduction** on the Next.js monorepo (27,732 files filtered to ~15 affected).
- **100% recall** on the impact-analysis benchmark.
- **Sub-2-second incremental updates** on a 2,900-file project.
- **24 languages supported** plus Jupyter notebooks.
- **28 MCP tools** exposed to host editors.

## Caption angle

Lead with star velocity (the trending metric) and the 49× reduction (the eye-popping number). Leave creator history, CrumbleUX, and Tree-sitter for the thread-reply Why-this-one.

## Why-this-one angle

Talk about the through-line from CrumbleUX to code-review-graph: same instinct, narrower problem, sharper result. London builder, MIT-licensed, Tree-sitter under the hood.
