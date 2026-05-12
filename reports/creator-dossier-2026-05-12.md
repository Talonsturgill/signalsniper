# Creator dossier · 2026-05-12

## Pick

**OpenHuman** by **Steven Enamakel** (@senamakel) under the **TinyHumans** label (@tinyhumansai).

- Project: https://github.com/tinyhumansai/openhuman
- License: GNU GPL3
- Latest release: v0.53.22 on 2026-05-09
- Stars: ~1.9k total, +366 in the last 24h on the Python trending board (Rust-heavy codebase, surfaces under Python via the embedded toolchain)
- Repo languages: Rust 69.6%, TypeScript 26.4%

## Creator

- Name: Steven Enamakel
- Handle (personal): https://twitter.com/senamakel
- Handle (org/brand): https://twitter.com/tinyhumansai
- Location: Dubai
- Bio (verbatim from GitHub): "Engineer specializing in deep-tech, web3, AI. I've been a builder first and a founder second."
- Personal hub: https://linktr.ee/enamakel
- Brand page: https://tinyhumans.ai/openhuman
- Followers (GitHub): 153

Steven leans builder-first. The bio admits it. The repo is shipped under a brand label (TinyHumans) but every commit and release thread routes back to him. Tag the personal handle in the tribute; the brand handle gets a mention in the dossier.

## Voice notes

- Self-deprecating about scope. The dev.to write-up is titled "I built OpenHuman" and explicitly frames it as "the first AI agent with big data capabilities", which is bold but immediately followed by an honest changelog.
- Treats infra detail as the romance, not a footnote: he names his token compression layer ("TokenJuice"), his memory subsystem ("memory tree"), and his autonomy beat ("subconscious loop").
- Build-in-public cadence is real. v0.53.22 is the 530-something published release. Issues bring feature requests; he responds in the thread.
- Privacy-as-stance, not as buzzword. "Private, Simple and extremely powerful" is the repo subtitle.

## Prior work

- Web3 deep-tech engineering before the AI pivot (per his self-bio).
- 5 public GitHub repos. OpenHuman is the pinned one. The rest are smaller utilities and reverse-engineering work.
- Quickdraw / Pair Extraordinaire / Pull Shark x2 / Starstruck x4 / YOLO badges, signal a long-running open-source habit.

## What he cares about

- Local-first. Memory lives on disk in markdown, not on someone else's GPU pool.
- Cost discipline. TokenJuice exists specifically to shrink prompts before they touch a paid API. He claims up to 80% reduction on tool outputs.
- Integration depth. 118 third-party connectors are wired by default (Gmail, Notion, GitHub, Slack, etc.) with a 20-minute background sync.
- Embodiment. There's a desktop mascot that lip-syncs to ElevenLabs and joins Google Meets as a participant. He treats the agent like a presence, not a chat window.

## The metric that's trending

- Star velocity: +366 in 24h on the Python trending board, which puts him in the mid-pack of solo builders shipping today (above kiro-gateway, well below NousResearch tier).
- Total stars crossing the 1.9k mark today; round-up framing ("just crossed 1.9k stars") reads honest.
- Release tempo: v0.53.22 three days ago. The "0.53.x" series is the memory-tree generation; he started this cycle 8 weeks ago.

## What's different about OpenHuman vs the rest of the lane

- **Subconscious loop.** Most agents are request/response. OpenHuman runs a background loop that re-reads its own memory tree, summarizes, and nudges itself to persist what's worth keeping. That's the agentic-loop pattern the lane cares about.
- **Memory tree on disk.** SQLite-backed but mirrors to Obsidian-compatible markdown, so the user can read or grep their own memory. No vendor lock-in on the substance.
- **TokenJuice in front of every call.** Cost-as-design, not cost-as-afterthought.
- **118 connectors out of the box, not via plugins.** Cuts the "install the integration first" tax that kills agent adoption.

## Tribute angle

He's a Dubai-based builder who picked the harder path: ship the agent locally, on the user's hardware, with the memory the user can actually open. The video should honor the architecture, not the mascot. SCHEMATIC framework, diagram of the subconscious loop, hold on the bet that local-first + deep memory wins.

## X caption growth metric (per writing-rules)

Lead with "just crossed 1.9k stars". Not the version number. The cadence story is the velocity, not the release tag.

## Sources

- https://github.com/tinyhumansai/openhuman
- https://github.com/senamakel
- https://twitter.com/senamakel
- https://tinyhumans.ai/openhuman
- https://github.com/tinyhumansai/openhuman/releases/tag/v0.53.22
- https://dev.to/neocortexdev/i-am-building-the-first-ai-agent-with-big-data-capabilities-70e
