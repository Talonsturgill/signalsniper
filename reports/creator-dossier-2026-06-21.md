# Creator Dossier — 2026-06-21

## Project
- **Name:** OpenMontage
- **Repo:** https://github.com/calesthio/OpenMontage
- **Tagline:** "The first open-source, agentic video production system."
- **License:** GNU AGPLv3

## Creator
- **Name / handle:** Calesthio (GitHub `calesthio`)
- **X handle:** @calesthioailabs
- **YouTube:** @OpenMontage
- **Personal site / other product:** crucix.live (Crucix)
- **One-line bio:** Building open-source intelligence tools. Creator of Crucix.
- **Geography:** Not publicly stated on profile. Do not assert a location.

## What it is
OpenMontage turns an AI coding assistant (Claude Code, Cursor, Copilot, Codex,
Windsurf) into a full video-production studio. You describe a video in plain
language and the agent runs the whole chain: live web research, scripting,
asset retrieval, timeline editing, and final composition. It exposes the work
as **12 production pipelines, 52 production tools, and 400+ agent skills** (the
repo headline rounds this to "500+ agent skills").

## The novel move (the angle that carries the tribute)
Most "AI video" tools animate a handful of stills (Ken Burns over images).
OpenMontage instead builds a **CLIP-searchable corpus from open archives** —
Archive.org, NASA, Wikimedia Commons, with optional Pexels/Unsplash — then
**semantically retrieves real motion clips, edits them into a timeline, and
renders finished footage**. It is actual footage editing, not slideshow
animation. That is the differentiator worth showing.

Supporting design choices that read as production-grade, not toy:
- Live web research wired into the pipeline *before* the script is written.
- Scored provider selection across 7 dimensions with auditable decision logs.
- Reference-video analysis: paste a YouTube link, get differentiated
  production concepts plus cost estimates.
- Quality gates with a post-render self-review pass.

## Prior work / what the creator cares about
Calesthio's other shipped project, **Crucix** (crucix.live), is a personal
intelligence agent: it pulls satellite fire detection, flight tracking,
radiation monitoring, market prices, conflict and sanctions data, and social
sentiment from 27 open-source intelligence feeds in parallel every 15 minutes,
and renders it all on a single Jarvis-style dashboard. The throughline across
both projects: agentic orchestration over many open data sources, rendered into
one finished artifact, built in public. Command-center sensibility.

## Metric that's trending (for the X caption growth lead)
- **Stars:** ~7,400 total on the repo.
- **Velocity:** roughly **+677 stars in the last day** (GitHub trending, daily).
- Currently on GitHub Trending (Python + overall) and Trendshift.
- Release model: no tagged GitHub releases yet; ships continuously off `main`.

## Voice notes (for caption + scenes)
Build-in-public, technical, confident, slightly maximalist ("world's first").
Match peer-to-peer admiration. Lead the caption with star velocity (never a
version number — there are no version tags anyway). Land the "real footage, not
stills" idea once, in one place, and let the other surfaces cover a different
angle (the open-archive corpus, the Crucix lineage, the build-in-public arc).
