# Creator Dossier — 2026-06-27

## Subject

- **Project:** Weave Router (`workweave/router`)
- **Repo:** https://github.com/workweave/router
- **Creator (human):** Andrew Churchill
- **Role:** Co-founder & CTO, Weave (YC W25)
- **Primary tag for X:** `@WorkWeave` (the project's official account)
- **Personal handles:** X `@andrewchurchiii`, GitHub `a-churchill`
- **Company site:** https://workweave.dev · Router site: https://weaverouter.com

## One-line bio

Andrew Churchill is the co-founder and CTO of Weave (YC W25), the team building
tooling to measure and right-size engineering and agent work. He was employee #1
at Causal, where he built the spreadsheet interface, the access-control system,
and the AI onboarding engine. CS + math background from MIT.

## What it is

Weave Router is a model router for agentic systems. It sits in front of
Anthropic, OpenAI, Gemini, and open-weight models (DeepSeek, Kimi, GLM, Qwen,
Llama, Mistral via OpenRouter), and for every single request it picks the model
that can do the job at the lowest cost. The routing decision runs locally in
under 50ms using a tiny on-box embedder plus a cluster scorer derived from the
Avengers-Pro research line. It is not a "send the prompt to a big model and ask
it which model to use" router. The model picks itself, on your box, before the
call leaves.

Tagline: "One endpoint. Every model. Always the right one."

## Voice / tone notes

- Builder-direct, infra-precise. Talks in latency numbers, token counts, and
  endpoint changes, not adjectives.
- The Show HN framing was measured and honest: "40% on tokens vs. what we
  otherwise would have paid, with no noticeable differences in quality or
  velocity." No hype, just the receipt.
- Peer-to-peer register. A small YC team shipping infra they themselves needed.

## What they care about

- Right-sizing inference for production agentic workloads (their own blog framing).
- Keeping provider keys local (BYOK with on-box encryption) and observability
  first-class (OTLP). Security-of-deployment posture, not just cost.
- Drop-in adoption: one endpoint change, speaks Anthropic Messages / OpenAI Chat
  Completions / Gemini native, works inside Claude Code, Codex, Cursor, opencode.

## Prior work / context

- Weave's first product measures engineering and agent work; Router is the
  inference-cost arm of that thesis.
- Announced a $4.2M seed round (workweave.dev/blog). YC W25 batch.
- Repo created 2026-04-27, developed privately, then opened with a Show HN.

## Momentum metric (the trending signal)

- **Show HN front page on 2026-06-26**: 154 points, 91 comments. Title:
  "Show HN: Smart model routing directly in Claude, Codex and Cursor."
- **305 GitHub stars** (and climbing the day after launch), 14 forks.
- Active today: last push 2026-06-27. Written in Go. Source-available under the
  Elastic License v2.
- Billed on its own site as the "#1 ranked prompt router."

## Latest technical move

The public Show HN launch of the source-available router on 2026-06-26, leading
with the on-box embedder routing approach and the 40-70% inference cost cut.

## Angle split (so copy surfaces don't collide)

- **Video / scene copy:** the mechanism. One door, every model, the embedder
  decides on your box in under 50ms, 40-70% off the bill.
- **X caption:** the momentum. Topped Show HN, who Andrew is, the one-line pitch.
- **Gmail Why-this-one:** the person and the discipline. Employee #1 at Causal,
  YC W25, honest "40% and no quality drop" framing, keys stay local.
