# PRISM Core Coding Agent Layer

This folder contains the reusable orchestration layer for coding-agent work.

## Files

- `context_manager.py`: loads saved prompt text and selected project files with size limits.
- `model_router.py`: resolves model routes such as `glm5`, `grok43`, and `grok420_reasoning`.
- `orchestrator.py`: CLI that builds context, calls a selected model route, and writes evidence to `reports/`.

## Authentication

Vertex MaaS routes use Google Cloud auth through `gcloud`:

```bash
gcloud auth login --no-launch-browser
gcloud auth application-default login --no-launch-browser
gcloud config set project ctoteam
```

No `XAI_API_KEY` is needed when calling Grok through Vertex AI.

## Dry Run

Build context and write evidence without calling a model:

```bash
python3 agents/core/orchestrator.py \
  --task "Review agents and propose fixes" \
  --model-route grok43 \
  --prompt-file prompts/prompt-0 \
  --context-root agents \
  --dry-run
```

## Live Model Run

Call Grok 4.3 through Vertex AI:

```bash
python3 agents/core/orchestrator.py \
  --task "Review the Vertex MaaS runner and propose next coding-agent improvements" \
  --model-route grok43 \
  --prompt-file prompts/prompt-0 \
  --context-root agents/runners \
  --context-root agents/core
```

Call GLM 5:

```bash
python3 agents/core/orchestrator.py \
  --task "Generate implementation plan" \
  --model-route glm5 \
  --prompt-file prompts/prompt-0 \
  --context-root agents
```

## Evidence Output

The orchestrator writes:

- `reports/orchestrator/context_manifest_*.json`
- `reports/orchestrator/composed_prompt_*.md`
- model response `.md` and raw `.json` under the selected route output directory, unless overridden with `--output-dir`.
