L_NAME)${NC}"
echo -e "Logging to: $LOG_FILE"

# Launch Aider
aider \
 --model "$MODEL_NAME" \
 --edit-format diff \
 --map-tokens 1024 \
 --no-auto-lint \
 --no-auto-test \
 --no-show-model-warnings \
 --no-check-model-accepts-settings \
 --stream \
 --yes \
 2>&1 | tee "$LOG_FILE"
(venv) appadmin@chn-mit-genai-dq1:~/projects/Ram_Projects/DiracDelta/ekf/scripts$

 i this wear ukg the gemin 2.5 whi teh toekn limt and we ne dth egood way can we crea te a pythin coe 

 # Print build environment information
 - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
>>>>>>> REPLACE


Tokens: 27k sent, 157 received. Cost: $0.04 message, $2.49 session.

requirements.txt
cloudbuild.yaml


<<<<<<< SEARCH
steps:
 # Print build environment information
 - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
=======
steps:
 # Step 1: Install dependencies and compile python modules (ensuring datacatalog is explicitly
installed)
 - name: 'python:3.11'
  entrypoint: 'bash'
  args:
   - '-c'
   - |
    pip install --upgrade pip
    pip install google-cloud-datacatalog
    if [ -f requirements.txt ]; then pip install -r requirements.txt; fi
    python -m compileall .

 # Print build environment information
 - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
>>>>>>> REPLACE


Tokens: 27k sent, 157 received. Cost: $0.04 message, $2.53 session.
Applied edit to cloudbuild.yaml
Commit 4b617d1 build: add python dependency installation step to cloudbuild.yaml
You can use /undo to undo and discard each aider commit.
───────────────────────────────────────────────────────────────────────────────────────────────────
                                        /

                 cloudbuild.yaml       requirements.txt terraform/ci-cd/mai                                        /



cloudbuild.yaml


<<<<<<< SEARCH
steps:
 # Step 1: Install dependencies and compile python modules (ensuring datacatalog is explicitly
installed)
 - name: 'python:3.11'
  entrypoint: 'bash'
=======
steps:
 # Step 1: Install dependencies and compile python modules (ensuring datacatalog is explicitly
installed)
 - name: 'python:3.12-slim'
  entrypoint: 'bash'
>>>>>>> REPLACE


Tokens: 28k sent, 101 received. Cost: $0.04 message, $2.57 session.
Applied edit to cloudbuild.yaml
Commit 7fe5eb9 build: upgrade python image to 3.12-slim
You can use /undo to undo and discard each aider commit.
───────────────────────────────────────────────────────────────────────────────────────────────────
                                        /

                  cloudbuild.yaml       requirements.txt terraform/ci-cd/ma                                        /



cloudbuild.yaml


<<<<<<< SEARCH
steps:
 # Step 1: Install dependencies and compile python modules (ensuring datacatalog is explicitly
installed)
 - name: 'python:3.12-slim'
  entrypoint: 'bash'
  args:
   - '-c'
   - |
    pip install --upgrade pip
    pip install google-cloud-datacatalog
    if [ -f requirements.txt ]; then pip install -r requirements.txt; fi
    python -m compileall .
=======
steps:
 # Step 1: Install dependencies and compile python modules (ensuring datacatalog is explicitly
installed)
 - name: 'python:3.12-slim'
  id: 'install-and-compile'
  entrypoint: 'bash'
  args:
   - '-c'
   - |
    pip install --upgrade pip
    pip install google-cloud-datacatalog
    if [ -f requirements.txt ]; then pip install -r requirements.txt; fi
    python -m compileall .
>>>>>>> REPLACE


Tokens: 28k sent, 214 received. Cost: $0.04 message, $2.62 session.
Applied edit to cloudbuild.yaml
Commit b803a43 chore: add id to install-and-compile step in cloudbuild.yaml
You can use /undo to undo and discard each aider commit.
───────────────────────────────────────────────────────────────────────────────────────────────────
                                        /

              cloudbuild.yaml       requirements.txt terraform/ci-cd/main.tf t                                        /





fix the code cat start_aider.sh
#!/bin/bash
unset GEMINI_API_KEY
unset GOOGLE_API_KEY

export GOOGLE_CLOUD_PROJECT="${GCP_PROJECT_ID:-ctoteam}"
export VERTEXAI_PROJECT="${GCP_PROJECT_ID:-ctoteam}"
export VERTEXAI_LOCATION="${VERTEXAI_LOCATION:-global}"
export GOOGLE_CLOUD_LOCATION="${GOOGLE_CLOUD_LOCATION:-global}"
export GOOGLE_REGION="${GOOGLE_REGION:-global}"

