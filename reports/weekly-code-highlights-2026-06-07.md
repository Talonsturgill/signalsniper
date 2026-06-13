# Code from the week — Issue 6

Install taste-skill into any of eight coding agents.

```bash
npx skills add Leonxlnx/taste-skill
```

Agent-Reach probes every channel and prints the active backend before it runs.

```bash
$ agent-reach doctor

Agent Reach Status
========================================
Ready to use:
  GitHub repos and code -- public repos readable and searchable
  YouTube video subtitles -- yt-dlp
  RSS/Atom feeds -- feedparser
  Web pages (any URL) -- Jina Reader API
```

fast-agent composes an MCP-backed agent into a chain workflow.

```python
@fast.agent(
    "url_fetcher",
    instruction="Given a URL, provide a complete and comprehensive summary",
    servers=["fetch"],
)
@fast.chain(
    name="post_writer",
    sequence=["url_fetcher", "social_media"],
    default=True,
)
```

agentsview reports cost straight from its local index.

```bash
agentsview usage daily --breakdown
agentsview usage daily --agent claude --since 2026-04-01
```

cua runs one agent loop over a swappable, ephemeral sandbox.

```python
import asyncio
from cua import Sandbox, Image, ComputerAgent

async def main():
    async with Sandbox.ephemeral(Image.linux()) as sb:
        agent = ComputerAgent(model="cua/anthropic/claude-sonnet-4.5", tools=[sb])
        async for result in agent.run([{"role": "user", "content": "Take a screenshot"}]):
            print(result)

asyncio.run(main())
```
