# Vertex AI Agent Engine - Deployment & Examples

Welcome! This directory contains everything you need to deploy AI agents to Google Cloud Vertex AI Agent Engine.

## Overview
This project provides a collection of production-ready scripts, templates, and examples for deploying intelligent agents to Google Cloud's Vertex AI. It simplifies the process of provisioning, configuring, and deploying Large Language Model (LLM) powered agents, ranging from simple conversational bots to advanced data analysis engines.

## Architecture
The repository follows an **Agent-based Architecture** leveraging Google Cloud Platform (GCP) managed services:
- **Orchestration:** Vertex AI Agent Engine (`vertexai.agent_engines.AgentEngine`)
- **Compute/Execution:** Serverless execution via GCP Vertex AI endpoints
- **Authentication:** Google Cloud IAM and Application Default Credentials (ADC)
- **Integration:** Designed to easily integrate with GCP tools (like BigQuery, GCS) and external APIs.

## Agent Types
Currently, the repository provides templates for two primary types of agents:

1. **Simple Conversational Agent (`simple_hello_agent.py`)**
   - **Purpose:** Basic Q&A and conversational interactions.
   - **Complexity:** Low. Perfect for learning and testing the deployment pipeline.
   - **Features:** Standard prompt instructions, basic Vertex AI initialization.

2. **Advanced Data Agent (`advanced_data_agent.py`)**
   - **Purpose:** Business intelligence, data analysis, and multi-step reasoning.
   - **Complexity:** High. Designed for enterprise workflows.
   - **Features:** Production-grade logging, configuration validation, complex system prompts, and readiness for tool/API integration.

## Key Scripts
| File | Purpose |
|------|---------|
| `quickstart.sh` | One-click bash deployment script. Handles GCP config, API enabling, and deployment automatically. |
| `simple_hello_agent.py` | Beginner-friendly Python deployment script for a basic agent. |
| `advanced_data_agent.py` | Production-grade Python deployment script with robust error handling and logging. |
| `QUICK_REFERENCE.md` | Cheat sheet for common gcloud commands, troubleshooting, and quick tasks. |
| `requirements.txt` | Python dependencies required for deployment. |

## How to Run

### Step 1: Prerequisites & Authentication
Ensure you have Python 3.8+ and the Google Cloud CLI installed.
```bash
# Login to Google Cloud
gcloud auth login
gcloud auth application-default login

# Set your project
export GCP_PROJECT_ID="your-project-id"
gcloud config set project $GCP_PROJECT_ID --quiet
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Deploy an Agent (Choose One Method)

**Method A: Quick Start (Easiest)**
```bash
bash quickstart.sh
```

**Method B: Simple Python Agent**
```bash
export AGENT_NAME="my-first-agent"
python3 simple_hello_agent.py
```

**Method C: Advanced Production Agent**
```bash
export AGENT_NAME="production-data-agent"
export GCP_REGION="us-central1"
python3 advanced_data_agent.py
```

### Step 4: Verification
After deployment, view your agent in the [Google Cloud Console](https://console.cloud.google.com/vertex-ai/agent-builder) or list it via CLI:
```bash
gcloud ai agents list --location=us-central1
```

## Dependencies
The project relies on the following core libraries (see `requirements.txt` for exact versions):
- `google-cloud-aiplatform`: Core Vertex AI SDK.
- `google-cloud-storage`: For managing agent artifacts and data.
- `google-auth` & `google-auth-oauthlib`: For secure GCP authentication.
- `vertexai`: High-level Vertex AI API wrapper.
- `python-dotenv`: For local environment variable management.

## Use Cases
- **Customer Support Automation:** Deploy the Simple Hello Agent to handle tier-1 customer inquiries and FAQs.
- **Business Intelligence:** Use the Advanced Data Agent to analyze sales trends, generate insights from BigQuery data, and create automated reports.
- **Internal Developer Tools:** Provide developers with an interactive CLI or chat interface to query system logs or documentation.
- **Rapid Prototyping:** Quickly spin up Vertex AI agents to test new LLM prompts and tool integrations before building full-stack applications.

---

## 🚨 Troubleshooting

| Issue | Solution |
|-------|----------|
| **Auth error** | Run `gcloud auth login` and `gcloud auth application-default login` |
| **API not enabled** | Run `gcloud services enable aiplatform.googleapis.com` |
| **Permission denied** | Ensure your account has the `roles/aiplatform.user` IAM role |
| **ImportError** | Run `pip install --upgrade google-cloud-aiplatform vertexai` |

## 🔗 Useful Links
- **Cloud Console:** [Vertex AI Agent Builder](https://console.cloud.google.com/vertex-ai/agent-builder)
- **Documentation:** [Vertex AI Agents Docs](https://cloud.google.com/vertex-ai/docs/agents)
- **Python SDK:** [Vertex AI Python Reference](https://cloud.google.com/python/docs/reference/vertexai)
