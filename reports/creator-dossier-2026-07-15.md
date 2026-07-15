# Creator Dossier — 2026-07-15

## Project
- **oh-my-pi** (`omp`) — a terminal-first AI coding agent. Tagline: "A coding agent with the IDE wired in."
- Repo: https://github.com/can1357/oh-my-pi
- Site: https://omp.sh
- License: MIT. Written in TypeScript with a ~55k-line Rust core.

## Creator
- **Name:** Can Bölük
- **X handle:** @_can1357 (https://x.com/_can1357)
- **GitHub:** https://github.com/can1357
- **LinkedIn:** https://nl.linkedin.com/in/canboluk — "Security researcher and reverse engineer"
- **Blog:** https://blog.can.ac (can.ac), also writes at secret.club
- **Geography:** Netherlands (shareable — public LinkedIn/blog).

## One-line bio
Reverse engineer and low-level security researcher (VMProtect devirtualizer, VTIL, kernel exploitation, Windows internals) who has turned that systems-level rigor onto AI coding agents.

## Voice notes
- Precise, low-level, unshowy. Ships serious engineering (Rust cores, native bindings, LSP/DAP) and lets the work speak. Not a hype account.
- His audience is the low-level / security / systems crowd who respect correctness and hate hand-waving. A tribute that's technically honest and shows the actual mechanism will land; a fluffy one will not.

## Prior work
- VMProtect 3.x devirtualizer, VTIL (Virtual-machine Translation Intermediate Language), CVE-2018-8897 kernel PoC, Hyperliquid validator reversing. Deep binary-analysis credibility.

## What they care about
- Correctness and mechanism over vibes. Tools that do the *right* thing at the systems level (real language-server calls, real debugger, edits that can't silently corrupt).

## Latest release / momentum
- v16.5.2 released 2026-07-14; repo pushed 2026-07-15 (today). Very actively maintained.
- Joined GitHub Trending 2026-05-23 (+475 stars in 24h at the time).

## The metric that's trending
- **~17.8k stars** (GitHub repo page) / **18k** (live shields.io badge), **1.6k forks**, as of 2026-07-15. Ship as "past 17k stars."

## The angle that's ours (different from the tweet's metric lead)
- The **hashline** mechanism: oh-my-pi anchors every edit to a content hash of the surrounding code, not to a line number. It edits by *what* the code is, not *where* it sits — so a stale or conflicting edit is caught and rejected instead of quietly corrupting the file. This is the reverse-engineer's instinct (anchor to content, distrust positions) brought to AI code editing. Only someone who read the repo would know it.

## Credit note
- oh-my-pi is a fork of pi-mono by Mario Zechner (@badlogic), extended into the batteries-included terminal agent. The tribute honors can1357's build; the PR notes acknowledge the pi-mono origin.

## LinkedIn tag
- `{"name": "Can Bölük", "url": "https://nl.linkedin.com/in/canboluk"}`
