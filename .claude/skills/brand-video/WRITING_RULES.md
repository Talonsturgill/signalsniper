# brand-video writing rules

The voice of every tribute is build-in-public peer-to-peer. Below are the specific rules the writer agent applies to every spec, every PR title, and every Gmail body. The critic agent enforces them.

## Voice

Bold declarative opens. Show, don't tell. Admiring without being sycophantic. Specifics over adjectives. Three short sentences beat one long one. Trust the reader.

## Contractions

Use contractions where they sound natural. We're not writing legal copy.

| Avoid | Prefer |
|---|---|
| `he is`, `she is`, `it is` | `he's`, `she's`, `it's` |
| `you will`, `we will`, `they will` | `you'll`, `we'll`, `they'll` |
| `does not`, `do not`, `did not` | `doesn't`, `don't`, `didn't` |
| `cannot`, `will not` | `can't`, `won't` |
| `that is`, `there is` | `that's`, `there's` |
| `you have`, `we have` | `you've`, `we've` |
| `let us` | `let's` |

Apostrophes for possession too. `Mario's monorepo`, not `Mario monorepo` or `the monorepo of Mario`.

## Hard-forbidden in scene text and copy

Already enforced by `validate_spec.py`:
- em dashes (`—`)
- en dashes (`–`)
- semicolons (`;`)
- colons in body sentences (titles and `stack.eyebrow` may have one)
- question marks (no question hooks)
- arrow characters (`→ ← ↑ ↓`)
- non-ASCII except smart quotes and apostrophes

## No-repeat across copy

Within one video and across the day's output (tweet + Gmail body + PR description + scene copy), no specific phrase or claim repeats verbatim. Pick one place to land each idea.

If the tweet says `47k stars and counting`, the Gmail's Why-this-one **does not** also say `47k stars`. The Gmail covers a different angle (creator history, technical move, build-in-public discipline) that complements the tweet.

If the fix scene says `minimal core. / you wire the rest.`, the close scene **does not** say `minimal core` again. Close re-frames the same thesis from a different angle.

## Length budgets

| Surface | Limit |
|---|---|
| X caption | 280 chars total, handle counts in budget |
| Why-this-one (Gmail body) | <= 280 chars, never repeat tweet content |
| PR commit subject | <= 70 chars |
| Scene copy | per-template limits in `validate_spec.py` |
| Total on-screen words | <= 55 across all scenes (validator warns; silent-feed viewers must read everything) |

## Fact check

Every numeral or verifiable claim that ships (in scenes, the tweet, the Why-this-one, or the PR body) must appear in `reports/fact-check-$DATE.json` with **two independent source URLs**. The critic kills anything untraced. Growth metrics say what they are ("climbing ~170 stars a day", "just crossed 9k") and never round up.

## Storyboard timing lock

The scene-spec's template sequence must match the approved storyboard exactly (`storyboard_check.py --spec` enforces). Structure changes go back through the board; the writing desk only changes words.

## Project dedup (lifetime)

A `project_url` already anywhere in `reports/style-history.json` is not covered again, ever, unless a major new release makes it a genuinely different story — and then the Gmail names the exception.

## Anti-repeat (style picks across days)

Maintained in `reports/style-history.json`. Each entry: `{date, brand_slug, aesthetic_slug, framework, project_url}`.

### Framework rotation rule

The five frameworks (`CLASSIC`, `RECEIPT`, `SCHEMATIC`, `MANIFESTO`, `DISPATCH`) rotate with **strict no-back-to-back-repeat**.

- If `style-history.json` has fewer than 5 entries, the new framework MUST NOT appear anywhere in history. The first 5 days each use a different framework.
- From day 6 onward, the new framework MUST NOT match the most recent entry's framework. Any of the other four is fair game.

This is stricter than the previous "filter the last 4 entries" rule and replaces it.

### Aesthetic / preset rotation rule

`(brand_slug, aesthetic_slug)` cannot match any entry within the last 14 history entries. When a creator's brand pack is in `brand-design-systems/brands/`, prefer that brand. Otherwise pick a preset pack from `presets.json` not in the last 14 entries.

### Music rotation rule

`.claude/skills/brand-video/music/catalog.json` lists every track available to the pipeline. Every successful run appends `{date, slug, project_url}` to `.claude/skills/brand-video/music/history.json`.

The rule is **strict lifetime no-repeat**: once a slug ships, it can never ship again. `music_select.py` enforces this — it strips used slugs from the candidate pool before scoring, and exits non-zero if the catalog is exhausted. When the selector exits non-zero, the operator must add new tracks to `catalog.json` before the next run.

`music_select.py --record` writes the chosen pick to `history.json`. The pipeline must call `--record` only AFTER the WOW gate passes, not before — a failed render shouldn't burn a track.

## Pre-flight check

`anti_repeat_check.py` reads `style-history.json` and the current `style-pick-$DATE.json`, exits non-zero if any rule is violated. Build pipeline runs it before render.

## Substance over scoreboard (v7, from operator feedback 2026-07-03)

The scoreboard is the hook; the mechanics are the story. Growth metrics prove people care — they say nothing about what the project does. The ECC run shipped a caption that was stars + thread views and a video whose one "product" beat typed a command that does not exist. Both are now measured failures.

### Caption
- Engagement metrics (stars, views, forks, downloads, likes, bookmarks, followers, "trending") appear **at most once** — the lead. The "one fact the video doesn't show" must be a **capability fact**: what it does, how it's built, what's inside.
- `deliverables-$DATE.json` names that fact in `capability_fact`; `deliverables_check.py` verifies it appears in the caption and contains no engagement nouns.

### Video
- **At most 2 scenes** may center engagement metrics (star charts, view counts, "climbing").
- **At least 2 scenes** must be repo-study-backed product truth: a terminal typing a real command, a diagram of real components, copy quoting real config or docs.
- Every terminal line must appear in `repo-study-$DATE.json` (`commands[]` for prompt lines, `outputs[]` for output lines), each entry carrying a source URL where it literally appears. If the docs don't show it, the video doesn't type it. `deliverables_check.py --spec --repo-study` enforces.
- Quotes attribute ONLY words the person actually said. An editorial line ships without an attribution.

## First reply is a deliverable (v7)

The post's first reply carries the repo link (links in the body are reach-penalized). The link is paste-ready COPY, not a mechanics note: `deliverables-$DATE.json.first_reply` MUST contain the project URL, and the Gmail MUST render a "First reply" block with it. The 2026-07-03 Gmail shipped the note without the link — `deliverables_check.py --gmail` now fails that run shape.

## The deliverables file and gate (v7)

Step 13.5 writes `reports/deliverables-$DATE.json`:
`{date, project_url, creator_handle, caption, capability_fact, first_reply, why_this_one, track_license, attribution_reply}`

`deliverables_check.py` validates: handle-first caption, effective lengths (URLs count 23), forbidden characters, the engagement-metric budget, the capability fact, the first-reply link, zero 4-gram overlap between caption and why-this-one, and CC BY attribution format. With `--spec`/`--repo-study` it adds the video-substance checks; with `--gmail reports/gmail-$DATE.html` it validates the exact HTML to be sent (repo link present, First-reply block present, MP4 + GIF links, no local paths, no style blocks). Non-zero exit → the run does not deliver.
