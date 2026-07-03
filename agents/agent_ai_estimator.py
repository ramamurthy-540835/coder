#!/usr/bin/env python3
"""
PRISM Agent 2: AI Estimator with Gemini 3.5 Flash
Generates architecture specification, WBS, and task estimation.
Logs token usage to BigQuery.
"""

import sys
import os
import json
import argparse
import subprocess
import urllib.request
import urllib.error
import ssl
from datetime import datetime, timezone
from google.cloud import storage, bigquery

def log_info(msg):
    print(f"INFO: {msg}")

def log_success(msg):
    print(f"🟢 SUCCESS: {msg}")

def log_error(msg):
    print(f"❌ ERROR: {msg}", file=sys.stderr)

def get_access_token() -> str:
    """Acquire GCP access token."""
    try:
        res = subprocess.run(
            ["gcloud", "auth", "application-default", "print-access-token"],
            capture_output=True, text=True, check=True
        )
        return res.stdout.strip()
    except Exception:
        log_error("GCP authentication failed.")
        sys.exit(1)

def download_gcs_text_file(bucket_name: str, path: str) -> str:
    """Download text from GCS."""
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(path)
    if not blob.exists():
        return ""
    return blob.download_as_text()

def resolve_estimation_model(models_json_path: str, preferred_model: str = "gemini-flash") -> dict:
    """Resolve the best model for estimation from models.json."""
    try:
        with open(models_json_path, "r") as f:
            models = json.load(f)

        # Prefer the passed model, fallback to default, then gemini-flash
        model_key = preferred_model
        if model_key not in models.get("models", {}):
            model_key = models.get("default_model", "gemini-flash")

        model_info = models["models"].get(model_key, {})
        api_model_id = model_info.get("api_model_id", "vertex_ai/gemini-3.5-flash")

        # Extract base model name for Vertex AI URL (e.g. gemini-3.5-flash)
        if "gemini" in api_model_id:
            model_name = api_model_id.split("/")[-1]
        else:
            model_name = "gemini-3.5-flash"  # safe default

        return {
            "model_key": model_key,
            "api_model_id": api_model_id,
            "vertex_model_name": model_name,
            "display_name": model_info.get("display_name", model_name)
        }
    except Exception as e:
        log_error(f"Failed to resolve model from models.json: {e}. Falling back to gemini-3.5-flash")
        return {
            "model_key": "gemini-flash",
            "api_model_id": "vertex_ai/gemini-3.5-flash",
            "vertex_model_name": "gemini-3.5-flash",
            "display_name": "Gemini 3.5 Flash (fallback)"
        }


def select_best_prompt_content(out_dir: str) -> tuple[str, str]:
    """
    Select the best available prompt content for estimation.
    Preference order (best first):
    1. final_assembled.md
    2. assembled_requirements.md
    3. extracted_content.txt + system_instructions.md
    """
    candidates = [
        os.path.join(out_dir, "final_assembled.md"),
        os.path.join(out_dir, "assembled_requirements.md"),
        os.path.join(out_dir, "extracted_content.txt"),
    ]

    for path in candidates:
        if os.path.exists(path) and os.path.getsize(path) > 100:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            log_success(f"Using prompt content from: {os.path.basename(path)}")
            return os.path.basename(path), content

    # Fallback: combine system + extracted if nothing better exists
    sys_path = os.path.join(out_dir, "system_instructions.md")
    ext_path = os.path.join(out_dir, "extracted_content.txt")

    combined = ""
    if os.path.exists(sys_path):
        with open(sys_path, "r", encoding="utf-8") as f:
            combined += f.read() + "\n\n"
    if os.path.exists(ext_path):
        with open(ext_path, "r", encoding="utf-8") as f:
            combined += f.read()

    log_info("Using fallback combined system + extracted content")
    return "combined_fallback", combined or "No prompt content found."


