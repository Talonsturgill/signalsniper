# brand-video PLAYBOOK

The strategy doc for the video pipeline. Synthesizes research on Higgsfield, HeyGen Hyperframes, Runway Gen-4, Sora 2, Veo 3, Pika, Kling, Anthropic's video voice, and current X engineering-creator practice (May 2026). Tells the writer agent how to make a video that does not read as templated.

This doc is canonical guidance, not a spec. The Explainer Writer (Step 6 of the routine) reads it before drafting scenes. The Critic (Step 7) checks output against it.

## Architecture validation

The pipeline we have (HTML + Playwright capture + ffmpeg mux + base64-embedded fonts) is the same architecture HeyGen ships as their open-source `hyperframes` framework: HTML + GSAP/Anime.js + Puppeteer + ffmpeg. They use it to render production AI video. This is the right stack. The bottleneck is not the renderer. The bottleneck is what we tell it to render.

## What separates "designed" from "templated"

Three patterns, in priority order. If a video has all three it reads as next-level. If it has none it reads as PowerPoint, regardless of how good the fonts are.

1. **Camera language.** Every scene has a committed motion verb. Push-in, pull-back, orbit, ken-burns, crash-zoom, whip-pan, parallax-drift. Higgsfield's entire differentiator is a 50-preset library of named camera moves on top of a generic model. CSS `transform` keyframes do all of this for free. A static frame held more than 1.2 seconds without sub-motion reads as cheap.

2. **Texture layer.** A 4-8% opacity SVG turbulence noise overlay, plus a soft vignette, plus optional halation glow on highlights, is the single biggest "designed vs templated" lever. Every modern AI-video tool ships grain by default. Clean digital reads cheap.

3. **Diegetic sound design over a music bed.** A music bed alone reads as YouTube tutorial. Layered sound design (whoosh on cuts, thud on emphasis, typewriter on text reveal, paper rustle on transitions, room tone) reads as production. Silence between beats also works. Stock library music is the worst option.

## Aesthetic preset packs (mirror Higgsfield SOUL)

Each daily-tribute aesthetic should map to a "preset pack" that bundles canvas + ink + accent + font + texture + audio palette. Not a one-off recipe per run.

Starter pack (8, one per common aesthetic_slug):

| Preset | Canvas | Ink | Accent | Font | Texture | Audio palette |
|---|---|---|---|---|---|---|
| `editorial-paper` | warm cream | near-black | terracotta or oxblood | EB Garamond / Fraunces | grain 6%, vignette 18%, halation off | felt piano + room tone |
| `mono-terminal` | near-black | off-white | matrix-green or magenta | JetBrains Mono | scan-lines 4%, vignette 22% | granular clicks + low pulse |
| `gallery` | pure white | near-black | one brand color | IBM Plex Serif | none, single radial spotlight | chamber strings + soft mallet |
| `subway-chrome` | dark steel | bright white | one icy color | JetBrains Mono | chromatic aberration 1px | sub bass + transit foley |
| `cctv` | washed gray | bright white | red | IBM Plex Mono | scan-lines 8%, timestamp overlay | room hum + tape stutter |
| `editorial-90s` | cream + 4:5 letterbox | ink | oversaturated brand | Fraunces | grain 9%, halation on highlights | piano + stamp foley |
| `geominimal` | flat brand color blocks | ink | secondary brand | Space Grotesk | none, hard color cuts | arpeggiated synth |
| `claude` (Anthropic-adjacent) | warm ivory parchment | slate | clay | IBM Plex Serif + Inter | grain 4%, vignette 14% | felt piano + paper rustle |

Add packs over time as new aesthetics warrant. Never invent a one-off aesthetic per run.

## Camera move library

Every scene template is rendered with one camera move from this list. The writer picks per scene; the renderer enforces.

| Move | Implementation | Best for |
|---|---|---|
| `push_in` | `scale: 1 → 1.10` over scene duration | title, fix, close |
| `pull_back` | `scale: 1.08 → 1.00` over scene duration | close, consequence |
| `ken_burns` | `scale: 1.05 → 1.12 + translate -0.5%, -0.3%` | quote, three_line, mono_block |
| `crash_zoom` | `scale: 1 → 2` over 200ms then hold | flash, emphasized fix |
| `whip_pan` | `translateX: -120% → 0` over 240ms with 4px motion blur | cuts between scenes (transition mode) |
| `orbit` | `perspective(1200px) rotateY: -8deg → 8deg` | diagram, schematic |
| `parallax_drift` | three layers at 1.0/0.6/0.3x translate | three_line, stack |
| `static_breathe` | imperceptible 1.0 → 1.005 sine | rare, only when stillness IS the point |

No scene should ever be `static` by default. Even quiet scenes get `static_breathe`.

## Composition vocabulary (scene templates)

Beyond centered text on canvas. Each template should be reachable; the writer picks per scene.

- `title` — already exists
- `stack` — already exists
- `two_line` / `three_line` — already exists
- `fix` — already exists; loudest beat
- `mono_block` — already exists
- `quote` — already exists
- `close` — already exists
- `diagram` — node graph, animated draw-on, 2-5 nodes (ADD)
- `flash` — full-bleed accent color, single huge word (ADD)
- `big_number` — receipt-of-numbers element, massive numeral with caption (ADD)
- `terminal` — monospace frame with traffic-light dots, animated cursor, typed text (ADD)
- `wire_dispatch` — top ticker with timestamp + dateline; below, headline + lede (ADD)
- `magazine_spread` — pull-quote in serif + hairline rules + marginalia (ADD)
- `split` — 50/50 or 60/40 split-screen; before/after, claim/proof (ADD)
- `three_up` — three cards in a row for comparison (ADD)

