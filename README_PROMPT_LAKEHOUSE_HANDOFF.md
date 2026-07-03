# PRISM Prompt Lakehouse Handoff (Launch Guide)

This document is the operational handoff for running the Prompt Lakehouse pipeline end-to-end.

## Scope

This pipeline does all of the following:
1. Fetches a saved prompt from Vertex AI Dataset API by `prompt_id`.
2. Extracts deterministic prompt content (system/user/model/attachments).
3. Writes local medallion artifacts (bronze/silver/gold).
4. Uploads artifacts to GCS under `saved-prompts/<prompt_id>/...`.
5. Registers run/chunks/attachments/events into BigQuery (`prism_prompt_catalog`) with SCD Type 2 versioning.

## Entry Point

Run this from:
`/home/appadmin/projects/Ram_Projects/DiracDelta/gcloud_run`

```bash
./scripts/extract_store_prompt.sh <PROMPT_ID> [--force]
```

Example:
```bash
./scripts/extract_store_prompt.sh 3381323161097207808 --force
```

## Core Components

- Extraction agent:
  - `agents/gcs_prompt_store.py`
- BigQuery catalog agent:
  - `agents/bigquery_prompt_catalog.py`
- Driver script:
  - `scripts/extract_store_prompt.sh`
- Schema:
  - `sql/prompt_catalog/create_tables.sql`

## Local Artifact Layout

Generated under:
`saved_prompts/<prompt_id>/runs/<run_id>/`

- `bronze/`
  - `raw.json`
  - `source_metadata.json`
- `silver/`
  - `raw_clean.json`
  - `system.md`
  - `user_messages/`
  - `model_messages/`
  - `chunks/chunk_*.md`
  - `attachments/*.json` (metadata)
  - `attachments_raw/*` (binary/text payload files)
  - `final_assembled.md`
- `gold/`
  - `master.md` (default = business-clean)
  - `master_business.md` (system + USER-only)
  - `master_full.md` (system + all messages)
  - `extraction_report.json`
  - `prompt_summary.json`

## GCS Layout

Uploaded under:
`gs://agentproject/saved-prompts/<prompt_id>/`

- `bronze/<run_id>/...`
- `silver/<run_id>/...`
- `gold/<run_id>/...`
- `gold/latest.json`

## BigQuery Tables

Dataset:
`ctoteam.prism_prompt_catalog`

Main tables:
- `prompt_versions` (SCD Type 2)
- `prompt_chunks`
- `prompt_attachments`
- `prompt_events`

Views:
- `latest_runs`
- `extraction_status`
- `chunk_distribution`

## Business Prompt Quality Mode

Current default for downstream coding prompt is business-clean:
- `gold/master.md` == `gold/master_business.md`
- excludes model-response noise
- best default for Gemini 3.5 execution quality

Full archive prompt remains available:
- `gold/master_full.md`

## Attachment Strategy (BigQuery-ready)

For each attachment:
- metadata JSON is saved in `silver/attachments/*.json`
- actual payload file is saved in `silver/attachments_raw/*`
- BigQuery `prompt_attachments.gcs_uri` points to `attachments_raw/...` when available

This enables downstream multimodal workflows over real files.

## Validation Commands

### 1) Check latest version row
```bash
bq query --use_legacy_sql=false "
SELECT prompt_uid, version_number, run_id, repeat_mode, is_current, status, valid_from, valid_to
FROM \`ctoteam.prism_prompt_catalog.prompt_versions\`
WHERE prompt_uid = 'vertexai:<PROMPT_ID>'
ORDER BY version_number DESC
LIMIT 5
"
```

### 2) Check latest run attachments
```bash
bq query --use_legacy_sql=false "
SELECT run_id, attachment_id, mime_type, local_path, gcs_uri, size_bytes, created_at
FROM \`ctoteam.prism_prompt_catalog.prompt_attachments\`
WHERE run_id = '<RUN_ID>'
ORDER BY created_at DESC
"
```

### 3) Check raw payload files in GCS
```bash
gsutil ls gs://agentproject/saved-prompts/<PROMPT_ID>/silver/<RUN_ID>/attachments_raw/
```

## Known Constraints

- Current bucket region is `ASIA-SOUTH1` while BigQuery dataset is `US`.
- BigQuery object-table/BQML multimodal over GCS may require region alignment.
- Core extraction + catalog registration works regardless.

## Optional BigQuery Multimodal Layer

If enabling BigQuery-native multimodal inference, add SQL assets for:
1. `CREATE CONNECTION`
2. `CREATE MODEL ... REMOTE WITH CONNECTION` (Gemini 3.5 endpoint)
3. external object table over `attachments_raw`
4. `ML.GENERATE_TEXT` extraction table
5. gold multimodal view

(Use only after resolving region compatibility requirements.)

## Launch Checklist (Yatindra)

1. Confirm auth:
```bash
gcloud auth list
```

2. Run extraction:
```bash
./scripts/extract_store_prompt.sh <PROMPT_ID> --force
```

3. Verify GCS + BQ rows using commands above.

4. Use `gold/master.md` as default coding prompt artifact.

---
If failures occur, start with:
- `python3 -m py_compile agents/gcs_prompt_store.py agents/bigquery_prompt_catalog.py`
- rerun extraction with `--force`
