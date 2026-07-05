# Cinematic craft — the research behind routine v10

Practitioner-grounded evidence for the v10 "cinematic layer" gates. Where a
number is grounded in the literature it is cited; where it is a threshold
engineered from a cited anchor it is flagged **[H]**. Compiled 2026-07-05 from
~20 live sources (film editors, colorists, motion designers, explainer studios).

The operator's five complaints map onto five research areas and five gates:
slideshow feel · same colors back to back · every video dark · a swipe on every
scene · words the picture never illustrates.

## 1. Cutting grammar — a movie, not a slideshow

- **The hard cut is the pro default, overwhelmingly.** In a finished feature ~99%
  of transitions are plain cuts, no effect. "Transition-effect-as-default" is
  itself the amateur/slideshow tell; the fix for "looks like a slideshow" is
  FEWER effects, not fancier ones. (StudioBinder Types of Transitions; FILMPAC
  dissolves-vs-cuts; Better Dev Screencasts "the best transition is often none".)
- **Murch's Rule of Six** (weighted priority a cut is judged against): Emotion 51%,
  Story 23%, Rhythm 10%, Eye-trace 7%, 2-D screen plane 5%, 3-D continuity 4%.
  Sacrifice from the bottom up; protect emotion and story. (StudioBinder; No Film
  School; TMFF.)
- **Motivated cut vocabulary** — each cut names a reason: hard cut, match-on-action
  (cut mid-movement so motion completes in the next shot — "the edit disappears"),
  match/graphic match, J-cut (incoming audio leads the picture), L-cut (outgoing
  audio lingers), cross-dissolve (= "time passed"; misuse screams amateur), smash
  cut, cut-on-motion, whip-pan. (Adobe Cuts in Film; MasterClass 11 Cuts; Backstage
  J/L; Filmsupply cutting-on-action.)
- **What makes a cut feel like film: motion carries THROUGH the cut.** Humans track
  motion, so cutting during movement lets the eye cross the splice; cutting on a
  parked/static frame exposes it. Stop-then-start (element decelerates to a dead
  freeze, then a new element starts from zero) is the literal definition of a
  slideshow held-frame. (StudioBinder Continuity Editing; Filmsupply.)

→ **v10 gates:** real hard cuts (no scene-to-scene dissolve), the reserved effect
spent on ONE cut (the money shot), motion carried through the cut.

## 2. Motion design for kinetic type

- **Easing always applies; `linear` reads robotic/cheap.** (Adobe/Willenskomer 12
  principles; Fiveable; JakeInMotion.) Entrances ease-*out*, exits ease-*in*/
  accelerate, hero words overshoot.
- **Concrete cubic-beziers (verified values):** easeOutCubic `0.33,1,0.68,1` ·
  easeOutQuart `0.25,1,0.5,1` · easeOutExpo `0.16,1,0.3,1` · **easeOutBack
  `0.34,1.56,0.64,1`** (overshoot/settle — the "alive" landing) · easeInOutCubic
  `0.65,0,0.35,1` · Material standard `0.4,0,0.2,1`, accelerate `0.4,0,1,1`,
  decelerate `0,0,0.2,1`. (easings.net; Material m2 speed; MDN cubic-bezier.)
- **Anticipation + follow-through + overlapping action (stagger).** Multi-word
  reveals offset each unit ~60–120 ms, not simultaneous. (School of Motion kinetic
  type Pt.3.)
- **Cameras never "park."** A decelerate-and-freeze camera IS the slideshow held
  frame; keep a slow continuous drift and cut while motion is live. **Motion blur =
  the 180° shutter rule** (blur ≈ ½ frame of travel) is the socially-learned "movie
  look". (Apple Motion Hold-Frame [the thing to avoid]; DIYPhotography/RED 180°.)

→ **v10:** money-shot scale-punch uses easeOutBack; the finishing 25→50fps blend
supplies motion blur; the renderer's cameras already run continuous (no parked
decel fill).

## 3. Color — across shots and across a series

- **Color script:** plan a deliberate emotional color ARC, not one flat wash.
  Pixar plots 1–3 key colors per scene that shift across the film. → declare **≥2
  temperature beats** across a 26–31s piece. (StudioBinder Color Script;
  Hyperallergic Art of Pixar; Toy Story 3 study.)
- **Structure: 60-30-10** (dominant / secondary / accent). **Teal-orange is the
  cliché** — highest complementary exposure contrast, became shorthand for
  "expensive," then "every video looks the same." Rotate the hue family.
  (No Film School 60-30-10; PetaPixel; Filmit.io.)
- **Series = fixed identity + variable palette.** LOCKED: type, layout, motion
  register, the palette RULE. VARIABLE per entry: hue family, canvas value,
  temperature, contrast. (Modern Diplomacy series-consistency; Puritano style guide.)
- **Perceptual color-difference math (the ruler):** CIEDE2000 (ΔE00) is the
  accurate standard. Scale: ΔE ≤1 imperceptible; **2–10 perceptible at a glance;
  11–49 "more different than similar"**; JND ≈ 2.3 ΔE*ab. Hue-angle: analogous
  ("same family") = within **30–60°**; complementary 180°, triadic 120°.
  (Wikipedia Color difference; Zschuessler Delta E 101; workwithcolor HSL schemer;
  Techkon ΔE00.)
