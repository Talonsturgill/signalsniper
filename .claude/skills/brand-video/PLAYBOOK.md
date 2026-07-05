# brand-video PLAYBOOK — v2

The strategy doc for the video pipeline. v2 synthesizes four commissioned research briefs (kinetic-typography craft, X launch-video practice 2025-26, studio production discipline, and headless-Chromium cinematography) plus the shipped learnings in `CRAFT_LOG.md`. The writer and director stages read this before drafting; the critic enforces it.

This doc is canonical guidance, not a spec. Numbers here are defaults, not laws — but depart from them on purpose, not by accident.

## Architecture validation

HTML + CSS keyframes + JS rAF timeline + Playwright screencast + ffmpeg finishing is the same architecture HeyGen ships as `hyperframes` and Replit uses for HTML-to-video. The renderer is not the bottleneck. What we tell it to render, and what we verify afterward, is.

## The three-layer quality model

1. **Camera language.** Every scene has a committed motion verb, and no frame is ever truly static: settles end in a breathe or through-drift, tails get a light sweep. A held static frame reads cheap after ~1.2s; a genuinely frozen one is a screening-room FAIL after 2s.
2. **Texture and light.** Grain + vignette + halation stay on. Light behaves: a single sheen pass timed to a word's landing (never looping), aurora fields derived from the brand accent, bloom gated to highlights in the finish. On near-black canvases use `screen` blends — `overlay` does nothing over black (shipped lesson, 2026-07-01).
3. **Sound design over a bed.** Licensed music bed + synthesized foley stem (whoosh INTO impact at cuts, stamp on emphasis), music sidechain-ducked ~4-6dB under each hit, two-pass loudnorm to −14 LUFS / −1.5 dBTP. Cuts land ON onsets: beat_align snaps boundaries, leading each cut 40ms so the visual hits with the transient.

## Easing (the single biggest tell)

- Entrances: strong custom ease-out — `cubic-bezier(0.16, 1, 0.3, 1)` family; expo `cubic-bezier(0.19, 1, 0.22, 1)` for hero words. Built-in `ease-out` is not strong enough; `linear` on an enter reads robotic.
- Exits ACCELERATE and run ~65% of the paired entrance duration. Never decelerate an exit.
- Ease-in-out (`cubic-bezier(0.37, 0, 0.63, 1)`) only for elements already on screen that move or morph (ken burns, orbit).
- Overshoot is a spice: one element per scene, excursion inside 0.95–1.05 (the JS `easeOutBack` is tuned to this).
- Related elements in one beat share one curve. Mixing curves in a choreographed group reads cheap.

## Timing and rhythm

- Durations scale with size: word 300–500ms, line 500–700ms, full-scene change 700–1000ms.
- Staggers: 15–40ms per character, ~80ms per word, 100–150ms per line, children trail parents 40–120ms on the same curve.
- Hold formula after a composition settles: `chars/12 + 0.5` seconds, max ~2s. The screening room measures a hard ceiling.
- Vary beat lengths deliberately (long–short–short). Equal-length scenes read metronomic; beat_align introduces musical variation naturally.
- Scene transitions are fade-through, never crossfade mush: outgoing finishes before incoming starts (the renderer already enforces this window). Chromatic tick on the cut.
- Compound entrances: opacity + translateY(0.3–0.45em) + blur(6–8px→0) + scale(0.97→1) together — the renderer's kinetic and generic paths both do this. Tracking-settle on hero words (logo_reveal does this automatically).

## Type in motion

- Max two typefaces per video; get contrast from weight/size/case within the family.
- Scale contrast between hero and support ≥ 2.5–4x. One-word-huge beats (word fills 60–80% of frame width) alternate with sentence-small beats.
- All-caps only for short kickers with +0.05–0.2em tracking; sentences stay mixed-case.
- Reveal granularity: letter-stagger for 1–4-word display type, word-stagger for sentences, line-stagger for blocks.
- Numerals: tabular figures, count-up over ~0.9s with expo-out (big_number does this for leading integers), width reserved so nothing reflows.
- Typewriter: ~26 chars/s in terminals, smooth cursor blink (never binary steps).

## Composition (1080×1080)

- Title-safe: keep type inside 90% (the default 8% padding satisfies this).
- Off-center placement is a system: thirds anchors (wire_dispatch is the left-anchored template); break the center only once per video, at the peak.
- Three depth layers minimum: background field (aurora/starfield/grid) at low opacity, midground rules/frames, foreground type.
- Whitespace is a designed element: hero beats are ~two-thirds empty.
- One focal point per beat. If everything stands out, nothing does.

## Color and light

