---
name: brand-video
description: Generate a short (12 to 32 second) 1080x1080 kinetic-typography video as a self-contained HTML page plus a screen-recorded MP4, styled with design tokens pulled from the brand-design-systems library (71 brands plus 67 aesthetics). Real fonts (Inter, JetBrains Mono, IBM Plex Serif, EB Garamond, Space Grotesk, Bricolage Grotesque, Fraunces) ship inside the skill and embed into the HTML via base64 @font-face for offline rendering. Variable scene count, variable duration, variable motion register. Use for daily tribute videos about other builders' AI work where each output should look like a different production, not the same template re-skinned.
---

# brand-video

A flexible kinetic-typography video generator. Replaces the old fixed-format `editorial-kinetic-type`. Where that skill locked you to 8 scenes, 25 seconds, two fallback fonts, and one motion language, this one accepts:

- 4 to 8 scenes from a library of 8 templates
- 12 to 32 seconds total duration
- Any of 8 bundled fonts (variable where possible)
- Three motion registers: `fade`, `cut`, `scale`
- Color tokens from any brand or aesthetic in `brand-design-systems`

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
- `accent` vs `canvas` >= 3.5:1 (looser than the old skill because some brand accents are deliberately muted)
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

### Per-scene fields

- `duration_s` (optional, default 3.0): seconds the scene holds. Total run = sum.
- `emphasize` (optional, default false): tells the audio engine to drop a mallet hit at scene start.

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

## Build

```bash
python .claude/skills/brand-video/validate_spec.py spec.json
python .claude/skills/brand-video/build_html.py    spec.json out.html
python .claude/skills/brand-video/record_mp4.py    out.html out.mp4
```

The recorder reads scene durations and emphasis flags from the spec via the HTML's `<meta name="bv-timeline">` block, so the audio synth gets its hits in the right places.

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
