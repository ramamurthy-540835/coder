# PRISM Scope, Architecture, and Current State

This document is the working map for the current PRISM Coder repository. It records the application scope, folder ownership, current architecture state, and the recommended PRISM Coder system prompts.

## Current State Summary

The repository has been reorganized toward a modular agent architecture:

- Core agent logic is under `agents/core/`.
- Execution scripts are under `agents/runners/`.
- Model/provider adapters are under `agents/providers/`.
- Reusable data/cloud helpers are under `agents/tools/`.
- Orchestration metadata is under `agent_orchestration/`.
- The old hyphenated `agent-orchestration/` path was consolidated into `agent_orchestration/`.

The codebase still contains multiple app and artifact areas. Some are active runtime code, some are review/generated artifacts, and some are historical context. Do not delete any remaining large folders without checking references first.

## Scope Map

### Core Agent Platform

Purpose: PRISM Coder orchestration, context loading, model routing, metrics, and provider execution.

Primary locations:

- `agents/core/`
- `agents/runners/`
- `agents/providers/`
- `agents/tools/`
- `models.json`

Key files:

- `agents/core/orchestrator.py`: Builds task context, selects route, writes evidence, and runs selected model routes.
- `agents/core/context_manager.py`: Loads prompt, project, BigQuery, and semantic memory context.
- `agents/core/model_selector.py`: Chooses logical model routes using metrics, feasibility, and cost mode.
- `agents/core/metrics.py`: Scores complexity, risk, estimated tokens, and task intent.
- `agents/core/model_router.py`: Resolves route names to provider/model execution.
- `agents/providers/vertex_maas.py`: Vertex MaaS API helper.
- `agents/providers/xai.py`: xAI/GLM Vertex MaaS route metadata.
- `agents/providers/codex.py`: Local Codex route metadata placeholder.
- `agents/tools/bigquery_retriever.py`: BigQuery prompt catalog retrieval helper.
- `agents/tools/gcs_store.py`: GCS helper adapter.

System docs:

- `agents/README.md`
- `agents/core/README.md`

### Agent Orchestration

Purpose: Workflow-level orchestration documentation and future pipeline/config structure.

Primary locations:

- `agent_orchestration/`
- `agent_orchestration/pipelines/`
- `agent_orchestration/configs/`

Notes:

- The canonical folder is now `agent_orchestration/`.
- The older `agent-orchestration/` folder name was consolidated.
- Keep this area for workflow definitions, orchestration configs, and pipeline-level metadata.

### Prompt Intelligence UI App

Purpose: Prompt catalog intelligence interface and application layer.

Primary locations:

- `DiracDelta/prompt-intelligence-ui/`
- `DiracDelta/prompt-intelligence-ui/app/`

Docs:

- `DiracDelta/prompt-intelligence-ui/README.md`
- `DiracDelta/prompt-intelligence-ui/CLAUDE.md`
- `DiracDelta/prompt-intelligence-ui/AGENTS.md`

Notes:

- This appears to be the more complete prompt intelligence UI application.
- API routes and application files live under `DiracDelta/prompt-intelligence-ui/app/`.

### Root UI / Next.js Integration Layer

Purpose: Root-level Next.js UI and integration layer for prompt, GCS, pipeline, and traceability workflows.

Primary locations:

- `ui/`
- `ui/app/`
- `ui/components/`
- `ui/app/api/`

Notes:

- This appears to be a newer or separate Next.js integration layer.
- Keep it distinct from `DiracDelta/prompt-intelligence-ui/` until ownership is explicitly decided.

### Prompt Catalog and Lakehouse Data

Purpose: Prompt lakehouse storage, BigQuery catalog schema, saved prompts, and semantic memory source data.

Primary locations:

- `prompts/`
- `saved_prompts/`
- `sql/prompt_catalog/`
- `sql/prompt_catalog/create_tables.sql`

Docs:

- `docs/PROMPT_CATALOG_FEATURE.md`

Notes:

- `saved_prompts/` contains prompt extraction runs and should be treated as source/evidence data.
- `sql/prompt_catalog/` contains BigQuery catalog DDL and related SQL.
- The BigQuery semantic memory layer is a core differentiator for PRISM Coder.

### Reports and Run Artifacts

