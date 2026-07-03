# Prompt Catalog + Requirement Gathering

This feature lets the team browse prompt lakehouse metadata without using Vertex AI UI and gives coding agents a consistent way to retrieve prompt context.

## Data Source

BigQuery dataset: `ctoteam.prism_prompt_catalog`

Primary tables:
- `prompt_versions`: SCD Type 2 prompt version metadata
- `prompt_chunks`: chunk metadata and GCS pointers
- `prompt_events`: lifecycle events
- `prompt_attachments`: attachment metadata
- `prompt_approvals`: approval state

Population flow:
1. `scripts/extract_store_prompt.sh <PROMPT_ID> --force`
2. `agents/gcs_prompt_store.py` fetches/extracts the prompt and writes GCS artifacts.
3. `agents/bigquery_prompt_catalog.py` registers versions, chunks, attachments, and events.

## API Routes

The Next.js UI exposes:

- `GET /api/prompt-catalog/search`
- `GET /api/prompt-catalog/[prompt_uid]`
- `GET /api/prompt-catalog/gaps`
- `POST /api/prompt-catalog/classify`

All routes use `GCP_PROJECT_ID` or `GOOGLE_CLOUD_PROJECT`, defaulting to `ctoteam`.

## Requirement Classification

V1 classification is deterministic and auditable. It categorizes prompt signals into:

- business requirement
- technical requirement
- data requirement
- security/compliance
- deployment/operational
- testing/acceptance
- unknown/needs triage

Model-based classification can be added later once the team approves the category contract.

## Gap Detection

The UI flags:

- missing current version
- chunk count mismatch
- zero extracted characters
- non-success status
- missing gold URI
- missing completed lifecycle event
- attachment count mismatch

This catches cases like a prompt version claiming chunks exist while `prompt_chunks` has no matching rows.


## Prompt Submission / Protection Intake

The existing `prompt_versions` and `prompt_chunks` schemas are optimized for the extraction pipeline:

- `prompt_versions` stores version metadata and GCS artifact pointers.
- `prompt_chunks` stores chunk metadata and GCS pointers, but does not store `chunk_text`.

To avoid breaking that pipeline, direct UI submissions use a non-breaking intake table:

`ctoteam.prism_prompt_catalog.prompt_submissions`

The submit API auto-provisions this table if it is missing. It stores:

- full submitted prompt text
- deterministic classification JSON
- categories
- protection level: `none | internal | production | critical`
- status: `draft | submitted | approved | protected`
- raw SHA-256 hash
- submitter and timestamps

API route:

- `POST /api/prompt-catalog/submit`

This table is the portal intake/protection path. A later promotion job can convert approved submissions into the existing bronze/silver/gold extraction flow and SCD `prompt_versions` records.


## Semantic Memory Layer

PRISM uses **unified retrieval**, not forced promotion into one physical storage schema. That means:

- UI submissions remain in `prompt_submissions`.
- Vertex-extracted prompts remain in `prompt_versions` / `prompt_chunks`.
- Agents retrieve from one semantic memory table.

Semantic table:

`ctoteam.prism_prompt_catalog.prompt_semantic_memory`

This table stores:

- `source_type` and `source_id`
- `prompt_uid`
- text used for retrieval
- text hash
- embedding vector
- embedding model identifier
- categories, status, and protection metadata

V1 uses `local-hash-embedding-v1` so indexing and retrieval are deterministic, auditable, and zero-cost. The schema is designed so the embedding source can later be replaced with Vertex AI or BigQuery ML embeddings.

Agent integration:

```bash
python3 agents/core/orchestrator.py \
  --task "Review relevant PRISM prompt governance context" \
  --semantic-query "security deployment BigQuery prompt governance" \
  --dry-run
```

The context manager retrieves ranked semantic memory and appends it to the model context.