## Audio palettes

Three palettes shipping with the skill. Each spec picks one based on aesthetic.

| Palette | Composition | Best for |
|---|---|---|
| `ambient` (default) | Cmaj9 pad, sub drone on C2, white-noise swells, mallet bells | editorial, claude, paper, refined |
| `electronic` | arpeggiated synth, sub pulse, glitch clicks, hard mallets | mono, brutalism, cosmic, matrix |
| `acoustic` | felt piano clusters, soft strings, wood mallets, paper rustle foley | terracotta, riso, refined, elegant |

Foley layer (always on, regardless of palette):
- `whoosh` 200ms before each scene boundary
- `thud` on impact at the boundary
- `typewriter` ticks at text-appearance moments
- `stamp` on scene with `emphasize: true`

## Narrative frameworks (rotation)

Every video should pick one of these five frameworks. The framework dictates which scene templates appear and in what order. Anti-repeat the framework over the last four runs.

### 1. CLASSIC (the reference baseline)
`title → stack → two_line → fix → three_line → close`
Balanced explainer. Setup, problem, fix, consequence. Use when the project is already well-known and you're framing the angle, not introducing.

### 2. RECEIPT (numbers do the proving)
`title → big_number → big_number → fix → close`
Stat → stat → so-what. Use for benchmark drops, momentum stories, anything where a number IS the headline.

### 3. SCHEMATIC (system diagram explainer)
`title → diagram → two_line → fix → close`
Use when the project's value is structural — a new pattern, a new loop, a new architecture. Karpathy whiteboard energy.

### 4. MANIFESTO (color-burst declaration)
`title → flash → fix → flash → close`
Single bold claim, color punctuation, restate. Use for opinionated takes, anti-framework positions, bold launches.

### 5. DISPATCH (wire-service field report)
`title → wire_dispatch → quote → three_line → close`
Cool, reportorial, dateline framing. Use when the project is meta — observations about the AI engineering field, a pattern across multiple builders.

The routine prompt's Step 6 picks one framework, records it in `style-history.json`, and refuses to repeat any framework in the last 4 entries.

## Pacing rules

From observed-and-measured top creators:

- First 1.5s is a stop-scroll beat. Single bold word, contradiction, or huge number.
- 2-3 beats per second in the first 4s, easing to 1.2 bps mid.
- Never hold a static frame longer than 1.2s without sub-motion (breathe, parallax, slow zoom).
- Cuts every 0.4-0.8s on average over the whole runtime.
- The "fix" beat lands at 60-65% of total duration, not the end.
- Audio beats and visual cuts must align. If you can't beat-detect, hand-mark.

## Anti-pattern list

- Static-text-on-canvas video without any camera move. Reads as PowerPoint.
- Ambient pad music with no foley layer. Reads as stock library.
- Single composition (centered text) for the entire run. Reads as templated.
- Same color palette as last week's run. Reads as automated.
- Same scene template structure as last week's run. Reads as automated.
- Decorative emojis, arrows, sparkle GIFs. Reads as generic AI slop.
- Stock motion-graphics typography (oversized sans, all-caps, bouncing in). Reads as 2018 LinkedIn explainer.
- "Tell-don't-show" copy. The video should show one specific thing, not narrate a paragraph.

## Phasing

This is what the brand-video skill should ship, in order of impact:

**Phase 1 (high impact, low effort):**
- Texture overlay on the stage (grain + vignette, always on, configurable strength)
- Three new templates: `diagram`, `flash`, `big_number`
- Three audio palettes: `ambient`, `electronic`, `acoustic`
- Foley layer: whoosh + thud at every scene boundary, stamp on emphasize
- 5-framework rotation in the routine prompt
- Camera moves on title/fix/close (push_in, pull_back, ken_burns)

**Phase 2 (higher effort, big payoff):**
- Five more templates: `terminal`, `wire_dispatch`, `magazine_spread`, `split`, `three_up`
- Full camera-move library applied to every template
- Aesthetic preset packs (canvas + ink + accent + font + texture + audio bundled per slug)
- Sub-shots inside long scenes (3 angles × ~2s instead of one 6s static)

**Phase 3 (research-grade):**
- Beat-snapped cuts (audio transient detection)
- Per-clip lighting arc (warm → neutral → cool gradient overlay)
- HDR / display-p3 color
- Held subject across cuts (shared header/wordmark element across scenes)

## Sources

This playbook synthesizes findings from:

- HeyGen Hyperframes (https://github.com/heygen-com/hyperframes)
- Higgsfield camera controls and SOUL preset library
- Runway Gen-4 / Gen-4.5 release notes
- OpenAI Sora 2 capabilities
- Google Veo 3 capabilities
- Pika 2.5 Pikaframes
- Luma Ray3 HDR pipeline
- Kling 3.0 storyboard tooling
- Anthropic "Keep Thinking" campaign and "A Time and a Place" Super Bowl spot
- X creator practice across Karpathy, levelsio, AI-tool launch trailers
- Motion design conventions from short-form explainer content (May 2026)
