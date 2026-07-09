# Creator dossier — 2026-07-09

## Who
- **Name:** Safi Shamsi
- **X handle:** @safishamsii
- **LinkedIn:** https://uk.linkedin.com/in/safi-shamsi (title: "Founder & CEO @Graphify Labs, YC S26")
- **GitHub:** https://github.com/safishamsi
- **Company:** Graphify Labs (Y Combinator S26). Previously AI Research Engineer at Valent, London.
- **Location (shareable):** London, United Kingdom.

## One-line bio
London builder, MSc Data Science (Distinction, University of Birmingham), came out of medical AI and knowledge-graph research and turned that into graphify: a knowledge-graph skill for AI coding assistants.

## Project (the subject)
**graphify** — an open-source skill for Claude Code, Codex, Cursor, Gemini CLI and others that turns any folder of code, docs, schemas, papers, images or videos into a queryable knowledge graph. You type `/graphify .` and it maps your project; you ask it questions in plain English and it walks a real graph to answer.

- **Repo:** https://github.com/safishamsi/graphify (MIT, Python)
- **Homepage:** https://graphifylabs.ai/
- **Stars:** more than 76,000 (star-history 76.6k, skillsllm 76.3k as of 2026-07-09), climbing fast on the daily trending board (~+850 the day of this run, single-source, not shipped).
- **Downloads:** 2.4M+ PyPI (single-source, not shipped as a numeral).

## What makes it different (the spine)
It does NOT embed your code into a vector store. It parses locally with **tree-sitter AST** (deterministic, no LLM, nothing leaves your machine) into a **real graph you traverse** — and every edge is labeled **EXTRACTED** (explicit in the source) or **INFERRED** (derived), so you can tell what it read from what it guessed. Ask `what connects attention to the optimizer?` and you get an actual path back, not 200 grep hits.

Stack under the hood: tree-sitter (parsing), NetworkX (graph), Leiden clustering (communities / the "god node").

## Voice notes (for tone alignment)
Ships fast, posts install one-liners and milestone updates, celebrates traction publicly. Comes from a research background (MICAD 2025, medical knowledge-graph RAG) so the "graph, not embeddings" stance is a real conviction, not marketing. A tribute that shows the tool actually answering a question — in graphify's own green-on-dark colors — is exactly what an engaged founder quote-posts.

## LinkedIn tag
- name: Safi Shamsi
- url: https://uk.linkedin.com/in/safi-shamsi

## Why-this-one angle (kept distinct from the caption)
The creator arc: a medical-AI / knowledge-graph researcher out of Birmingham who took the "graph, not embeddings" idea from healthcare into dev tooling, shipped it as a skill any coding agent can install, and rode it into YC S26. The caption leads with the star count and the capability; the Why-this-one leads with the builder's path.

## Latest activity
Active releases (repo shows v-tagged branches through v8); trending on the GitHub daily board on the run date.
