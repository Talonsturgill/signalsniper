# Source List · This Week in AI · Issue 5 (May 31 to June 6, 2026)

Fact-check source map. One bullet per claim with its primary-source URL, grouped by project.
Compiled 2026-06-06. Live counts confirmed against `weekly-livedata-2026-05-31.json` (pulled 2026-06-06).

## headroom (@chopra_tejas)

- Crossed GitHub daily trending at #2 on June 1; +3,000 stars in a day — sourced research `weekly-research-2026-05-31.json` (momentum_delta: peak +3,150 on 2026-06-01 at HN/press spike, ranked #2 on GitHub daily trending). Trending board is ephemeral and not re-snapshottable on 2026-06-06.
- ~15,000 stars now (livedata 15,045) — https://github.com/chopratejas/headroom (repo header shows 15.1k) + livedata.
- Climbed from ~11,000 to ~15,000 stars; "+4,045 in 2 days" — livedata (15,045) minus research baseline (11,000) = 4,045. Arithmetic-consistent delta.
- 60-95% reduction — https://github.com/chopratejas/headroom (README subtitle: "60-95% fewer tokens").
- Code-search 17,765 -> 1,408 tokens — https://github.com/chopratejas/headroom (README benchmark, ~92% reduction).
- GSM8K accuracy 0.870 baseline held — https://github.com/chopratejas/headroom (README benchmark, 0.870 maintained).
- Six compressors — https://github.com/chopratejas/headroom (README "6 algorithms": SmartCrusher, CodeCompressor, Kompress-base, CacheAligner, IntelligentContext, CCR).
- Reversible compression (CCR), originals on disk, retrievable on demand — https://github.com/chopratejas/headroom (README "CCR - reversible compression"; "originals never deleted; LLM retrieves on demand").
- v0.23 released June 4 with GitHub Copilot mode — https://github.com/chopratejas/headroom/releases (v0.23.0, 2026-06-04, GitHub Copilot subscription mode).
- Library, proxy, MCP server (drops into a stack three ways) — https://github.com/chopratejas/headroom (repo description: "Library, proxy, MCP server").
- Tejas Chopra is a Netflix storage engineer (petabyte-scale) — https://www.linkedin.com/in/chopratejas/ ; https://www.theregister.com/ai-ml/2026/05/31/netflix-wiz-creates-app-to-slash-ai-bills-then-open-sources-it/ (Senior Software Engineer, Data Storage Platform, Netflix; prior petabyte storage at Box).
- ~$700,000 saved — https://www.theregister.com/ai-ml/2026/05/31/netflix-wiz-creates-app-to-slash-ai-bills-then-open-sources-it/ (figure stated by Chopra at Open Source Summit; ~$700K saved, ~200B tokens). Post now attributes the figure to Chopra (his Open Source Summit talk and press coverage), which is the correct source. Resolved.
- Quote "Remember, a model is no longer a moat!" attributed to @chopra_tejas — https://x.com/chopra_tejas/status/2031543876633383055 (X URL returns HTTP 402, not directly fetchable). Verbatim substring confirmed against sourced research creator_quote: "Remember, a model is no longer a moat! Headroom OSS works with LLMLingua-2, but you know what's coming? Our own OSS model, specific for agentic compression." Attribution and "next sentence promised an open model" both consistent.
- Apache-2.0 license, Python — https://github.com/chopratejas/headroom + livedata.

## FastMCP (@jlowin)

- ~25,500 stars — https://github.com/jlowin/fastmcp (repo header 25.5k stars).
- v3.4 release this week (June 2), bridges stdio-only hosts to remote HTTP/SSE servers with OAuth — https://github.com/jlowin/fastmcp/releases (v3.4.0 Remote Control 2026-06-02; latest v3.4.2 2026-06-06) ; https://gofastmcp.com/updates.
- Folded original FastMCP into the official MCP SDK — https://github.com/jlowin/fastmcp (docs: "FastMCP 1.0 was incorporated into the official MCP Python SDK in 2024").
- @jlowin is Jeremiah Lowin, Prefect founder — https://github.com/jlowin ; https://www.linkedin.com/in/jlowin (founder/CEO Prefect, creator of FastMCP). Repo owner org is PrefectHQ.
- Apache-2.0, Python — https://github.com/jlowin/fastmcp.
- One-decorator code snippet — https://github.com/jlowin/fastmcp (README quickstart).