def generate_gemini_estimation(project_id: str, location: str, model_config: dict,
                               token: str, system_inst: str, prompt_content: str,
                               source_file: str) -> tuple:
    """Call Vertex AI with the resolved model (dynamic, not hardcoded)."""

    model_name = model_config["vertex_model_name"]
    url = f"https://aiplatform.googleapis.com/v1/projects/{project_id}/locations/global/publishers/google/models/{model_name}:generateContent"

    architect_prompt = f"""You are a Principal Enterprise Software Architect. Analyze the following requirement and provide detailed Software Estimation and Architecture Specification.

SYSTEM INSTRUCTIONS:
{system_inst or "(None)"}

REQUIREMENTS:
{prompt_content}

---
Deliver a markdown report with:
1. COMPLEXITY ANALYSIS & GRADING (1-10 scale)
2. LANGCHAIN & ENTERPRISE ARCHITECTURE FRAMEWORK
3. WORK BREAKDOWN STRUCTURE (WBS) & TASK-HOUR ESTIMATION
4. FILES MODIFICATION MAP (create/modify lists)
"""

    payload = {
        "contents": [{
            "role": "user",
            "parts": [{"text": architect_prompt}]
        }],
        "generationConfig": {
            "temperature": 0.2,
            "maxOutputTokens": 8192,
            "topP": 0.95,
            "topK": 40
        }
    }

    req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"))
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("x-goog-user-project", project_id)
    req.add_header("Content-Type", "application/json")

    context = ssl.create_default_context()

    try:
        log_info(f"Invoking Vertex AI {model_config['display_name']} ({model_name}) for estimation...")
        with urllib.request.urlopen(req, context=context) as response:
            res_body = response.read().decode("utf-8")
            res_json = json.loads(res_body)

            text = res_json["candidates"][0]["content"]["parts"][0]["text"]
            usage = res_json.get("usageMetadata", {})

            return text, {
                "prompt_tokens": usage.get("promptTokenCount", 0),
                "completion_tokens": usage.get("candidatesTokenCount", 0),
                "total_tokens": usage.get("promptTokenCount", 0) + usage.get("candidatesTokenCount", 0),
                "model_used": model_config["display_name"],
                "source_prompt_file": source_file
            }
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8") if e.fp else ""
        log_error(f"Vertex AI API error: {e.code}")
        if err_body:
            print(err_body, file=sys.stderr)
        sys.exit(1)

def ensure_estimation_table_exists(client, project_id: str):
    """Create the estimation_results table if it doesn't exist (idempotent)."""
    dataset_id = "agent_telemetry"
    table_id = f"{project_id}.{dataset_id}.estimation_results"

    try:
        client.get_table(table_id)
    except Exception:
        schema = [
            bigquery.SchemaField("timestamp", "TIMESTAMP"),
            bigquery.SchemaField("prompt_id", "STRING"),
            bigquery.SchemaField("run_id", "STRING"),
            bigquery.SchemaField("agent", "STRING"),
            bigquery.SchemaField("model", "STRING"),
            bigquery.SchemaField("source_prompt_file", "STRING"),
            bigquery.SchemaField("estimation_markdown", "STRING"),
            bigquery.SchemaField("prompt_tokens", "INT64"),
            bigquery.SchemaField("completion_tokens", "INT64"),
            bigquery.SchemaField("total_tokens", "INT64"),
            bigquery.SchemaField("complexity_grade", "STRING"),
        ]
        table = bigquery.Table(table_id, schema=schema)
        table = client.create_table(table, exists_ok=True)
        log_success(f"Created BigQuery table: {table_id}")


