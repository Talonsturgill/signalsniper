---
name: editorial-kinetic-type
description: Generate a 25-second 1080x1080 editorial kinetic-typography video as a self-contained HTML page (deployable to GitHub Pages, viewable in any browser, paste-the-URL-back-to-Claude editable) plus a screen-recorded MP4 with synced audio for posting on LinkedIn or X. Anthropic-adjacent visual language (cream and clay default, fully brand-themable). 8 punchy scenes of bold serif headlines on a soft background, ambient atmospheric audio with mallet hits on emphasis moments, no diagrams, no node graphs, no robots, no faces. Use when a LinkedIn or social post needs a modern educational video that reads like a magazine edit, not a SaaS explainer. Trigger especially when the user requests "modern," "Anthropic style," "editorial," "kinetic typography," or critiques an existing video as "old-looking" or "generic."
---

# editorial-kinetic-type

A skill that produces a 25-second 1080x1080 editorial kinetic-typography video. The visual language is intentionally minimal: a warm-paper background, deep-ink headlines in a high-contrast serif, a single accent color used sparingly, and a sans-serif used only for eyebrow labels and small italic copy. Audio is ambient electronic, not boom-bap. No drums. The only percussive elements are mallet bell hits on the emphasis moments.

This skill is the visual baseline. The colors, typography, and tonal copy are all parameters. The structure is fixed because the structure is what makes it work.

## What you produce

For every run the skill emits **two artifacts**:

1. **A self-contained HTML page** at `<repo>/videos/linkedin-video-YYYY-MM-DD.html`.
   This is the canonical, source-of-truth video. It plays in any modern browser, gets auto-deployed to GitHub Pages by `.github/workflows/pages.yml`, and stays editable: paste its raw URL back into a Claude session and ask for changes (color, copy, timing, scene order — Claude reads the file and edits it directly).

2. **A muxed MP4** at `<repo>/reports/linkedin-video-YYYY-MM-DD.mp4`.
   This is the upload-ready artifact. LinkedIn and X want video files, not HTML, so the skill screen-records the HTML in headless Chromium, synthesizes the soundtrack separately, and muxes them into an H.264 + AAC MP4 around 1-2 MB.

The HTML is the editable thing. The MP4 is downstream — re-record it any time the HTML changes.

## When to use

Use this skill any time a LinkedIn or social post needs a video and the user wants a modern educational tone. Trigger words and contexts:

- "Anthropic style," "Stripe-like," "editorial," "modern," "kinetic typography"
- The user has critiqued a previous video as "old," "generic," "stock," "corporate"
- The post is a teardown, a pattern explanation, a contrarian take, or a builder's note
- The audience is engineers, designers, or technical operators (not marketing/sales)

Do NOT use this skill for:

- Product demos that require showing UI
- Architecture diagrams (use a node-graph skill instead)
- Anything that needs talking-head footage or stock video
- Posts longer than one focused idea (this format compresses to one takeaway)

## Required inputs

Before invoking the builder, you write a `scene-spec.json` with the eight scenes filled in. The spec is the only thing that varies per video. The skill ships a default theme; the spec can override it.

### Scene roles (fixed structure, do not reorder)

1. **Title** — `<headline>` (the topic) + `<eyebrow>` (small sans copy under it)
2. **Three things** — eyebrow label + 3 stacked items, each with a small italic descriptor
3. **The problem** — two-line statement, accent color on one line
4. **The specific case** — three-line statement, accent on the middle line
5. **The fix** — primary statement (largest type in the video) + a secondary delayed line
6. **The mechanism** — three sequential lines describing how it works, accent on the punchline
7. **The consequence** — three-line statement that hammers the inverse of scene 5
8. **The close** — primary line + accent line + small italic subtitle

### Theme inputs

Either pass `theme: "default"` (cream/clay/ink, the baseline shown to the user) or supply a custom theme:

```json
"theme": {
  "background": "#F0EEE6",
  "ink": "#191919",
  "accent": "#CC785C",
  "muted": "#7C7C7C",
  "rule": "#D9D5C8",
  "serif": "'Bitstream Charter', 'DejaVu Serif', Georgia, serif",
  "sans": "'DejaVu Sans', sans-serif"
}
```

