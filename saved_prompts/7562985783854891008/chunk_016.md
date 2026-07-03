n Navin Dedhia;​Anupama Gangadhar;​Swamyayyappa Subbaraochillimunta;​Soundararajan C;​Piyush Murli Agarwal​
Hi Ranga,
As we continue expanding Generative AI and agentic engineering capabilities across Mastech, I believe we have an opportunity to proactively define a scalable enterprise approach rather than allowing adoption to evolve in a fragmented manner.
Today, AI usage is growing organically across teams, but the current model is largely decentralized, with engineers independently using different models, repeating similar prompt patterns, and directly invoking premium inference endpoints for development workflows. While this accelerates experimentation, it creates long-term concerns around cost scalability, governance, security, and architectural consistency.
I would like to propose a Unified AI Agent Engineering Framework built on our Enterprise Knowledge Fabric (EKF) and OSSA governance principles to establish a standardized, secure, and cost-optimized foundation for enterprise AI engineering across Mastech.
The framework would be anchored on three core principles.
First, cost optimization by design.
One of the biggest enterprise risks in scaling AI engineering is uncontrolled token consumption. Our most common engineering workloads are developer persona interactions—code generation, debugging, architecture guidance, documentation generation, refactoring, agent orchestration support, repository-aware development assistance, and engineering copilots.
These workflows repeatedly carry large context windows including architecture documents, repositories, execution traces, prompt history, and conversation memory.
To illustrate the economics, below is an indicative comparison for 100 engineers actively using AI development agents.

Model Strategy
Example Latest Models
Approx Cost per 1M Tokens
Estimated Monthly Cost (100 Engineers)
Premium Reasoning Stack
GPT-5, Claude Opus 4, Claude Sonnet 4.5 (high reasoning usage)
$15–$30+
$30,000 – $60,000+
Standard Enterprise Coding Stack
GPT-4o, Claude Sonnet 4, DeepSeek R1 enterprise
$3–$8
$6,000 – $15,000
Fast Cost-Efficient Stack
Gemini 3.5 Flash (direct uncached usage)
~$1.50
~$3,000
EKF + OSSA Optimized Engineering Stack
Gemini 3.5 Flash + Context Caching + Centralized Routing + Governance
Effective blended ~$0.15
~$300
Illustrative potential savings:
vs premium reasoning stacks: up to 99% reduction
vs standard coding stacks: 95%+ reduction
vs direct Gemini Flash without caching: ~90% reduction
The economics become transformative when repeated engineering context is cached and reused rather than reprocessed across every interaction.
Second, governance and enterprise security.
As adoption scales, governance cannot remain optional.
A centralized AI Governance Gateway within EKF would provide:
PII detection and redaction
token spend guardrails
role-based access enforcement
prompt and output auditability
standardized model access policies
enterprise observability and usage monitoring
This allows innovation without compromising security, compliance, or financial control.
Third, vendor-neutral execution.
Rather than teams building directly against isolated model endpoints, we should establish a unified orchestration abstraction capable of routing workloads intelligently across:
Google Gemini
AWS Bedrock (Claude)
Snowflake AI workloads
future enterprise AI platforms
This gives us portability, workload optimization, and governance consistency without vendor lock-in.
My recommendation would be to approach this incrementally.
Phase 1 would define architecture, governance guardrails, reusable SDKs, developer templates, and agent engineering standards.
Phase 2 would pilot selected engineering workflows to validate cost efficiency, productivity impact, and governance enforcement.
Phase 3 would scale across broader engineering teams based on measured outcomes.
I believe this positions Mastech to build AI capabilities in a way that is sustainable, governed, and economically viable at enterprise scale.
I would value your thoughts, sponsorship, and guidance on whether we should evolve this into a broader strategic initiative.
Happy to continue this as a working discussion thread and refine the approach collaboratively based on your inputs.

Thank you for your support.
Best regards,
Ramamurthy Valavandan
Enterprise Architect
Mastech Digital
 
15 additional security updates can be applied with ESM Apps.
Learn more about enabling ESM Apps service at https://ubuntu.com/esm


