# brand-video music library

Curated tracks for the daily-tribute pipeline. Pick a track whose mood and audio palette match the chosen preset pack. The Step 8 ffmpeg formula in the routine prompt handles the actual mux and warmup trim.

## Catalog

| Slug | Title | BPM | Mood | Best for | License |
|---|---|---|---|---|---|
| `tyrant` | Tyrant | — | industrial / dark electronic | subway-chrome, mono-terminal, cctv | CC BY 4.0 (Kevin MacLeod, incompetech.com) |
| `nightline` | Nightline | 88 | dub-techno | subway-chrome, mono-terminal, cctv | in-house, public domain |
| `signal` | Signal | 112 | minimal techno | geominimal, editorial-90s | in-house, public domain |
| `paper-room` | Paper Room | 70 | felt piano + room | editorial-paper, claude, gallery | in-house, public domain |
| `dispatch` | Dispatch | 92 | cinematic piano | gallery, claude, DISPATCH framework | in-house, public domain |

The full programmatic catalog lives in `catalog.json` next to this file. The routine should consume it.

## Required attribution

`tyrant` is licensed CC BY 4.0 and **requires** an attribution reply on X when used. Use the verbatim text:

```
Music. Tyrant by Kevin MacLeod (incompetech.com), licensed under CC BY 4.0.
```

The four in-house tracks (`nightline`, `signal`, `paper-room`, `dispatch`) are public-domain originals authored by `signalsniper studio` via `build_music_library.py`. No attribution required.

## Regenerating the in-house tracks

```bash
python3 .claude/skills/brand-video/build_music_library.py --total 60
```

Renders `nightline.mp3`, `signal.mp3`, `paper-room.mp3`, `dispatch.mp3` into this directory and rewrites `catalog.json`. Re-run after editing `build_music_library.py` to refresh.

The `Tyrant.mp3` file is downloaded directly from incompetech.com and **is not regenerated** by the script. The script preserves whatever Tyrant entry already lives in the catalog if you re-run with `--only` set to skip Tyrant, or you can hand-edit the catalog.

## Anti-repeat across days

The routine should track which slug shipped on which date and avoid reusing the same slug back-to-back, the same way it rotates frameworks and aesthetics. Tyrant has shipped on 2026-05-09; tomorrow's run should not pick `tyrant` again.