Color contract:
- `background` — the paper/canvas color, must be light enough for `ink` to read at AA contrast or better (4.5:1)
- `ink` — primary text, must contrast strongly against background
- `accent` — used on exactly one phrase per scene where used, never more
- `muted` — eyebrow labels and small italic descriptors only
- `rule` — the thin divider line under the eyebrow in scene 2

If the user gives you brand colors, you map them to these roles using this priority:
1. Brand background color → `background`
2. Brand primary text → `ink`
3. Brand accent / call-to-action color → `accent`
4. If only two brand colors are given, derive `muted` as a 50% blend of `ink` toward `background`, derive `rule` as a 90% blend
5. Always verify contrast. If `ink` on `background` is below 4.5:1, fall back to `#191919` ink or `#F0EEE6` background and tell the user

Typography contract:
- `serif` is a stack with at least 3 fallbacks. Always include `Georgia, serif` as the final fallback so any environment renders something.
- `sans` is a stack ending in `sans-serif`.
- Never load remote fonts. The HTML must render offline. Use only fonts present in the cloud sandbox: `Bitstream Charter`, `DejaVu Serif`, `Georgia`, `DejaVu Sans`.

### Copy rules (hard, no exceptions)

These rules come from the calibration that makes the format land. They apply to every line of text in the spec:

- No em dashes
- No semicolons
- No colons in body sentences (eyebrow labels and titles are fine)
- No emojis
- No questions
- No arrow characters (→ ← ↑ ↓). The available serif fonts in the cloud sandbox do not include glyphs for these.
- Headlines max 22 characters per line, max 2 lines
- Emphasis lines max 18 characters
- Eyebrow labels are uppercase, small caps style, max 16 characters
- Italic descriptors max 24 characters
- The whole script across all 8 scenes should read in under 12 seconds when spoken silently. If you have to rush mentally, it's too dense.

Voice: pattern-recognition, builder's POV, declarative. No hedging. No "perhaps." No "it could be argued." If the user has a `write-like-X` skill committed to the repo, use it to draft the copy first, then trim to fit the character limits.

## Workflow

### Step 1: Read or create the scene spec

If a scene spec already exists at `<repo>/reports/scene-spec-YYYY-MM-DD.json`, read it. Otherwise, draft one from the source post or topic. Save to that path before proceeding.

Spec shape:

```json
{
  "date": "2026-04-29",
  "topic": "mem0 gated hybrid retrieval",
  "theme": "default",
  "scenes": {
    "title":         { "headline": "Hybrid Retrieval", "eyebrow": "what mem0 just shipped" },
    "three_things": {
      "eyebrow": "THREE SIGNALS",
      "items": [
        {"name": "Semantic", "descriptor": "vector match"},
        {"name": "BM25", "descriptor": "lexical match"},
        {"name": "Entity match", "descriptor": "named entities"}
      ]
    },
    "problem":       { "line_a": "Fusion alone", "line_b": "ships bugs.", "accent_line": "b" },
    "specific_case": { "line_a": "BM25 can rescue", "line_b": "a semantically wrong", "line_c": "match.", "accent_line": "b" },
    "fix":           { "primary": "Gate first.", "secondary": "Fuse second." },
    "mechanism":     { "line_a": "If the semantic score", "line_b": "is below threshold", "line_c": "drop.", "accent_line": "c" },
    "consequence":   { "line_a": "BM25 can't rescue", "line_b": "what the gate", "line_c": "already dropped." },
    "close":         { "primary": "Gate first.", "accent": "Fuse second.", "subtitle": "the part most builders miss." }
  }
}
```

### Step 2: Validate the spec

```bash
python .claude/skills/editorial-kinetic-type/validate_spec.py reports/scene-spec-YYYY-MM-DD.json
```

This checks every text field against the copy rules, enforces character limits, and (for custom themes) verifies WCAG AA contrast (`ink`/`background` ≥ 4.5:1, `accent`/`background` ≥ 4.5:1, `muted`/`background` ≥ 3.0:1). Fix and re-run until it passes.

### Step 3: Build the HTML video

```bash
python .claude/skills/editorial-kinetic-type/build_html.py \
  reports/scene-spec-YYYY-MM-DD.json \
  videos/linkedin-video-YYYY-MM-DD.html
```

The output is a single self-contained HTML file. CSS animations drive the typography on a 1080x1080 stage that scales to the viewport. The Web Audio API drives the soundtrack. No external assets, no remote fonts, no JS dependencies. Open it in any modern browser to play.

