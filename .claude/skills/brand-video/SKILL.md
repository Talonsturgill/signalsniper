---
name: brand-video
description: Generate a short (12 to 32 second) 1080x1080 kinetic-typography video as a self-contained HTML page plus a screen-recorded MP4, styled with design tokens pulled from the brand-design-systems library (71 brands plus 67 aesthetics). Real fonts (Inter, JetBrains Mono, IBM Plex Serif, EB Garamond, Space Grotesk, Bricolage Grotesque, Fraunces) ship inside the skill and embed into the HTML via base64 @font-face for offline rendering. Variable scene count, variable duration, variable motion register. Use for daily tribute videos about other builders' AI work where each output should look like a different production, not the same template re-skinned.
---

# brand-video

> **Read `PLAYBOOK.md` first.** It is the strategy doc. The writer agent must consult it before drafting scenes; the critic agent must enforce it. The PLAYBOOK supersedes any conflict with this file.

A flexible kinetic-typography video generator. Replaces the old fixed-format `editorial-kinetic-type`. The skill now ships:

- **18 scene templates**: `title`, `stack`, `two_line`, `three_line`, `fix`, `mono_block`, `quote`, `close`, `diagram`, `flash`, `big_number`, `terminal`, `split`, `logo_reveal`, `sparkline`, `word_cascade`, `wire_dispatch`, `panes`
- **11 camera moves** per scene: `push_in`, `pull_back`, `ken_burns`, `crash_zoom`, `orbit`, `parallax_drift`, `static_breathe`, `rack_focus`, `dolly_up`, `tilt_reveal`, `none`
- **Kinetic type engine**: per-character reveals with blur-in + overshoot settle on `title`, `flash`, `logo_reveal`; word-stagger on `wire_dispatch` headlines; count-up numerals in `big_number`; character typing in `terminal` and `wire_dispatch` tickers
- **Premium easing**: expo-out entrances, accelerating exits, `easeOutBack` settles (0.95-1.05 band)
- **3 motion registers**: `fade`, `cut`, `scale`
- **4 background styles**: `starfield` (default), `aurora` (accent-derived drifting blobs), `grid` (perspective floor), `none` — `design.background: {style, intensity}`
- **Light sweep**: `sheen: true` per scene (default on `logo_reveal`); single pass at 52-82% of the scene, `screen`-blended on dark canvases
- **3 audio palettes** for the preview score, plus a shippable foley stem (`synth_audio.py --foley-only`) that the finishing mux ducks the licensed bed under
- **Texture overlay** (configurable grain + vignette + halation, always on)
- **Lighting arc** (full-stage hue drift across the runtime)
- **Held subject** (persistent corner wordmark, appears after scene 1, hides on `flash`)
- **8 aesthetic preset packs** in `presets.json`, plus **project-native palettes** via `brand_extract.py`
- **5 narrative frameworks** to rotate (CLASSIC, RECEIPT, SCHEMATIC, MANIFESTO, DISPATCH) — see PLAYBOOK
- **3 to 8 scenes**, 12 to 32 seconds total
- **8 bundled OFL fonts** (Inter, JetBrainsMono, IBMPlexSerif, EBGaramond, SpaceGrotesk, BricolageGrotesque, Fraunces) base64-embedded for offline rendering
- Color tokens from the project's own site, any brand, or any aesthetic in `brand-design-systems`

Two artifacts per run, same as before:

1. **HTML page** at `<repo>/videos/<name>-YYYY-MM-DD.html`. Self-contained. Fonts are base64-embedded so it renders offline.
2. **MP4** at `<repo>/reports/<name>-YYYY-MM-DD.mp4`. Screen-recorded by Playwright headless Chromium, soundtrack synthesized separately, muxed via ffmpeg.

## When to use

Use whenever the daily-tribute routine (or any caller) needs a video that:

- Honors a specific brand identity (Linear, Vercel, Stripe, Claude, etc.)
- Honors a specific aesthetic (mono, editorial, brutalism, terracotta, neon, etc.)
- Should not look like the previous video

Do **not** use for diagrams, talking-head footage, or product UI demos.

## Pipeline

```
spec.json (with design tokens + scenes)
   |
   v   build_html.py
HTML (1080x1080, self-contained, fonts embedded)
   |
   v   record_mp4.py  (Playwright captures webm + synth_audio.py writes wav)
MP4 (H.264 baseline + AAC)
```

