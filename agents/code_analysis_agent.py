#!/usr/bin/env python3
"""
PRISM Code Analysis Agent (xAI Grok-4.3 Multi-Project Spec Generator)

Statically scans multiple specified project directories dynamically,
resolves prompt requirements, and calls Grok-4.3 to output a unified task spec 'prompt.md'.
"""

import os
import sys
import argparse
import json
import logging
from pathlib import Path
from datetime import datetime, timezone
from typing import List
from google.cloud import bigquery

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("logs/code_analysis_agent.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("CodeAnalysisAgent")


def get_gcp_token_and_client() -> tuple:
    """Acquires GCP credentials and BigQuery client natively."""
    try:
        import google.auth
        import google.auth.transport.requests
        credentials, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
        credentials.refresh(google.auth.transport.requests.Request())
        client = bigquery.Client(credentials=credentials, project=credentials.project)
        return credentials.token, client
    except Exception as e:
        logger.error(f"GCP Authentication or BQ Client failed: {e}")
        logger.info("Please run: gcloud auth application-default login")
        sys.exit(1)


def assemble_prompt_from_bq(client: bigquery.Client, prompt_uid: str) -> str:
    """Reconstructs the full prompt text sequentially from BigQuery chunks."""
    logger.info(f"Querying BigQuery chunks for {prompt_uid}...")
    query = """
    SELECT chunk_order, chunk_file
    FROM `ctoteam.prism_prompt_catalog.prompt_chunks`
    WHERE prompt_uid = @prompt_uid
    ORDER BY chunk_order ASC
    """
    job_config = bigquery.QueryJobConfig(
        query_parameters=[bigquery.ScalarQueryParameter("prompt_uid", "STRING", prompt_uid)]
    )
    try:
        query_job = client.query(query, job_config=job_config)
        rows = list(query_job.result())
        if not rows:
            return ""
            
        local_content = []
        prompt_id = prompt_uid.split(":")[-1]
        for row in rows:
            possible_paths = [
                Path(f"saved_prompts/{prompt_id}/runs"),
                Path(f"../gcloud_run/saved_prompts/{prompt_id}/runs")
            ]
            found = False
            for runs_root in possible_paths:
                if runs_root.exists():
                    for run_dir in sorted(runs_root.iterdir(), key=lambda p: p.stat().st_mtime, reverse=True):
                        chunk_path = run_dir / "silver" / "chunks" / row["chunk_file"]
                        if chunk_path.exists():
                            local_content.append(chunk_path.read_text(encoding="utf-8"))
                            found = True
                            break
                if found:
                    break
            
            if not found:
                fallback_path = Path(f"saved_prompts/{prompt_id}/{row['chunk_file']}")
                if fallback_path.exists():
                    local_content.append(fallback_path.read_text(encoding="utf-8"))
                    
        if local_content:
            return "\n".join(local_content)
        return ""
    except Exception as e:
        logger.warning(f"Failed to query BigQuery chunks: {e}")
        return ""


def auto_detect_local_requirements() -> tuple:
    """Scans local directories to auto-detect requirements if prompt-id is omitted."""
    saved_prompts_dir = Path("saved_prompts")
    if not saved_prompts_dir.exists():
        return "", "Unknown Prompt"
        
    prompt_dirs = [d for d in saved_prompts_dir.iterdir() if d.is_dir() and d.name.isdigit()]
    if not prompt_dirs:
        return "", "Unknown Prompt"
        
    latest_prompt_dir = max(prompt_dirs, key=lambda d: d.stat().st_mtime)
    prompt_id = latest_prompt_dir.name
    logger.info(f"Auto-detected most recent local prompt cache: ID {prompt_id}")
    
    content_paths = [
        latest_prompt_dir / "final_assembled.md",
        latest_prompt_dir / "extracted_content.txt",
        latest_prompt_dir / "master.md"
    ]
    for path in content_paths:
        if path.exists():
            return path.read_text(encoding="utf-8"), f"vertexai:{prompt_id}"

    return "", f"vertexai:{prompt_id}"


def read_codebase_contents(base_dirs: List[Path]) -> str:
    """Recursively reads all relevant code files across multiple specified base directories."""
    code_context = []
    ignore_dirs = {".git", "node_modules", "venv", "__pycache__", ".aider.tags.cache.v4", ".claude", "generated_code", ".next", "out"}
    allowed_suffixes = {".py", ".sh", ".ts", ".tsx", ".sql", ".json"}

    for base_dir in base_dirs:
        base_path = Path(base_dir).resolve()
        if not base_path.exists():
            logger.warning(f"Specified directory does not exist: {base_path}")
            continue
            
        logger.info(f"Scanning target directory: {base_path.name}...")
        for root, dirs, files in os.walk(base_path):
            dirs[:] = [d for d in dirs if d not in ignore_dirs]
            for file in files:
                file_path = Path(root) / file
                if file_path.suffix in allowed_suffixes and not file.startswith("."):
                    try:
                        rel_path = file_path.relative_to(base_path)
                        content = file_path.read_text(encoding="utf-8", errors="ignore")
                        code_context.append(f"=== FILE: {base_path.name}/{rel_path} ===\n{content}\n")
                    except Exception as e:
                        logger.warning(f"Skipped file {file}: {e}")

    return "\n\n".join(code_context)


def run_grok_analysis(token: str, scope: str, codebase: str) -> str:
    """Invokes xAI Grok-4.3 reasoning model to generate prompt.md task spec."""
    try:
        import openai
        
        client = openai.OpenAI(
            base_url="https://aiplatform.googleapis.com/v1/projects/ctoteam/locations/global/endpoints/openapi",
            api_key=token
        )
        
        system_instructions = (
            "You are an expert enterprise Principal Architect and AI Code Spec Generator. "
            "You are reviewing multiple codebase directories (e.g., Next.js frontend, Python Sentinel, Python backend coder). "
            "Identify the gap between the requirements and current implementation. Specifically, trace "
            "why the frontend cannot connect to the backend, locate hardcoded port/IP bottlenecks, "
            "and output a detailed, highly structured task specification file called 'prompt.md'. "
            "This file will be used by downstream Aider coding agents to apply the fixes. "
            "Ensure you specify the exact file paths and code modifications cleanly."
        )
        
        prompt_content = f"""
TARGET SPECIFICATION SCOPE:
{scope}

======================================================================
ACTIVE MULTI-PROJECT CODEBASE:
{codebase}
"""
        
        logger.info("Invoking xai/grok-4.3 on Vertex OpenAI endpoint (reasoning_effort: low)...")
        response = client.chat.completions.create(
            model="xai/grok-4.3",
            messages=[
                {"role": "system", "content": system_instructions},
                {"role": "user", "content": prompt_content}
            ],
            reasoning_effort="low"
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Grok-4.3 API Inference failed: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="PRISM Multi-Project Code Analysis & prompt.md Spec Generator")
    parser.add_argument("--prompt-id", help="Vertex AI Dataset Saved Prompt ID")
    parser.add_argument("--dirs", nargs="+", default=["."], help="Directories of the codebases to analyze")
    
    args = parser.parse_args()
    
    # Map raw string inputs to Path objects
    target_dirs = [Path(d) for d in args.dirs]
    
    logger.info("==================================================")
    logger.info("PRISM AGENT 1: GROK-4.3 MULTI-PROJECT ANALYSIS")
    logger.info("==================================================")
    logger.info(f"Target Scan Directories: {[str(d.resolve()) for d in target_dirs]}")

    token, client = get_gcp_token_and_client()
    scope_content = ""
    prompt_uid = "Unknown"

    # Step 1: Resolve requirements scope
    if args.prompt_id:
        prompt_uid = f"vertexai:{args.prompt_id}"
        scope_content = assemble_prompt_from_bq(client, prompt_uid)
        
    if not scope_content:
        scope_content, prompt_uid = auto_detect_local_requirements()

    if not scope_content:
        logger.error("Could not find or assemble any requirements scope specifications.")
        sys.exit(1)
        
    logger.info(f"Target Prompt Context Resolved: {prompt_uid}")

    # Step 2: Read multi-project codebase files across the specified directories
    codebase_content = read_codebase_contents(target_dirs)
    if not codebase_content:
        logger.error("No valid source code files found in the specified target directories.")
        sys.exit(1)
        
    logger.info(f"Collected codebases context ({len(codebase_content)} characters).")

    # Step 3: Run High-Reasoning Grok-4.3 Inference to generate prompt.md
    prompt_md_spec = run_grok_analysis(token, scope_content, codebase_content)

    # Step 4: Write prompt.md in current directory
    prompt_file = Path("prompt.md")
    prompt_file.write_text(prompt_md_spec, encoding="utf-8")
    
    # Save a copy in reports for tracking
    reports_dir = Path("reports")
    reports_dir.mkdir(exist_ok=True)
    (reports_dir / f"prompt_{prompt_uid.replace(':', '_')}.md").write_text(prompt_md_spec, encoding="utf-8")

    logger.info("==================================================")
    logger.info(f"🟢 SUCCESS: Saved Multi-Project Task Spec File: {prompt_file}")
    logger.info("==================================================")


if __name__ == "__main__":
    main()
