# GCS Prompt Puller & AI Estimator

An automated agent that pulls prompt layers from GCS Silver layer, runs advanced project complexity grading and task estimations using Vertex AI Gemini, and compiles Claude-compatible copy-pasteable context prompts.

## Architecture Overview

This system implements a 4-stage medallion architecture:

1. **Gold Layer** (gs://agentproject/saved-prompts/<prompt_id>/gold/)
   - Contains `latest.json` pointer to the active run
   - Tracks version numbers and run IDs

2. **Silver Layer** (gs://agentproject/saved-prompts/<prompt_id>/silver/<run_id>/)
   - `system.md` - System instructions and rules
   - `final_assembled.md` - Complete requirement specifications

3. **Gemini Estimation** (Vertex AI API)
   - Analyzes prompt requirements
   - Generates complexity scoring (1-10)
   - Creates detailed WBS (Work Breakdown Structure)
   - Suggests LangChain architecture patterns
   - Estimates effort in developer-hours

4. **Local Output** (saved_prompts/<prompt_id>/)
   - `ai_estimation.md` - Full architectural report
   - `claude_prompt.md` - Claude-ready context prompt

## Quick Start

### Prerequisites

Ensure you have Google Cloud SDK installed and authentication configured:

```bash
# Install Google Cloud SDK (if not present)
curl https://sdk.cloud.google.com | bash
exec -l $SHELL

# Login and set default project
gcloud auth application-default login --no-launch-browser
gcloud config set project ctoteam

# Verify credentials
gcloud auth application-default print-access-token
```

### Run the Estimator

```bash
cd /home/appadmin/projects/Ram_Projects/DiracDelta/coder

# Make script executable
chmod +x scripts/pull_and_estimate.sh

# Execute with prompt ID
./scripts/pull_and_estimate.sh 3381323161097207808
```

### Output Files

After execution, you'll find:

- **AI Estimation Report**: `saved_prompts/3381323161097207808/ai_estimation.md`
  - Complexity grading (1-10 scale)
  - Architectural constraints and recommendations
  - Scope boundaries (Phase 1/2 breakdown)
  - LangChain module specifications
  - Agent state and memory design
  - Detailed WBS with task-level hour estimates
  - Critical path risk analysis
  - File modification maps

- **Claude Context Prompt**: `saved_prompts/3381323161097207808/claude_prompt.md`
  - Copy-paste directly into Anthropic Claude
  - Contains full system instructions
  - Includes architectural specifications
  - Ready for immediate implementation

## Advanced Options

### Using a Different Gemini Model

```bash
python3 agents/gcs_prompt_puller_and_estimator.py \
  --prompt-id 3381323161097207808 \
  --model gemini-2.0-flash-001
```

Available models:
- `gemini-2.0-flash-001` (default, fastest)
- `gemini-1.5-flash-002` (balanced)
- `gemini-2.0-pro` (most capable, slower)

### Custom GCS Bucket

```bash
python3 agents/gcs_prompt_puller_and_estimator.py \
  --prompt-id YOUR_PROMPT_ID \
  --bucket my-custom-bucket
```

## Troubleshooting

### Authentication Error: "gcloud.auth.application-default..."

**Solution**: Set up Application Default Credentials:
```bash
gcloud auth application-default login --no-launch-browser
```

### Error: "Latest pointer not found..."

**Verify the GCS path exists**:
```bash
gsutil ls -r gs://agentproject/saved-prompts/3381323161097207808/
```

### Error: "Failed to communicate with Vertex AI API..."

**Check Vertex AI API is enabled**:
```bash
gcloud services enable aiplatform.googleapis.com --project=ctoteam
```

**Verify access token**:
```bash
gcloud auth application-default print-access-token
```

## Project Structure

```
DiracDelta/coder/
├── agents/
│   └── gcs_prompt_puller_and_estimator.py   # Main estimator agent
├── scripts/
│   └── pull_and_estimate.sh                 # Bash runner
├── saved_prompts/                           # Output directory (auto-created)
│   └── {prompt_id}/
│       ├── ai_estimation.md                 # Generated estimation report
│       └── claude_prompt.md                 # Claude-ready prompt
└── README_ESTIMATOR.md                      # This file
```

## Key Features

✅ **Medallion Architecture** - Gold/Silver layer abstraction for data quality
✅ **Vertex AI Integration** - Uses Gemini 3.5 Flash for fast analysis
✅ **Enterprise-Grade Estimation** - WBS, complexity scoring, effort estimation
✅ **LangChain Architecture Design** - Suggests specific modules and patterns
✅ **Claude-Optimized Output** - Copy-paste ready for immediate implementation
✅ **Error Handling** - Comprehensive logging and validation
✅ **GCP Authentication** - Supports both gcloud login and ADC flows

---

*Enterprise Prompt Engineering & AI Estimation Platform*
