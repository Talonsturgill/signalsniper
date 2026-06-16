# Creator Dossier — 2026-06-16

## Subject

- **Name:** Shuvonn (goes by handle `shuvonsec`)
- **X handle:** [@shuvonsec](https://x.com/shuvonsec)
- **GitHub:** [github.com/shuvonsec](https://github.com/shuvonsec)
- **Project:** [`claude-bug-bounty`](https://github.com/shuvonsec/claude-bug-bounty)

## One-line bio

Security researcher and tool builder working the bug-bounty lane. Ships an AI-driven
recon-to-report toolkit that runs as both a Claude Code plugin and a standalone CLI.

## What the project is

`claude-bug-bounty` automates the bug-bounty workflow end to end from the terminal:

- **Recon:** subdomain enumeration, live-host discovery.
- **Test:** probes 20+ vulnerability classes (IDOR, XSS, SQLi, SSRF, SSTI, and more).
- **Validate:** a **7-Question Gate** that each finding must pass before it's written up.
  This is the false-positive-reduction layer that the v5.0.0 release centered on.
- **Report:** generates submission-ready writeups for HackerOne, Bugcrowd, Intigriti,
  and Immunefi.

It runs both as a Claude Code plugin and a standalone CLI (Python, 74%).

## Authorization framing (verbatim from README)

> "For authorized security testing only. Always test within an approved bug bounty
> program scope."

Five core rules headline the README: read full scope first, only test what the program
says you can, never go out of scope. The tribute honors this framing. The video is about
disciplined, scope-bound, authorized research, not indiscriminate scanning.

## Voice notes

Operator voice. Terse, scope-disciplined, checklist-driven. Talks in the language of
recon, scope, and findings, not hype. The product copy reads like a runbook.

## Prior work / trajectory

- Latest release **v5.0.0** (June 9, 2026): "False Positive Reduction + Repository Polish."
  The headline of the release is the validation gate, not new attack surface.
- The project crossed **3.3k stars** and is trending again on GitHub this week (~135 stars
  in a day during the current spike).

## What they care about

Signal over noise. The whole v5 arc is about *not* drowning a triage queue in
false positives. The 7-Question Gate is the thesis: a finding earns its writeup.
Scope discipline is treated as a first-class feature, not a disclaimer.

## Geography

Not reliably shareable from public profile. Omit from copy.

## The trending metric (feeds the X caption)

- **Stars total:** ~3.3k, climbing.
- **Velocity:** ~135 stars/day during the current spike.
- **Recency:** v5.0.0 landed June 9, 2026; trending again on GitHub the week of June 16.

## The different angle (feeds Why-this-one)

Most autonomous scanners win on coverage and lose on noise. This one's release notes
lead with subtraction: a gate that throws findings away. The build-in-public story is a
security researcher hardening *trust* in an autonomous agent's output, not just widening
what it can touch.