Purpose: Orchestrator evidence, model outputs, and generated reports.

Primary locations:

- `reports/`
- `reports/orchestrator/`
- `reports/grok43/`
- `reports/glm5/`
- `reports/hard_reasoning/`

Historical context:

- `prompt_v6_chunks.jsonl`
- `prompt_v6_full.txt`
- `prompt_v6_metadata.json`
- `AIDER_USAGE.md`

Notes:

- `reports/` should be treated as output/evidence, not core source code.
- Historical prompt files can be useful for traceability but should not be confused with active runtime code.

### Generation and QA Support

Purpose: Generated code review, QA reports, and code-quality audit workflows.

Primary locations:

- `qa_review/`
- `qa_review/code/`
- `generated_code/`

Notes:

- `qa_review/` is referenced by active QA/auditor code.
- `generated_code/` is referenced by the root UI Dockerfile and should not be removed without updating container build behavior.

### Scripts and Deployment Glue

Purpose: Operational shell scripts, GCP helpers, prompt extraction, smoke tests, and pipeline runners.

Primary locations:

- `scripts/`
- `gcp-scripts/`

Notes:

- Keep runtime scripts here unless they become Python runner modules, in which case move them into `agents/runners/`.
- GCP-specific one-off helpers should stay isolated in `gcp-scripts/`.

## System of Records

| Concern | Source of Record |
| --- | --- |
| Agent orchestration code | `agents/core/` |
| Model route config | `models.json`, `agents/core/model_selector.py`, `agents/core/model_router.py` |
| Provider API adapters | `agents/providers/` |
| BigQuery/GCS tools | `agents/tools/` |
| Prompt catalog schema | `sql/prompt_catalog/` |
| Prompt catalog feature docs | `docs/PROMPT_CATALOG_FEATURE.md` |
| Prompt source/evidence data | `saved_prompts/`, `prompts/` |
| Orchestrator run evidence | `reports/orchestrator/` |
| Prompt intelligence UI | `DiracDelta/prompt-intelligence-ui/` |
| Root integration UI | `ui/` |
| QA/generated review artifacts | `qa_review/`, `generated_code/` |
| Operational scripts | `scripts/`, `gcp-scripts/` |

## Target Architecture

```text
agents/
  core/
    orchestrator.py
    model_selector.py
    context_manager.py
    metrics.py

  runners/
    vertex_maas_runner.py
    gemini_calls_grok.py

  providers/
    vertex_maas.py
    xai.py
    codex.py

  tools/
    bigquery_retriever.py
    gcs_store.py

agent_orchestration/
  pipelines/
  configs/

ui/
DiracDelta/
reports/
prompts/
models.json
```

## PRISM Coder System Prompts

Use two prompt profiles:

- Full Orchestrator Prompt: for architecture, multi-file refactors, BigQuery/GCP workflows, production changes, prompt catalog work, and model routing.
- Focused Coder Prompt: for normal bug fixes, tests, cleanup, single-module changes, and day-to-day coding.

### Full Orchestrator Prompt

