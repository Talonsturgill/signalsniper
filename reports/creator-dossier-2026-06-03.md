# Creator dossier — 2026-06-03

## Subject

- **Name:** Jeremiah Lowin
- **X handle:** [@jlowin](https://x.com/jlowin)
- **GitHub:** [jlowin](https://github.com/jlowin)
- **Project:** FastMCP — https://github.com/jlowin/fastmcp
- **One-line bio:** Founder and CEO of Prefect (workflow orchestration) and the creator of FastMCP, the Pythonic framework for building Model Context Protocol servers and clients.

## What the project is

FastMCP is the high-level Python framework for the Model Context Protocol. You
decorate an ordinary Python function with `@mcp.tool` and FastMCP turns it into
a fully-formed MCP server, handling the protocol's schema generation, transport,
and message plumbing for you. The pitch is collapse-the-boilerplate: the part
that used to be hand-written JSON-RPC wiring becomes a decorator.

FastMCP 1.0 was contributed into the official MCP Python SDK (it is the
`mcp.server.fastmcp` module that ships there), which is a large part of why the
project's design is everywhere in the MCP ecosystem. The actively-developed line
went well past that baseline: it can proxy an existing MCP server, compose
several servers into one, auto-generate a server from an OpenAPI or FastAPI app,
do client-side LLM sampling, and (in the more recent releases) add MCP-native
middleware so cross-cutting concerns like auth and logging understand your tools
and resources.

## Prior work

- **Prefect** — the workflow-orchestration engine used by thousands of data
  teams. Jeremiah founded it and is CEO. FastMCP grew out of that same
  "make the hard infrastructure feel like writing normal Python" instinct.
- **Prefect Horizon** — a more recent launch framed as a "context layer" where
  AI agents interface with a company's proprietary data, tools, and workflows.
  Same throughline: give agents a clean, governed surface to the messy backend.

## Voice notes

Build-in-public, engineer-to-engineer. Ships announcements on X with crisp
"here's what's new, here's the one-liner" framing and a healthy amount of
ecosystem cheerleading ("let's keep growing the MCP ecosystem"). Not a hype
account — the posts are feature-dense and practical. The right register for a
tribute is peer-to-peer respect for the API design, not fan noise.

## What he cares about

- Making protocol-level infrastructure disappear behind ordinary Python.
- The MCP ecosystem as a shared, growing standard rather than a land-grab.
- Governance and the "context layer" — how agents safely reach real tools.

## Geography

Prefect is headquartered in Washington, D.C. (remote-first company). Treat the
DC tie as company-level, not a personal-address claim.

## Trending metric (feeds the X caption)

- **Stars:** past 25,000 on `jlowin/fastmcp` and climbing (live read ~25.5k on
  2026-06-03).
- **Why it's hot now:** still shipping actively in June 2026; the framework is
  widely treated as the default way Python developers stand up MCP servers, so
  star velocity tracks MCP adoption itself.

## Angle for the tribute (different from the caption)

- **Caption angle:** the star milestone + the decorator-collapses-the-protocol
  thesis.
- **Why-this-one angle:** the creator arc — Prefect founder, FastMCP folded into
  the official SDK, then the v2 line (proxy / compose / OpenAPI generation).
  Keep these two surfaces from overlapping.
