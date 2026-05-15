# Code Highlights — Week of May 9, 2026

## skills by @mattpocockuk

```bash
# Install the full loop in one command
npx skills@latest add mattpocock/skills

# The composition sequence — each feeds the next
# grill-me      → set intent before the session
# tdd           → inner development loop
# diagnose      → triage errors without losing context
# zoom-out      → reframe when the agent is stuck
# improve-codebase-architecture → audit entropy on a longer horizon
```

Source: https://github.com/mattpocock/skills

---

## react-doctor by @aidenybai

```bash
# Install as a coding-agent skill (works in Claude Code, Cursor, 50+ agents)
npx react-doctor@latest install
# Writes SKILL.md, AGENTS.md, .cursorrules to the repo root

# Scan a codebase — outputs 0-100 health score across 47 rules
npx react-doctor@latest scan ./src

# Wire into CI with inline PR annotations
npx react-doctor@latest scan ./src --annotations
# Emits ::error:: and ::warning:: for GitHub Actions
```

Source: https://github.com/millionco/react-doctor

---

## hermes-agent by @Teknium

```bash
# Install
npm install -g hermes-agent

# Start (CLI mode, any of 200+ providers)
hermes-agent --provider openrouter --model hermes-4

# v0.13.0 Hermes Curator: synthesizes skills from completed runs
# Skills persist to ~/.hermes/skills/ — the agent compounds its capabilities
hermes acp --setup-browser   # bootstraps browser tools for registry installs

# YOLO mode (autonomous, no confirmations)
hermes-agent --yolo
```

Source: https://github.com/NousResearch/hermes-agent

---

## needle by @hmunachii (Cactus Compute)

```python
# 26M parameter Simple Attention Network — no feedforward layers, only attention
# Distilled from Gemini 3.1 for single-shot function calling on wearable hardware

from cactus import load_model

model = load_model("Cactus-Compute/needle-26m")

# Single-shot function call — the only task this model is designed for
result = model.function_call(
    tools=tools,       # JSON tool schema
    prompt=user_query  # natural language
)
# Output: {"tool": "get_weather", "args": {"city": "London"}}
```

Source: https://github.com/cactus-compute/needle

---

## openhuman by @senamakel

```bash
# The subconscious loop: agent re-reads its own memory tree between requests
# Memory persists as Obsidian-compatible markdown — grep-able, human-readable

# Install
npm install -g openhuman

# Memory tree location (SQLite-backed, mirrors to markdown)
ls ~/.openhuman/memory/
# topics/  summaries/  rules/  sessions/

# The loop runs in the background automatically
# TokenJuice compresses tool outputs before they hit any paid API endpoint
# (up to 80% token reduction on large tool responses)
```

Source: https://github.com/tinyhumansai/openhuman