set -euo pipefail

# =============================================
# EKF Aider Launcher - Dynamic Model Router
# =============================================
# Usage:
#  ./scripts/start_aider.sh [model_key]
#
# Examples:
#  ./scripts/start_aider.sh gemini-flash   # Best for repo work
#  ./scripts/start_aider.sh gemini-pro
#  ./scripts/start_aider.sh grok-fast
#
# To see all available models: ./scripts/test_vertex_models.sh

ENV_FILE=".env.local"
PROJECT_DIR="/home/appadmin/projects/Ram_Projects/DiracDelta/ekf"
LOG_FILE="logs/aider_session_$(date +%Y%m%d_%H%M%S).log"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}=========================================${NC}"
echo -e "${BLUE} 🚀 EKF AIDER LAUNCHER (Dynamic Router)${NC}"
echo -e "${BLUE}=========================================${NC}"

cd "$PROJECT_DIR"
mkdir -p logs

# Pre-flight checks
check_dep() {
  if ! command -v "$1" &> /dev/null; then
    echo -e "${RED}❌ Missing dependency: $1${NC}"
    exit 1
  fi
}
check_dep gcloud
check_dep bq
check_dep git
check_dep jq

if [ ! -f "$ENV_FILE" ]; then
  echo -e "${RED}❌ $ENV_FILE missing!${NC}"
  exit 1
fi

if [ ! -f "models.json" ]; then
  echo -e "${RED}❌ models.json missing!${NC}"
  exit 1
fi

set -a
source "$ENV_FILE"
set +a

# Authentication
echo -e "${GREEN}☁️ Authenticating...${NC}"
gcloud config set project "${GCP_PROJECT_ID:-ctoteam}" >/dev/null
if ! gcloud auth application-default print-access-token >/dev/null 2>&1; then
  echo -e "${RED}❌ ADC missing. Run: gcloud auth application-default login${NC}"
  exit 1
fi

# Workspace checks
if [ ! -d ".git" ]; then
  echo -e "${RED}❌ Not a git repository.${NC}"
  exit 1
fi

if [ ! -f ".aiderignore" ]; then
  echo -e "Creating .aiderignore..."
  cat > .aiderignore << EOF
.venv*
.terraform*
.git
__pycache__
*.pyc
logs/
EOF
fi

# Model selection
MODEL_KEY="${1:-gemini-flash}"
MODEL_NAME=$(jq -r ".models.\"$MODEL_KEY\".api_model_id" models.json)
IS_SUPPORTED=$(jq -r ".models.\"$MODEL_KEY\".aider_supported" models.json)

if [ "$MODEL_NAME" = "null" ] || [ -z "$MODEL_NAME" ]; then
  echo -e "${RED}❌ Unknown model key: $MODEL_KEY${NC}"
  echo -e "Available: $(jq -r '.models | keys | join(", ")' models.json)"
  exit 1
fi

if [ "$IS_SUPPORTED" != "true" ]; then
  echo -e "${RED}❌ Model $MODEL_KEY is not supported with Aider.${NC}"
  echo -e "Use a model with aider_supported=true (e.g. gemini-flash)"
  exit 1
fi

DISPLAY_NAME=$(jq -r ".models.\"$MODEL_KEY\".display_name" models.json)

echo -e "${GREEN}💎 Starting Aider | Model: $DISPLAY_NAME ($MODEL_NAME)${NC}"
echo -e "Logging to: $LOG_FILE"

# Launch Aider
aider \
 --model "$MODEL_NAME" \
 --edit-format diff \
 --map-tokens 1024 \
 --no-auto-lint \
 --no-auto-test \
 --no-show-model-warnings \
 --no-check-model-accepts-settings \
 --stream \
 --yes \
 2>&1 | tee "$LOG_FILE"
(venv) appadmin@chn-mit-genai-dq1:~/projects/Ram_Projects/DiracDelta/ekf/scripts$

 as it tnt ot celar or we ne dto save the promt isalreayd in  fi

if [ "$IS_SUPPORTED" != "true" ]; then
  echo -e "${RED}❌ Model $MODEL_KEY is not supported with Aider.${NC}"
  echo -e "Use a model with aider_supported=true (e.g. gemini-flash)"
  exit 1
fi

DISPLAY_NAME=$(jq -r ".models.\"$MODEL_KEY\".display_name" models.json)

echo -e "${GREEN}💎 Starting Aider | Model: $DISPLAY_NAME ($MODEL_NAME)${NC}"
echo -e "Logging to: $LOG_FILE"

