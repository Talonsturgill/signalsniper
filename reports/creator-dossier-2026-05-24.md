# Creator dossier — Yohei Nakajima — 2026-05-24

## Identity

- **Name:** Yohei Nakajima
- **X handle:** @yoheinakajima
- **GitHub:** github.com/yoheinakajima
- **Role:** General Partner at Untapped Capital (NYC, co-founded 2020 with Jessica Jackley)
- **Lineage:** Creator of BabyAGI (March 2023, ~220 lines of Python that spawned the autonomous-agent meme)
- **Geography:** New York City
- **Bio one-line:** VC by day, builds AI runtimes by night. Treats infra like haiku.

## Today's drop

- **Project:** ActiveGraph (github.com/yoheinakajima/activegraph)
- **Stars today:** ~201, climbing this week
- **v1.0 stable:** shipped this month
- **arXiv paper:** 2605.21997 — "The Log is the Agent: Event-Sourced Reactive Graphs for Auditable, Forkable Agentic Systems" (sole author: Nakajima)
- **README headline:** "The graph is the world. Behaviors are physics. The trace is the proof."

## What it does (in his words)

A reactive, event-sourced graph runtime that gives long-running agents a shared world to act on. Append-only event log is the source of truth. Behaviors (functions, classes, LLM routines) react to changes in a deterministic graph projection of that log and emit new events. All coordination happens through the shared graph, never agent-to-agent.

## Why it's novel

Most agent frameworks ship an orchestrator: agents talk to agents, the state lives in their conversation. ActiveGraph inverts the substrate. The log is the source of truth. The graph is a projection. Behaviors are pure reactions. You get deterministic replay, cheap forking, full audit lineage — properties most agent frameworks can't claim because their state IS the messages.

## Voice signature

Terse, poetic, technical. Short declarative cadence. Aphoristic taglines ("VC by day, builder by night"). Treats infra as creative work. Builds in public. No hyperbole. Confident. Closest cousin: a systems paper written in haiku.

## What he says about ActiveGraph (quotable)

- "The graph is the world. Behaviors are physics. The trace is the proof."
- "The trace is the deliverable."
- "ActiveGraph makes the whole operating reality persistent — what the system believes, what it's doing, what depends on what."

## Caption growth metric

Lead with "ActiveGraph just hit 200 stars and a fresh arxiv paper drops with it." (no version number, real momentum, paper as authority signal). Honest about the small star count; the BabyAGI lineage hook does the heavy lifting.

## Why-this-one (different angle from caption)

Caption owns: the technical mechanism + the BabyAGI lineage hook.
Why-this-one should own: the personal arc + the discipline. He runs a fund by day, writes systems papers by night. Three years from a 220-line while-true loop to a substrate that needed peer-reviewable formalism. The patience IS the story.

## Sources

- github.com/yoheinakajima/activegraph
- arxiv.org/abs/2605.21997
- activegraph.ai
- yoheinakajima.com
- cognitiverevolution.ai/ai-identity-from-east-and-west-with-yohei-nakajima-gp-at-untapped-capital-and-babyagi-creator
