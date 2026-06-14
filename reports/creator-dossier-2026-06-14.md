# Creator Dossier — 2026-06-14

## Project
- **Name:** LMCache
- **Repo:** https://github.com/LMCache/LMCache
- **One-liner:** Open-source KV cache layer that stores and reuses LLM key-value caches across queries and serving engines, so warm caches get pulled from a shared tier instead of recomputed on the GPU every request.
- **Latest release:** v0.4.7 (June 13, 2026)
- **Trending metric:** ~9,000 GitHub stars, still climbing (~+238/day on GitHub trending). 220+ contributors from 30+ industry partners. 1.3k forks, 46 releases.

## Creator
- **Name:** Yihua Cheng
- **X handle:** @ChengYihuaA
- **Role:** Co-founder and CTO of Tensormesh; lead author of the LMCache paper; researcher out of the University of Chicago.
- **Team:** Co-built with Yuhan Liu (5th-year PhD, UChicago), Jiayi Yao, and the UChicago systems group. Project account: @lmcache.
- **One-line bio:** Systems researcher who turned a UChicago KV-cache project into the open-source cache layer that vLLM, TGI and NVIDIA Dynamo lean on.

## What they care about
- KV cache as first-class, engine-independent infrastructure — not a throwaway recomputed per request.
- Open source as the substrate. The June 2, 2026 blog "A New Chapter for LMCache and the KV Cache Community" reaffirms the open-source commitment even as Tensormesh raised ($4.5M seed + $20M round, backers include AMD, NVIDIA, CoreWeave).
- Performance on the workloads that actually hurt: long context, multi-round chats, RAG with repeated document reads.

## Prior work / context
- LMCache paper: "An Efficient KV Cache Layer for Enterprise-Scale LLM Inference" (arXiv:2510.09665). MLSys 2026 invited talk.
- Founded ~1 year ago at UChicago; now broadly adopted and integrated into mainstream serving stacks (vLLM V1 P/D disaggregation + NIXL support, NVIDIA Dynamo, KServe, TGI).

## Geography
- University of Chicago roots; Tensormesh (US). Shareable.

## The technical move (feeds Why-this-one)
- Treats KV cache as a shared "Knowledge Delivery Network (KDN)." Engine-independent daemon persists caches across tiers (CPU RAM, local disk, Redis, cloud object storage) and reuses non-prefix chunks via CacheBlend, so any serving engine can pull a warm cache.

## Headline numbers (feeds the big_number scenes; all project/paper claims)
- **Up to 8x faster** time-to-first-token and **8x lower cost** (lmcache.ai).
- **Up to 15x throughput** on multi-round and document-based (RAG) workloads (paper/site).
- Prompt caching 8-10x faster response; RAG 4-10x faster response.

## Caption angle
- Growth metric lead: just crossed ~9k GitHub stars, still climbing.
- Novel claim: the first open-source KV cache delivery network — cache reuse across engines, not just prefix reuse within one.

## Why-this-one angle (distinct from caption)
- Creator history + adoption: academic systems project a year ago, now 220 contributors from 30+ companies with AMD/NVIDIA/CoreWeave backing. The cache layer the ecosystem is standardizing on.
