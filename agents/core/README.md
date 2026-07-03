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

## Auto Model Selection

The orchestrator defaults to `--model-route auto`. Auto mode chooses a logical route first, then resolves that route to the currently configured physical model in `models.json`.

Logical route map for v1:

| Logical route | Current physical model | Use case |
| --- | --- | --- |
| `fast_code` | `xai/grok-4.3-fast` | Simple code generation, CRUD, scaffolds, straightforward refactors |
| `balanced_code` | `xai/grok-4.3` | General coding, review, and moderate architecture work |
| `hard_reasoning` | `xai/grok-4.3` | Security, architecture, hard debugging, production risk |
| `large_context` | `gemini-3.5-flash` | Large context runs that exceed smaller model windows |
| `data_report` | `gemini-3.5-flash` | SQL, BigQuery, ETL, reports, summarization |
| `local_edit` | `gpt-5.3-codex` | Registered placeholder for future direct-edit flows; not auto-selected yet |

GLM-5 is deferred until it is added to `models.json`.

The selector computes:

- complexity score, clamped to 1-10
- risk score, clamped to 1-10
- estimated tokens from task + prompt + loaded context
- feasibility exclusions from `models.json` max token limits
- estimated chosen-model and alternative-model costs
- scorecard signals with point values

Safety precedence:

```text
risk floor > token feasibility > cost-mode bias > base complexity route
```

Cost mode:

```bash
--cost-mode low       # bias down one tier only when risk < 6
--cost-mode balanced  # no bias
--cost-mode best      # bias up one tier when feasible
```

By default it uses the deterministic local selector:

```bash
python3 agents/core/orchestrator.py   --task "Review the agents for security and architecture risks"   --model-route auto   --selector-mode heuristic   --cost-mode balanced   --prompt-file prompts/prompt-0   --context-root agents   --dry-run
```

Use Gemini as a JSON selector only when you want model-assisted routing. Gemini receives the computed metrics and must choose from feasible logical routes:

```bash
python3 agents/core/orchestrator.py   --task "Choose the best model and review this code for production risks"   --model-route auto   --selector-mode gemini   --selector-model gemini-3.5-flash   --cost-mode balanced   --prompt-file prompts/prompt-0   --context-root agents   --dry-run
```

Selector evidence is written to:

```text
reports/orchestrator/model_selection_*.json
```


## BigQuery Context

The orchestrator can add prompt catalog metadata from BigQuery:

```bash
python3 agents/core/orchestrator.py \
  --task "Summarize prompt catalog context" \
  --bigquery-prompt-uid vertexai:3381323161097207808 \
  --context-root agents/runners \
  --dry-run
```

This requires `google-cloud-bigquery` in the Python runtime. On an externally managed host, use a virtual environment instead of system pip:

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install google-cloud-bigquery requests
```

If BigQuery is unavailable, dry-runs continue and record `bigquery_context_status` in the context manifest.
