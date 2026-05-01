# Creator Dossier: Dax Raad

- **Name:** Dax Raad
- **X handle:** @thdxr
- **One-line bio:** NYC-based founder of Anomaly Innovations, creator of SST (Serverless Stack) and OpenCode, the open-source terminal-first coding agent.
- **Voice notes:** Direct, terse, lowercase, lightly profane. Skips capitalization and punctuation in tweets, favors flat declarative statements over hype. Recent examples: "llms don't give a shit what you put in there" and on Omarchy bundling OpenCode: "if coding agents become an important tool for building software they can't all be proprietary and vendor locked. it's not that opencode is amazing yet, there's just a deep need for a project like it." Speaks the same way in podcasts, calls his own command palette "a junk drawer, more or less."
- **Prior work:** SST (formerly Serverless Stack), the TypeScript IaC framework for full-stack AWS apps used by thousands of teams. OpenAuth (standards-based auth provider). Co-maintainer on OpenNext (Next.js adapter for AWS). Also building Bumi.
- **What he cares about:** Product restraint over feature velocity, DX as a first-class discipline, open source as a hedge against vendor lock-in, skepticism of AI pricing distortions, terminal-native workflows, indie/bottom-up dev tool adoption.
- **Geography:** New York City.

## OpenCode specifics

- **Model-agnostic in practice:** Works with 75+ LLM providers via Models.dev, plus local models. Critically, it can authenticate with existing GitHub Copilot and ChatGPT Plus/Pro subscriptions via `/connect`, you bring your own plan, OpenCode is just the agent harness. Differs from Claude Code which is locked to Anthropic.
- **Architecture:** Client/server split written mostly in TypeScript. The server is headless, clients include the TUI (built by neovim devs), a desktop app (macOS/Windows/Linux beta), and IDE extensions. Remote operation falls out of this naturally. Auto-loads LSPs to feed the model.
- **Two agent modes:** "build" (full write access) and "plan" (read-only analysis). Has a unified "workspace" abstraction collapsing git worktrees, Docker, and cloud sandboxes into one concept. Supports parallel agents on the same project and shareable session links for debugging.
- **Current state:** ~153k stars, ~17.6k forks, v1.14.30 as of April 2026, 781 releases, 850+ contributors. Recently bundled by default in Omarchy.

## Tribute defense (Agent 3)

OpenCode hits the day's lane dead center. Dax Raad shipped a model-agnostic coding agent CLI as an open alternative to Claude Code, and it landed at 1,274 points on Hacker News in the last 24 hours with 619 comments. Coming from the SST creator gives it builder credibility most CLI projects never earn. The project sits in the agent tooling and builder-tier infrastructure pocket, and @thdxr is a reachable, active builder voice. The novelty is real because OpenCode is not another Claude Code wrapper, it is a deliberately vendor-neutral harness, which lets the tribute argue something specific instead of cheerleading.
