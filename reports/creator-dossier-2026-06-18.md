# Creator Dossier — 2026-06-18

## Subject
**Alex L. Zhang** — researcher, MIT CSAIL (OASYS lab).

- **X handle:** [@a1zhang](https://x.com/a1zhang) (verified against his own GitHub profile and personal blog footer; display name "alex zhang").
- **Project:** RLM — Recursive Language Models. `alexzhang13/rlm`.
- **Project URL:** https://github.com/alexzhang13/rlm
- **Personal site:** https://alexzhang13.github.io

## One-line bio
MIT CSAIL grad student who builds inference-time machinery for language models and ships it as a clean, drop-in library, then asks the community to break it.

## What RLM is (technical, verified)
A **Recursive Language Model** is a thin wrapper around an LM that can spawn recursive LM calls for intermediate computation. The user prompt is placed in a Python variable inside a REPL; the root model programmatically examines, decomposes, and recursively calls itself (or sub-models) over snippets instead of reading the whole document at once. CodeAct-style: the model writes code that launches sub-RLM calls. The API surface is a one-line swap — `llm.completion()` becomes `rlm.completion()`. Result: effectively unbounded context.

## The metric that's trending (verified from his blog)
- **OOLONG @ 132k tokens:** RLM(GPT-5-mini) beats GPT-5 by **over 34 points (~114% increase)** at roughly the **same total API cost**.
- **OOLONG @ 263k tokens:** RLM(GPT-5-mini) beats GPT-5 by over 15 points (~49%) and is cheaper per query on average.
- **BrowseComp-Plus (1000 docs):** RLM(GPT-5) reaches near-perfect performance where base GPT-5 drops off.
- VentureBeat framed it as processing on the order of **10 million tokens** without the usual collapse.

## Momentum
- ~**5,000 stars** on the repo, climbing.
- Launch tweet ~**120k views / 941 reposts**.
- Strongest signal: **independent strangers re-implementing it** (e.g. `grishahq/recursive-llm`, `fullstackwebdev/rlm_repl`). The idea has escaped the author.
- Latest release on the repo: late May 2026 (iPython sandbox support added). [No version numbers go into copy.]

## Prior work / what he cares about
- Inference-time strategies for LMs; long-context behavior; agentic decomposition.
- Paper "Recursive Language Models" (Dec 2025), co-authored with Tim Kraska and Omar Khattab (MIT CSAIL).
- Build-in-public posture: ships rough, invites the community to stress-test, links the blog and code openly.

## Angle split (so copy surfaces do not collide)
- **X caption (growth metric):** lead with the star momentum / "a small model beating a bigger one."
- **Why-this-one (different angle):** the build-in-public discipline and the fact that strangers re-implemented it before he asked.
- **Scene copy (the idea):** the recursion loop and the same-cost inversion.