*** System restart required ***
Last login: Sat May 23 03:57:30 2026 from 10.100.96.20
cd appadmin@chn-mit-genai-dq1:~$ cd projects/Ram_Projects/DiracDelta/
appadmin@chn-mit-genai-dq1:~/projects/Ram_Projects/DiracDelta$ cd ekf/
appadmin@chn-mit-genai-dq1:~/projects/Ram_Projects/DiracDelta/ekf$ ls -la
total 1924
drwxrwxr-x 22 appadmin appadmin  4096 May 22 18:55 .
drwxrwxr-x 8 appadmin appadmin  4096 May 22 02:33 ..
drwxr-xr-x 2 appadmin appadmin  4096 May 22 08:17 .agents
-rw-rw-r-- 1 appadmin appadmin 1675227 May 22 15:30 .aider.chat.history.md
-rw-rw-r-- 1 appadmin appadmin   78 May 21 02:41 .aiderignore
-rw-rw-r-- 1 appadmin appadmin  74044 May 22 07:12 .aider.input.history
-rw-rw-r-- 1 appadmin appadmin  4937 May 19 08:52 AIDER_QUICK_REF.md
drwxr-xr-x 2 appadmin appadmin  4096 May 22 15:30 .aider.tags.cache.v4
-rw-rw-r-- 1 appadmin appadmin  8173 May 21 10:23 architecture.md
drwxrwxr-x 7 appadmin appadmin  4096 May 22 18:39 backend
-rw-rw-r-- 1 appadmin appadmin  18193 May 22 19:36 .backend_start.log
drwxrwxr-x 7 appadmin appadmin  4096 May 22 08:26 bigquery
drwxrwxr-x 2 appadmin appadmin  4096 May 22 18:56 .claude
-rw-rw-r-- 1 appadmin appadmin  4126 May 22 07:12 cloudbuild.yaml
drwxr-xr-x 2 appadmin appadmin  4096 May 22 08:17 .codex
drwxrwxr-x 2 appadmin appadmin  4096 May 22 06:08 config
drwxrwxr-x 2 appadmin appadmin  4096 May 22 08:21 docs
-rw-rw-r-- 1 appadmin appadmin  2909 May 21 04:06 EKF_AIDER_PROMPTS.md
-rw-rw-r-- 1 appadmin appadmin  12090 May 19 08:52 EKF_QUICK_START.md
-rw-rw-r-- 1 appadmin appadmin  1400 May 21 08:57 .env.local
-rw-rw-r-- 1 appadmin appadmin  3968 May 21 10:16 execution.md
-rw-rw-r-- 1 appadmin appadmin   66 May 21 01:13 fastapi.log
drwxrwxr-x 5 appadmin appadmin  4096 May 22 18:53 frontend
drwxrwxr-x 8 appadmin appadmin  4096 May 22 19:34 .git
-rw-rw-r-- 1 appadmin appadmin   69 May 21 12:01 .gitignore
-rwxrwxr-x 1 appadmin appadmin  3921 May 22 04:07 launch_model.sh
drwxrwxr-x 2 appadmin appadmin  4096 May 22 14:09 logs
-rw-rw-r-- 1 appadmin appadmin  10059 May 22 17:06 mock_customer_data.csv
-rw-rw-r-- 1 appadmin appadmin  1439 May 21 12:04 models.json
drwxrwxr-x 3 appadmin appadmin  4096 May 20 13:05 path
-rw-rw-r-- 1 appadmin appadmin  2175 May 22 15:47 prompt_requirements.json
drwxrwxr-x 14 appadmin appadmin  4096 May 22 18:44 prompts
drwxrwxr-x 3 appadmin appadmin  4096 May 22 06:23 .pytest_cache
-rw-rw-r-- 1 appadmin appadmin  2791 May 22 08:21 README.md
-rw-rw-r-- 1 appadmin appadmin   155 May 22 06:40 requirements.txt
drwxrwxr-x 5 appadmin appadmin  4096 May 23 04:35 scripts
drwxrwxr-x 3 appadmin appadmin  4096 May 21 06:22 src
drwxrwxr-x 5 appadmin appadmin  4096 May 22 13:23 terraform
drwxrwxr-x 3 appadmin appadmin  4096 May 22 15:47 tests
drwxrwxr-x 5 appadmin appadmin  4096 May 20 03:00 .venv
drwxrwxr-x 5 appadmin appadmin  4096 May 20 03:35 .venv-vllm
appadmin@chn-mit-genai-dq1:~/projects/Ram_Projects/DiracDelta/ekf$
 
thiank swe we a [Sat May 23 06:37:52 AM UTC 2026] 🚀 Running... do not kill
[Sat May 23 06:38:12 AM UTC 2026] ☕ Gone for coffee... system alive
[Sat May 23 06:38:32 AM UTC 2026] ☕ Gone for coffee... system alive
[Sat May 23 06:38:52 AM UTC 2026] ☕ Gone for coffee... system alive
[Sat May 23 06:39:12 AM UTC 2026] ☕ Gone for coffee... system alive
[Sat May 23 06:39:32 AM UTC 2026] ☕ Gone for coffee... system alive
[Sat May 23 06:39:52 AM UTC 2026] 🚀 Running... do not kill
[Sat May 23 06:40:12 AM UTC 2026] ☕ Gone for coffee... system alive
^C
(.venv-vllm) appadmin@chn-mit-genai-dq1:~$ cd projects/Ram_Projects/DiracDelta/
(.venv-vllm) appadmin@chn-mit-genai-dq1:~/projects/Ram_Projects/DiracDelta$ cluuade^C
(.venv-vllm) appadmin@chn-mit-genai-dq1:~/projects/Ram_Projects/DiracDelta$
 