# Launch Aider
aider \
 --model "$MODEL_NAME" \
 --edit-format diff \
 --map-tokens 1024 \
 --no-auto-lint \
 --no-auto-test \
 --no-show-model-warnings \
 --no-check-model-accepts-settings \
 --stream \
 --yes \
 2>&1 | tee "$LOG_FILE"
(venv) appadmin@chn-mit-genai-dq1:~/projects/Ram_Projects/DiracDelta/ekf/scripts$ ls -l prc^C
(venv) appadmin@chn-mit-genai-dq1:~/projects/Ram_Projects/DiracDelta/ekf/scripts$ cd ..
(venv) appadmin@chn-mit-genai-dq1:~/projects/Ram_Projects/DiracDelta/ekf$ ls -l prompt
prompt_requirements.json prompts/
(venv) appadmin@chn-mit-genai-dq1:~/projects/Ram_Projects/DiracDelta/ekf$ ls -l prompts/
total 104
-rw-rw-r-- 1 appadmin appadmin 2785 May 21 10:42 advanced.py
-rw-rw-r-- 1 appadmin appadmin 3497 May 21 10:42 base.py
-rw-rw-r-- 1 appadmin appadmin 1715 May 21 10:42 beam.py
-rw-rw-r-- 1 appadmin appadmin 1422 May 21 10:42 bigquery_optimization.py
-rw-rw-r-- 1 appadmin appadmin 1475 May 21 10:42 cicd.py
-rw-rw-r-- 1 appadmin appadmin 1353 May 21 10:42 documentation.py
-rw-rw-r-- 1 appadmin appadmin 1301 May 21 10:42 enrichment.py
-rw-rw-r-- 1 appadmin appadmin 1433 May 21 10:42 __init__.py
-rw-rw-r-- 1 appadmin appadmin 1556 May 21 10:42 lineage.py
-rw-rw-r-- 1 appadmin appadmin 1976 May 21 10:42 metadata_alignment.py
drwxrwxr-x 2 appadmin appadmin 4096 May 21 10:43 phase-01-ingestion
drwxrwxr-x 2 appadmin appadmin 4096 May 21 10:43 phase-02-bigquery
drwxrwxr-x 2 appadmin appadmin 4096 May 21 10:43 phase-03-metadata
drwxrwxr-x 2 appadmin appadmin 4096 May 21 10:43 phase-04-quality
drwxrwxr-x 2 appadmin appadmin 4096 May 21 10:43 phase-05-security
drwxrwxr-x 2 appadmin appadmin 4096 May 21 10:43 phase-06-cicd
drwxrwxr-x 2 appadmin appadmin 4096 May 21 10:43 phase-07-testing
drwxrwxr-x 2 appadmin appadmin 4096 May 21 11:14 phase-08-docs
drwxrwxr-x 2 appadmin appadmin 4096 May 21 10:43 phase-09-advanced
-rw-rw-r-- 1 appadmin appadmin 1491 May 21 10:42 quality.py
-rw-rw-r-- 1 appadmin appadmin 1456 May 21 10:42 quality_remediation.py
-rw-rw-r-- 1 appadmin appadmin 1718 May 21 10:42 security.py
-rw-rw-r-- 1 appadmin appadmin 1932 May 21 10:42 sql.py
-rw-rw-r-- 1 appadmin appadmin 1493 May 21 10:42 templates.py
-rw-rw-r-- 1 appadmin appadmin 1682 May 21 10:42 terraform.py
-rw-rw-r-- 1 appadmin appadmin 1491 May 21 10:42 testing.py
(venv) appadmin@chn-mit-genai-dq1:~/projects/Ram_Projects/DiracDelta/ekf$ -rw-rw-r-- 1 appadmin appadmin 1456 May 21 10:42 quality_remediation.py
-rw-rw-r-- 1 appadmin appadmin 1718 May 21 10:42 security.py
-rw-rw-r-- 1 appadmin appadmin 1932 May 21 10:42 sql.py
-rw-rw-r-- 1 appadmin appadmin 1493 May 21 10:42 templates.py
-rw-rw-r-- 1 appadmin appadmin 1682 May 21 10:42 terraform.py
-rw-rw-r-- 1 appadmin appadmin 1491 May 21 10:42 testing.py
(venv) appadmin@chn-mit-genai-dq1:~/projects/Ram_Projects/DiracDelta/ekf$
(venv) appadmin@chn-mit-genai-dq1:~/projects/Ram_Projects/DiracDelta/ekf$ ls
AIDER_QUICK_REF.md config        fastapi.log   prompt_requirements.json src
architecture.md   docs         launch_model.sh prompts          terraform
backend       EKF_AIDER_PROMPTS.md logs       README.md         tests
bigquery      EKF_QUICK_START.md  models.json   requirements.txt
cloudbuild.yaml   execution.md     path       scripts
(venv) appadmin@chn-mit-genai-dq1:~/projects/Ram_Projects/DiracDelta/ekf$ cat prompt_requirements.json
{
 "project": "Enterprise Knowledge Fabric (EKF)",
 "last_updated": "2026-05-21",
 "phases": [
  {
   "id": "phase-1",
   "title": "Data Ingestion Pipelines",
   "status": "completed",
   "output_path": "src/dataflow/",
   "recommended_model": "grok-fast"
  },
  {
   "id": "phase-2",
   "title": "BigQuery Analytics Measures & Views",
   "status": "completed",
   "output_path": "bigquery/views/",
   "recommended_model": "gemini-flash"
  },
  {
   "id": "phase-3",
   "title": "Knowledge Catalog & Metadata Management",
   "status": "completed",
   "output_path": "scripts/metadata/",
   "recommended_model": "gemini-pro"
  },
  {
   "id": "phase-4",
   "title": "Data Quality & Monitoring",
   "status": "completed",
   "output_path": "scripts/quality/",
   "recommended_model": "gemini-flash"
  },
  {
   "id": "phase-5",
   "title": "Security & Governance",
   "status": "completed",
   "output_path": "terraform/security/",
   "recommended_model": "gemini-pro"
  },
  {
   "id": "phase-6",
   "title": "CI/CD & Deployment",
   "status": "pending",
   "output_path": "terraform/ci-cd/",
   "recommended_model": "gemini-flash"
  },
  {
   "id": "phase-7",
   "title": "Testing & Validation",
   "status": "in_progress",
   "output_path": "tests/",
   "recommended_model": "grok-fast"
  },
  {
   "id": "phase-8",
   "title": "Documentation & Discovery",
   "status": "in_progress",
   "output_path": "docs/",
   "recommended_model": "grok-fast"
  },
  {
   "id": "phase-9",
   "title": "Advanced Analytics",
   "status": "pending",
   "output_path": "bigquery/analytics/",
   "recommended_model": "gemini-flash"
  }
 ]
}
(venv) appadmin@chn-mit-genai-dq1:~/projects/Ram_Projects/DiracDelta/ekf$



 

