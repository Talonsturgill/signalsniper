# brand-video

Flexible kinetic-typography video generator. Replaces `editorial-kinetic-type` with a system that:

- Pulls design tokens from `brand-design-systems` (71 brands, 67 aesthetics)
- Bundles 8 OFL fonts and embeds them into the HTML via base64 @font-face
- Supports 4-8 scenes, 12-32 seconds, 8 scene templates, 3 motion registers
- Produces a self-contained HTML and a screen-recorded H.264+AAC MP4

See `SKILL.md` for the full spec format and usage.

## Files

- `SKILL.md`              — usage and spec contract
- `build_html.py`         — spec → self-contained HTML
- `record_mp4.py`         — HTML → MP4 (Playwright + synth + ffmpeg)
- `synth_audio.py`        — parametric soundtrack generator
- `validate_spec.py`      — copy rules, char limits, contrast
- `fonts/`                — 8 OFL TTF files (Inter, JetBrainsMono, IBMPlexSerif x2, EBGaramond, SpaceGrotesk, BricolageGrotesque, Fraunces)
- `examples/`             — sample specs

## Workflow

```bash
python validate_spec.py spec.json
python build_html.py    spec.json out.html
python record_mp4.py    out.html out.mp4
```

The HTML is self-contained. Drop it on GitHub Pages or paste the raw URL back into Claude to revise.

## Font sources

All fonts are SIL Open Font License via the `google/fonts` repo on GitHub:

- Inter, JetBrains Mono, EB Garamond, Space Grotesk, Bricolage Grotesque, Fraunces — variable axes (weight et al.)
- IBM Plex Serif Regular and Bold — static, paired

## Attribution

Replaces editorial-kinetic-type v2.0. Design tokens consumed from
[brand-design-systems](../brand-design-systems/).