- 60-30-10: canvas ~60%, secondary tone/texture ~30%, accent ≤10% and only where it means something.
- **The project's own palette first** (`brand_extract.py`). Never pure #000/#FFF canvases — they melt into X's Lights Out / light chrome; the extractor nudges automatically.
- Dark canvas + one high-chroma accent is the premium-tech default; counter-programmed warm cream stands out in a dark feed — both are valid, pick by the project's own brand.
- Glow/halation only on the accent, at most one element per frame. Sheen: single 1.5–2.5s pass, `screen` blend on dark canvases.
- Lock one palette for the piece; color meanings stay consistent across scenes.

### Brightness physics (dim is a design failure, not a grade setting)

- **Ink floors.** Dark canvas → primary ink ≥ 230 luma; light canvas → ≤ 60. The screening gate demands p99.3 ≥ 180 with spread ≥ 120 at every scene midpoint (540px sampling — 270px smears thin mono type ~20-30 levels into the background and lies).
- **Accent is graphic, not text.** Mid-luma accents (most brand blues/reds, 120-170 luma) read dim as hero glyphs on black. `build_html.py` derives `--accent-ink` (accent blended toward white to ~205 luma; toward black to ~60 on light canvases) for ALL text-scale accents; the raw `--accent` stays on dots, fills, strokes, glows, and inverted-field backgrounds where mid-luma is the point.
- **Muted that carries content gets lifted.** `--muted-content` = muted blended 60% toward ink; activity lines, detail rows. Raw `--ink-muted` only for decorative whispers.
- **A frame's light source must cover pixels.** Sparse bright type at small sizes fails the gate honestly — grow the hero, or give the scene a bright plate. Panes: names 2.7cqw nowrap, lines 2.7cqw, plates at 0.06 white on dark.
- **The grade must not fight the page.** Filmic curve LIFTS (0.25→0.27, gamma 1.03), never crushes; one vignette only (the page's — the old ffmpeg vignette double-dipped ~10% off the mean).
- **Blend in RGB, verify with a gate.** ffmpeg's `blend` runs per-plane: a screen blend on YUV chroma (centered 128) pushes U/V toward 192 — the bloom manufactured a magenta cast over every dark canvas for weeks and read as "dim purple murk." Bloom now blends in `gbrp`; the chroma-neutrality gate (median R−G/B−G of final vs raw, drift > 8 FAILs) makes the whole bug class unshippable.
- **Dark ink on a light canvas needs MORE size than the symmetric case suggests.** The readability gate's light-polarity branch reads p0.7 (darkest 0.7% of pixels): sRGB gamma anti-aliases dark-on-light thinner than bright-on-dark at the same nominal size, so a font-size that clears the dark-canvas p99.3 check with room to spare (bright text on black) can still fail the light-canvas p0.7 check (dark text on cream) at 540px sampling. Shipped fix (2026-07-03, `claude` preset, ECC video): every hero/body text class now carries a hairline `-webkit-text-stroke: 3.6px currentColor` (fattens glyphs without changing hue, harmless on dark canvases too since stroke color always matches fill), plus larger type than the dark-canvas defaults for `stack` (11cqw), `terminal` (5.6cqw, in a widened 94%-width frame), `close` (10.8cqw), and `diagram` labels (5.5px in a widened 30-unit node box). Check ANY new light-canvas preset's full scene set against the readability gate before shipping — do not assume dark-canvas type sizes transfer.

## X feed physics (why the defaults are what they are)

- **Frame 0 is the poster.** Muted autoplay + thumbnail duty: scene 1 must show the project name within its first second, with motion already alive (no fade-from-black). The finisher's 1.5s trim lands frame 0 mid-cascade with the wordmark readable.
- **14–22s.** ≥12s so the ranker's quality-view threshold is reachable; under ~22s for peak completion. The end card visually rhymes with the open so the autoloop replays clean (replays are a ranking signal).
- **Silent-first, ≤55 words total**, ≥1s per 13 characters on screen, ≤2 lines and 5–8 words per card. Small captions ≥ ~3cqw (the templates' floors were raised for feed legibility).
- **Encode**: supersample capture at 1620, lanczos down to 1080, CRF 20 + aq-mode=3 + deband + temporal grain (kills near-black banding through X's re-encode), upload via web.
- **Post mechanics** (for the Gmail notes): repo link in the first reply, one @mention in the body, one fact the video doesn't show, Tue–Thu 10:00–12:00 creator-timezone. The single highest-value outcome is the tagged creator replying or quote-posting; the video being in THEIR brand colors is the recognition trigger.

## Camera moves (11)

| Move | Reads as | Best for |
|---|---|---|
| `push_in` | slow commitment | title, fix |
| `pull_back` | reveal, resolve (now drifts through the tail) | close |
| `ken_burns` | documentary pan | quote, big_number |
| `crash_zoom` | impact | flash |
| `orbit` | 3D depth | diagram, sparkline |
| `parallax_drift` | layered depth | three_line, terminal |
| `static_breathe` | stillness with life | rare, when stillness IS the point |
| `rack_focus` | blur→sharp arrival | terminal, product beats |
| `dolly_up` | ascent | sparkline, momentum beats |
| `tilt_reveal` | unveiling | logo_reveal, title |
| `none` | — | never ship it |

≥4 distinct moves per video, ≥1 orbit-or-tilt for real 3D.

## Scene templates (17)

Text: `title` (kinetic per-char headline), `stack`, `two_line`, `three_line`, `fix`, `mono_block`, `quote`, `close`.
Heroes: `diagram` (draw-on graph + particles), `flash` (accent burst, kinetic word), `big_number` (count-up numeral), `terminal` (typed session, per-line accents, `white-space: pre` alignment), `split`, **`logo_reveal`** (per-char wordmark + tracking settle + rule + tagline + sheen), **`sparkline`** (animated data curve + end-dot + value pop — the momentum receipt), **`word_cascade`** (words slam in on beats, previous dim), **`wire_dispatch`** (ticker types on, dateline, word-staggered headline, lede).

Every video: ≥1 hero; prefer one REAL-product beat (terminal for CLIs, diagram for systems, sparkline for growth stories) — demonstrated capability out-engages abstract type.

## Backgrounds

`design.background.style`: `starfield` (deterministic particles, accent-tinted), `aurora` (three accent-derived blobs, ±24° hue spread, screen-blended on dark — the brand "breathing"), `grid` (perspective floor, infra flavor), `none`. Don't repeat yesterday's style; keep intensity ≤1.

## Sound design

- Palettes (`ambient`/`electronic`/`acoustic`) drive the PREVIEW score only; the shipped bed is licensed CC BY music.
- The shipped foley stem (`synth_audio.py --foley-only`, v10): NO per-cut swipe — a whoosh on every boundary is the amateur-slideshow tell (and the operator's top gripe). The transient family (`foley_style`) fires ONLY on the money/emphasis beat (the trailer "button"); the ordinary hard cut is carried by the music. `finish.py` sidechain-ducks the bed under the hit.
- Music-first editing: pick the track, THEN `beat_align.py` retimes scene durations onto its onsets (±0.45s window, scenes stay 2.5–4.5s), cuts lead transients by one frame.
- Targets: −14 LUFS integrated, ≤−1.5 dBTP, measured two-pass, `linear=true` so ducking survives.

## Cinematic grammar (v10 — cut like an editor, color like a colorist, light like a DP)

Full cited evidence base: `CINEMATIC_RESEARCH.md`. The rules, each enforced as a gate:

- **Hard cuts by default.** No scene-to-scene dissolve (the renderer no longer fades scenes out-to-black then in-from-black). Pros hard-cut ~99% of the time; an effect on every cut is the slideshow tell. The ONE reserved `transition_style` effect fires on the money-shot cut only. Motion carries THROUGH the cut (a scene enters already moving), never stop-then-start.
- **Easing library — never `linear` on a reveal/move.** Entrances ease-out, exits ease-in/accelerate, hero words overshoot: easeOutCubic `0.33,1,0.68,1`, easeOutExpo `0.16,1,0.3,1`, **easeOutBack `0.34,1.56,0.64,1`** (the money-punch), easeInOutCubic `0.65,0,0.35,1`. Stagger multi-word reveals ~60–120 ms.
- **Color anti-repeat + color script.** Consecutive videos: accent Δhue ≥ 60° AND ΔE00 ≥ 11, OR a canvas-value / temperature flip (`variety_check.py`). Plan ≥ 2 temperature beats across the runtime (60-30-10 dominant/secondary/accent); teal-orange is the "every video looks the same" grade — rotate the hue family.
- **Brightness is a FRAME property, not a type property.** The brightness gate FAILs a dark wash (mean luma < 46 AND < 30% bright scenes). Earn it with a lighter canvas or ≥ 2 bright beats (bright plates, a second inverted flash); never lift it in the grade.
- **The picture illustrates the word.** Each scene declares `illustrates` (how the visual enacts its copy — Mayer's dual-coding); the copy names ONE `differentiator` (Duarte's Big Idea), not a feature list.

## The production chain (who does what)

| Stage | Artifact | Gate |
|---|---|---|
| Producer | `producer-brief-$DATE.json` (audience, ONE-sentence takeaway, tone, references, success criteria) | storyboard_check |
| Director | `storyboard-$DATE.json` (per-shot intent, camera, sound cue, energy curve, ONE money shot at 60–80%) | storyboard_check |
| Music supervisor | track pick + offset | catalog/lifetime rules |
| Writer | `scene-spec-$DATE.json` (template sequence LOCKED to the board) | validate_spec + storyboard_check --spec |
| Animatic editor | beat-snapped durations | beat_align + re-validate |
| Critic | edits keyed to scene index | fact-check + brief alignment + no-repeat |
| Animator | HTML + raw capture | render sanity |
| Finisher | graded, mixed MP4 | finish.py |
| QC | — | wow_check + screening_room + 8-keyframe vibes pass |
| Producer (retro) | `CRAFT_LOG.md` entry | next run reads it |

Stage-locked notes: story/structure notes at the BOARD (cheapest), timing notes at the animatic, polish notes at screening. Never restructure at the writing desk.

## Anti-pattern list (cheap tells)

- Default/linear easing, identical durations everywhere, everything animating at once.
- Static text held >2s; floaty >500ms moves on small elements; crossfade mush.
- Center-aligned same-layout scene after scene (the Corporate-Memphis fingerprint).
- Decorative emojis, arrows, sparkle assets; stock 2018-corporate bounce-ins.
- Ambient bed with no foley; cuts ignoring the music; version numbers as hooks.
- Pure #000/#FFF canvases; accents that mean nothing; looping shimmer (loading-state idiom).
- Tell-don't-show: narrating a paragraph instead of showing one specific thing.

## Hard-won environment lessons (do not relearn)

- **CSS scene animations start at page LOAD, not scene start.** Any camera/effect keyed to a scene must be scrubbed by the timeline driver (`animation-play-state: paused` + negative `animation-delay` per frame) or every scene past the first shows a parked end-pose. This shipped unnoticed for 47 videos.
- **Playwright's video recorder throttles the page to ~9fps** (in-process VP8 backpressure). Record via CDP JPEG screencast with instant acks; verify with the raw unique-frame gate, never with post-grain output (finishing grain fakes uniqueness).
- **Decelerating easings park the camera.** For feed-scale drift moves use linear timing with the shape in the keyframes, so velocity persists to the last frame; ~2x bolder travel than desktop taste (the feed shows the video at ~350px).
- **Zooming a flat background changes nothing.** Full-bleed color scenes (flash, split) need the TEXT sized so camera travel keeps edges inside frame (clipping) while captions carry motion.
- **Base `.scene` centering shrink-wraps stretch layouts** — split/panes style templates must set `align-items: stretch` themselves.
- **Events beat entrances.** A pane flipping blocked-red mid-scene, a number counting WITH a drawing curve, staggered typing — in-scene events are what "something is always happening" means; entrance animations alone read as still cards.

- `walkReset` resets DIRECT children only; template animators own their deep state each frame. Recursive resets once left nested text wrappers permanently invisible IN THE CAPTURE while computed styles looked fine.
- `audioCtx.resume()` never settles under blocked autoplay — always raced against a 400ms timeout, or the whole visual timeline hangs.
- Debug renders with the freeze probe (override `performance.now`, step `window.__t`) — wall-clock waits are flaky because `fonts.ready` on ~1.5MB of embedded fonts varies run to run.
- The recorder falls back to `/opt/pw-browsers/chromium`; never run `playwright install` in the sandbox.
- HN Algolia `numericFilters` 400s through the proxy; filter client-side.
- incompetech direct MP3s: `https://incompetech.com/music/royalty-free/mp3-royaltyfree/<Title%20Case>.mp3`.

## Sources

Four research briefs (2026-07-01, transcripts in the session log) synthesizing: animations.dev, easings.net, Material 3 + Carbon motion, NN/g, GSAP SplitText guidance, PremiumBeat title-design guidelines, SMPTE safe areas, Advids launch-video analysis, X open-source ranker analyses, legibility.info, RocketShip HQ, Socialinsider/OpusClip completion data, Buffer/hashmeta link-penalty coverage, Ordinary Folk + Buck process posts, StudioBinder, Murch's rule of six, premiumbeat 60/30/15 cutting discipline, artlist/bitcut beat-sync, krotos/pixflow foley grammar, loudness standards (−14 LUFS), Josh Comeau `linear()`, Keith Clark CSS parallax, CSS-Tricks grain/motion-blur, Codrops feTurbulence, zayne.io ffmpeg grades, CPJKU onset detection, k.ylo.ph loudnorm, Playwright screencast internals, Replit/HeyGen HTML-to-video write-ups.