scripts/run_prompt.py#!/usr/bin/env python3
import os
import sys
import json
import glob
import subprocess

def load_json_file(filepath):
    if not os.path.exists(filepath):
        print(f"Error: {filepath} not found.")
        sys.exit(1)
    with open(filepath, "r") as f:
        return json.load(f)

def run_aider_with_prompt(model_id, prompt_file, files_to_edit):
    """Executes aider with the exact file context and the prompt file instructions."""
    cmd = [
        "aider",
        "--model", model_id,
        "--edit-format", "diff",
        "--map-tokens", "1024",
        "--no-auto-lint",
        "--no-auto-test",
        "--no-show-model-warnings",
        "--no-check-model-accepts-settings",
        "--stream",
        "--yes",
        "--message-file", prompt_file
    ] + files_to_edit

    print(f"Running Command: {' '.join(cmd)}")
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error during Aider execution: {e}")
        sys.exit(e.returncode)

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 run_prompt.py <phase_id_or_number>")
        print("Example: python3 run_prompt.py phase-6")
        sys.exit(1)

    phase_arg = sys.argv[1].strip()
    # Normalize input like "6" to "phase-6"
    if phase_arg.isdigit():
        phase_arg = f"phase-{phase_arg}"

    project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    os.chdir(project_dir)

    # Load configuration structures
    requirements = load_json_file("prompt_requirements.json")
    models_config = load_json_file("models.json")

    # Locate phase
    target_phase = None
    for phase in requirements.get("phases", []):
        if phase.get("id") == phase_arg:
            target_phase = phase
            break

    if not target_phase:
        print(f"Error: Phase '{phase_arg}' not found in prompt_requirements.json")
        sys.exit(1)

    # Map recommended model to API Model ID
    model_key = target_phase.get("recommended_model", "gemini-flash")
    model_entry = models_config.get("models", {}).get(model_key)
    if not model_entry:
        print(f"Warning: Model key '{model_key}' not found in models.json, defaulting to gemini-flash")
        model_entry = models_config.get