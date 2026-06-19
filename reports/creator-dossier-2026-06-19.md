# Creator dossier — Ollama — 2026-06-19

## Identity
- **Project:** Ollama (`github.com/ollama/ollama`)
- **Org / maker handle (tag on X):** `@ollama`
- **Founder / lead:** Jeffrey Morgan, CEO and co-founder — personal X `@jmorgan`
- **One-line bio:** The team that made running open models locally a one-line install. Founder is ex-Docker / Twitter / Google, based in Palo Alto.
- **Geography:** Palo Alto, CA (shareable).

## What it is
Ollama is the local runtime for open models. `curl | sh`, then `ollama run <model>` and a frontier-class open model is answering on your own machine, no API key, no data leaving the laptop. The whole product is a CLI plus a tiny daemon, and the marketing surface is deliberately a Markdown-README aesthetic — paper white, one black pill, a terminal mockup, a hand-drawn llama.

## The trending move (last 24-48h)
- **Release v0.30.10 (June 17, 2026):** Command A and the North model family now run on Apple Silicon through Ollama's **MLX engine**, with the underlying llama.cpp engine updated alongside.
- This sits on top of the larger arc: since the March 2026 MLX preview, Ollama on Apple Silicon is built on Apple's MLX framework and unified-memory architecture, roughly **doubling decode speed (~58 to ~112 tokens/sec)** on qualifying M-series hardware, and using the M5 GPU Neural Accelerators for faster time-to-first-token.
- `ollama launch` now drives agentic apps (Claude Code and other coding tools, long-running agent workflows via models like Nemotron 3 Ultra) against a fully local backend.

## The metric that's trending
- **174,000 GitHub stars** on `ollama/ollama` — one of the most-starred AI projects, still climbing.
- Star velocity remains high off the back of the MLX speedups and local-agent story.

## Voice notes (for caption tone)
- Understated, documentation-first, no hype. Lets the install command and the speed numbers do the talking.
- The honest peer-to-peer angle: this is infrastructure that gives builders back control — the model runs where you do, the data stays put.

## Why this one (the different angle the Gmail uses)
The caption leads with reach (stars) and the local-inference thesis. The Why-this-one covers the build discipline instead: a founder who carried the Docker-Desktop "make hard infra a one-liner" instinct into local AI, and a project whose entire brand is restraint — the README is the marketing.

## Lane fit
Local / secure AI deployment and builder-tier infrastructure. Agentic via `ollama launch`. Squarely in the lane.

## Anti-repeat note
`ollama/ollama` does not appear in the last 14 days of `reports/style-history.json`. The `ollama` brand pack has not shipped before. Today uses a creator brand pack (not a preset) because all 8 preset packs fall inside the 14-day cooldown window — the lane-aligned default when presets are exhausted.
