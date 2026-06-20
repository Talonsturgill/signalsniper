# Code from the week — Issue 7 (2026-06-14 to 2026-06-20)

One verbatim snippet per pick. LMCache's KV-offload config lives in the Tactical Lesson section of the post, so it is not repeated here.

## rlm — the same call, recursion underneath

```python
from rlm import RLM

rlm = RLM(
    backend="openai",
    backend_kwargs={"model_name": "gpt-5-nano"},
    verbose=True,
)

print(rlm.completion("Print the first 100 powers of two, each on a newline.").response)
```
Source: README, https://github.com/alexzhang13/rlm

## superpowers — the trigger is in the front-matter

```yaml
---
name: brainstorming
description: "You MUST use this before any creative work - creating features, building components, adding functionality, or modifying behavior. Explores user intent, requirements and design before implementation."
---
```
Source: skills/brainstorming/SKILL.md, https://github.com/obra/superpowers

## ctx — scan, score, dry-run, then install

```bash
ctx-scan-repo --repo . --recommend   # scored skill/agent/MCP bundle for this repo
ctx-harness-install text-to-cad --dry-run   # inspect before anything runs
ctx-harness-install text-to-cad             # install after reviewing the plan
```
Source: README, https://github.com/stevesolun/ctx

## ollama — one line to a local backend

```bash
ollama launch claude --model qwen3.5:35b-a3b-coding-nvfp4
```
Source: https://ollama.com/blog/mlx
