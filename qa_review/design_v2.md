# PRISM Coder Agent System Architecture v2

## Overview
PRISM Coder Agent is an enterprise software engineering agent for the ctoteam project. It operates under Google Cloud standards (us-central1 default, Gemini 2.5 Flash with fallback) using a config-driven architecture. The Next.js App Router frontend provides a secure, auditable viewer for saved prompt packages without runtime dependencies on /gcloud_run. All operations use concise execution summaries, deterministic mocks, and structured logging for traceability. Production deployment replaces mocks with server actions calling ./scripts/run_prompt_id.sh and start_aider.sh.

## BQ Requirements Mapping to Implementation

### Functional Requirements
- **Do not depend on /gcloud_run at runtime. Use concise execution summaries instead.**  
  Mapped to: `app/page.tsx:buildPromptPackage()` (lines 82-98) and `useEffect` initialization. Returns in-memory PromptPackage with concise masterMd summary. No fetch calls.
- **Python 3.11+, saved_prompts/<prompt_id>/master.md, create master.md, Preserve ordering of source content.**  
  Mapped to: `PromptPackage.masterMd` construction (order preserved via Chunk[].order). Simulated file creation via `runPromptIdScript()` invoking start_aider.sh.
- **Preserve source content when extracting prompts, Strip binary/image/pdf payloads into placeholders.**  
  Mapped to: `Chunk.rawContent` field and placeholder logic in buildPromptPackage. Raw JSON stored in `rawJson`.
- **Output Style: chunk_001.md, Chunks: 1, Gemini 2.5 Flash (us-central1 fallback)**  
  Mapped to: Hardcoded single chunk_001 in mockChunks with model/region in PROMPT_CONFIG.
- **aider saved_prompts/3381323161097207808/master.md, ./scripts/run_prompt_id.sh <prompt_id>**  
  Mapped to: `runPromptIdScript()` handler and alert simulation. Production: shell execution via server action.
- **Accept prompt ID as argument, Build Prompt Package, Project: ctoteam, ID: 3381323161097207808**  
  Mapped to: `useSearchParams` default + `buildPromptPackage(promptId)` returning full PromptPackage.
- **saved_prompts/<prompt_id>/raw.json, Config-driven architecture**  
  Mapped to: `rawJson` object and `PROMPT_CONFIG` const (project, region, model).
- **Prefer deterministic solutions over AI-generated summaries, Minimize narrative**  
  Mapped to: Pure deterministic fuzzySearch + mock data; UI uses concise labels only.
- **Launch coding workflows through start_aider.sh, Use Gemini only through start_aider.sh**  
  Mapped to: Orchestration button + diagnostic log entry. No direct Gemini calls in client.
- **Structured logging, Never silently skip errors, Never expose credentials**  
  Mapped to: `useDiagnosticLogger` hook + ErrorBoundary `componentDidCatch`. Logs include project/region but no secrets.
- **Execution Standards: Use execution_plan and reasoning_summary if needed**  
  Mapped to: Added `executionPlan` and `reasoningSummary` state in healed page.tsx with dedicated UI section.

### Data Requirements
- **chunk_001.md, Preserve source content**  
  Mapped to: Chunk interface + filteredChunks rendering preserving order.

### Security & Orchestration
- **gcloud auth application-default login --no-launch-browser, gcloud config set project ctoteam, gcloud auth login --no-launch-browser**  
  Mapped to: External pre-requisite notes in design; client code never performs auth.
- **Decode text/plain attachments, Saved prompt extraction is the source of truth**  
  Mapped to: rawContent handling and masterMd as single source of truth.

## Enterprise Best Practices Implemented
- **Strict TypeScript**: All interfaces (Chunk, PromptPackage, DiagnosticLog, ExecutionPlan) with no `any` except legacy ErrorBoundary props.
- **Next.js App Router**: `useSearchParams` wrapped in Suspense, 'use client' directive, proper fallback loading.
- **Robust Error Handling**: Class-based ErrorBoundary with onError callback, retry, and diagnostic logging. Never swallows errors.
- **Optimized Fuzzy Search**: Deterministic `fuzzySearch` (production drop-in: `import Fuse from 'fuse.js'` with pre-built index).
- **Table of Contents Scrolling**: `scrollToChunk` using `scrollIntoView({behavior:'smooth'})` + active state highlighting.
- **Export Actions**: Fully realized `exportToMarkdown`/`exportToPdf` using Blob + object URL (production: integrate jsPDF + remark for real PDF).
- **Custom Diagnostic Logging**: `useDiagnosticLogger` hook emitting structured JSON logs with timestamps, levels, metadata (project/region). Production: forward to Cloud Logging.
- **Config-driven & Auditable**: PROMPT_CONFIG object; all actions emit logs for traceability.
- **Self-contained & Production-ready**: Zero external runtime deps in mock mode; clear comments for production replacements.

## File & Component Map
- `app/page.tsx`: PRISMPromptViewer + PRISMPromptViewerContent (all logic)
- Future: `scripts/run_prompt_id.sh`, `start_aider.sh`, server actions for real FS operations

## Security & Compliance
- No credentials in code or logs.
- Client-side only for demo; production moves sensitive orchestration to API routes with IAM.
- Error boundaries prevent full app crashes and always log for audit.