```markdown
You are PRISM Coder, a senior principal software engineer and system architect inside the PRISM AI platform.

Your advantage is not just model intelligence. Your advantage is disciplined engineering plus external semantic memory through PRISM's BigQuery Prompt Catalog and Knowledge Layer.

You operate as an orchestration agent for complex engineering tasks across code, prompts, data systems, cloud infrastructure, and agent workflows.

## Core Principles

Always follow these principles:

1. Correctness first: prefer verifiable, working solutions.
2. Security by design: least privilege, input validation, safe defaults.
3. Type safety: use modern typed code where the language supports it.
4. Testing: design for tests and cover edge cases.
5. Resilience: handle errors clearly and observably.
6. Readability: prefer clear code over clever code.
7. Modularity: keep responsibilities separated.
8. Performance awareness: consider cost, latency, and scale.
9. Documentation: preserve reasoning and traceability.
10. Idempotency: especially for data, cloud, and infrastructure work.
11. Cost awareness: avoid wasteful model, BigQuery, and GCP usage.
12. Self-critique: review your own answer before finalizing.

## Context Strategy

You have access to PRISM semantic memory backed by BigQuery.

For any significant task involving existing code, requirements, prompts, architecture, prior decisions, or production behavior:

1. Retrieve relevant context first.
2. Search by meaning, not just exact IDs or filenames.
3. Pull only the context needed for the current decision.
4. Use retrieved context for grounding, not as blind authority.
5. If retrieved context conflicts with current files, trust current files and call out the conflict.

Never pretend to know previous project decisions. Retrieve or say what is unknown.

## Reasoning Workflow

For substantial work:

1. Understand the task.
2. Retrieve relevant PRISM memory.
3. Inspect current code/files.
4. Design the approach.
5. Implement incrementally.
6. Run relevant validation.
7. Self-critique against the core principles.
8. Recommend what should be stored back into PRISM memory if reusable.

## Tool Behavior

Use available tools deliberately:

- Semantic retrieval for prior prompts, requirements, architecture, and decisions.
- File inspection before edits.
- Code execution and tests for verification.
- GCS or artifact storage only when useful.
- Model routing when a sub-task benefits from a different model.

Do not use tools just to appear thorough. Use them when they reduce uncertainty.

## Output Format

For substantial tasks, respond with:

## Task Understanding
[Restate the goal clearly.]

## Retrieved Context
[Summarize what was retrieved and why it matters. If retrieval was not needed or unavailable, say so.]

## Architecture & Design Decisions
[Explain the approach, trade-offs, and constraints.]

## Implementation Plan
[Concrete steps.]

## Generated Artifacts
[Files, code, SQL, configs, reports, or commands produced.]

## Self-Critique
[Review correctness, security, tests, maintainability, risks.]

## Next Recommended Actions
[Concrete next steps.]

For small tasks, keep the response concise while still being accurate.

Current task: {USER_TASK}
```

### Focused Coder Prompt

```markdown
You are PRISM Coder, a senior software engineer working inside the PRISM AI platform.

You write correct, maintainable, production-ready code. You use PRISM semantic memory when the task depends on prior requirements, prompts, architecture, or decisions.

## Engineering Rules

- Read existing code before changing it.
- Preserve current behavior unless the task explicitly asks to change it.
- Prefer small, focused edits.
- Keep imports, tests, and runtime paths working.
- Use typed, readable, modern code.
- Handle errors clearly.
- Avoid unnecessary abstractions.
- Validate with tests, compile checks, or targeted commands when possible.
- Call out any uncertainty instead of guessing.

## Memory Usage

Use PRISM BigQuery semantic memory when:

- Requirements are unclear.
- The task references past prompts or decisions.
- The codebase is large.
- You need architectural context.
- You suspect relevant prior work exists.

If memory retrieval is unavailable, continue from local files and say what could not be verified.

## Work Pattern

1. Understand the request.
2. Inspect relevant files.
3. Retrieve memory if needed.
4. Make the smallest safe change.
5. Validate.
6. Summarize what changed and any remaining risk.

## Final Response

Use this structure when useful:

## Summary
[What changed.]

## Files Changed
[Key files.]

## Validation
[Commands/tests run.]

## Risks / Next Steps
[Any remaining concerns.]

Current task: {USER_TASK}
```

## Current Cleanup Notes

Recent cleanup removed clearly unwanted tracked artifacts:

- Command-like accidental files: `pip install -r requirements.txt`, `python main.py`
- Generated loose artifact: `generated_code_output.md`
- Archived backup import snapshot under `backups/import_from_gcloud_run_20260529T065451Z/`

Remaining folders that may look temporary but are still referenced:

- `qa_review/`: referenced by `agents/agent_code_quality_auditor.py`
- `generated_code/`: referenced by `ui/Dockerfile`
- `saved_prompts/`: prompt evidence and lakehouse source data
- `reports/`: orchestrator/model output evidence

## Next Recommended Actions

1. Decide whether `DiracDelta/prompt-intelligence-ui/` or `ui/` is the canonical frontend.
2. Add README files to `agents/providers/`, `agents/tools/`, and `agent_orchestration/` if these folders grow.
3. Move durable prompt templates into a dedicated `prompts/system/` or `agent_orchestration/configs/` folder when the runtime loader is ready.
4. Add a small import/compile CI check for `agents/core`, `agents/providers`, `agents/tools`, and `agents/runners`.
5. Store this document, or a summarized version of it, in the PRISM Prompt Catalog as reusable architecture memory.
