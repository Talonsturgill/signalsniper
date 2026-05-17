# Creator Dossier — 2026-05-17

## Creator

- **Name:** Ben Cochran
- **X handle:** `@azurewraith` (inferred — see note below)
- **GitHub:** https://github.com/azurewraith
- **LinkedIn:** https://www.linkedin.com/in/cochranb/
- **Hacker News:** `azurewraith`

> **Handle note.** Ben uses the identical username `azurewraith` on GitHub, Hacker News, and as the founder voice behind statewright.ai. Multiple secondary sources attribute his X/Twitter handle as `azurewraith`. X profile pages cannot be machine-verified from this environment (X returns HTTP 402 to fetch), so the caption uses `@azurewraith` as the lane-aligned default. The Gmail flags this so the user can eyeball it before posting.

## One-line bio

Distinguished engineer with 20+ years across full-stack, DevOps, HPC and ML — stints at NVIDIA and AMD — now building Statewright solo in the open.

## The project

- **Name:** Statewright
- **Repo:** https://github.com/statewright/statewright
- **Site:** https://statewright.ai
- **Tagline:** "State machine guardrails for AI agents." Engine framing: "Agents are suggestions, states are laws."
- **What it is:** A deterministic Rust state-machine engine (no LLM in the loop) that constrains which tools a coding agent can call in each workflow phase. Plan states are read-only; implement unlocks edits behind guards that block destructive ops; test allows only whitelisted commands. The model never sets state — it *requests a transition*, and the engine evaluates guards (data carried along the run) to accept or reject it. Ships as MCP plugins for Claude Code, Codex, Cursor, opencode and Pi.
- **Why it's novel:** Rules in a prompt are advice a model can rationalize away ("this task is simple, maybe I don't need worktrees"). Statewright moves enforcement out of the transformer and into deterministic code. The engine is the part that can't hallucinate — it doesn't judge, it enforces. This collapses the agent's reachable tool/solution space per phase, which is what actually fixes doom loops, mass-edit reversions and death spirals.
- **The metric that's trending:** On a 5-task SWE-bench subset, two small local models (a 13.8 GB and a 19.9 GB build) went from **2/10 to 10/10** once wrapped in Statewright constraints. That's the headline result and it carries the video's `fix`/`close`.
- **Momentum:** Front-paged via Show HN on 2026-05-12 (124 points, 47 comments); ~314 GitHub stars and climbing; active shipping (fixes and license corrections landed live in the launch thread through 2026-05-14).
- **License posture:** Split — the engine and agent crates are fully open source; the plugin layer is FSL-1.1-ALv2 with a 3-year ALv2 conversion clock, with an explicit PATENTS.md grant.

## Voice notes (for copy)

Peer-to-peer build-in-public engineer. Dry, precise, low ego, uses "^_^". Strong opinions stated flatly: "the state engine is the part that can't hallucinate," "rules in prompts are suggestions the model can rationalize away," "the models are good enough, the harness operating them is what's holding things back." He answers hard technical questions in full and ships corrections same-day. Tribute voice should match: declarative, structural, contrast carries the praise — no superlatives.

## Anti-repeat angles (so tweet / Why-this-one / scenes don't collide)

- **X caption angle:** momentum off the HN debut + the 2/10 -> 10/10 result + the one-line positioning.
- **Why-this-one angle:** creator pedigree (NVIDIA / AMD distinguished engineer) and build-in-public discipline (open-sourced the engine, answered everything, shipped same-day).
- **Scene angle:** the structural thesis — prompts are advice, the engine is law; determinism over scale — rendered as a phase-gated state diagram.

## Style mapping rationale

The brand-design-systems presets are all inside the 14-entry anti-repeat window, so a brand pack is required. HashiCorp is the closest authentic match: its identity *is* deterministic infrastructure, state and policy-as-code (Terraform state, Sentinel guardrails) on a near-black ground with chromatic product accents. Statewright is policy/state guardrails for agents — same idea, new domain. Terraform purple is the natural accent for a "state machine" piece. `hashicorp` is absent from the last 14 history entries, so it clears the anti-repeat gate.
