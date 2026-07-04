#Author : Ramamurthy - Mastech Digital - Thanks to GCP - Gemini 3.5 - I am your fan!
# agents/gcp_deployer_langgraph.py
import os
import sys
import json
import uuid
import argparse
import subprocess
import logging
import urllib.request
import time
import re
from datetime import datetime
from typing import TypedDict, Literal
from langgraph.graph import StateGraph, END

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger("GCPDeployer")

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
BACKEND_DIR = PROJECT_ROOT
FRONTEND_DIR = os.path.abspath(os.path.join(PROJECT_ROOT, "..", "prompt-intelligence-ui"))

DEPLOY_TARGETS = {
  "sentinel-backend": {
    "dir": PROJECT_ROOT,
    "service": "sentinel-backend",
    "config_file": "cloudbuild.yaml",
  },
  "prism-frontend": {
    "dir": FRONTEND_DIR,
    "service": "prism-frontend",
    "config_file": "cloudbuild.yaml",
  }
}

class AgentState(TypedDict):
  target_service: str
  target_dir: str
  config_file: str
  gcp_project: str
  gcp_region: str
  model_id: str
  telemetry_table: str
  scan_results: dict
  cloudbuild_content: str
  error_logs: str
  attempts: int
  max_attempts: int
  healed: bool
  status: str
  user_email: str
  live_url: str

def fetch_build_logs(output_text: str) -> str:
  """Extracts the build ID from gcloud output/stderr and fetches the logs."""
  # Match any standard uuid4 pattern after /builds/
  build_id_match = re.search(r"builds/([a-f0-9\-]{36})", output_text)
  if not build_id_match:
    return "Could not find build ID in gcloud output."

  build_id = build_id_match.group(1)
  logger.info(f"Fetching detailed build logs for build ID: {build_id}")

  try:
    log_fetch_cmd = [
      "gcloud", "builds", "log", build_id, "--project=ctoteam"
    ]

    proc = subprocess.run(log_fetch_cmd, capture_output=True, text=True, check=True)
    return proc.stdout
  except Exception as e:
    return f"Failed to fetch build logs for build ID {build_id}: {e}"

def call_reasoning_model(model_id, prompt_text):
  # Using Vertex AI OpenAPI endpoint (Grok / Gemini / etc.)
  import google.auth
  import google.auth.transport.requests
  import openai
  credentials, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
  credentials.refresh(google.auth.transport.requests.Request())
  client = openai.OpenAI(
    base_url="https://aiplatform.googleapis.com/v1/projects/ctoteam/locations/global/endpoints/openapi",
    api_key=credentials.token
  )
  target_model = model_id.replace("xai/", "xai/") # No-op, preserves original model id
  payload = {"model": target_model, "messages": [{"role": "user", "content": prompt_text}]}
  response = client.chat.completions.create(**payload)
  return response.choices[0].message.content

def get_cloud_run_url(service_name, project, region):
  cmd = ["gcloud", "run", "services", "describe", service_name,
      f"--region={region}", f"--project={project}", "--format=value(status.url)"]
  try:
    proc = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return proc.stdout.strip()
  except Exception:
    return None

def verify_endpoint_health(url, service_name):
  import time
  health_url = f"{url}/health" if "sentinel" in service_name else f"{url}/api/status"
  logger.info(f"Starting reactive health check for {service_name} at {health_url}...")

  start_time = time.time()
  sleep_interval = 1.0  # Start with a fast 1-second check
  max_timeout_sec = 60

  while time.time() - start_time < max_timeout_sec:
    try:
      with urllib.request.urlopen(health_url, timeout=5) as r:
        if r.getcode() == 200:
          duration = time.time() - start_time
          logger.info(f"✓ Health check passed for {service_name} in {duration:.1f}s: {r.getcode()}")
          return True
    except Exception as e:
      logger.info(f"⏳ Service booting or cold-starting... checking again in {sleep_interval:.1f}s...")

    time.sleep(sleep_interval)
    # Exponential backoff up to 8 seconds
    sleep_interval = min(sleep_interval * 1.5, 8.0)

  logger.error(f"❌ Health check failed: {service_name} failed to respond after {max_timeout_sec}s.")
  return False

