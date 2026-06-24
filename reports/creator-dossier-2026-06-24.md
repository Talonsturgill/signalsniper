# Creator Dossier — 2026-06-24

## Who

- **Name:** Mahipal Jangra
- **X handle:** [@Mukul_jangra](https://twitter.com/Mukul_jangra)
- **GitHub:** [mukul975](https://github.com/mukul975)
- **Personal site:** https://www.mahipal.engineer
- **LinkedIn:** in/mahipal975 · **ORCID:** 0009-0003-4474-946X
- **Geography:** Berlin, Germany (shareable, listed publicly on his GitHub profile)

## One-line bio

Cybersecurity researcher and front-end developer. MSc in AI Security. Self-describes as "Cybersecurity | Dev | Street Photographer | MSc | Research & AI Security." Works at the seam of threat intelligence and agent tooling.

## The project

**Anthropic-Cybersecurity-Skills** (community project, explicitly *not* affiliated with Anthropic PBC; the name references the Claude Agent SDK / agent-skills format).

- **817 production-grade cybersecurity skills** for AI agents.
- **29 security domains.**
- **286 distinct MITRE ATT&CK techniques** mapped, spanning all 15 Enterprise tactics.
- **Six-framework cross-mapping** — every skill is simultaneously indexed to:
  1. MITRE ATT&CK (v19.1)
  2. NIST CSF 2.0
  3. MITRE ATLAS (v5.4)
  4. MITRE D3FEND (v1.3)
  5. NIST AI RMF (1.0)
  6. MITRE Fight Fraud Framework (F3, v1.1)
- **agentskills.io standard:** YAML frontmatter + structured Markdown (When to Use, Prerequisites, Workflow, Verification). Each skill directory carries `SKILL.md`, `references/`, `scripts/`, `assets/`.
- **Progressive disclosure / token economics:** ~30 tokens to scan a skill's frontmatter, 500-2,000 tokens to fully load. An agent can sweep all 817 before committing context.
- **Portability:** loads in Claude Code, GitHub Copilot, Cursor, Cline, LangChain, CrewAI, OpenAI Codex CLI, Gemini CLI — "all platforms that support the agentskills.io standard, zero config."
- **License:** Apache 2.0.

## What's trending (the metric)

- **~20.3k GitHub stars**, **2.4k forks** as of 2026-06-24.
- **Star velocity: roughly +1,073 stars in the last 24h** — still climbing, sits high on GitHub trending and the daily Python board. This is the headline metric for the X caption.
- **Latest release: v1.3.0, June 22, 2026** (2 days before this run).

## Timeline

- **v1.0.0 — March 11, 2026:** 734 skills, 26 domains, ATT&CK + NIST CSF 2.0 mapping, ATT&CK Navigator layer.
- Post-1.0 additions: ATLAS, D3FEND, AI RMF, then F3 — now 817 skills across 29 domains at v1.3.0.

## Voice notes (for caption + scene register)

Precise, standards-literate, security-practitioner register. He speaks in frameworks and technique IDs, not hype. The tribute should match: itemized, exact, no superlatives. The contrast (a PDF playbook a human reads vs. a skill an agent runs) carries the praise.

## Prior work / what he cares about

- **EmailGuard AI** — adversarial phishing detection (ML + NLP over email content and metadata).
- Builds **MCP servers** for AI agents and publishes research on securing them.
- **Portfolio-v2**, front-end work in React / Next.js.
- Cares about: AI security, secure agent deployment, NIS2, OWASP, threat intelligence, making security knowledge machine-readable.

## Angle separation (so surfaces don't collide)

- **X caption →** star velocity + the six-framework positioning + the novel "agent-loadable security skill" claim.
- **Why-this-one (Gmail) →** the creator: Berlin researcher, MSc AI Security, the EmailGuard / MCP-server through-line, the token-economics discipline (scan cheap, load deep). Different angle, no shared phrases.
- **Scene copy →** the cross-framework map (diagram), the 286-technique coverage, the "not docs, skills" thesis.
