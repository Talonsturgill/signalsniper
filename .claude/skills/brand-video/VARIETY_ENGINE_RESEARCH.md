# Variety engine — the research behind the producer brain (routine v11)

The problem, named: **Kate Compton's "10,000 Bowls of Oatmeal Problem"** — you can generate infinitely many outputs that are each numerically unique yet all look the same to a human. Our videos rotate parameters (color, transition, music, which of 17 templates) over a FIXED recipe (wordmark → node diagram → terminal → flash → wordmark), so they're numerically varied but perceptually identical. The fix is to inject variety at the level the viewer actually perceives — **structure, arc, visual device** — not the parameters decorating it. (Compton: https://galaxykate0.tumblr.com/post/139774965871 ; Emily Short: https://emshort.blog/2016/09/21/bowls-of-oatmeal-and-text-generation/)

Core shift: **template-driven → concept-driven.** Hold brand grammar fixed (wordmark, voice, format, quality bar, the GOAL); vary concept-level structure per project; select with **Quality-Diversity / novelty-search** logic; gate on **structural distance**; front it all with a **producer's reasoning phase**. (Imaginary Forces "form performs meaning" https://imaginaryforces.com/grid/what-we-do-design-title-sequences ; Saul Bass https://www.artofthetitle.com/designer/saul-bass/titles/ ; auteur variety https://nofilmschool.com/defining-auteur-directors)

The formal model of "a producer who doesn't make two of the same movie" = **novelty search + quality floor over an archive** (Lehman & Stanley https://www.cs.swarthmore.edu/~meeden/DevelopmentalRobotics/lehman_ecj11.pdf ; MAP-Elites, Mouret & Clune https://arxiv.org/abs/1504.04909 ; QD-for-PCG https://arxiv.org/abs/1907.04053). Constrain the GOAL, free the EXECUTION (Bierut "the problem contains the solution"; tight-brief theory https://arun.is/blog/creative-power-constraints/).

---

## ENCODABLE VARIETY ENGINE

### (A) THE BANKS (author as data)
Sized so no single axis value repeats within a ~6-video window; the combinatorial product is huge but that's not the point — every *perceived axis* differs between consecutive videos.

- **ARCS (13–14):** PAS (problem→agitate→solution) · BAB (before→after→bridge) · origin/build-log (Story Spine) · watch-it-work demo · teardown/how-it-works · single sustained metaphor · data story (a number is the protagonist) · countdown/list · question→answer · myth vs reality · "what if" hypothetical · day-in-the-life · head-to-head compare · first-person POV.
- **VISUAL DEVICES (11–12):** kinetic type · diegetic UI · first-person screen capture · abstract metaphor illustration · data-viz-driven · node/architecture diagram · terminal/code · object/prop metaphor · split-screen compare · single continuous camera-move · transformation morph · (photographic/collage). NOTE: node-diagram and terminal are now **2 of 12**, rate-capped.
- **OPENING SHAPES (8):** cold-open on the result · provocative question on black · a single number slam · problem-as-friction · extreme close-up of one UI detail · a metaphor object entering · wordmark reveal (rate-limited) · in-media-res.
- **CLOSING SHAPES (8):** wordmark lockup (rate-limited) · call-to-look · the transformed "after" held · one-line thesis card · loop-back to the opening image · the number re-stated · builder credit · punchline/reversal.
- **HERO MOMENTS (8–10):** speed reveal · scale reveal · side-by-side flip · the "aha" data spike · one-command-does-everything · a morph completing · impossible-made-possible · live counter racing · a single elegant line of output · the reaction/consequence.

### (B) SELECTION (fit + novelty, no favorite-collapse) — Quality-Diversity
For each project produce `S = {arc, device, scene_seq, hero, open, close}`:
1. **FIT (quality):** producer phase scores `fit(value|project) ∈ [0,1]` — how well each value expresses THIS project's singular truth (CLI→terminal high; data tool→data-viz high; X→Y model→transformation-morph + BAB high).
2. **NOVELTY (diversity):** archive of last N=12 shipped specs. `recency_penalty(value) = Σ w_i·1[video_i used value]`, `w_i = 0.6^age`.
3. **Combined:** `score = fit − λ·recency_penalty`, λ≈0.7.
4. **Anti-collapse:** `score −= μ·usage_share_alltime`, μ≈0.3 (fill empty cells, MAP-Elites intuition).
5. **Assemble** 3–5 candidate whole specs (softmax over scores, temp~0.5); pick highest-fit that PASSES gate (C). None pass → regenerate with λ up.

### (C) PERCEPTUAL-SIMILARITY GATE (replaces the weak template-set overlap)
Feature vector per video: `{arc, device, hero, open, close (categorical); scene_seq, device_seq (ordered)}`.
Distance `D(A,B) = 0.45·d_cat + 0.40·d_seq + 0.15·d_set` where
- `d_cat` = Hamming over the 5 categoricals / 5,
- `d_seq` = normalized Levenshtein over scene_seq (and device_seq),
- `d_set` = Jaccard distance over the template set (the OLD weak check, now only 15%).
Gate:
- **Hard fail vs previous video:** `D(S, prev) ≥ 0.55`. (Two legacy-recipe videos score `d_cat=0, d_seq≈0` → D≤0.15 → FAIL — exactly today's clones.)
- **Rolling novelty:** `novelty(S) = mean D(S,v)` over k=4 nearest of last 12 ≥ 0.50.
- **Absolute bans:** no `(arc,device)` pair within 6 videos; no single categorical value within 3.
- **Instrumentation:** every ~30 videos, Expressive-Range plot of the feature vectors (Smith & Whitehead https://ar5iv.labs.arxiv.org/html/2304.02366) — dense cluster = drifting back to oatmeal.

### (D) GOAL ANCHOR (freedom, not randomness)
Invariant objective the gate never overrides: **"Make a viewer instantly get the ONE genuinely cool/different thing about THIS project — the thing nobody else's video would show."** Producer phase must output `singular_truth` + `money_thing`; the `hero` MUST dramatize `money_thing`; `arc`+`device` must be justified as the best vehicle for `singular_truth`. Hard quality floor: `fit < 0.6` → reject even if maximally novel (QD insists on quality AND diversity).

### (E) THE PRODUCER'S REASONING PHASE (runs BEFORE any template)
Reads `project_dossier` + `series_memory` (last 12 videos' `{singular_truth, arc, device, hero, open, close, scene_seq}` + all-time usage). Steps, each producing a field:
1. **INTERROGATE:** list 5–8 things true of the project; cross out anything also true of a generic AI project; what remains is `singular_truth`; name the ONE thing nobody else would show → `money_thing`.
2. **GENERATE:** propose 4 genuinely different concepts (no two share arc AND device) — over-generate ("bad ideas give birth to the big idea").
3. **KILL THE DEFAULT:** state the obvious treatment (node-diagram + terminal + flash), explicitly REJECT it unless the singular truth makes it uniquely right; justify → `rejected_default`.
4. **PRESSURE-TEST vs MEMORY:** reject any angle whose {arc,device,hero} matches a video in the last 3–6; prefer best-fit AND most-unlike-recent (novelty vs archive).
5. **COMMIT + MOODBOARD:** choose one; write `logline`, pick open/close, specify `scene_seq` as concrete beats, note 2–3 reference touchstones.
6. **SELF-CRITIQUE:** (a) recognizably OURS? (b) shows the ONE cool thing? (c) next to the last 3, does it look like a *different production*? any "no" → back to step 2.

Artifact `concept-$DATE.json` (downstream judged against it):
```json
{"singular_truth":"...","money_thing":"...","logline":"...","rejected_default":"...",
 "arc":"before_after_bridge","device":"transformation_morph","hero":"morph_completing",
 "open":"cold_open_on_result","close":"loop_back_to_open",
 "scene_seq":["COLD_RESULT","THE_BEFORE","THE_MORPH","HERO_COMPLETE","THESIS_CARD"],
 "device_seq":["morph","split","morph","morph","kinetic_type"],
 "references":["...","..."],"novelty_vs_archive":0.63,"fit_score":0.81}
```
The producer phase is a **novelty-search loop with a quality floor over an archive** — if the gate fails, re-run from step 2 with the failed axes banned.

---
Full source list: Compton oatmeal; Smith & Whitehead ERA + "The Right Variety" (arxiv 2304.02366); Lehman & Stanley novelty search; Mouret & Clune MAP-Elites; Gravina et al. QD-for-PCG (arxiv 1907.04053); WFC (boristhebrave.com); brand consistency vs creative diversity (tandfonline 10.1080/00913367.2021.1883488); Imaginary Forces / Saul Bass / auteur; copywriting arcs (PAS/BAB/AIDA/PASTOR) + Story Spine; visual-metaphor method (weareshifta, rmcad); tight-brief theory (ideou, arun.is); showrunner/creative-development process (studiobinder mood board, elementthree concepting).
