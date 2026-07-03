# GCP Automation & Data Scripts

## Overview
This directory contains a collection of Python scripts designed to automate various Google Cloud Platform (GCP) operations. The scripts primarily focus on two main areas:
1. **Vertex AI Agent Deployment:** Rapidly provisioning and deploying LLM-powered agents using Vertex AI Agent Engine.
2. **Data Engineering & Integration:** Setting up BigQuery datasets, creating BigLake federated connections to MySQL, and loading/profiling data from Google Cloud Storage (GCS) and MySQL into BigQuery.

## Tech Stack
- **Language:** Python 3
- **GCP Services:** Vertex AI, BigQuery, BigLake, Google Cloud Storage (GCS)
- **External Systems:** MySQL
- **Key Libraries:** `google-cloud-aiplatform`, `google-cloud-bigquery`, `google-cloud-storage`, `mysql-connector-python`, `pandas`

## Key Components

### 🤖 Vertex AI Agent Deployment
- `DEPLOY_VERTEX_AGENT.py` / `deploy_vertex_agent.py`: Comprehensive, all-in-one scripts to set up prerequisites, enable APIs, and deploy a Gemini-powered reasoning engine to Vertex AI.
- `deploy_agent_now.py`: A streamlined, immediate deployment script for a Vertex AI agent.
- `agent.py` & `agent_gcs_loader.py`: Definitions for `LlmAgent` instances using the `google.adk.agents` framework, specifically tailored for data engineering, BigQuery profiling, and GCS data loading.

### 📊 BigQuery & BigLake Integration
- `setup_bigquery.py`: Initializes a BigQuery dataset (`mattelteam`) and populates a table with dummy data for testing.
- `deploy_bigquery_connection.py`: Creates an external federated connection from BigQuery to a local MySQL database and sets up federated views.
- `create_biglake_connection.py` / `create_biglake_connection_v2.py`: Scripts to establish BigLake connections to MySQL using the BigQuery Connection API.
- `test_bigquery_mysql_connection.py`: A comprehensive test suite to verify MySQL connectivity, GCP authentication, and federated query execution.

### 🔄 Data Pipelines & Ingestion
- `gcs_loader_helper.py`: Utility to load CSV files from GCS directly into BigQuery and automatically run data quality profiling (null counts, duplicates, etc.).
- `mysql_to_bigquery.py`: Extracts archive logs from a MySQL database, converts them to a Pandas DataFrame, and uploads them to BigQuery.

## Architecture Type
- **Automation & Provisioning:** Infrastructure-as-Code (IaC) style Python scripts for GCP resource creation.
- **Data Pipeline:** ELT (Extract, Load, Transform) scripts for moving data from GCS/MySQL to BigQuery.
- **Agent-based:** LLM orchestration using Vertex AI Reasoning Engines and MCP (Model Context Protocol) tools.

## Dependencies
To run these scripts, you need the following Python packages installed:
```bash
pip install google-cloud-aiplatform google-cloud-bigquery google-cloud-storage google-cloud-bigquery-connection mysql-connector-python pandas
```

## How to Run

### Prerequisites
Ensure you are authenticated with Google Cloud and have set your default project:
```bash
gcloud auth login
gcloud auth application-default login
gcloud config set project ctoteam
```

### Running a Script
Most scripts can be executed directly via Python. For example, to deploy a Vertex AI agent:
```bash
python3 deploy_vertex_agent.py
```

To load and profile data from GCS:
```bash
python3 gcs_loader_helper.py customers
```

To test the BigQuery to MySQL connection:
```bash
python3 test_bigquery_mysql_connection.py
```

## Suggested Improvements
- **Configuration Management:** Move hardcoded values (like `PROJECT_ID = "ctoteam"`, database credentials, and region) into a `.env` file or a centralized configuration module.
- **Error Handling:** Standardize logging across all scripts instead of using `print()` statements.
- **Consolidation:** Merge duplicate deployment scripts (`DEPLOY_VERTEX_AGENT.py` and `deploy_vertex_agent.py`) into a single parameterized CLI tool.
