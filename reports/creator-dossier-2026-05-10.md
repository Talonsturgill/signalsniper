# Creator dossier — 2026-05-10

## Subject
**Aiden Bai** — founder of Million Software, Inc. (million.dev). Builds open-source performance and diagnostic tools for the React ecosystem.

- X: [@aidenybai](https://x.com/aidenybai) (~67k followers as of May 2026)
- GitHub: [@aidenybai](https://github.com/aidenybai); ships under [@millionco](https://github.com/millionco) for the org
- Website: https://www.aidenybai.com/
- Email: aiden@million.dev
- Geography: US (publicly shared)

## One-liner
He turns each React performance idiom into a CLI you can run.

## Voice notes
Builder-tier, terse, declarative. Posts working code in the screenshot. Frames pitches around what the tool does in one command, not what it could become. Energetic and optimistic but never hype-padded. Lowercase prose where it sounds natural. Lets the npm install line be the punchline.

## Prior work (the lineage matters)
| Year | Project | What it does |
|---|---|---|
| 2021–present | [Million.js](https://github.com/aidenybai/million) | Optimizing compiler for React; started at age 16 |
| 2024 | React Scan | Sees which components re-rendered and why |
| 2025 | React Grab | Pulls component-tree state during a session |
| 2026-02 | **React Doctor** | Scans a React codebase, scores it 0–100, lists fixable anti-patterns |

The pattern: a single noun verb. Million compiles. Scan watches. Grab extracts. Doctor diagnoses. Each tool is a one-liner npx away.

## What he cares about
"I care a great deal about speed. In order to allow anyone to access great technology, you need to make it fast." Performance as access. Open source as default. Tooling that runs without setup.

## Today's signal — why this is the day
React Doctor shipped in February 2026 as a CLI. On 2026-05-09 he posted a thread launching the **Agent Skill** version: `npx react-doctor@latest install` plugs into Claude Code, Cursor, and 50+ other coding agents so the agent can scan and fix bad React it just generated. The follow-up post: "wild stat — React Doctor has scanned 84k+ projects in the past 24 hours."

That 84k number is the trending metric. Star velocity on the repo: roughly +806 stars in the last 24h on a ~7.4k base. The agent-skill angle is the reason the lane cares: this is the first React-quality tool that targets agent-generated code as a first-class workflow.

## Latest activity timestamps
- 2026-05-09: agent-skill launch thread on X
- 2026-05-09: GitHub Actions integration release announced
- 2026-05-08: rule pack expanded to 47 rules

## Numbers worth quoting
- **84k+ projects** scanned in the last 24 hours
- **47 rules** across performance, accessibility, dead code, security, architecture
- ~7.4k stars on `millionco/react-doctor`
- 50+ coding-agent harnesses supported via the install command
- 0–100 health score, deterministic, runnable in CI

## What to avoid in copy
- Don't position this as "Million's third release" — most of the lane doesn't care about the brand stack, they care that it catches the bug their agent just wrote.
- Don't use a version number. The story is the velocity, not the v.
- Don't repeat his tagline ("your agent writes bad React. This catches it.") in the X post if it's also the loudest scene in the video.

## Angles available
1. **The 84k velocity** — receipt-of-numbers angle (covered in the video's `big_number` scene).
2. **The lineage** — Scan → Grab → Doctor, the diagnostic line (Why-this-one in the Gmail).
3. **Agent-first quality tooling** — first major React audit tool to ship as a coding-agent skill (PR description angle).

The video uses angle 1. The Gmail Why-this-one uses angle 2. The PR description summarizes angle 3. No surface repeats another's claim.
