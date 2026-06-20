# Creator Dossier — 2026-06-20

## Subject

**Jesse Vincent** — builds as **obra**.

- **X handle (for the tag):** `@obra` — canonical handle across the web (GitHub `obra`, blog `fsck.com`, IRC/email nick `obra` for ~20 years).
  - Verification note: X profile is behind an auth wall and Wikipedia lists no socials, so the handle could not be 100% machine-confirmed this run. Adjacent confirmed handles: Threads `@obrajesse`, Mastodon `@jesse@metasocial.com`. `@obra` is the lane-aligned default; flagged in the Gmail for a human glance before posting.
- **Project:** Superpowers — `https://github.com/obra/superpowers`
- **Company:** Prime Radiant (founded early 2026; organizational home for Superpowers). `primeradiant.com`
- **Blog:** Massively Parallel Procrastination — `https://blog.fsck.com`

## One-line bio

The man who wrote Request Tracker in 1994, ran the Perl language for three years, and co-founded a keyboard company is now codifying twenty years of engineering discipline into skills that coding agents have to follow.

## Voice notes

Plain, dry, deeply experienced. Writes like a staff engineer who has seen every way a project can rot and is patient about it. Not a hype person. The README reads like an opinionated runbook, not a pitch. Treats agents the way a seasoned engineering manager treats junior staff: clear specs, mandatory process, review before merge. There is even a "feelings journal" skill for the agent, which tells you he is half-serious and half-playful about the anthropomorphism.

## Prior work (the pedigree)

- **Request Tracker (RT)** — 1994, written at Wesleyan. Became the most widely deployed open-source ticketing system on Earth. Spawned Best Practical Solutions (2001).
- **Perl 5** — served as project/release lead ("pumpking") for three years.
- **K-9 Mail** — the long-running Android email client, later folded into Mozilla / Thunderbird for Android.
- **Keyboardio** — co-founded 2014, shipped the Model 01 heirloom-grade ergonomic mechanical keyboard. He is a literal gearhead.
- **VaccinateCA** — led the volunteer-run COVID vaccine availability project in 2021.

## What he cares about

Process that survives contact with reality. Test-driven development (RED-GREEN-REFACTOR), root-cause debugging, planning before coding, small reversible steps, and writing things down so the next person (or the next agent) doesn't re-derive them. Open source. Building his own tools, all the way down to the keycaps.

## The project — Superpowers

An agentic **skills framework and software-development methodology** for coding agents. Skills are reusable markdown instruction sets, but the key move is that they are **mandatory pre-task workflows, not suggestions** — the relevant skill fires automatically before the agent acts. The agent clarifies requirements, presents a design, writes a plan, executes through subagent-driven development, and runs code review, with TDD throughout.

Ships skills for: test-driven development, systematic debugging with root-cause analysis, brainstorming, plan writing, subagent dispatch, code review, git worktree management, self-updating memory notes, and the feelings journal.

Runs across **Claude Code, Codex, Cursor, Gemini CLI, OpenCode, and Copilot CLI** (and as of v6.0.0, Kimi Code, Pi, and Antigravity).

### Latest technical move (build-in-public)

- **v6.0.3** (June 18, 2026): relocated Subagent-Driven Development scratch files (task briefs, implementer reports, review diffs, progress ledgers) out of `.git/` — which Claude Code treats as protected — into a self-ignoring `.superpowers/sdd/` directory, organized per worktree, kept out of version control.
- **v6.0.0**: unified the two reviewer prompts into a single spec-compliance + quality pass; added new harness support; plans now carry Global Constraints blocks and per-task Interfaces sections; sandboxed the brainstorming companion with per-session auth keys.

## The trending metric

- **~234k GitHub stars**, 20.7k forks, and **climbing roughly a thousand stars a day** (GitHub trending: +1,110 on 2026-06-20).
- 8 releases, 609 commits on main; v6.0.3 shipped two days before this run.
- Widely cited in June 2026 as the leading skills framework across both Claude Code and Codex.

## Angle split (so copy surfaces don't collide)

- **X caption** -> the growth metric (crossed 230k, still climbing) plus the pedigree (RT, Perl) that earns the methodology.
- **Video** -> the mechanic: the enforced loop (clarify, plan, build, review) and "rules, not tips."
- **Why-this-one** -> the build-in-public cadence: the latest release moving working notes out of git, the breadth of supported harnesses, the feelings journal.
