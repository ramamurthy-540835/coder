# Agent Orchestration Platform

## Overview
The Agent Orchestration Platform (by BrickLabs / Mastech InfoTrellis) is a robust orchestration layer designed to build end-to-end AI solutions by chaining multiple Databricks agent serving endpoints into sequential workflows. It allows users to create, configure, and execute multi-agent pipelines with ease. 

In a larger AI platform, this project acts as the central nervous system that connects user interfaces, external APIs, and specialized AI agents. It manages the state, execution order, and data passing between different AI models, ensuring that the output of one agent seamlessly becomes the input for the next.

## Architecture
- **Backend**: Built with Node.js and Express.js, providing a lightweight and fast server environment.
- **API Routing**: Modularized routing (e.g., `routes/api.js`, `routes/pages.js`) to handle UI rendering and RESTful API requests for workflow execution.
- **UI Layer**: Server-side rendered views using EJS (`views/`), styled with custom CSS, providing an intuitive dashboard for workflow design and execution.
- **Integration Layer**: 
  - `gcp-adapter.js` for Google Cloud Platform integrations (Cloud Storage and external Flask APIs).
  - Python scripts for direct interaction with Databricks infrastructure.
- **Data Store**: Local JSON-based storage (`data/store.js`) for managing workspaces, solutions, and workflow steps.

## Key Components

### Server
- **`server.js`**: The main entry point of the application. It initializes the Express application, configures middleware (JSON parsing, static assets, EJS view engine), and registers the API and page routes.

### Routes
- **API Endpoints & Orchestration Logic**: Handles CRUD operations for workspaces and solutions, and contains the core orchestration logic to execute agents sequentially, passing context and outputs between steps.

### GCP Integration
- **`gcp-adapter.js`**: Replaces legacy Azure/Databricks direct calls with GCP equivalents. It handles uploading/reading workflow states and reports to/from Google Cloud Storage (GCS) and communicates with a Flask backend to fetch agent statuses and trigger agent executions.

### Python Utilities
- **`manage_endpoints.py`**: A CLI utility to monitor, start, stop, and validate Databricks serving endpoints. It interacts directly with the Databricks REST API to ensure the underlying models are in a `READY` state before workflows are executed.

### UI Layer
- **`views/` & Public Assets**: Contains EJS templates (`index.ejs`, `solution-form.ejs`, `solution-detail.ejs`, `settings.ejs`) that provide a drag-and-drop workflow designer, execution monitoring panels, and workspace configuration interfaces.

## Data Flow
1. **Request**: A user triggers a workflow execution via the UI, providing an initial input prompt or file.
2. **Orchestration**: The Node.js backend initializes the workflow state and begins iterating through the defined sequence of agent steps.
3. **Agent**: For each step, the input (combined with previous outputs if in broadcast mode) is formatted and sent to the respective Databricks serving endpoint or GCP-backed agent.
4. **Response**: The agent processes the data and returns an output. The orchestrator logs the result, updates the workflow state, and passes the output to the next agent in the pipeline. Final results are rendered in the UI.

## Setup Instructions

### Install dependencies
