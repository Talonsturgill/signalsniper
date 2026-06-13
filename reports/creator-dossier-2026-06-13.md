# Creator Dossier — 2026-06-13

## Subject
- **Name:** Dan McInerney
- **X handle:** [@DanHMcInerney](https://x.com/danhmcinerney)
- **GitHub:** [DanMcInerney](https://github.com/DanMcInerney)
- **Project:** [architect-loop](https://github.com/DanMcInerney/architect-loop)

## One-line bio
Lead AI threat researcher at Protect AI (now part of Palo Alto Networks), 15 years of red-team work, top-ranked Python developer on GitHub, credited with seven CVEs in AI tooling.

## What architect-loop is
A Claude Code skill that runs a **cross-vendor agent loop**: Claude Fable 5 acts as the architect (writes specs and acceptance gates, reviews evidence), GPT-5.5 Codex acts as the builder (writes the actual code), and the git repo itself is the shared memory.

The discipline is the novelty:
- Specs and acceptance **gates are written and committed before any builder starts**.
- The architect dispatches **parallel isolated builders in separate git worktrees** ("one fresh codex exec per lane").
- The architect **runs the gate commands itself** and only commits/merges lanes that pass.
- A second mode (`/architect-research`) fans out 3-6 topic-specific research lanes under token budgets, then the architect verifies findings before writing reports.

The thesis: neither model fully trusts the other, so evidence (passing gates, committed artifacts) is the only thing that moves work forward. It is adversarial collaboration between two rival labs' models, refereed by the file system.

## Why it sits in the lane
Agentic patterns, adversarial/critic agent loops, cross-vendor orchestration, builder-tier infrastructure, gates-as-guardrails. This is exactly the secure-by-construction agent tooling the lane is about, and it comes from a security researcher whose day job is breaking AI systems.

## Voice notes (for caption register)
- His X voice: terse, technical, dry. Python, hacking, AI, MMA data.
- He frames things in terms of evidence and verification, not hype. The tribute should mirror that: show the loop, let the discipline carry the praise. No superlatives.

## Prior work / what he cares about
- Lead threat researcher at Protect AI; offensive security on emerging tech (3D printing, ML pipelines).
- Seven CVEs in AI tools; SANS instructor; bylines at Dark Reading and SecurityWeek ("puzzle-driven hacking").
- Cares about: verifiable security, reproducibility, models that check each other rather than a single trusted oracle.

## Geography
US-based (red-team / Protect AI). Not emphasizing in copy.

## Trending metric
- **Latest commit: June 13, 2026** (today). v2.3 shipped June 12-13 with scout-first designed research lanes and per-skill flow diagrams.
- **On the Hacker News front page right now** (Show-HN-style post, climbing). 255 GitHub stars on a 23-commit repo, fresh velocity.
- Metric to lead the caption: **trending now / just hit the Hacker News front page** (no version number per rules).

## Angle split (so caption and Why-this-one do not overlap)
- **Caption angle:** the mechanism — Fable plans/reviews, Codex builds in throwaway branches, neither trusts the other.
- **Why-this-one angle:** the creator — a security researcher with seven AI CVEs making two rival models referee each other, still hardening it daily.
