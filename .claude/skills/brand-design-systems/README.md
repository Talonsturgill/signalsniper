# Brand Design Systems · Claude Skill

A consolidated design system skill that gives Claude (and other coding agents) instant access to:

- **71 brand design systems** — Linear, Vercel, Stripe, Claude, Notion, Apple, Tesla, Ferrari, etc. Real production tokens, not approximations.
- **67 aesthetic styles** — editorial, brutalism, glassmorphism, modern, mono, neon, claymorphism, etc.

Sourced from [VoltAgent/awesome-design-md](https://github.com/VoltAgent/awesome-design-md) and [bergside/awesome-design-skills](https://github.com/bergside/awesome-design-skills) (both MIT). Consolidated and indexed for single-skill use.

## Why this skill

Default agent design output is generic — Inter font, purple gradients, predictable card layouts. This skill gives the agent a real spec to follow. Tell it "make this look like Linear" or "use editorial style" and it will pull the actual color tokens, typography rules, spacing system, and anti-patterns instead of guessing.

## Install

### Claude.ai (Pro/Max)

1. Go to **Settings → Capabilities → Skills**
2. Click **Upload skill**
3. Upload the `brand-design-systems.zip`
4. Activate it

The skill auto-triggers on visual artifact requests. Or invoke explicitly: *"Use the brand-design-systems skill and apply Linear's design language to this graphic."*

### Claude Code

```bash
# From project root
mkdir -p .claude/skills
cp -r brand-design-systems .claude/skills/

# Or globally
mkdir -p ~/.claude/skills
cp -r brand-design-systems ~/.claude/skills/
```

### Cursor

```bash
mkdir -p .cursor/skills
cp -r brand-design-systems .cursor/skills/
```

### Other agents (Codex, Gemini CLI, OpenCode, etc.)

The `SKILL.md` is plain markdown with standard agent-skills frontmatter — point your agent at it however your tool loads skills.

## Usage examples

```
"Build me a LinkedIn graphic about agent-skills. Apply Linear's design language."
→ Reads brands/linear.app.md, uses #010102 canvas, #5e6ad2 accent, Linear Display font

"Make a landing page hero in editorial style."
→ Reads aesthetics/editorial.md, applies serif typography, structured grid

"Stripe-style pricing table but with our brand colors"
→ Reads brands/stripe.md for layout/typography, swaps in your colors
```

## Structure

```
brand-design-systems/
├── SKILL.md               # Master skill file (entry point)
├── README.md              # This file
├── _brand_catalog.md      # Index of all 71 brands, categorized
├── _aesthetic_catalog.md  # Index of all 67 aesthetics
├── brands/                # Full DESIGN.md per brand
│   ├── linear.app.md
│   ├── vercel.md
│   ├── claude.md
│   └── ... (71 files)
└── aesthetics/            # Full SKILL.md per aesthetic
    ├── editorial.md
    ├── modern.md
    ├── brutalism.md
    └── ... (67 files)
```

## Updating

The source repos update regularly. To pull fresh specs:

```bash
git clone https://github.com/VoltAgent/awesome-design-md.git
git clone https://github.com/bergside/awesome-design-skills.git
# Copy new/updated DESIGN.md files into brands/ and SKILL.md files into aesthetics/
# Regenerate _brand_catalog.md and _aesthetic_catalog.md with the included script
```

## License

MIT. Same license as both source repos. Brand identities remain property of their respective owners.
