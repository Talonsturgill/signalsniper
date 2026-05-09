---
name: brand-design-systems
description: Apply real, production-grade design systems from 71 brand specs (Linear, Vercel, Stripe, Claude, Notion, Apple, Tesla, etc.) and 67 aesthetic styles (editorial, brutalism, glassmorphism, modern, mono, etc.) when generating UI, posters, LinkedIn graphics, dashboards, landing pages, presentations, or any visual artifact. Use when the user references a brand by name ("make it look like Linear/Stripe/Claude"), names a design style ("editorial", "brutalist", "glassmorphic", "modern minimal"), asks for design that "looks like a real product" or "not generic AI slop", or when generating any visual artifact where aesthetic discipline matters more than improvisation.
license: MIT
metadata:
  author: Talon (consolidated from VoltAgent/awesome-design-md and bergside/awesome-design-skills)
  version: "1.0"
---

# Brand Design Systems

A library of real, extracted design systems for AI agents to apply instead of inventing generic styles. Two complementary collections:

1. **Brands** (71 specs) — full design token systems lifted from real production sites (Linear, Vercel, Stripe, Claude, Notion, Apple, Tesla, Ferrari, etc.). Use when the user names a brand or wants a specific company's aesthetic.
2. **Aesthetics** (67 specs) — abstract design language skills (editorial, brutalism, glassmorphism, modern, mono, neon, etc.). Use when the user names a style or wants a vibe rather than a specific brand.

## When to activate

Activate this skill when generating any visual artifact:
- LinkedIn graphics, social posts, posters, OG images
- Landing pages, dashboards, marketing pages, app UI
- Presentations, slide decks, one-pagers
- Hero sections, pricing tables, feature grids
- Any HTML/React/CSS artifact where design quality matters

Activate especially when the user signals they want intentional, branded, or non-generic design — phrases like "make it look modern", "not AI slop", "looks like Linear/Stripe", "editorial style", "more design polish", or names a specific aesthetic.

## How to use

### Path A: Brand-matched design

When the user names a brand or wants to match an existing product's look:

1. Pick the closest match from `_brand_catalog.md`
2. Read the full spec from `brands/{slug}.md`
3. Extract the relevant tokens: colors (with semantic roles), typography scale, spacing, component patterns, do/don't rules
4. Apply them to the artifact you're building, faithfully

### Path B: Aesthetic-driven design

When the user names a style or vibe:

1. Pick the closest match from `_aesthetic_catalog.md`
2. Read the full spec from `aesthetics/{slug}.md`
3. Apply the foundations: typography, color palette, spacing, component rules
4. Honor the do/don't rules and quality gates

### Path C: Hybrid

Often the best move is to combine: pull a brand's color/typography from `brands/`, then apply an aesthetic's structural rules from `aesthetics/`. Example: Google's color signal + Linear's layout discipline.

## Loading reference files

Reference files live in `brands/` and `aesthetics/`. Load only the specific file(s) you need — never read the whole library. The catalogs (`_brand_catalog.md` and `_aesthetic_catalog.md`) are the index; the individual `.md` files are the source of truth.

Example flow:
```
User: "Make this LinkedIn graphic look like Linear"
→ Read brands/linear.app.md
→ Apply: --canvas #010102, ink #f7f8f8, accent #5e6ad2, hairline borders, 
  Linear Display font, tight tracking, charcoal panels
```

## Quality gates (non-negotiable)

Before shipping any artifact, verify:

- [ ] **Token fidelity**: colors, fonts, spacing match the reference spec exactly (use the exact hex codes, not approximations)
- [ ] **Hierarchy honored**: the reference's typography scale is preserved (don't substitute generic sizes)
- [ ] **Anti-patterns avoided**: every "don't" rule in the reference is respected
- [ ] **Restraint**: accent colors used as the spec dictates (often once or twice, not everywhere)
- [ ] **No AI-slop tells**: no generic gradients, no Inter/Arial when the spec calls for something specific, no decorative emojis when the spec is editorial

## Anti-rationalization gates

Common excuses for skipping the spec, with rebuttals:

| Excuse | Rebuttal |
|--------|----------|
| "Inter is close enough to the brand font" | No. Use the exact font or its specified fallback. Generic substitutions destroy the signal. |
| "I'll use a gradient on the heading for impact" | Only if the spec uses gradients. Linear and Vercel forbid this. |
| "More color makes it pop" | The spec's restraint IS the design. Adding colors usually weakens it. |
| "I'll add some emojis to make it friendlier" | Check the writing tone. Editorial/professional specs forbid emojis entirely. |
| "The user just wants something modern" | "Modern" without a spec produces generic output. Pick a specific aesthetic from the catalog. |

## Catalogs

See `_brand_catalog.md` for all 71 brand design systems with descriptions.
See `_aesthetic_catalog.md` for all 67 aesthetic styles with descriptions.

## Sources & attribution

- **Brand specs** sourced from [VoltAgent/awesome-design-md](https://github.com/VoltAgent/awesome-design-md) (MIT)
- **Aesthetic specs** sourced from [bergside/awesome-design-skills](https://github.com/bergside/awesome-design-skills) (MIT) via typeui.sh

Both are public, MIT-licensed, and represent publicly visible design tokens. No ownership of any brand's visual identity is claimed by either source repo or this consolidation.
