# Creator Dossier — 2026-06-02

## Project
- **Name:** Scrapling
- **Repo:** https://github.com/D4Vinci/Scrapling
- **One-liner:** An adaptive web-scraping framework that relocates your elements automatically when a site's HTML changes, so scrapers survive redesigns instead of breaking.
- **Lane fit:** agent tooling / web interaction. Ships a built-in MCP server, so it plugs straight into LLM agent stacks that need to read and act on the live web.

## Creator
- **Name:** Karim Shoair
- **X handle:** @D4Vinci1 (https://x.com/D4Vinci1)
- **GitHub:** https://github.com/D4Vinci (handle `D4Vinci`)
- **Project account:** @Scrapling_dev
- **Geography:** Egypt (shareable — listed publicly on his profiles).
- **One-line bio:** Pythonista with 10+ years building, a CS degree, and seven years in ethical hacking before pivoting hard into web scraping and automation. Top-rated-plus freelancer, prolific open-source author.

## Voice notes
- Engineer-first, security-brain. Talks about keeping scrapers *alive* as the web changes, not just standing them up.
- Frames the problem as maintenance pain ("how do you keep it alive as the web changes") rather than novelty for its own sake.
- Build-in-public cadence: ships fast, documents thoroughly (multi-language READMEs, readthedocs), runs a Discord, takes sponsorships.

## Prior work
- Background in ethical-hacking tooling and Python security frameworks; wrote articles for tech outlets and a Python ethical-hacking course.
- Pivoted to scraping/automation over the last couple of years; Scrapling is the flagship.

## What he cares about
- Durability of scrapers against site churn (the core thesis of Scrapling).
- Speed and a unified API — single request up through full concurrent crawls.
- Real anti-bot handling (Cloudflare Turnstile bypass), checkpointed pause/resume crawling.
- Meeting AI agents where they are: an MCP server so agents can scrape natively.

## Latest release / momentum
- **Latest release:** v0.4.8, May 11, 2026.
- **Stars:** ~58.5k total.
- **Star velocity:** +1,486 in the last 24h — still climbing, not saturated. This is the trending metric.

## The metric that's trending
- **Star velocity (+1,486/day on 58.5k).** Use for the X caption's growth lead.

## Verified technical claims (for the Critic)
- **Adaptive relocation ("smart element tracking"):** pass `adaptive=True`; when a page's structure changes, Scrapling re-finds the saved element via similarity algorithms instead of a rigid selector. Source: README + readthedocs + third-party coverage (cloudnews.tech, thewebscraping.club).
- **Relocation speed:** ~2.39 ms vs AutoScraper's ~12.45 ms finding a similar element after a structural change — ~5x faster. Source: README benchmarks.
- **Parsing speed:** text extraction ~2 ms (on par with Parsel/Scrapy); outperforms BeautifulSoup variants by ~750–1600x. Source: README benchmarks.
- **MCP server** for AI integration, Cloudflare Turnstile bypass, checkpointed pause/resume crawling. Source: README.

## Angle split (so surfaces don't repeat)
- **X caption →** star velocity (the growth metric).
- **Why-this-one →** the maintenance thesis + creator's security-to-scraping arc, the MCP-server angle.
- **Scenes →** the adaptive-relocation mechanism (diagram), the 1600x parsing stat (big_number), the self-healing thesis (fix/close). Qualitative, no star number.
