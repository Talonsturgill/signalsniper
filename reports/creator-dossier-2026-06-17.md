# Creator Dossier — 2026-06-17

## Project: ctx
- Repo: https://github.com/stevesolun/ctx
- Docs: https://stevesolun.github.io/ctx/
- License: MIT. Language: Python. Created 2026-04-08, last pushed 2026-06-16 (actively shipping).
- Install: `pip install claude-ctx` then `ctx-init`.

## Creator
- **Name:** Steve Solun
- **X handle:** @SteveSolun (joined October 2019). NOTE: not linked from his GitHub profile (GitHub `twitter_username` is null; his GitHub links LinkedIn only). The handle is inferred with high confidence from an exact distinctive-name match, an AI/data-science bio and 2019 vintage consistent with his professional profile, and the account co-surfacing with his ctx project in search. The user should eyeball it once before posting.
- **LinkedIn:** https://www.linkedin.com/in/solunsteve/
- **GitHub:** stevesolun (34 followers).
- **Bio / one-liner:** Applied-AI leader, 10+ years across AI, data science, and analytics. Describes himself as a "fast learner data scientist and enthusiastic researcher."
- **Track record:** VP Data Science & AI (Kubiya.ai per public org charts); previously Chief Data Scientist at Velotix (data-access governance); earlier roles incl. Bank Leumi and the IDF Cybersecurity Unit. The data-governance + security background reads straight through into ctx: someone who has spent a career on "who gets to load what" now applies that discipline to an agent's context window.
- **Other repos:** CV_Boutique_Agency (18 stars), micro-skills (9), Chameleon (3).

## What ctx is
A recommendation engine for agent context. It watches what you are building, walks a **102,928-node** "LLM-wiki" graph (2.9M edges), and recommends a small, top-scored bundle of skills, agents, and MCP servers for the current task. You approve, it installs. You stop using something, it unloads.

The graph indexes:
- **91,464** skill entity pages (89,465 hydrated, installable SKILL.md files)
- **467** agents
- **10,790** MCP servers
- **207** harnesses (local / API model runs)

## The problem it attacks
1. **Discovery** — nobody can hand-pick from 91k skills + 10k MCP servers.
2. **Context budgeting** — loading everything wastes tokens and degrades quality. Load the 10-to-15 that matter.
3. **Skill rot** — stale, unused skills clutter the context and get scored out.

## The novel angle (for Why-this-one)
The inversion. The whole ecosystem is racing to add more skills, more agents, more MCP servers to an agent's environment. ctx goes the other way: it treats the entire tool inventory as a scored knowledge graph and loads only the minimal relevant subset for the task in front of you. Selective context loading, not another catalog.

## The trending metric (for the caption)
- **509 stars** (62 forks, 803 commits, 26 releases). Created early April, climbing.
- Second-order signal: ctx is generating *inbound* integration requests from other ecosystem projects (open issues referencing ctx on vercel-labs/skills #1009, addyosmani/agent-skills, affaan-m/ECC #2112). Other tool catalogs want to plug into it.

## Voice notes
Build-in-public, measured, technical. He ships releases steadily (26 of them) and writes precise README claims with exact counts. The tribute should match: specifics over adjectives, the contrast carries the praise, no superlatives.

## Lane fit
Squarely in agent tooling / context engineering / MCP infrastructure. A builder-tier individual, novel approach, reachable creator. Clean fit.

## Field note (2026-06-17)
Thin cycle for verified-handle candidates. GitHub trending skewed to non-lane repos (TTS, freeCodeCamp) and HF trending was all frontier-lab model dumps. Strong in-lane near-misses (Centri, SigmaShake, Kintsugi) were dropped for having no findable X handle. ctx was the clear standout on novelty + momentum + a confirmable creator, so the routine proceeded on it rather than skipping.