## Spec shape

The spec is a single JSON file:

```json
{
  "date": "2026-05-09",
  "topic": "pi-mono, the anti-framework agent toolkit",
  "creator_handle": "@badlogicgames",
  "project_url": "https://github.com/badlogic/pi-mono",

  "design": {
    "brand_slug": "linear.app",
    "aesthetic_slug": "mono",

    "tokens": {
      "canvas":     "#010102",
      "ink":        "#f7f8f8",
      "ink_muted":  "#8a8f98",
      "accent":     "#5e6ad2",
      "hairline":   "#23252a"
    },

    "fonts": {
      "display": "JetBrainsMono",
      "body":    "JetBrainsMono",
      "italic":  "JetBrainsMono"
    },

    "typography": {
      "display_weight":      600,
      "body_weight":         400,
      "letter_spacing_em":  -0.02,
      "case":               "preserve",
      "italic_descriptors": false
    },

    "motion": {
      "register":    "cut",
      "scene_in_s":  0.18,
      "scene_out_s": 0.12,
      "stagger_s":   0.18
    },

    "layout": {
      "padding_pct":        8,
      "rule_thickness_px":  1,
      "stage_radius_px":    8
    }
  },

  "scenes": [
    {"template": "title",      "headline": "pi-mono",         "eyebrow": "agent toolkit, minus the framework", "duration_s": 3.0},
    {"template": "stack",      "eyebrow": "THE STACK",         "items": [
      {"name": "Coding CLI",  "descriptor": "terminal harness"},
      {"name": "LLM router",  "descriptor": "one API, fifteen LLMs"},
      {"name": "vLLM pods",   "descriptor": "self-host the model"}
    ], "duration_s": 3.5},
    {"template": "two_line",   "lines": ["Most agent kits", "ship a framework."], "accent_idx": 1, "duration_s": 3.0},
    {"template": "three_line", "lines": ["They pick your tools", "and your runtime", "before you start."], "accent_idx": 1, "duration_s": 3.0},
    {"template": "fix",        "primary": "Minimal core.", "secondary": "You wire the rest.", "emphasize": true, "duration_s": 3.0},
    {"template": "three_line", "lines": ["One LLM router.", "Fifteen providers.", "Zero opinions."], "accent_idx": 2, "duration_s": 3.0},
    {"template": "close",      "primary": "Minimal core.", "accent": "You wire the rest.", "subtitle": "what most agent kits skip.", "emphasize": true, "duration_s": 3.5}
  ]
}
```

### Design tokens

The five color tokens map to canonical roles. Pull them from `brand-design-systems/brands/{slug}.md` (`colors.canvas`, `colors.ink`, `colors.ink-subtle`, `colors.primary`, `colors.hairline`) or derive them from `brand-design-systems/aesthetics/{slug}.md`.

Contrast minimums (the validator enforces these against `canvas`):

- `ink` vs `canvas` >= 4.5:1
- `accent` vs `canvas` >= 3.0:1 by default. Warm-earth accents (terracotta, clay, riso orange) live in this band naturally and are part of the editorial / paper / refined identity. Raise this floor by setting `design.accent_contrast_min` in the spec, e.g. `4.5` for mono / neon / dashboard / matrix aesthetics where the accent is meant to pop.
- `ink_muted` vs `canvas` >= 3.0:1

If a token fails, fall back to the brand's spec-stated alternative or to a safe default.

### Fonts

Available font keys (resolve to the file in `fonts/`):

| Key                  | File                          | Best for                                |
|----------------------|-------------------------------|-----------------------------------------|
| `Inter`              | Inter.ttf (variable)          | corporate, professional, clean, modern  |
| `JetBrainsMono`      | JetBrainsMono.ttf (variable)  | mono, codex, brutalism, hacker          |
| `IBMPlexSerif`       | IBMPlexSerif-Regular.ttf      | editorial, claude, publication          |
| `IBMPlexSerif-Bold`  | IBMPlexSerif-Bold.ttf         | (bold weight for IBMPlexSerif)          |
| `EBGaramond`         | EBGaramond.ttf (variable)     | refined, elegant, luxury, terracotta    |
| `SpaceGrotesk`       | SpaceGrotesk.ttf (variable)   | modern, clean, sleek, contemporary      |
| `BricolageGrotesque` | BricolageGrotesque.ttf (var.) | expressive, bold, neobrutalism          |
| `Fraunces`           | Fraunces.ttf (variable)       | bold, dramatic, paper, riso             |