- **Two palettes read as genuinely DIFFERENT** when the dominant/accent rotates
  **Δh ≥ 60°** (past the analogous band) **[H, grounded]** AND **ΔE00 ≥ 11** (past
  "more different than similar") **[H, on a cited scale]**. ΔE JND is
  chromaticity-dependent → gate on hue AND ΔE together, plus a temperature/value
  flip as an alternative satisfier.

→ **v10 color gate** (`variety_check.py`): accent Δh ≥ 60° AND ΔE00 ≥ 11 vs each
of the last 2, OR a canvas-value / temperature flip.

## 4. Transition sound — kill the whoosh reflex

- A whoosh is "the audio equivalent of a fast cross-fade — it tells the audience
  'we just jumped' without making them think about why." A crutch that ANNOUNCES
  the edit; the hallmark of slideshow/corporate templates because it fires on every
  cut regardless of motivation. Defensible ONLY when matched to real on-screen
  motion (a whip-pan, an object crossing frame), sitting quietly under the mix.
  (Ocular Sounds; Pixflow.)
- **What pros do instead:** J-cut audio lead (the next idea's sound pulls you
  across), a musical hit/"button" on the money beat as punctuation (1–2 per 30s),
  sparse sub-drops, or silence letting the track carry. The transient belongs on
  the money beat, NOT every cut. (Epidemic Sound J/L; BOOM Library trailers;
  Ableton impacts; Toolfarm edit-to-beat.)

→ **v10:** `synth_audio.py` emits no per-cut transient; the foley family fires only
on the emphasis/money beat.

## 5. Explainer craft — the picture must do the work

- **Dual-coding** (Paivio): verbal + visual channels; a picture is encoded twice.
  **Picture superiority:** pictures recalled up to ~2× words. (Wikipedia dual-coding;
  Gorilla.)
- **Mayer's multimedia principles:** Multimedia (words+pictures > words), **Spatial
  & Temporal Contiguity** (the visual for a line appears WITH that line), **Redundancy**
  (don't paste the whole VO on screen — on-screen text = the KEYWORD), Coherence &
  Signaling (cut anything off-point; cue the one thing per beat). (Educational
  Technology; ResearchGate.)
- **Studios:** Kurzgesagt = visual metaphors ("you remember the idea because you
  remember the picture"); Vox/Caswell = "the whole point of video is you're talking
  about the thing on-screen," visuals follow logic beat by beat; explainer writing =
  "show don't tell," a two-column AV script pairing each line with its picture.
- **Isolate ONE differentiator:** Duarte's **Big Idea** — one key message, everything
  supports it; "including every fact leads to overload and people tune out." Good
  copy names the single novel thing, not a feature list; the visual for that beat
  ENACTS it.

→ **v10 explainer gate** (`deliverables_check.py`): a `differentiator` field (one
idea, named in the caption) + a per-scene `illustrates` field the critic verifies.

---

## ENCODABLE FRAMEWORK (what v10 implements)

**(A) Pre-planning** — brief/board must decide before render: the ONE
`differentiator`; a color script with ≥2 temperature beats steered off the last 2
videos; each cut's motivation; ≤1 effect cut; each scene's `illustrates` (picture↔
word map); ≥30% of scenes bright.

**(B) Rendering** — non-`linear` easing (bezier library above); entrances ease-out,
exits ease-in, hero overshoot (easeOutBack); motion carried through the cut (no
stop-then-start); cameras never park; the reserved effect on the money cut only; a
scale-punch on the money beat; no per-cut swipe (transient on the money beat).

**(C) Quality gates** — consecutive-video accent Δh ≥ 60° AND ΔE00 ≥ 11 (or value/
temp flip); ≤1 effect cut; frame brightness floor (mean luma ≥ 46 OR ≥30% bright
scenes); ≥1 temperature change across runtime; differentiator present and named in
copy; picture-word correspondence per scene (critic).

---

## Sources

**Cutting:** StudioBinder (Rule of Six, Continuity Editing, Types of Transitions) ·
No Film School (Rule of Six) · FILMPAC (dissolves vs cuts) · Better Dev Screencasts ·
Adobe (Cuts in Film) · MasterClass (11 Cuts) · Backstage (J-cut, L-cut) · Filmsupply
(cutting on action). **Motion:** easings.net · Material m2 (speed) · MDN (cubic-bezier) ·
Adobe/Willenskomer (12 principles) · School of Motion (kinetic type Pt.3) ·
DIYPhotography / RED (180° shutter) · Eyecandy (speed ramping) · Apple Motion (Hold
Frame). **Color:** StudioBinder (Color Script) · Hyperallergic (Art of Pixar) · No Film
School (60-30-10) · PetaPixel / Filmit.io (teal-orange) · Zschuessler (Delta E 101) ·
Wikipedia (Color difference) · Techkon (ΔE00) · workwithcolor (HSL schemer) · Modern
Diplomacy (series consistency). **Sound:** Ocular Sounds (whoosh) · Epidemic Sound (J/L
cuts) · Toolfarm (edit to beat) · BOOM Library (trailers) · Ableton (impact sounds).
**Explainer:** Wikipedia (dual-coding) · Gorilla (picture superiority) · Educational
Technology / ResearchGate (Mayer principles) · School of Motion (Vox/Caswell) ·
Kurzgesagt · StudioBinder (explainer script) · Duarte (Big Idea).
