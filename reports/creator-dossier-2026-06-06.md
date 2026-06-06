# Creator Dossier — 2026-06-06

## Project
- **Name:** last30days-skill (`/last30days`)
- **Repo:** https://github.com/mvanhorn/last30days-skill
- **One-liner:** An agent skill that researches any topic across Reddit, X, YouTube, TikTok, Hacker News, Polymarket, GitHub, and the web from the last 30 days, then synthesizes one grounded, cited brief ranked by what people actually engage with.

## Creator
- **Name:** Matt Van Horn
- **X handle:** @mvanhorn (verified via his own post URL `x.com/mvanhorn/...`)
- **GitHub:** https://github.com/mvanhorn (2.2k followers, 1.2k repos)
- **LinkedIn:** in/mattvanhorn
- **One-line bio:** "Co-founded June ('self-driving oven,' acquired by Weber) and the company that became Lyft. Building again, more soon."

## Voice notes
- Operator-founder, ships fast and talks plainly. Build-in-public, distribution-savvy (he posts the install one-liner directly: "Tell your bot: install the last30days skill").
- Frames the tool as plumbing for agents, not a chatbot. Peer-to-peer engineering register, not marketing hype.

## Prior work
- **June** — the "self-driving oven," acquired by Weber. Consumer hardware + computer vision.
- Co-founded the company that became **Lyft** (very early).
- **Printing Press** (~4.2k stars) — generates production-ready CLIs for APIs, agent-first design.
- **Printing Press Library** — official collection of community CLIs.
- **agentcookie** — syncs agent browser sessions to a Mac, encrypted over Tailscale.

## What he cares about
- Agents that can actually reach the live internet and act on it.
- Grounding answers in primary sources (real posts, real engagement) instead of SEO-optimized web pages.
- Low-friction distribution: one message installs the skill; works across Claude Code, Codex CLI, and Gemini CLI.

## Geography
- Not publicly specified on the profile. Not used in copy.

## Latest commit / release
- Launched ~March 20-25, 2026; hit #1 on GitHub Trending almost immediately.
- v3.3.0 released 2026-05-17. 621 commits on `main`.

## Trending metric (feeds the X caption)
- ~28.4k stars total, gaining ~731 stars/day, still on the GitHub daily trending board (live momentum, not saturated).

## The novel angle (feeds the Why-this-one and the video)
- Treats social platforms as primary sources of truth and resolves entities (people, products, companies) into their real communities before searching.
- Two-phase parallel search with multi-signal scoring: text relevance, engagement velocity, source authority, cross-platform convergence, temporal recency.
- **Cross-platform convergence detection:** when the same story is hot on Reddit AND HN AND X at once, that overlap is flagged as a high-confidence signal.
- An AI-judge synthesis step merges duplicate clusters and writes a brief with inline citations. No API keys required for Reddit, HN, Polymarket, or GitHub.

## Technical claims to keep accurate (re-verified against README/search)
- Platforms covered: Reddit, X, YouTube, TikTok, Hacker News, Polymarket, GitHub, and the web (Bluesky/Instagram via optional keys).
- Ranking is engagement-weighted (upvotes, likes, view counts, prediction-market odds), not editorial/SEO ranking.
- Output is a single synthesized brief with real citations; optional shareable HTML brief.
- Compatible with Claude Code, Codex CLI, and Gemini CLI.