def scan_node(state: AgentState) -> AgentState:
  logger.info(f"Validating Cloud Build target: {state['target_service']}")
  path = state["target_dir"]
  has_build = os.path.exists(os.path.join(path, state["config_file"]))
  if not has_build:
    logger.error(f"Cloud Build config missing: {os.path.join(path, state['config_file'])}")
    return {**state, "status": "failed", "error_logs": "Cloud Build config missing"}

  with open(os.path.join(path, state["config_file"]), "r") as f:
    build_content = f.read()

  return {
    **state,
    "scan_results": {"has_cloudbuild": has_build},
    "cloudbuild_content": build_content,
    "status": "idle"
  }

def build_node(state: AgentState) -> AgentState:
  logger.info(f"Starting Cloud Build for {state['target_service']} (Attempt {state['attempts'] + 1})...")

  if state.get("status") == "failed":
      logger.error("Build node aborted due to prior initialization failure.")
      return {**state, "attempts": 99}

  cmd = [
    "gcloud", "builds", "submit",
    f"--config={state['config_file']}",
    f"--project={state['gcp_project']}",
    "."
  ]

  try:
    proc = subprocess.run(cmd, cwd=state["target_dir"], capture_output=True, text=True, check=True)
    logger.info("✅ Cloud Build succeeded!")

    service_name = state["target_service"]
    live_url = get_cloud_run_url(service_name, state["gcp_project"], state["gcp_region"])

    if live_url:
      logger.info(f"🌐 Live URL: {live_url}")
      verify_endpoint_health(live_url, service_name)

    return {**state, "status": "success", "live_url": live_url or ""}
  except subprocess.CalledProcessError as e:
    logger.error("❌ Build failed")
    detailed_logs = fetch_build_logs(e.stderr + "\n" + (e.stdout or ""))
    logger.error("="*20 + " DETAILED BUILD LOGS " + "="*20)
    logger.error(detailed_logs)
    logger.error("="*62)
    return {**state, "status": "failed", "error_logs": detailed_logs, "attempts": state["attempts"] + 1}

def heal_node(state: AgentState) -> AgentState:
  logger.info("--- NODE: SELF-HEALING RECOVERY ---")
  logger.warning("Cloud-only mode disables automatic self-healing. Returning failure for Cloud Build review.")
  return {
    **state,
    "status": "failed",
    "error_logs": state.get("error_logs", "") or "Self-healing is disabled in cloud-only deployment mode.",
    "healed": False,
  }

def log_node(state: AgentState) -> AgentState:
  logger.info("Logging deployment to BigQuery...")
  if state.get("status") == "failed" and state.get("attempts") == 99:
      logger.warning("Audit Log bypassed due to initialization failure.")
      return state
      
  try:
    from google.cloud import bigquery
    client = bigquery.Client(project=state["gcp_project"])
    log_row = {
      "log_id": str(uuid.uuid4()),
      "user_email": state["user_email"],
      "action_type": "deploy",
      "prompt_id": state["target_service"],
      "model_id": f"{state['model_id']}-langgraph-healed-{state.get('healed', False)}",
      "input_tokens": 1500,
      "output_tokens": 500,
      "cost_usd": 0.0,
      "output_file_or_uri": f"gcp:cloud-run:{state['target_service']}",
      "timestamp": datetime.utcnow().isoformat()
    }
    client.insert_rows_json(state["telemetry_table"], [log_row])
    logger.info("✓ Logged deployment to BigQuery successfully!")
  except Exception as e:
    logger.warning(f"Failed to log deployment telemetry to BigQuery: {e}")
  return state

# =====================================================================
# 3. Dynamic Conditional Router
# =====================================================================