i will us ethe __pycache__/      start_aider.sh
quality/        start_all.sh
(.venv-vllm) appadmin@chn-mit-genai-dq1:~/projects/Ram_Projects/DiracDelta/ekf$ cat scripts/start_aider.sh
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
#  ./scripts/start_aider.sh [model_key] [prompt_file_or_phase]
#
# Examples:
#  ./scripts/start_aider.sh gemini-flash
#  ./scripts/start_aider.sh gemini-flash phase-6
#  ./scripts/start_aider.sh gemini-flash prompts/cicd.py

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

# Handle prompt file or phase argument
AIDER_EXTRA_ARGS=()
PROMPT_ARG="${2:-}"

if [ -n "$PROMPT_ARG" ]; then
 if [[ "$PROMPT_ARG" =~ ^phase-[0-9]+$ || "$PROMPT_ARG" =~ ^[0-9]+$ ]]; then
  # Resolve phase path or python run_prompt handler
  echo -e "${GREEN}Phase detected: $PROMPT_ARG. Routing through python prompt execution wrapper...${NC}"
  python3 scripts/run_prompt.py "$PROMPT_ARG"
  exit 0
 elif [ -f "$PROMPT_ARG" ]; then
  echo -e "${GREEN}Using prompt file: $PROMPT_ARG${NC}"
  AIDER_EXTRA_ARGS+=("--message-file" "$PROMPT_ARG")
 else
  echo -e "${RED}Warning: Prompt file or phase '$PROMPT_ARG' not found. Launching standard chat...${NC}"
 fi
fi

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
 "${AIDER_EXTRA_ARGS[@]}" \
 2>&1 | tee "$LOG_FILE"
(.venv-vllm) appadmin@chn-mit-genai-dq1:~/projects/Ram_Projects/DiracDelta/ekf$rchitecture.md   EKF_QUICK_START.md  models.json        src
backend       execution.md     path           terraform
bigquery      fastapi.log      prompt_requirements.json tests
cloudbuild.yaml   frontend       prompts
config       launch_model.sh    README.md
docs        logs         requirements.txt
(.venv-vllm) appadmin@chn-mit-genai-dq1:~/projects/Ram_Projects/DiracDelta/ekf$ cd scripts/
(.venv-vllm) appadmin@chn-mit-genai-dq1:~/projects/Ram_Projects/DiracDelta/ekf/scripts$ ls
deploy_ekf.sh     run_beam_pipeline.sh test_all_phases.sh
deploy.sh       run_prompt.py     test_backend.sh
list_vertex_models.py snowflake_setup.sql  test_vertex_models.sh
metadata        start_aider_7b.sh   validate_deployment.sh
__pycache__      start_aider.sh
quality        start_all.sh
(.venv-vllm) appadmin@chn-mit-genai-dq1:~/projects/Ram_Projects/DiracDelta/ekf/scripts$ ./start_all.sh
Backend failed on 127.0.0.1:8000
  config.load_app()
 File "/home/appadmin/projects/Ram_Projects/DiracDelta/ekf/.venv-vllm/lib/python3.12/site-packages/uvicorn/config.py", line 415, in load_app
  return import_from_string(self.app)
      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
 File "/home/appadmin/projects/Ram_Projects/DiracDelta/ekf/.venv-vllm/lib/python3.12/site-packages/uvicorn/importer.py", line 22, in import_from_string
  raise exc from None
 File "/home/appadmin/projects/Ram_Projects/DiracDelta/ekf/.venv-vllm/lib/python3.12/site-packages/uvicorn/importer.py", line 19, in import_from_string
  module = importlib.import_module(module_str)
       ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
 File "/usr/lib/python3.12/importlib/__init__.py", line 90, in import_module
  return _bootstrap._gcd_import(name[level:], package, level)
      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
 File "<frozen importlib._bootstrap>", line 1387, in _gcd_import
 File "<frozen importlib._bootstrap>", line 1360, in _find_and_load
 File "<frozen importlib._bootstrap>", line 1310, in _find_and_load_unlocked
 File "<frozen importlib._bootstrap>", line 488, in _call_with_frames_removed
 File "<frozen importlib._bootstrap>", line 1387, in _gcd_import
 File "<frozen importlib._bootstrap>", line 1360, in _find_and_load
 File "<frozen importlib._bootstrap>", line 1324, in _find_and_load_unlocked
ModuleNotFoundError: No module named 'backend'
Backend failed on 127.0.0.1:8080
  config.load_app()
 File "/home/appadmin/projects/Ram_Projects/DiracDelta/ekf/.venv-vllm/lib/python3.12/site-packages/uvicorn/config.py", line 415, in load_app
  return import_from_string(self.app)
      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
 File "/home/appadmin/projects/Ram_Projects/DiracDelta/ekf/.venv-vllm/lib/python3.12/site-packages/uvicorn/importer.py", line 22, in import_from_str