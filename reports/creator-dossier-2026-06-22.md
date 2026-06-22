# Creator dossier — 2026-06-22

## Subject
- **Name:** Raiyan Yahya
- **X handle:** [@raiyan_yahya](https://x.com/raiyan_yahya)
- **GitHub:** [raiyanyahya](https://github.com/raiyanyahya)
- **Site:** https://raiyanyahya.com
- **Geography:** Sweden (shareable)
- **One-line bio:** Solo developer who builds small, sharp developer tools and LLM teaching material. GitHub bio: "Developer. I am very passionate about building things."

## Project
- **Name:** Recall
- **URL:** https://github.com/raiyanyahya/recall
- **What it is:** A fully-local project-memory plugin for Claude Code. It auto-captures each session into an append-only `history.md`, then regenerates a compact `context.md` digest that the next session resumes from. Solves the "cold-start problem" of re-explaining a project every session.
- **The novel move:** The summarizer is entirely on-device and deterministic. It vectorizes session sentences with TF-IDF, builds a cosine-similarity graph, and runs TextRank (PageRank-style power iteration) to keep the most central sentences. No API call, no API key, no third-party model, no network. If numpy is importable it accelerates the math; otherwise an identical pure-Python path runs. Summary generation costs zero model tokens; a resume costs ~1-2K tokens for the compact digest instead of replaying a full transcript.
- **Security posture (a quieter detail):** A redaction pass strips common secret shapes (API keys, tokens, `.env` assignments, PEM keys) before anything hits disk. Git integration is hardened against code execution from a malicious `.git/config`, and `output_dir` is confined to the project root (no `../..` traversal). Shared `context.md` is treated as untrusted input and fenced.

## Metric that's trending
- **Stars:** ~190+ and climbing, off a single launch.
- **Signal:** Front-paged Hacker News on 2026-06-21 ("Show HN: Recall — Local project memory for Claude Code", 110+ points).
- **Release cadence:** v0.3.4 shipped 2026-06-21 (same day as the HN post). Repo active, CI/CD enabled.

## Prior work (for the Why-this-one angle)
- **how-to-train-your-gpt** — ~2.3k stars. A fully-annotated notebook that builds a modern LLM line by line with simplified explanations. His calling card and the source of the "teacherly rigor" angle.
- **freshenv** (~176 stars) — provisioning and managing developer environments across local and cloud.
- **prompt** (~105 stars) — Python CLI for the ChatGPT API.
- **zapq** (~40 stars) — Go in-RAM FIFO message queue microservice.
- **kit** (~37 stars) — JS app centering AI across editor, browser, mail, terminal, agent.

## Voice notes
- Plain, build-in-public, unhyped. Ships small tools that do one thing. README leans practical and precise about guarantees ("best-effort, not a guarantee" on redaction) rather than salesy. The tribute copy should mirror that: specifics over adjectives, the contrast carries the praise.

## Angles to split across surfaces
- **X caption (growth metric + positioning):** trending on HN, local memory for Claude Code, zero-token deterministic digest.
- **Why-this-one (different angle):** his teaching-first prior work (how-to-train-your-gpt) and the security hardening (secret redaction, poisoned git-config defense), solo in Sweden.
- **Video (show, don't tell):** the zero-token receipt, the `recall save` terminal, the session-to-digest flow, the no-cloud thesis.
