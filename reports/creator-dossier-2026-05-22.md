# Creator Dossier — 2026-05-22

## Subject
**Andrej Karpathy** (@karpathy)

## Project
`karpathy/autoresearch` — AI agents running research on single-GPU nanochat training automatically.

- URL: https://github.com/karpathy/autoresearch
- Stars: 82.7k and climbing
- License: MIT
- Latest motion: trending #1 in Python last 24h
- Lineage: simplified single-GPU `nanochat` plus agent driver loop

## One-line bio
Founder of Eureka Labs, formerly Director of AI at Tesla and a founding member of OpenAI. Probably the most-followed individual AI researcher on the open-source side, in part because of the way he ships.

## Voice notes
Karpathy writes the way he builds: small, self-contained, declarative. Every public project ships as one or two readable files. Markdown over YAML. He prefers `program.md` instructions to a config schema. His tweet voice is dry and observational, frequently leaning on a single contrast ("meat computers" vs. agent loops). Tribute copy should imitate that compression: short clauses, concrete nouns, no jargon padding.

## Why the project trends right now
The README's opening is a quotable line that hit X within hours of the repo going up:

> One day, frontier AI research used to be done by meat computers in between eating, sleeping, having other fun, and synchronizing once in a while using sound wave interconnect in the ritual of "group meeting". That era is long gone.

The line landed because the project ships the joke. The agent edits `train.py`, trains nanochat for exactly 5 minutes, scores with `val_bpb`, keeps the win or reverts, and goes again. About 12 experiments per hour. About 100 experiments while you sleep. The science of architecture search done by a script that runs all night.

## What's novel
- **Autonomous research loop as a primitive.** Most agent demos talk to an API. This one mutates a `train.py`, runs CUDA, reads a loss, makes a decision. Closed loop, no human in it.
- **Fair-comparison protocol.** Fixed 5-minute wall clock per experiment (excluding compile and warmup). Architecture-agnostic metric (`val_bpb`). The protocol IS the contribution.
- **One file. One GPU.** The whole iteration target is a single Python file. The whole infrastructure target is a single NVIDIA card. Anyone with a 4090 can run it tonight.
- **Markdown instructions.** `program.md` is the agent's brief. Not YAML, not JSON. Karpathy keeps treating natural language as the right interface to the model.

## Prior work that explains the move
- `nanoGPT` — one-file GPT trainer, ~39k stars
- `llm.c` — LLM training in pure C, ~30k stars
- `micrograd` — autograd in 100 lines, used in his YouTube series
- `nanochat` — the trainer this loop drives
- The "Zero to Hero" YouTube series, which has a generation of ML engineers learning from his single-file `lecture.py` style

autoresearch is the next move in the same direction: keep the kernel tiny, push the iteration outside it.

## Geography
San Francisco / Bay Area. Eureka Labs HQ.

## The metric we lead with
Star count crossed 82k in the first 72 hours. That number is the public signal. The private signal is 100 experiments per night — and that's the angle the Why-this-one in Gmail can use without colliding with the X caption.

## Angles for the tribute (writer agent should pick distinct ones per surface)
1. **The loop itself.** Agent edits `train.py`, trains 5 min, scores `val_bpb`, keeps or reverts. Diagram-worthy.
2. **The protocol.** Fixed 5-min budget makes apples-to-apples comparison possible across architectures.
3. **100 experiments overnight.** Numbers tell the whole story.
4. **One-file pedagogy.** The Karpathy through-line. Small enough to read in one sitting.
5. **End of "meat computers".** His framing of the death of the group meeting as a research method.

## Source attribution to leave intact
- The README quote belongs to Karpathy. Don't lift it verbatim into scene copy. Paraphrase.
- The 5-minute and 100-experiment numbers come from the README and are safe to repeat.
- `val_bpb` is the metric in code; treat it as the technical handle the audience earns by the close.