A spec sets `display`, `body`, and optional `italic` keys. The renderer base64-embeds whichever fonts are referenced.

### Motion register

| Register | Scene fade in | Scene fade out | Y-translate | Children stagger | Best for                              |
|----------|---------------|----------------|-------------|------------------|---------------------------------------|
| `fade`   | 0.40s         | 0.27s          | 14px        | 0.27s            | editorial, claude, paper, refined     |
| `cut`    | 0.05s         | 0.05s          | 0           | 0.10s            | mono, brutalism, neobrutalism         |
| `scale`  | 0.45s         | 0.27s          | 0           | 0.30s            | bold, dramatic, energetic             |

### Scene templates

| Template     | Required fields                                                       | Notes                                            |
|--------------|------------------------------------------------------------------------|--------------------------------------------------|
| `title`      | `headline`, `eyebrow`                                                  | The only place an eyebrow can hold a colon       |
| `stack`      | `eyebrow`, `items[2..5]` (each with `name`, `descriptor`)              | The eyebrow is uppercase + small caps            |
| `two_line`   | `lines[2]`, optional `accent_idx`                                      |                                                  |
| `three_line` | `lines[3]`, optional `accent_idx`                                      |                                                  |
| `fix`        | `primary`, `secondary`                                                 | Largest type beat. Set `emphasize: true`         |
| `mono_block` | `lines[1..6]`, optional `accent_idx`                                   | Renders in mono font regardless of design.fonts  |
| `quote`      | `quote`, optional `attribution`                                        | Italic display type                              |
| `close`      | `primary`, `accent`, optional `subtitle`                               | Set `emphasize: true` so audio hits the mallet   |
| `logo_reveal`| `word`, optional `tagline`                                             | Per-char cascade + tracking settle + rule + sheen; the poster-frame opener |
| `sparkline`  | `values[5..24]`, `value_label`, `caption`, optional `eyebrow`          | Animated data curve with end-dot pop; the momentum receipt |
| `word_cascade`| `words[3..6]`, optional `accent_idx`                                  | Words slam in on beats, previous dim to 55%      |
| `wire_dispatch`| `ticker`, `dateline`, `headline`, `lede`                             | Left-anchored wire report; ticker types on; ticker/dateline may hold a colon |
| `terminal` (upgraded) | `title`, `lines[1..6]` — line dicts take `prompt`, `accent`   | Prompt lines type at 26 cps; `white-space: pre` preserves column alignment |
| `big_number` (upgraded) | `numeral`, `caption`, optional `sub`                        | Leading integer counts up over 0.9s, width-locked, tabular numerals |
| `panes`      | `panes[2..4]` (each `name`, `lines[<=3]`, `state`, optional `flip_to`+`flip_at`), optional `eyebrow` | Live multi-agent session: typed activity, pulsing status dots, and a mid-scene state flip (border+badge swap with a shake) |

### Per-scene fields

- `duration_s` (optional, default 3.0): seconds the scene holds. Total run = sum. `beat_align.py` retimes these onto the music's onsets.
- `emphasize` (optional, default false): tells the audio engine to drop a mallet hit at scene start, and the foley layer to add a stamp.
- `camera` (optional, default `static_breathe`): one of `push_in`, `pull_back`, `ken_burns`, `crash_zoom`, `orbit`, `parallax_drift`, `static_breathe`, `rack_focus`, `dolly_up`, `tilt_reveal`, `none`.
- `sheen` (optional; default true only on `logo_reveal`): one light sweep across the scene at 52-82% of its runtime. Use on scenes whose tail would otherwise go still.

### Top-level design fields (new)

