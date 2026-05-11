# Creator dossier · 2026-05-11

## Subject

- **Name.** Jun Kim
- **GitHub.** [@jundot](https://github.com/jundot)
- **X.** [@jundotkim](https://x.com/jundotkim)
- **Website.** https://omlx.ai
- **Geography.** Seoul, Korea

## Bio (verbatim)

> Data engineer by day, AI dreamer by night. I build the tools I wish existed for my Mac, then open-source them.

The voice is craft, not flex. Solo builder energy. Open-source by default. Quiet, measured posts on X amplified by the MLX community (Ivan Fioravanti, AI Builder Club, bstn).

## Project

**oMLX** — `github.com/jundot/omlx` — an LLM inference server with continuous batching and paged SSD KV caching for Apple Silicon, managed from the macOS menu bar.

### Why it matters

The Apple Silicon local-LLM lane was stuck. mlx-lm worked for demos, but the KV cache wasn't reused across requests. Every prompt redid the full prefill. oMLX fixes the inference layer that everyone else skipped, and ships it as a `.dmg` you drag into Applications.

### The novel technical move

- **Tiered KV cache.** Hot RAM tier plus cold SSD tier in safetensors format. Prefix cache survives server restarts.
- **Continuous batching** via mlx-lm BatchGenerator with per-model concurrency limits.
- **Multi-model serving.** LLMs, vision-language models, embeddings, rerankers all in one EnginePool with LRU eviction and per-model TTL.
- **OpenAI + Anthropic API compatible.** Drop-in replacement at `localhost:8000/v1` and `/v1/messages`.
- **`omlx launch claude`** one-liner to wire Claude Code to local inference.
- **Native MTP** (Multi-Token Prediction) for DeepSeek V4 and Qwen 3.5/3.6 in the latest dev build.

### Momentum

- **13.5k stars**, 1.1k forks.
- Trending Python repo today (+185 stars in 24h).
- v0.3.8 shipped April 30, 2026: async SSD cache writes moved decode-speed recovery from 8.65 to 22.66 tokens per second.
- v0.3.9.dev1 shipped May 6, 2026: DeepSeek V4 SSD cache + native MTP.
- Peer endorsements on X from Ivan Fioravanti (MLX power user), AI Builder Club, bstn (dflash-mlx author who credits oMLX as inspiration).

### Latest commit / release date

- v0.3.9.dev1: May 6, 2026 (five days ago).
- v0.3.8 stable: April 30, 2026.

## Voice notes for the writer

- Build-in-public engineer. Doesn't oversell. Lets the cache stats speak.
- The hook isn't the binary, it's the persistence model. KV cache survives restarts. Prefix cache reconnects. That's the line peers quote.
- Avoid framing this as "another inference server." Frame it as the inference layer Apple Silicon was missing.

## Different-angle hooks (for Why-this-one, not for the tweet)

- Solo Seoul builder shipping at vllm-pace.
- Inspired a parallel project (bstn's dflash-mlx) that explicitly credits the cache design.
- Built around the dev-by-day / hacker-by-night ritual. The README reads like the changelog of someone scratching their own itch.
