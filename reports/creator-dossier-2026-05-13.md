# Creator dossier · 2026-05-13

## Pick

**Needle** by **Henry Ndubuaku** (@hmunachii) under the **Cactus Compute** label.

- Project: https://github.com/cactus-compute/needle
- Latest activity: top of GitHub trending and HN front page (444 points) for the May 12, 2026 cycle
- Stars: ~795 total, +444 HN points in the last 24h putting it at the top of the AI/ML lane
- Repo languages: Python (training), with deployment targets that include Mac/PC and Cactus's mobile engine
- License: open weights and code on Hugging Face under `Cactus-Compute`

## Creator

- Name: Henry Ndubuaku
- Handle (personal X): https://twitter.com/hmunachii
- Org GitHub: https://github.com/cactus-compute
- Founder & CTO: Cactus Compute (YC S25)
- Location: London
- Bio (verbatim from GitHub): "EECS + MS AI + 4x ICLR + YC S25"
- Personal GitHub: https://github.com/HenryNdubuaku

Henry is a research-trained founder. The four ICLR notches are the giveaway: this isn't a wrapper builder, it's someone who runs the experiments and writes the paper. Cactus is the product surface (the on-device inference engine, 4.8k stars). Needle is the research artifact that proves the product's reason to exist.

## Voice notes

- Plainspoken about scale. README says "26m parameter Simple Attention Network" without dressing it up.
- Comfortable naming competitors. Calls out FunctionGemma-270m, Qwen-0.6B, Granite-350m, LFM2.5-350m by name, and notes the trade ("they're better at conversation, we're better at single-shot function call").
- Architectural honesty. The Simple Attention Network is literally "no feedforward networks, only attention." That's a research bet, not a marketing claim.
- Builds in public via the Hugging Face org page and direct GitHub releases. No press cycle, no thread of teasers.

## Prior work

- Cactus (4.8k stars). The low-latency mobile inference engine. The reason Needle can target watches and glasses, not just phones.
- Maths-CS-AI Compendium (3.7k stars). A curriculum repo. Signals the educator instinct.
- 4x ICLR papers (per the GitHub bio). Quantization, mobile optimization, efficient architectures.
- YC S25 batch graduate.

## What he cares about

- On-device AI that's actually on-device. Not "small model" as a marketing fig leaf for a 7B parameter fine-tune. 26 million parameters, designed to run on a watch.
- Function calling as the unlock. The bet is that the agent use case for tiny AI is "talk to your apps," not "write me a sonnet." Function calling, JSON discipline, and tool selection are the only capabilities that matter at this size.
- Hardware-aware design. The model architecture (no FFN, only attention) was picked because attention compiles down to a handful of GEMMs that mobile NPUs already love.
- Distillation over training-from-scratch. He distilled from Gemini 3.1, not pretrained from raw text. Cost discipline.

## The metric that's trending

- Hacker News position: #5 on the front page, 444 points, top AI/ML story of the day.
- GitHub star velocity: the repo crossed 795 stars from a standing start. Most of that traffic came in the 18 hours after the HN submission landed.
- The headline number people remember: **26M**. Distilled from a frontier model, tuned for a single capability, sized to run on a watch.

## What's different about Needle vs the rest of the lane

- **Distillation target is a real frontier model.** Gemini 3.1, not a synthetic dataset, not a smaller open-weight teacher.
- **Architecture is a research bet, not a config tweak.** Simple Attention Network strips out FFN layers entirely. That's a structural decision, not hyperparameter tuning.
- **The deployment surface is a watch.** Not "edge-friendly," not "quantized for mobile" — the explicit promise is glasses and watches.
- **Single-capability scoping.** The model is bad at conversation and the README says so. The win is single-shot function call accuracy at 26M parameters.

## Tribute angle

Henry made a research bet most people won't make: that the future of on-device AI isn't a smaller chat model, it's a tiny specialist that calls tools well. The video should honor the size collapse (26M parameters distilled from a frontier model) and the architectural minimalism (no feedforward layers, only attention). MANIFESTO framework reads well here because the project itself is a position — a stake in the ground for tiny-specialist over general-small.

## X caption growth metric (per writing-rules)

Lead with HN momentum. "Top of HN today" or "just hit the HN front page" beats "v0.x dropped" by a mile. Project just crossed 795 stars. Avoid the version number entirely.

## Sources

- https://github.com/cactus-compute/needle
- https://github.com/cactus-compute/needle/blob/main/docs/simple_attention_networks.md
- https://github.com/HenryNdubuaku
- https://twitter.com/hmunachii
- https://huggingface.co/Cactus-Compute
- https://www.ycombinator.com/companies/cactus
- https://news.ycombinator.com/from?site=github.com/cactus-compute (HN submission, 444 points)