def log_estimation_to_bigquery(project_id: str, prompt_id: str, run_id: str,
                               token_stats: dict, model: str, source_file: str,
                               estimation_markdown: str):
    """
    Save BOTH token usage AND the full estimation markdown result to BigQuery.
    This enables audit, approval workflow, and historical comparison.
    """
    try:
        client = bigquery.Client(project=project_id)
        dataset_id = "agent_telemetry"

        # Ensure dataset exists
        try:
            client.get_dataset(f"{project_id}.{dataset_id}")
        except Exception:
            client.create_dataset(f"{project_id}.{dataset_id}", exists_ok=True)

        # Ensure table exists with proper schema
        ensure_estimation_table_exists(client, project_id)

        table_id = f"{project_id}.{dataset_id}.estimation_results"

        # Try to extract a simple complexity grade from the markdown (best effort)
        complexity_grade = "Unknown"
        for line in estimation_markdown.splitlines():
            if "Complexity Grade" in line or "Grade:" in line:
                complexity_grade = line.strip()
                break

        row = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "prompt_id": prompt_id,
            "run_id": run_id,
            "agent": "ai_estimator",
            "model": model,
            "source_prompt_file": source_file,
            "estimation_markdown": estimation_markdown,
            "prompt_tokens": token_stats.get("prompt_tokens", 0),
            "completion_tokens": token_stats.get("completion_tokens", 0),
            "total_tokens": token_stats.get("total_tokens", 0),
            "complexity_grade": complexity_grade,
        }

        errors = client.insert_rows_json(table_id, [row])
        if errors:
            log_error(f"BigQuery estimation insert errors: {errors}")
        else:
            log_success(f"Saved full estimation result to BigQuery ({len(estimation_markdown)} chars)")
    except Exception as e:
        log_error(f"Failed to save estimation to BigQuery: {e}")

def main():
    parser = argparse.ArgumentParser(description="PRISM Agent 2: AI Estimator")
    parser.add_argument("--prompt-id", required=True, help="Prompt ID")
    parser.add_argument("--project-id", default="ctoteam")
    parser.add_argument("--location", default="us-central1")
    parser.add_argument("--model", default="gemini-3.5-flash", help="Gemini model")
    parser.add_argument("--bucket", default="agentproject")

    args = parser.parse_args()

    # Load system instructions and requirements
    out_dir = os.path.join("saved_prompts", args.prompt_id)
    sys_path = os.path.join(out_dir, "system_instructions.md")
    asm_path = os.path.join(out_dir, "assembled_requirements.md")
    meta_path = os.path.join(out_dir, "run_metadata.json")

    if not os.path.exists(sys_path) or not os.path.exists(asm_path):
        log_error("Missing system instructions or requirements. Run agent_gcs_puller first.")
        sys.exit(1)

    with open(sys_path, "r") as f:
        system_inst = f.read()
    with open(asm_path, "r") as f:
        full_assembled = f.read()
    with open(meta_path, "r") as f:
        meta = json.load(f)

    run_id = meta.get("run_id")

    # Generate estimation
    token = get_access_token()
    # Select best available prompt content
    source_file, prompt_content = select_best_prompt_content(out_dir)

    # Resolve model dynamically from models.json
    models_json_path = os.path.join("..", "coder", "models.json") if os.path.exists("../coder/models.json") else "models.json"
    if not os.path.exists(models_json_path):
        models_json_path = os.path.join(out_dir, "..", "..", "models.json")  # fallback

    model_config = resolve_estimation_model(models_json_path, args.model)

    estimation_text, token_stats = generate_gemini_estimation(
        args.project_id, args.location, model_config, token,
        system_inst, prompt_content, source_file
    )

    # Save estimation
    est_path = os.path.join(out_dir, "ai_estimation.md")
    with open(est_path, "w", encoding="utf-8") as f:
        f.write(estimation_text)
    log_success(f"Saved AI Estimation: {est_path}")

    # Save full estimation result + tokens to BigQuery (for audit + approval workflow)
    log_estimation_to_bigquery(
        args.project_id, args.prompt_id, run_id, token_stats,
        model_config["display_name"], source_file, estimation_text
    )

    # Save token stats
    tokens_path = os.path.join(out_dir, "token_stats.json")
    with open(tokens_path, "w", encoding="utf-8") as f:
        json.dump(token_stats, f, indent=2)
    log_success(f"Token stats: {token_stats}")

if __name__ == "__main__":
    main()
