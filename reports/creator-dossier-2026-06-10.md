# Creator Dossier - 2026-06-10

## Creator
- **Name:** Shaun Smith
- **X handle:** @evalstate
- **GitHub:** https://github.com/evalstate
- **Org / banner:** llmindset (llmindset.co.uk), contact fastagent@llmindset.co.uk
- **Geography:** United Kingdom (shareable - llmindset is a UK practice)

## One-line bio
Independent AI engineer who builds Model Context Protocol tooling in the open. Author of fast-agent, a deep MCP contributor, and a fixture of the MCP-client community.

## Project
- **Name:** fast-agent
- **URL:** https://github.com/evalstate/fast-agent
- **PyPI:** `fast-agent-mcp`
- **Language:** Python (98.8% of the codebase)
- **README tagline (verbatim):** "Code, Build and Evaluate agents - excellent Model and Skills/MCP/ACP Support"
- **Stars:** ~3.8k (climbing; positioned as the first MCP-native agent framework)
- **Latest release:** v0.7.17, shipped 2026-06-10 ("Anthropic Fable + Safety Warning update")
- **Cadence:** near-daily point releases. Patch stream is the momentum signal, not the star count alone.

## What's novel (the different angle)
fast-agent was architected around MCP from the first commit instead of treating the protocol as a connector bolted onto an existing framework. Concretely:
- **Full MCP feature surface, end to end tested:** sampling, elicitations, MCP prompts, roots, and streamable-HTTP transport diagnostics.
- **MCP OAuth 2.1** with keyring storage - the secure-deployment angle the lane cares about.
- **Workflow patterns as first-class primitives:** chain, parallel, evaluator-optimizer, router, orchestrator, agents-as-tools, and MAKER (k-vote error reduction).
- CLI-first - `uv pip install fast-agent-mcp`, then `fast-agent go` drops you into an interactive agent. Setup and bootstrap scaffolds ship in-box.
- Multi-provider out of the box (Anthropic incl. Fable, OpenAI, Google, Azure, Ollama, Deepseek).

## Voice notes
Dry, precise, spec-literate. He talks about conformance and test coverage, not hype. Posts demos as terminal recordings. Treats MCP edge cases (transport, auth, elicitation) as the interesting part. A tribute should match that register: show the command, name the hard features, let the contrast carry the praise.

## What he cares about
- Spec-compliant MCP - the paths other frameworks skip (sampling, elicitation, OAuth).
- Testability and deterministic agent workflows.
- Secure transport and auth as a default, not an add-on.
- Building in the open with a fast release loop.

## Prior work
- Long-running MCP contributor and MCP server author (publishes servers and Hugging Face Spaces under `evalstate`).
- Active voice in the MCP-client ecosystem (cited by PulseMCP as the first MCP-native agent framework).

## Metrics that are trending
- **Star count:** ~3.8k and climbing.
- **Release velocity:** v0.7.17 today; point releases nearly every day.
- **Positioning:** "first MCP-native agent framework" - the framing that's pulling attention as MCP adoption accelerates.

## Caption / Why-this-one inputs
- Caption growth metric: "just crossed 3.8k stars" (no version number).
- Why-this-one angle: solo UK engineer, near-daily release discipline, conformance-test origin story - kept distinct from the caption's feature claims.
