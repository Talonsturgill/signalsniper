# Creator dossier — 2026-06-23

## Project
**Oak** — version control built for AI agents. A from-scratch Rust VCS (not a git wrapper) with content-addressed storage, lazy mounts, and a branch-per-session model. Tagline: "version control at the speed of agents."

- Repo: https://github.com/oakdotspace/oak
- Site: https://oak.space
- License: Apache-2.0
- Stage: public beta (latest release 2026-06-21)
- Language: Rust (96.6%)
- Crates: `oakvcs-core` (the VCS library, imported as `oak_core`) and `oakvcs-cli` (the `oak` binary)

## Creator
- **Zach Geier** — software engineer, Seattle. Builds Oak; day job background in web dev, graphics programming, and game development.
- Personal site: https://zdgeier.com  |  GitHub: https://github.com/zdgeier  |  LinkedIn: https://www.linkedin.com/in/zdgeier/
- **Adam Morse** shapes the product and the visual system (design partner).
- **X / Twitter handle to tag: `@oakdotspace`** (the official project account linked from oak.space; the personal handle is not publicly surfaced, so the project account is the correct tag).

## One-line bio
A working engineer who got tired of agents paying the full-clone tax on every task and rebuilt version control around how agents actually operate.

## Voice notes
Calm, precise, builder-to-builder. The site copy leads with the mechanism, not hype: "the speed is a consequence of the design, not the pitch." No frontier-lab grandiosity. Honors craft (Rust, a real data model) over buzzwords. A tribute should match that register: specifics over adjectives, the contrast carries the praise.

## What they care about
- Making the agent inner-loop fast: an agent should pick up a repo and start editing in seconds, not wait on a clone.
- A real data model, not a git veneer. Oak has its own Blob / Manifest / Commit / Tree model.
- Correctness primitives done properly: BLAKE3 content hashing, content-defined chunking, diff/merge.
- Branch-per-session as the natural unit of agent work, with branch descriptions standing in for per-commit messages.

## Prior work
Independent open-source and personal projects under `zdgeier` (web/graphics/game-dev experiments). Oak is the current flagship — his first project squarely in the AI-agent-tooling lane.

## Latest release / commit date
- v0.99.0 public beta, 2026-06-21.

## The metric that's trending
- Star count is still small (around 43 on the repo) because the project is days into public beta. The live momentum signal is the **Hacker News front page** placement today (~182 points on the Show HN), which is the honest "trending now" hook — far more meaningful for a day-one launch than the raw star count.
- Caption metric to lead with: "just landed on the Hacker News front page." No version number in the caption (hard rule).

## Verified technical claims (from README, for the critic)
- "version control at the speed of agents."
- Content-addressed lazy mounts: manifest comes down on mount, file contents stream in on first read.
- Every task gets its own working tree on its own branch (branch-per-session).
- BLAKE3 content hashing, content-defined chunking, diff/merge, Blob/Manifest/Commit/Tree data model.
- CLI verbs: `oak mount`, `oak clone`, `oak push`, `oak pull`, `oak commit`, `oak upgrade`, `oak branch`.
- "far faster than git for agent workloads."
- Platforms: macOS (Apple Silicon), Linux (x86_64), Windows x86_64 (mount needs ProjFS).
- Install: `curl -fsSL oak.space/install | sh` or `cargo install oakvcs-cli`.

## Angle for the tribute
The Why-this-one leans on creator/craft (Geier + Morse, a real data model, not a wrapper). The caption leans on momentum + positioning (HN front page, Rust VCS for agents, mount in seconds, branch per session). Two different surfaces, no shared phrasing.
