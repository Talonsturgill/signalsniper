# Creator Dossier — 2026-07-01

## Project
- **Name:** herdr
- **Repo:** https://github.com/ogulcancelik/herdr
- **Tagline (verbatim):** "Run all your coding agents in one terminal. See who's blocked, working, or done at a glance."
- **What it is:** A terminal-based *agent multiplexer*. It runs many AI coding agents side by side in one interface, each in a real terminal (full-screen TUIs render correctly), and surfaces each agent's live state at a glance: blocked, working, done, idle. Workspaces, tabs, panes, mouse-native controls, persistent detach/reattach sessions, a local socket API for orchestration, and scriptable plugins in any language.
- **License:** AGPL-3.0-or-later (open source); commercial licenses offered.
- **Latest release:** v0.7.1, June 24, 2026.

## Creator
- **Name:** Can Çelik (Oğulcan Çelik)
- **GitHub:** https://github.com/ogulcancelik (214 followers, 11 following)
- **X handle:** @ogulcancelik  (https://x.com/ogulcancelik)
- **Personal site:** https://oddbit.ai
- **Geography:** not publicly listed on the profile; name is Turkish. Not asserting a city in shipped copy.
- **Prior work (pinned repos):**
  - `pi-extensions` — extensions for pi, the terminal coding agent (TypeScript, ~160 stars)
  - `unity-bridge` — minimal single-file C# HTTP bridge for AI-driven Unity Editor control
  - `claudify` — Claude-API playlist generator (TypeScript)
  A pattern of small, sharp, single-purpose developer tools that wire AI into an existing workflow rather than replacing it.

## Voice notes
- Ships plain, unhyped README copy. The pitch is subtraction, not adjectives.
- Memorable line (verbatim): "one local rust binary, not an app: no gui, no electron, no mac-only wrapper, no account, no telemetry."
- Positions herdr against both tmux (persistence and panes, but no agent-awareness) and GUI managers like Conductor / CMux (app-wrapped, heavier). herdr is the middle path: tmux's persistence plus agent-awareness in a ~10MB binary that runs anywhere over SSH.

## What he cares about
- Terminal-native tooling. No Electron, no wrapper app, no account, no telemetry.
- Breadth of agent support: Claude Code, Codex, Pi, Droid, Amp, OpenCode, Grok CLI, Devin CLI, Cursor Agent, GitHub Copilot CLI, Kilo Code CLI, and 15+ more — herdr is agent-agnostic plumbing, not a bet on one vendor.
- Small binaries and honest engineering. Rust, single binary, cross-platform (Linux, macOS, Windows in beta).

## Metrics that are trending
- **Stars:** ~9.1k.
- **Velocity:** ~+169 stars/day on GitHub Trending (Trendshift repo id 32084) — climbing, not saturated.
- **Trending source signal:** on GitHub Trending (daily) and Terminal Trove / LinuxLinks coverage as a "tmux-like agent multiplexer."

## Angles the copy can use (kept distinct per surface)
- **X caption (growth metric):** star velocity — climbing now, agent-agnostic breadth.
- **Why-this-one (Gmail, different angle):** the anti-bloat engineering stance (one Rust binary, no Electron, no telemetry) and his track record of small terminal tools.
- **Scenes:** the number contrast — many agents, one terminal, a 10MB binary — plus a terminal beat.

## Framework + style rationale
- **Framework: RECEIPT.** herdr is a momentum-and-numbers story (fast-climbing stars, 26+ supported agents, one 10MB binary). The big_number beats let the count do the proving. Avoids re-running the 2026-06-26 MANIFESTO+terminal structure. Most-recent framework was SCHEMATIC, so RECEIPT is clear of the back-to-back rule.
- **Aesthetic: linear.app brand pack.** Near-black canvas, light-gray ink, a single lavender accent — the "quietly luxurious software-craft" register fits a polished terminal tool, and gives the big numbers a signature color to land on. Not used in the last 14 entries. Pure-mono x.ai was the thematic runner-up but risked a flat, accent-less render.