def after_build(state: AgentState) -> Literal["heal", "log"]:
    if state["status"] == "success":
        return "log"
    if state["attempts"] < state["max_attempts"]:
        return "heal"
    return "log"

def run_decoupled_deployment_graph(args):
  workflow = StateGraph(AgentState)

  workflow.add_node("scan", scan_node)
  workflow.add_node("build", build_node)
  workflow.add_node("heal", heal_node) # Cloud Build review node
  workflow.add_node("log", log_node)

  workflow.set_entry_point("scan")

  def after_scan(state: AgentState) -> Literal["build", "log"]:
    if state["status"] == "failed":
      return "log"
    return "build"

  workflow.add_conditional_edges(
    "scan",
    after_scan,
    {
      "build": "build",
      "log": "log"
    }
  )
  
  # Register the dynamic build-to-heal/log conditional edges
  workflow.add_conditional_edges(
    "build",
    after_build,
    {
      "heal": "heal",
      "log": "log"
    }
  )

  # Route heal node back to scan to execute the complete validation loop
  workflow.add_edge("heal", "scan")
  workflow.add_edge("log", END)

  app = workflow.compile()

  initial_state = AgentState(
    target_service=args.service or os.path.basename(args.dir),
    target_dir=args.dir,
    config_file=args.config_file,
    gcp_project=args.project,
    gcp_region=args.region,
    model_id=args.model,
    telemetry_table=args.telemetry_table,
    scan_results={},
    cloudbuild_content="",
    error_logs="",
    attempts=0,
    max_attempts=args.max_attempts,
    healed=False,
    status="idle",
    user_email=args.user_email,
    live_url=""
  )

  logger.info("Running LangGraph deployment workflow...")
  final_state = app.invoke(initial_state)
  logger.info(f"Deployment finished with status: {final_state['status']} (Live URL: {final_state.get('live_url', 'N/A')})")
  return final_state

if __name__ == "__main__":
  parser = argparse.ArgumentParser(description="Flexible GCP Cloud Run Deployer")
  parser.add_argument("mode", nargs="?", default=None, help="Use 'deploy' to deploy the GCP target")
  parser.add_argument("--dir", required=False, help="Deprecated. Cloud-only mode uses the GCP deployment target.")
  parser.add_argument("--service", required=False, help="Cloud Run service name")
  parser.add_argument("--config-file", default="cloudbuild.yaml", help="Cloud Build config file")
  parser.add_argument("--project", default="ctoteam")
  parser.add_argument("--region", default="us-central1")
  parser.add_argument("--model", default="xai/grok-4.3")
  parser.add_argument("--max-attempts", type=int, default=2)
  parser.add_argument("--user-email", default="ramamurthy.valavandan@mastechdigital.com")
  parser.add_argument("--telemetry-table", default="ctoteam.prism_sentinel_audit.usage_logs")

  args = parser.parse_args()

  if args.mode not in (None, "deploy", "both"):
    parser.error("Only cloud deployment modes are supported: deploy or both.")

  if args.mode == "both":
    logger.info("Deploying BOTH services (sentinel-backend → prism-frontend)")
    for s_name in ["sentinel-backend", "prism-frontend"]:
      target = DEPLOY_TARGETS[s_name]
      deploy_args = argparse.Namespace(**vars(args))
      deploy_args.dir = target["dir"]
      deploy_args.service = target["service"]
      deploy_args.config_file = target["config_file"]
      run_decoupled_deployment_graph(deploy_args)
  else:
    service_name = args.service or "sentinel-backend"
    target = DEPLOY_TARGETS.get(service_name)
    if not target:
      parser.error(f"Unsupported Cloud Run service: {service_name}")

    deploy_args = argparse.Namespace(**vars(args))
    deploy_args.dir = target["dir"]
    deploy_args.service = target["service"]
    deploy_args.config_file = target["config_file"]
    run_decoupled_deployment_graph(deploy_args)
