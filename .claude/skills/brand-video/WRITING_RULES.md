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
