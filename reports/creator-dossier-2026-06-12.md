# Creator dossier — 2026-06-12

## Who
- **Name:** Francesco Bonacci
- **X handle:** @francedot (project account: @trycua)
- **Project:** cua — open-source infrastructure for Computer-Use Agents
- **Repo:** https://github.com/trycua/cua
- **Site:** https://cua.ai
- **Co-founder:** Alessandro Puppo

## One-line bio
Founder and CEO of Cua (YC X25), building the open-source operator layer that lets AI agents control full desktops. Previously at Xbox and Microsoft AI, where he co-authored Windows Agent Arena.

## What cua is
Open-source infrastructure for agents that drive real computers. cua gives any agent its own sandboxed machine and full desktop control across macOS, Linux, and Windows through one unified SDK. It ships container/VM sandboxes, SDKs, benchmarks, and RL training environments, and the same agent code runs whether the desktop lives in the cloud or on your own laptop. It is the missing piece between an LLM that can reason and a real operating system it can actually operate, without that operating system being your live machine.

## The novel angle
Most computer-use demos either drive your real desktop (dangerous, unrepeatable) or live behind a closed cloud product. cua makes the machine itself a first-class, swappable, sandboxed primitive with one API across operating systems and across cloud-or-local. That cross-OS, cloud-or-local parity, plus built-in benchmarks and RL training environments, is what separates it from a one-off automation script.

## Voice notes (for caption + scenes)
Builder-to-builder, calm and exact. Francesco talks about agents the way someone who has watched them fail on real operating systems talks: concrete, unglamorous, focused on the harness and the environment rather than the model. No hype words. Let the contrast (a real machine, but sandboxed) carry the praise. Cursor's editorial-cream brand with one orange voltage matches this measured-but-confident register.

## Prior work / what he cares about
- Co-authored **Windows Agent Arena** at Microsoft (a benchmark for agents operating a real Windows desktop). Deep domain knowledge of where agents break on real OSes.
- Cares about open infrastructure: open-sourcing the kind of agent harness frontier labs keep private, and shipping it in public through YC.
- Reproducibility and evaluation: sandboxes and benchmarks are core, not afterthoughts.

## Geography
Cua is a YC X25 company; Francesco is based in California, United States. (Shareable, lightly.)

## Trending metric
- **~17.9k GitHub stars** and climbing (call it "just crossed 17k" in the caption — star total, not a version number).
- Fresh release **lume-v0.3.10 on June 8, 2026** (used only as a freshness signal in the dossier/PR, never in the caption — version numbers are banned there).
- 3,492 commits on main; multi-language (Python SDK, Rust, Swift lume virtualization layer).

## Accuracy anchors (verified against repo + abstract of prior work)
- Cross-OS: macOS, Linux, Windows. ✓
- Cloud or local desktops, same SDK. ✓
- Sandboxes / container-VM isolation + RL training environments + benchmarks. ✓
- Founder co-authored Windows Agent Arena at Microsoft; ex-Xbox/Microsoft AI. ✓
- YC X25. ✓
