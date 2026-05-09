# brand-video music library

Curated tracks for the daily-tribute pipeline. Each track is licensed CC BY 4.0 from Kevin MacLeod (incompetech.com); ship requires the verbatim attribution reply on X.

## Catalog (v2)

| Slug | Title | Mood | Best for |
|---|---|---|---|
| `tyrant` | Tyrant | industrial / dark electronic | subway-chrome, mono-terminal, cctv, MANIFESTO |
| `backed-vibes-clean` | Backed Vibes Clean | smooth hip-hop instrumental | subway-chrome, geominimal, DISPATCH |
| `inspired` | Inspired | uplifting cinematic strings | editorial-paper, claude, gallery, MANIFESTO |
| `lightless-dawn` | Lightless Dawn | atmospheric dark cinematic | cctv, claude, gallery, DISPATCH |
| `decisions` | Decisions | dramatic cinematic build | gallery, geominimal, MANIFESTO |
| `local-forecast-elevator` | Local Forecast - Elevator | retro playful electronic | editorial-90s, geominimal, RECEIPT |

The full catalog with `preset_packs`, `frameworks`, `default_offset_s`, and required attribution strings lives in `catalog.json`. Pipeline reads from there.

## Lifetime no-repeat rotation

**Rule: a track slug never repeats. Once it ships, it's done.**

`history.json` is the ledger. Every successful run appends `{date, slug, project_url}`. The next run's `music_select.py` reads it and removes used slugs from the candidate pool.

When the catalog is exhausted, the selector exits non-zero. That's the signal to expand the library before the next run.

## Required attribution

Every track in this catalog is CC BY 4.0. The X thread reply must include the verbatim string from the track's `attribution_required` field. Example:

```
Music. Tyrant by Kevin MacLeod (incompetech.com), licensed under CC BY 4.0.
```

The Gmail draft surfaces this as a "Required attribution reply" section.

## Selecting a track for today's run

The pipeline calls `music_select.py` after the style pick is finalized:

```bash
python3 .claude/skills/brand-video/music_select.py \
  --preset subway-chrome \
  --framework RECEIPT
```

Prints the chosen track entry as JSON. Score: +100 for a direct `preset_packs` hit, +50 for a `frameworks` hit, plus a small length tiebreak. The selector falls back to any unused track if nothing matches the preset or framework, with a `WARN` on stderr.

To record the pick into history (do this AFTER WOW gate passes, not before):

```bash
python3 .claude/skills/brand-video/music_select.py \
  --preset subway-chrome --framework RECEIPT \
  --record --date 2026-05-10 --project https://github.com/foo/bar
```

## Adding new tracks

When the library is close to exhausted, add new tracks by:

1. Download the MP3 to this directory. Replace spaces with underscores in the filename.
2. Append a new entry to `catalog.json` with all fields populated.
3. Run `music_select.py` with the new preset/framework to verify it scores correctly.
4. Commit + push. The selector picks it up on the next run automatically.

Suggested sources (all CC BY 4.0 unless noted):

- [incompetech.com](https://incompetech.com/music/royalty-free/music.html) — Kevin MacLeod, large catalog, predictable URLs
- [freepd.com](https://freepd.com/) — public domain, no attribution required
- [pixabay.com/music](https://pixabay.com/music/) — Pixabay license, no attribution required (network access permitting)

## Music mux step (Step 8 of the routine)

```bash
DURATION=$(jq '[.scenes[].duration_s] | add' reports/scene-spec-$DATE.json)
FADE_OUT_START=$(echo "$DURATION - 1.5" | bc)
TRACK=$(jq -r '.file' /tmp/today-music.json)
OFFSET=$(jq -r '.default_offset_s' /tmp/today-music.json)

ffmpeg -y -ss 1.5 -i /tmp/tribute-raw-$DATE.mp4 \
  -ss $OFFSET -t $DURATION -i .claude/skills/brand-video/music/$TRACK \
  -map 0:v:0 -map 1:a:0 \
  -c:v libx264 -profile:v baseline -level 3.1 -pix_fmt yuv420p -crf 20 -preset medium \
  -af "afade=t=in:st=0:d=0.6,afade=t=out:st=$FADE_OUT_START:d=1.5,loudnorm=I=-16:TP=-1.5:LRA=11" \
  -c:a aac -b:a 192k -ar 44100 -ac 2 -movflags +faststart -t $DURATION \
  reports/tribute-$DATE.mp4
```