## Scrapling (@D4Vinci1)

- 61,387 stars (livedata) — https://github.com/D4Vinci/Scrapling (header 61.4k) + livedata.
- +2,887 in 4 days — livedata 61,387 minus research baseline 58,500 = 2,887 over 2026-06-02 to 2026-06-06. Arithmetic-consistent delta.
- BSD-3-Clause — https://github.com/D4Vinci/Scrapling + livedata.
- @D4Vinci1 is Karim Shoair — https://github.com/D4Vinci/Scrapling (owner Karim Shoair).
- Built-in MCP server — https://github.com/D4Vinci/Scrapling (README: built-in MCP server for AI-assisted scraping).
- Adaptive element relocation (auto_save fingerprint then adaptive re-find) — https://github.com/D4Vinci/Scrapling (Smart Element Tracking; auto_save=True / adaptive=True).

## boxes.dev (@nbushak)

- 100 HN points on launch (June 4) — https://news.ycombinator.com/item?id=48399358 (Show HN, 100 points, 74 comments).
- ~109 Product Hunt upvotes — sourced research `weekly-research-2026-05-31.json` (launch_metrics product_hunt_upvotes 109, rank #13). Not independently re-confirmable via search on 2026-06-06; consistent with sourced research.
- @nbushak is Nick Bushak, ex-Gem/Facebook — https://www.linkedin.com/in/nbushak/ ; https://www.crunchbase.com/person/nick-bushak (Co-founder/CTO of Gem; ~7 years at Facebook).
- Hosted product, no repo; cloud Linux machine per agent — https://news.ycombinator.com/item?id=48399358 ("first cloud-only agentic dev environment"; run Claude Code / Codex in the cloud).

## last30days-skill (@mvanhorn)

- 28,392 stars (livedata) — https://github.com/mvanhorn/last30days-skill + livedata.
- Velocity cooled to flat (was +731/day) — sourced research `weekly-research-2026-05-31.json` (momentum_delta: tribute-era +731/day cooled to ~flat; 28,400 -> 28,392). Consistent with near-flat live snapshot.
- MIT license, Python — https://github.com/mvanhorn/last30days-skill + livedata.
- @mvanhorn is Matt Van Horn — https://github.com/mvanhorn/last30days-skill (owner).
- Reads Reddit/X/YouTube/HN/Polymarket — https://github.com/mvanhorn/last30days-skill (SKILL.md engagement-scoring hierarchy).

## What I'm watching

- Crawl4AI by @unclecode (LLM-first crawler) — https://github.com/unclecode/crawl4ai.
- Open compression model promised by @chopra_tejas — https://x.com/chopra_tejas/status/2031543876633383055 (402; corroborated by research shipping_next: "OSS model specific for agentic compression").
- FastAPI-MCP by tadata (turns FastAPI app into MCP server) — https://github.com/tadata-org/fastapi_mcp (Tadata Inc.).

## Reading list

- SWE-Pruner arXiv 2601.16746 — https://arxiv.org/abs/2601.16746 ("SWE-Pruner: Self-Adaptive Context Pruning for Coding Agents"). Title verbatim confirmed.
- FastMCP 3.0 HN thread — https://news.ycombinator.com/item?id=46699037 ("FastMCP 3.0: From Tool Servers to Context Applications").
- Coding-agent sandboxes gist — https://gist.github.com/wincent/2752d8d97727577050c043e4ff9e386e (curated landscape; cited in research as boxes.dev reading candidate).
