# Creator Dossier — 2026-06-08

## Who

- **Name:** Neo Reid
- **X handle:** [@Neo_Reidlab](https://x.com/Neo_Reidlab)
- **GitHub:** [Panniantong](https://github.com/Panniantong)
- **Contact on file:** pnt01@foxmail.com (plus a WeChat group QR in the repo)
- **One-line bio:** Solo founder shipping AI-agent infrastructure. Profile motto: "Ship it. Open-source it. Move on." Describes the company as "Solo founder. All employees are AI."
- **Geography:** UTC+8 (China). Active on GitHub since 2020.

## The project

- **Name:** Agent Reach
- **URL:** https://github.com/Panniantong/Agent-Reach
- **Tagline (verbatim):** "Give your AI agent eyes to see the entire internet. Read & search Twitter, Reddit, YouTube, GitHub, Bilibili, XiaoHongShu — one CLI, zero API fees."
- **Latest release:** v1.4.0 (March 31, 2026). Created March 26, 2026.

### What it is

A CLI that lets coding agents (Claude Code, Cursor, Windsurf, OpenClaw) read and
search across 14+ platforms: Twitter/X, Reddit, YouTube, GitHub, Bilibili,
XiaoHongShu, Douyin, LinkedIn, WeChat official accounts, Weibo, V2EX, Xueqiu,
Xiaoyuzhou podcasts, RSS, and general web reading.

### The novel angle (the thing most "agent web access" tools get wrong)

Agent Reach is **not a framework**. It does not wrap the platforms behind a new
abstraction or a hosted API. It is *scaffolding* — it installs and configures
battle-tested open-source CLIs and lets the agent invoke them directly:

- web read: Jina Reader (no key)
- Twitter: twitter-cli (cookie auth)
- Reddit: rdt-cli (cookie auth)
- YouTube / Bilibili transcripts: yt-dlp
- GitHub: official `gh` CLI
- semantic search / structured data: Exa MCP, douyin-mcp-server, linkedin-mcp-server

Each integration is pluggable and replaceable, so swapping the underlying tool
doesn't touch the rest. Credentials (cookies / tokens) stay on the user's machine.
A `agent-reach doctor` command self-diagnoses every channel, and a safe mode
previews operations before they run.

### Why it matters

Most agent "internet access" is either a paid managed API or a brittle bespoke
scraper. Agent Reach gives the agent reach across the open web with **zero API
fees**, no managed service, and no data leaving the box, by standing on tools
engineers already trust. The maintenance discipline is the quiet differentiator:
Neo keeps the scrapers updated as platforms change their layouts.

## Metrics trending now

- **~23.6k GitHub stars**, **2k forks**.
- **+961 stars in the last day** (GitHub trending, Python + overall). Still climbing.
- Solo-maintained.

## Feeds the deliverables

- **X caption growth metric:** "just crossed 23k stars" / "+961 today" (never the version number).
- **Why-this-one different angle:** the creator (solo founder, "all employees are AI") and the maintenance-as-a-feature discipline — distinct from the caption's product framing.
- **Video thesis:** not a framework, it's scaffolding/glue — the SCHEMATIC diagram shows the agent wired straight into the platform CLIs.

## Sources

- https://github.com/Panniantong/Agent-Reach
- https://github.com/Panniantong/Agent-Reach/blob/main/docs/README_en.md
- https://github.com/Panniantong
- https://trendshift.io/repositories (GitHub trending placement)
