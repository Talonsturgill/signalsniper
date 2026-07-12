# Creator dossier — 2026-07-12

## Subject
- **Name:** Michael Neale
- **X handle:** **@michaelneale** (https://x.com/michaelneale) — VERIFIED high confidence. His personal site michaelneale.net links the same handle alongside github.com/michaelneale (which owns mesh-llm) and linkedin.com/in/michaelneale.
- **LinkedIn:** https://au.linkedin.com/in/michaelneale — VERIFIED. `linkedin_tag = {name: "Michael Neale", url: "https://au.linkedin.com/in/michaelneale"}`
- **GitHub:** github.com/michaelneale · **Site:** michaelneale.net
- **Geography:** Blue Mountains, Australia (public on his GitHub profile — shareable).

## One-line bio
Australian engineer and serial open-source builder. Co-founder/Chief Scientist of CloudBees, now Principal Engineer at Block on the open-source **goose** AI agent, and the builder behind **Mesh LLM** — peer-to-peer, distributed LLM inference "for the people."

## Voice notes
Dry, self-deprecating, engineer-to-engineer. Frames big projects modestly ("pretty early-stage", "happy to answer questions"). Understated and practical, not hypey. Signature line from his own site: *"I once said that Mosaic was rubbish, and the graphical web would never take off. Sometimes I am mistaken."*

## Prior work
- Co-founded **CloudBees** (Chief Scientist).
- Helped start the **Drools** rule engine; **JBoss → Red Hat**; **deltacloud** (cross-cloud API).
- At **Block**, co-creator/maintainer of **goose** (Block's open-source AI agent). Also authored goose-perception, mcp-stress-test.

## What he cares about
Decentralization and peer-to-peer compute, open source, self-hosted / local AI, privacy. Mesh LLM's own tagline captures it: *"Distributed AI/LLM for the people. Share compute privately or publicly to power your agents and chat."* Pool GPUs and laptops so people can run models they could never self-host alone.

## The project (Mesh LLM)
- **What it is:** pools GPUs and memory across machines and exposes the result as ONE OpenAI-compatible API (default port 9337). Built on **iroh** (P2P, NAT traversal) + llama.cpp. Rust, Apache-2.0.
- **The move:** the **skippy** runtime stage-splits a model's layers across machines when it won't fit on one; single-machine fit is tried first, then it spills to peers. Plugs straight into Claude Code, goose, opencode, pi.
- **Latest release:** v0.72.2, 2026-07-01 (123 releases — very active).

## Trending metric
- GitHub **~1.3k stars** (API 1,341), 158 forks, as of 2026-07-12.
- HN front page: **228 points / 51 comments** — "Mesh LLM: distributed AI computing on iroh" (2026-07-11), https://news.ycombinator.com/item?id=48876505.

## Notes on collaborators
Primary individual builder = Michael Neale (owns the repo). Named collaborators exist: the "skippy" splitting engine was authored by a contributor posting as "i386" (real name unconfirmed); the HN story was submitted by user "tionis"; the iroh-side writeup was by Rae McKelvey of n0/iroh. Tribute subject is Neale.
