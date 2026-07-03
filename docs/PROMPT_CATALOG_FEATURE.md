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