It belongs under `<repo>/videos/` because that path is auto-deployed to GitHub Pages by `.github/workflows/pages.yml`. Once committed and pushed to `main`, the deployed URL is `https://<owner>.github.io/<repo>/linkedin-video-YYYY-MM-DD.html` (typically live within ~60 seconds).

### Step 4: Record the MP4 for upload

```bash
python .claude/skills/editorial-kinetic-type/record_mp4.py \
  videos/linkedin-video-YYYY-MM-DD.html \
  reports/linkedin-video-YYYY-MM-DD.mp4
```

This script:
1. Installs Playwright + Chromium if missing
2. Loads the HTML in a headless 1080x1080 browser, records 26 seconds of webm
3. Synthesizes the soundtrack to wav via `synth_audio.py`
4. Muxes webm + wav into an H.264 baseline + AAC MP4 with `+faststart`

Tab audio cannot be captured by Playwright, which is why we synthesize the audio separately. The schedule in `synth_audio.py` is calibrated to match the JS sync points in the HTML (scene transitions at 3-21s, mallet hits at 12.0s and 21.0s/22.5s).

### Step 5: Validate outputs

- HTML opens in Chrome and plays through to the end with no console errors
- MP4 size is between 500 KB and 5 MB
- MP4 duration is 25.0 seconds exactly (`ffprobe -i ... -show_format`)
- Audio is audible in the MP4 (`ffprobe` shows an `aac` stream)
- Both files exist at the expected paths

If you can run a headless playthrough check, do it. The recorder already runs the page for 26 seconds, so a hard JS error will surface as a corrupted webm or a Playwright timeout.

### Step 6: Embed in the LinkedIn draft

If a LinkedIn draft markdown file exists at `<repo>/reports/linkedin-draft-YYYY-MM-DD.md`, prepend a media reference block:

```markdown
**Watch:** https://<owner>.github.io/<repo>/linkedin-video-YYYY-MM-DD.html
**Edit (paste into Claude):** https://github.com/<owner>/<repo>/raw/<branch>/videos/linkedin-video-YYYY-MM-DD.html
**Upload:** reports/linkedin-video-YYYY-MM-DD.mp4

---

(existing draft content)
```

## Visual language reference

### Scene timing (fixed)

| Scene | Start | End | Duration |
|-------|-------|-----|----------|
| 1. Title | 0s | 3s | 3s |
| 2. Three things | 3s | 6s | 3s |
| 3. Problem | 6s | 9s | 3s |
| 4. Specific case | 9s | 12s | 3s |
| 5. Fix | 12s | 15s | 3s |
| 6. Mechanism | 15s | 18s | 3s |
| 7. Consequence | 18s | 21s | 3s |
| 8. Close | 21s | 25s | 4s |

Every scene fades in over 0.4s and out over 0.27s. Scene 5 gets a subtle scale-in on the primary line. Scene 8 holds longer because it carries the closing weight.

### Type sizing (do not improvise)

Sizes are expressed in `cqw` (container query width) so they scale with the stage. Do not switch to absolute pixels.

| Element | Size | Weight | Family |
|---------|------|--------|--------|
| Scene 1 headline | 10.2cqw | 700 | serif |
| Scene 1 eyebrow | 3cqw | 400 | sans |
| Scene 2 eyebrow | 2.4cqw | 600 | sans, letter-spacing 0.36em |
| Scene 2 item name | 5.9cqw | 700 | serif |
| Scene 2 descriptor | 2.05cqw | 400 italic | sans |
| Scene 3 lines | 8.9cqw | 700 | serif |
| Scene 4 lines | 5.9cqw | 400 (700 on accent) | serif |
| Scene 5 primary | 13cqw | 700 | serif |
| Scene 5 secondary | 5.9cqw | 400 italic | serif |
| Scene 6 lines | 5.2cqw (6.7cqw on accent) | 400 (700 on accent) | serif |
| Scene 7 line a | 6.5cqw | 700 | serif |
| Scene 7 line b/c | 5.2cqw | 400 (italic on c) | serif |
| Scene 8 primary/accent | 9.3cqw | 700 | serif |
| Scene 8 subtitle | 2.4cqw | 400 italic | sans |

### Animation tokens (do not improvise)