- `design.framework`: one of `CLASSIC`, `RECEIPT`, `SCHEMATIC`, `MANIFESTO`, `DISPATCH`. Recorded in bv-meta and the style-history ledger; the routine rotates through these to keep videos from feeling templated. See PLAYBOOK Section "Narrative frameworks".
- `design.audio_palette`: `ambient` (default), `electronic`, `acoustic`. Picks the music bed in `synth_audio.py`. Foley always plays on top.
- `design.held_subject`: optional short string (e.g. project slug). Renders as a persistent wordmark in the lower-left corner across all scenes for visual continuity.
- `design.texture`: optional sub-object with keys `grain` (0..0.20), `vignette` (0..0.40), `halation` (0..0.20), `lighting_arc` (0..0.50). Defaults: 0.06 / 0.20 / 0.0 / 0.30.
- `design.accent_contrast_min`: float threshold (default 3.0). Raise to 4.5 for mono/neon/dashboard aesthetics that want hot accents. Validator enforces.

### Preset packs

`presets.json` ships 8 ready-made design blocks. The routine picks one based on aesthetic_slug and merges it into the spec, eliminating per-run hand-rolling of tokens/fonts/motion. See `presets.json` for the full table.

### Hard copy rules (validator-enforced)

Same as the old skill, slightly relaxed:

- No em dashes (`—`)
- No en dashes (`–`)
- No semicolons
- No colons in body text (titles and `stack.eyebrow` may have one)
- No emojis or non-ASCII characters except smart quotes
- No question marks
- No arrow characters

Per-template character limits live in `validate_spec.py`.

## Build (full production chain)

```bash
python validate_spec.py     spec.json
python beat_align.py        --music music/T.mp3 --offset 30 --spec spec.json --write
python build_html.py        spec.json out.html
python record_mp4.py        out.html raw.mp4 --viewport 1620   # supersampled capture
python synth_audio.py       --bv-meta '<from html meta>' --foley-only --output foley.wav
python finish.py            --raw raw.mp4 --spec spec.json --music music/T.mp3 \
                            --music-offset 30 --foley foley.wav --out final.mp4
python wow_check.py         spec.json final.mp4 out.html
python screening_room.py    spec.json final.mp4 --report screening.json
```

Supporting tools:

- `brand_extract.py --url <site>` — mine the project's own palette (CSS custom props, theme-color, frequency heuristics), contrast-fixed; exit 3 → fall back to brands/presets.
- `storyboard_check.py brief.json board.json [--spec spec.json]` — pre-production gate: brief completeness, shot intent, variety, money-shot position, template-sequence timing lock.
- `beat_align.py` — spectral-flux onset detection + BPM estimate; snaps interior cuts to onsets (±0.45s, scenes stay in bounds), leads each cut by one frame, records `design.beat`.
- `finish.py` — the conform: fps normalize → lanczos 1080 → filmic S-curve → gated bloom → whisper CA → vignette → sharpen → deband → temporal grain → CRF 20/aq-mode 3; audio bed + foley sidechain duck + two-pass −14 LUFS loudnorm.
- `screening_room.py` — post-render QC on real pixels/audio: dead-air ceiling, energy-arc peak position, poster-frame content, loudness dynamics, cut-to-onset drift, conform sanity.
- `record_mp4.py` falls back to the pre-installed Chromium (`/opt/pw-browsers/chromium`, or `$BV_CHROMIUM`) when the Playwright CDN is unreachable; never run `playwright install` in the sandbox.

The recorder reads scene durations and emphasis flags from the spec via the HTML's `<meta name="bv-timeline">` block, so the foley stem gets its hits in the right places.

## Anti-repeat (caller's responsibility)

The skill itself is stateless. Callers (e.g., the daily-tribute routine) maintain a `style-history.json` ledger and refuse to pick a `(brand_slug, aesthetic_slug)` combination already used in the last N runs.

## Failure handling

- A font key in the spec doesn't resolve to a file in `fonts/`: fail loud, do not fall back.
- A token fails the contrast check: fail loud, the caller should fall back to that token's safe default and re-run.
- Spec total duration outside 12 to 32 seconds: fail.
- Scene template unknown: fail.
- Playwright install fails: write the HTML and exit non-zero. The HTML is still publishable.

## Versioning

- v1.0 of brand-video replaces editorial-kinetic-type. The old fixed 8-scene/25s format is gone.
- Bundled fonts are pinned to whatever shipped at v1.0; bumping fonts is a minor version.
- New scene templates are minor version bumps. New motion registers are minor version bumps.
