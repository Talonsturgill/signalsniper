# 10x visual quality in code — the research behind the renderer upgrade (routine v11)

Diagnosis: the videos read "clean generated," not "premium studio," and it's NOT the type — it's the **depth, light, material, optical behavior, and easing** around the type. Flat CSS-gradient canvases (banding-prone), naive tweens, and a crude ffmpeg optics chain are the tells. The 10x comes from adding **real light/depth (a GPU background), correct optics (WebGL post), and designed motion (a real easing engine)** — not more type effects.

Film-look north star: Steve Yedlin's four operations — **color response, grain, halation, gate weave** (https://nofilmschool.com/four-elements-film-emulation).

## ENCODABLE VISUAL UPGRADE — ranked (1080², ~30s, code-rendered, headless-Chromium captured)

### TIER 1 — biggest jump per effort (~80% of the perceived 10x)
1. **Full-frame WebGL shader background** — replace flat CSS gradients with one fragment-shader layer: domain-warped fBm noise → Iñigo Quilez cosine palette → soft directional-light term (dot-product or IQ's derivative lighting, no normals). Real depth, atmosphere, chromatic richness; kills banding at the source. Learn: Book of Shaders ch.11–13 (https://thebookofshaders.com/13/), IQ palettes (https://iquilezles.org/articles/palettes/). Stack: `<canvas>` WebGL (raw GLSL or three.js fullscreen `ShaderMaterial`), `uTime` uniform from the deterministic clock.
2. **Move ALL optics into a WebGL post chain** (`pmndrs/postprocessing`, https://github.com/pmndrs/postprocessing): HDR bloom (threshold LINEAR luma, `HalfFloatType`, tone-mapping off) + **red-biased halation** on bright edges (NOT global CA — halation ≠ chromatic aberration, https://mononodes.com/film-elements/) + subtle `ChromaticAberrationEffect` + `VignetteEffect` + film-emulation `LUT3DEffect`. Retire the ffmpeg screen-blend bloom + global rgbashift (both LDR/crude). Learn: postprocessing docs + Yedlin.
3. **GSAP timelines + CustomEase + SplitText** — replace hand-rolled rAF tweens with authored easing curves (overshoot-and-settle), orchestrated timelines, SplitText reveals. This is where "designed motion feel" lives. Learn: GSAP CustomEase (https://gsap.com/docs/v3/Eases/CustomEase/). Drive by frame index (`timeline.time(frame/fps)`, `gsap.ticker.lagSmoothing(0)`) — never wall-clock.

### TIER 2 — strong support
4. **Real scanned 35mm grain plate**, composited Soft-Light/Overlay at matched gamma (replaces synthetic temporal noise — glues layers, hides banding, authentic). Easiest as a final ffmpeg `blend=softlight` overlay of a looped grain clip, color-space matched. (https://www.holygrain.com/blog/best-film-grain-overlays-premiere-pro-davinci-resolve-final-cut/)
5. **Variable-font animation** — a real variable display face with the `opsz` optical-size axis at large sizes, animate `wght`/`wdth`/`opsz` over the timeline (reads as type design, not DOM scaling). (https://pixelambacht.nl/2021/optical-size-hidden-superpower/, https://24ways.org/2019/interactivity-and-animation-with-variable-fonts/)
6. **Swiss grid + modular type scale** (1.25/1.333 ratio), asymmetric placement on a column/baseline grid with intentional negative space instead of centered defaults. Near-zero runtime cost. (https://www.printmag.com/featured/swiss-style-principles-typefaces-designers/)

### TIER 3 — polish
7. **Gate weave** — sub-pixel whole-frame jitter (deterministic seed); trivial, authentic film cue.
8. **Camera parallax / DoF** — offset background-shader UVs vs foreground type by the camera move; subtle `DepthOfFieldEffect` on a hero beat.
9. **Volumetric godrays** for one hero beat (Maxime Heckel raymarch/postprocessing, https://blog.maximeheckel.com/posts/shaping-light-volumetric-lighting-with-post-processing-and-raymarching/) — high wow, higher cost, sparingly.

## CAPTURE CAVEATS (headless Chromium via CDP) — engineer for these or it breaks
- **Determinism is everything.** Drive shader `uTime`, GSAP timeline, grain/gate-weave seeds off ONE virtual frame clock (`frameIndex/fps`), never `performance.now()`. Prefer BeginFrame-driven capture over free-running screencast for frame-perfect output.
- **WebGL needs real GL in headless.** Launch flags `--use-gl=angle`/`--use-gl=egl` (+ `--enable-gpu`) or you get a software rasterizer / blank canvas (https://github.com/puppeteer/puppeteer/issues/9555). Pin the ANGLE backend for cross-machine reproducibility.
- **Color space.** Shader math in linear, explicit sRGB on output, one working space end-to-end so LUT + grain-plate gamma match (mismatch = the washed-out/over-contrasty failure).
- **Reconsider `minterpolate` motion blur** (optical-flow blend artifacts on fast type) — prefer higher-fps render + shader/temporal-accumulation blur, deterministic; let ffmpeg only normalize/encode.
- **Bloom banding** — keep HDR (`HalfFloatType`) through the post chain, dither before the 8-bit capture.

## Craft signals that separate premium from generated (why the above matters)
Physics-based weight/easing (12 principles: slow-in/out, follow-through, overlapping/secondary motion — https://www.schoolofmotion.com/blog/follow-through-tutorial); real layered depth + soft directional light + tactile texture; grain as connective tissue that hides banding (https://www.premiumbeat.com/blog/using-film-grain-digital-video/); correct optics (HDR bloom, red halation, subtle CA, vignette, gate weave); Swiss compositional discipline (grid, modular scale, hierarchy, negative space).

## The four canonical deep-dives
Book of Shaders (https://thebookofshaders.com/13/) · Iñigo Quilez articles (https://iquilezles.org/articles/) · pmndrs/postprocessing (https://github.com/pmndrs/postprocessing) · GSAP CustomEase (https://gsap.com/docs/v3/Eases/CustomEase/) · film-look north star: Yedlin's four operations (https://nofilmschool.com/four-elements-film-emulation).

## Implementation note for THIS pipeline
Tier 1 is a real renderer change: introduce a WebGL background + post-processing layer and a GSAP-driven deterministic timeline into `build_html.py`, and move optics out of `finish.py`'s ffmpeg chain into the WebGL post pass (keep ffmpeg for the grain-plate overlay + x264 encode). All libs must be inlined/base64'd for offline self-contained HTML, must render in headless Chromium with `--use-gl=angle`, and must be driven by the existing deterministic frame clock so the CDP screencast stays frame-perfect. Build behind the existing gates (wow/screening/brightness/color) so quality never regresses; Tier 1 first, prove the jump on one render, then Tier 2–3.
