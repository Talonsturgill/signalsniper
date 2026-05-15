# AI All Stars Weekly · May 7–13, 2026
# Code highlights — one snippet per featured project

## 1. proofshot — @JBerthom
> The record/stop lifecycle: ProofShot wraps agent-browser with timestamped capture so every browser action gets bundled into a proof artifact with compact element refs.
```bash
# Open browser, begin recording, capture server logs
proofshot start --run "npm run dev" --port 3000 --description "Login form verification"

# Agent drives the browser using compact element refs
agent-browser open http://localhost:3000/login
agent-browser fill @e2 "test@example.com"
agent-browser click @e5
agent-browser screenshot ./proofshot-artifacts/step-login.png

# Stop: bundle video + screenshots + errors into proof artifact
proofshot stop
```

## 2. react-doctor — @aidenybai
> One install command writes agent-aware rule files for Claude Code, Cursor, Codex, and 50+ other coding agents so they generate idiomatic React by default.
```bash
# Install as a coding agent skill (auto-detects which agents are present)
npx -y react-doctor@latest install

# Skip prompts, write rules for all detected agents immediately
npx -y react-doctor@latest install --yes

# Run a one-shot health scan of your codebase (returns a 0 to 100 score)
npx -y react-doctor@latest .
```

## 3. oMLX — @jundotkim
> The tiered KV cache: hot blocks stay in RAM, cold blocks spill to SSD in safetensors format, and the prefix cache rebuilds on matching prefix across restarts.
```bash
omlx serve --model-dir ~/models \
  --paged-ssd-cache-dir ~/.omlx/cache \
  --hot-cache-max-size 20% \
  --max-model-memory 32GB \
  --max-concurrent-requests 16 \
  --api-key your-secret-key
```

## 4. OpenHuman — @senamakel
> The global memory client bootstraps asynchronously from the workspace config directory, giving every CLI subcommand a single shared MemoryClientRef backed by SQLite.
```rust
async fn create_memory_client() -> Result<crate::openhuman::memory::MemoryClientRef> {
    let config = crate::openhuman::config::Config::load_or_init()
        .await
        .unwrap_or_default();
    crate::openhuman::memory::global::init(config.workspace_dir)
        .map_err(anyhow::Error::msg)
}
```

## 5. Needle — @hmunachii
> The 26M-param attention-only model: no feedforward layers, load checkpoint, call generate with a tool schema, get a function call back.
```python
from needle import SimpleAttentionNetwork, load_checkpoint, generate, get_tokenizer

params, config = load_checkpoint("checkpoints/needle.pkl")
model = SimpleAttentionNetwork(config)  # 12 encoder + 8 decoder layers, no FFN
tokenizer = get_tokenizer()

result = generate(
    model, params, tokenizer,
    query="What's the weather in San Francisco?",
    tools='[{"name":"get_weather","parameters":{"location":"string"}}]',
    stream=False,
)
```
