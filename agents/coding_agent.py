#!/usr/bin/env python3
import os
import sys
import json
import uuid
import logging

# Add the project root to sys.path so that 'agents' package can be found when executed directly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from agents.pipeline.shared import get_bq_client, fetch_prompt_chunks, log_build_state, upload_to_gcs
from agents.pipeline.agent1_discovery import Agent1_StackDiscovery
from agents.pipeline.agent2_design import Agent2_SystemDesign
from agents.pipeline.agent3_audit import Agent3_DevSecOpsAudit
from agents.pipeline.agent4_compiler import Agent4_PolyglotCompiler
from agents.pipeline.agent5_release import Agent5_ReleaseManager

# Minimal local temp only
os.makedirs("logs", exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] [%(name)s] %(message)s',
    handlers=[logging.FileHandler("logs/coding_agent_execution.log"), logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("Prism5AgentOrchestrator")


# ==================== ORCHESTRATOR ====================

def execute_cooperative_pipeline(prompt_id, user_email="ramamurthy.valavandan @mastechdigital.com"):
    client = get_bq_client()
    if not client:
        return {"status": "error", "message": "BigQuery auth failed"}

    run_uuid = str(uuid.uuid4())[:12]
    prompt_spec = fetch_prompt_chunks(client, prompt_id)

    if not prompt_spec:
        return {"status": "error", "message": "No prompt chunks found"}

    logger.info(f"🚀 Starting 5-Agent Pipeline for Prompt {prompt_id}")

    try:
        # Agent 1
        agent1 = Agent1_StackDiscovery()
        stack = agent1.analyze(prompt_spec)
        log_build_state(client, user_email, prompt_id, run_uuid, "DISCOVERY", "SUCCESS", json.dumps(stack))

        # Agent 2
        agent2 = Agent2_SystemDesign()
        design = agent2.design(prompt_spec, stack)
        design_uri = upload_to_gcs("agentproject", f"prompts/{prompt_id}/{run_uuid}/01_design/design.md", design)
        log_build_state(client, user_email, prompt_id, run_uuid, "DESIGN", "SUCCESS", design_uri)

        # Agent 3
        agent3 = Agent3_DevSecOpsAudit()
        audit = agent3.audit(design, stack)
        audit_uri = upload_to_gcs("agentproject", f"prompts/{prompt_id}/{run_uuid}/02_review/review-report.md", audit)
        log_build_state(client, user_email, prompt_id, run_uuid, "AUDIT", "SUCCESS", audit_uri)

        # Agent 4
        agent4 = Agent4_PolyglotCompiler()
        project_payload = agent4.compile(prompt_spec, stack, design, audit, prompt_id)
        log_build_state(client, user_email, prompt_id, run_uuid, "COMPILE", "SUCCESS", f"{len(project_payload.get('files', {}))} files")

        # Agent 5
        agent5 = Agent5_ReleaseManager()
        zip_uri = agent5.package(client, user_email, prompt_id, run_uuid, project_payload, stack)

        logger.info(f"🎉 Pipeline Complete! ZIP: {zip_uri}")

        return {
            "status": "success",
            "run_uuid": run_uuid,
            "tech_stack": stack,
            "design_uri": design_uri,
            "audit_uri": audit_uri,
            "release_zip": zip_uri,
            "files_generated": len(project_payload.get('files', {}))
        }

    except Exception as e:
        logger.error(f"Pipeline failed: {e}", exc_info=True)
        log_build_state(client, user_email, prompt_id, run_uuid, "FAILURE", "FAILED", str(e))
        return {"status": "error", "message": str(e)}


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"status": "error", "message": "Usage: python3 agents/coding_agent.py <prompt_id>"}))
        sys.exit(1)

    prompt_id = sys.argv[1]
    result = execute_cooperative_pipeline(prompt_id)
    print(json.dumps(result, indent=2))
