#!/bin/bash
# Clear standard direct API keys to force native GCP Vertex AI authentication (ADC)
unset GEMINI_API_KEY
# Unset Google API Key to prevent direct Gemini API usage
unset GOOGLE_API_KEY
unset AIDER_GEMINI_API_KEY
unset AIDER_GOOGLE_API_KEY

set -euo pipefail

export GOOGLE_CLOUD_PROJECT="${GCP_PROJECT_ID:-ctoteam}"
export VERTEXAI_PROJECT="${GCP_PROJECT_ID:-ctoteam}"
export VERTEXAI_LOCATION="${VERTEXAI_LOCATION:-global}"
export GOOGLE_CLOUD_LOCATION="${GOOGLE_CLOUD_LOCATION:-global}"
export GOOGLE_REGION="${GOOGLE_REGION:-global}"

# =============================================
# PRISM Aider Launcher - Dynamic Model Router
# Fully verified and loaded.
# =============================================

ENV_FILE="${ENV_FILE:-.env.local}"

# Dynamic project root resolution: Detect whether start_aider.sh is in root or scripts/
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ -f "$SCRIPT_DIR/models.json" ]; then
 PROJECT_DIR="$SCRIPT_DIR"
else
 PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
fi

# Define log file with timestamp
LOG_FILE="$PROJECT_DIR/logs/aider_session_$(date +%Y%m%d_%H%M%S).log"

# Colors for output formatting
RED='\033[0;31m'
GREEN='\033[0;32m' # Green color for success messages
BLUE='\033[0;34m' # Blue color for headers
YELLOW='\033[0;33m'
NC='\033[0m' # No Color (reset)

echo -e "${BLUE}==================================================${NC}"
echo -e "${BLUE} 🚀 PRISM Aider Launcher (Dynamic Router)  ${NC}"
echo -e "${BLUE}==================================================${NC}"

cd "$PROJECT_DIR"
# Ensure logs directory exists
mkdir -p logs

# Pre-flight dependency checks
check_dep() {
 if ! command -v "$1" &> /dev/null; then
  echo -e "${RED}❌ Missing required dependency CLI: $1${NC}" >&2
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

# Model selection
MODEL_KEY="${1:-gemini-flash}"

# Query the models array safely using jq
MODEL_ENTRY=$(jq -r ".models[] | select(.id == \"$MODEL_KEY\")" models.json)

# Map legacy/fallback keys to available production ones
if [ -z "$MODEL_ENTRY" ]; then
  if [ "$MODEL_KEY" = "gemini-flash" ] || [ "$MODEL_KEY" = "gemini-1.5-flash" ]; then
    MODEL_KEY="gemini-3.5-flash"
    MODEL_ENTRY=$(jq -r ".models[] | select(.id == \"$MODEL_KEY\")" models.json)
  fi
fi

if [ -z "$MODEL_ENTRY" ]; then
 echo -e "${RED}❌ Unknown model key: $MODEL_KEY${NC}"
 echo -e "Available: $(jq -r '.models[].id' models.json | tr '\n' ',' | sed 's/,$//' | sed 's/,/, /g')"
 exit 1
fi

# Check if model is enabled
IS_ENABLED=$(echo "$MODEL_ENTRY" | jq -r '.enabled')
if [ "$IS_ENABLED" != "true" ]; then
 echo -e "${RED}❌ Model $MODEL_KEY is disabled in models.json.${NC}"
 exit 1
fi

# Formulate Aider's model identifier
PROVIDER=$(echo "$MODEL_ENTRY" | jq -r '.provider')
MODEL_ID=$(echo "$MODEL_ENTRY" | jq -r '.id')

if [ "$PROVIDER" = "vertexai" ]; then
  AIDER_MODEL="vertex_ai/$MODEL_ID"
else
  AIDER_MODEL="$MODEL_ID"
fi

DISPLAY_NAME=$(echo "$MODEL_ENTRY" | jq -r '.name')
echo -e "${GREEN}💎 Starting Aider | Model: $DISPLAY_NAME ($AIDER_MODEL)${NC}"

# Handle prompt file or phase argument
AIDER_EXTRA_ARGS=()
PROMPT_ARG="${2:-}"

# Execute aider with the formulated model name
if [ -n "$PROMPT_ARG" ]; then
 if [[ "$PROMPT_ARG" == *.md ]] || [[ "$PROMPT_ARG" == *.py ]]; then
  exec aider --model "$AIDER_MODEL" --no-auto-commits "$PROMPT_ARG"
 else
  exec aider --model "$AIDER_MODEL" --no-auto-commits --message "$PROMPT_ARG"
fi
else
 exec aider --model "$AIDER_MODEL" --no-auto-commits
fi
