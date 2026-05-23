# Code from the week — Issue 3 archive

## autoresearch by @karpathy
Source: https://github.com/karpathy/autoresearch (README/protocol)

```bash
uv run train.py
# train.py prints val_bpb (bits-per-byte, lower = better) at completion.
# Agent reads score, compares to baseline. If improved: keep the edit.
git checkout train.py
# Fixed 5-minute wall clock per run makes every experiment directly comparable.
```

## oh-my-pi by @_can1357
Source: https://github.com/can1357/oh-my-pi (README, Hashline feature #09)

```bash
npx oh-my-pi
# Hashline: model references a content hash anchor, not a line number.
# If the file shifts, the anchor resolves to the new location.
# If the content no longer exists, the patch is rejected before application.
# 61% fewer output tokens measured on Grok 4 Fast.
```

## code-review-graph by @tirth_8205
Source: https://github.com/tirth8205/code-review-graph (graph.py)

```python
def get_impact_radius(
    self, changed_files: list[str],
    max_depth: int = MAX_IMPACT_DEPTH,
    max_nodes: int = MAX_IMPACT_NODES,
) -> dict[str, Any]:
    # BFS from changed files to find all impacted nodes within depth N.
    # SQL path: WITH RECURSIVE impacted(node_qn, depth) AS (
    #   SELECT qn, 0 FROM _impact_seeds UNION
    #   SELECT e.target_qualified, i.depth+1 FROM impacted i
    #   JOIN edges e ON e.source_qualified = i.node_qn WHERE i.depth < ? )
```

## statewright by @azurewraith
Source: https://github.com/statewright/statewright (README, state machine config)

```json
"planning":     { "allowed_tools": ["Read","Grep","Glob"],
                  "max_iterations": 8,
                  "on": { "READY": "implementing" } },
"implementing": { "allowed_tools": ["Read","Edit","Write"],
                  "max_edit_lines": 20, "max_files_per_state": 3,
                  "on": { "DONE": "testing" } },
"testing":      { "allowed_tools": ["Read","Bash"],
                  "allowed_commands": ["pytest","cargo test","npm test"],
                  "on": { "PASS": { "target": "completed",
                                    "guard":  "tests_passed" } } }
```

## semble by @TvDongen
Source: https://github.com/MinishLab/semble (src/semble/search.py)

```python
def _rrf_scores(scores: dict[Chunk, float]) -> dict[Chunk, float]:
    """Convert raw scores to RRF weights: 1 / (k + rank)."""
    ranked = sorted(scores, key=lambda c: -scores[c])
    return {chunk: 1.0 / (_RRF_K + rank)
            for rank, chunk in enumerate(ranked, 1)}

combined = {chunk: alpha * normalized_semantic.get(chunk, 0.0)
                 + (1-alpha) * normalized_bm25.get(chunk, 0.0)
            for chunk in all_candidates}
```
