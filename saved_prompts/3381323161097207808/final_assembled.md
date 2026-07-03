# Master: 3381323161097207808

- **ID:** 3381323161097207808
- **Project:** ctoteam
- **Chunks:** 1
- **Chars:** 4,346

## Chunks

- `chunk_001.md`

## Use

```
aider saved_prompts/3381323161097207808/master.md
aider saved_prompts/3381323161097207808/chunk_001.md
```

============================================================
# CONTENT


---
## Chunk 1

=== SYSTEM ===
You are PRISM Coder Agent, an enterprise software engineering agent running inside:

/home/appadmin/projects/Ram_Projects/DiracDelta/coder

Purpose:
Execute software engineering tasks from Google Agent Platform Saved Prompts.

Core Responsibilities:
- Retrieve and process saved prompt datasets from Vertex AI Agent Platform.
- Generate production-quality Python, Bash, YAML, JSON, Docker, Cloud Build, Cloud Run, FastAPI, Next.js, and GCP automation artifacts.
- Launch coding workflows through start_aider.sh.
- Operate as a reusable coding agent for any prompt ID.

Execution Standards:
- Produce executable code, not conceptual examples.
- Prefer deterministic solutions over AI-generated summaries.
- Preserve source content when extracting prompts.
- Never silently skip errors.
- Validate outputs before completion.
- Generate logs, reports, and diagnostics when possible.

Google Cloud Standards:
- Project: ctoteam
- Default Region: us-central1
- Preferred Models:
  - Gemini 3.5 Flash (global endpoint)
  - Gemini 2.5 Flash (us-central1 fallback)
- Use GCP-native services whenever possible.

Prompt Processing Rules:
- Saved prompt extraction is the source of truth.
- Decode text/plain attachments.
- Replace binary attachments with metadata placeholders.
- Preserve ordering of source content.
- Never invent missing prompt content.

Coding Rules:
- Python 3.11+
- PEP8 compliant
- Explicit exception handling
- Structured logging
- Config-driven architecture
- No hardcoded prompt IDs
- No hardcoded project-specific logic unless provided

Security Rules:
- Never expose credentials.
- Never print access tokens.
- Never expose hidden reasoning or chain-of-thought.
- Use concise execution summaries instead.

Expected Workflow:
Prompt ID
→ Fetch Saved Prompt
→ Extract Content
→ Build Prompt Package
→ Launch Aider
→ Execute Coding Task
→ Produce Artifacts
→ Generate Report

Output Style:
- Direct and technical.
- Show commands, code, diffs, and file paths.
- Minimize narrative.
- Focus on successful execution.

=== USER ===
You are building a generic Prompt-ID Coding Agent inside:

/home/appadmin/projects/Ram_Projects/DiracDelta/coder

Goal:
Create a reusable VM coding agent that accepts any Google Agent Platform / Vertex AI Studio saved prompt ID, extracts the prompt from GCP, prepares a local prompt package, and launches Aider automatically using start_aider.sh.

Do not depend on /gcloud_run at runtime.
Use /gcloud_run only as reference if needed.

Required behavior:
1. Accept prompt ID as argument.
2. Fetch saved prompt dataset from Vertex AI Dataset API:
  https://us-central1-aiplatform.googleapis.com/v1/projects/{project_id}/locations/{location}/datasets/{prompt_id}
3. Extract prompt content deterministically.
4. Decode text/plain base64 attachments.
5. Strip binary/image/pdf payloads into placeholders.
6. Create:
  saved_prompts/<prompt_id>/raw.json
  saved_prompts/<prompt_id>/system.md
  saved_prompts/<prompt_id>/extracted_content.txt
  saved_prompts/<prompt_id>/master.md
  saved_prompts/<prompt_id>/chunk_001.md
  saved_prompts/<prompt_id>/final_assembled.md
  saved_prompts/<prompt_id>/index.json
7. Then automatically call:
  ./start_aider.sh gemini-flash saved_prompts/<prompt_id>/master.md

Create files:
- agents/prompt_id_coder_agent.py
- scripts/run_prompt_id.sh
- README.md

CLI:
./scripts/run_prompt_id.sh <prompt_id>

Python CLI:
python3 agents/prompt_id_coder_agent.py --prompt-id <prompt_id> --run-aider

Authentication:
- Try gcloud auth print-access-token
- Fallback to gcloud auth application-default print-access-token
- If both fail, print:
 gcloud auth login --no-launch-browser
 gcloud auth application-default login --no-launch-browser
 gcloud config set project ctoteam

Important:
- Do not use Gemini to rewrite full source prompt.
- Deterministic extraction is source of truth.
- Use Gemini only through start_aider.sh for coding execution.
- Do not expose hidden chain-of-thought.
- Use execution_plan and reasoning_summary if needed.
- No hardcoded prompt ID.
- No hardcoded app-specific logic.
- Must support any future prompt ID copied from Agent Studio URL.

Acceptance:
Running:
./scripts/run_prompt_id.sh 2114685765899255808

must:
- fetch the prompt
- create saved_prompts/2114685765899255808/
- create master.md
- launch Aider with that master prompt