- Scene fade in: 0.4s, ease-out cubic
- Scene fade out: 0.27s, ease-out cubic
- Y-translate on intro: 8 to 14 px, resolves to 0
- Stagger between elements within a scene: 0.27s to 0.55s
- Scene 5 primary scale-in: 0.95 to 1.00 over 0.55s

## Audio language reference

The soundtrack is synthesized in two places and they must stay in sync:

- **In the HTML**: Web Audio API code in `build_html.py`'s `JS_DRIVER`. This plays when a viewer clicks replay in the browser.
- **For the MP4**: `synth_audio.py` produces a wav using numpy/scipy that the recorder muxes into the file.

The composition is the same in both:

- **Pad layer 1**: Cmaj9 chord (C-E-G-B-D), stacked sines with subtle detune, slow LFO breathing at 0.12 Hz
- **Pad layer 2**: C-G fifth one octave down for warmth
- **Sub drone**: C2 sine + 2nd harmonic, slow tremolo at 0.13 Hz
- **Scene transition swells**: bandpass white noise, ~1.2s crescendo peaking at the cut, soft sub thump on the boundary, at every scene boundary except the very first (3s, 6s, 9s, 12s, 15s, 18s, 21s)
- **Mallet bells**: 12.0s (scene 5 enter, C5+G4), 21.0s (scene 8 enter, C5+E5), 22.5s (scene 8 second beat, G5)
- **UI ticks**: high-passed noise bursts at text-appearance moments (around 0.6, 3.4, 3.8, 4.1, 4.4, 6.4, 9.4, 15.4, 15.8, 16.4, 18.4 seconds)
- **Master**: gentle tanh saturation, 13 kHz low-pass, 2.5-second outro fade, peak normalized to 0.6

The mallet hits are the only intentional sync points. They land precisely on the entrance of the largest type moments. If you're tempted to add a kick drum, don't. The format gets its energy from typography pacing, not percussion.

The audio does NOT vary by theme. Brand colors change the visual; the soundtrack is part of the format identity.

## What "good" looks like

Do this:
- Trim copy aggressively. Each scene says one thing.
- Use the accent color exactly once per scene where it's used. More than once dilutes it.
- Let scene 5 be the loudest visual beat. Don't compete with it.
- Match the user's brand colors exactly when supplied. If they say "our blue is #1234AB," use #1234AB, not what you think a better blue would be.

Do not do this:
- Stretch the format past 25 seconds. The pacing is part of the identity.
- Add background music with vocals or melody. The pad is meant to recede.
- Use stock typography (Helvetica, Arial). The serif is what makes it editorial.
- Replace the white-noise swells with whoosh sound effects. Whooshes signal YouTube tutorial; swells signal magazine-quality production.
- Add the brand wordmark to the outro frame. The outro is for the takeaway. Branding goes in the LinkedIn post body, not the video.

## File map

```
.claude/skills/editorial-kinetic-type/
├── SKILL.md                     (this file)
├── build_html.py                (spec + theme -> self-contained HTML)
├── record_mp4.py                (HTML -> mp4 via Playwright + ffmpeg)
├── synth_audio.py               (synthesizes the 25-second soundtrack to wav)
├── validate_spec.py             (enforces copy rules, char limits, contrast)
├── default_theme.json           (the cream/clay/ink baseline)
├── mem0-retrieval.json          (the original example spec)
└── README.md                    (developer notes for editing the skill itself)
```

## Failure handling

- `build_html.py` produces unexpectedly small output (under 10 KB): the spec is missing required scene fields. Re-run `validate_spec.py`.
- `record_mp4.py` Playwright install fails: usually a network or sandbox issue. Ship the HTML alone and tell the user to record the MP4 locally.
- `record_mp4.py` produces a webm but the mux fails: check ffmpeg is in PATH and the wav exists.
- MP4 has no audio stream: `synth_audio.py` failed silently. Re-run it directly to see the error.
- Theme contrast check fails: tell the user which color failed and why, fall back to default theme for that property only.

## Versioning notes

- The visual structure (8 scenes, fixed timing) is v1.0 and should not change without a version bump.
- The audio composition is v1.0 and should not change without a version bump.
- The output format changed in v2.0 from rendered MP4 (PNG frame sequence + ffmpeg) to self-contained HTML + recorded MP4. Old SVG-based renderer is removed.
- Themes and copy can be edited freely without versioning.
