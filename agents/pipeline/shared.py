import json
import logging
from datetime import datetime

from google.cloud import bigquery
from google.cloud import storage
import google.auth
import google.auth.transport.requests
import openai

logger = logging.getLogger("Prism5AgentOrchestrator")


def get_bq_client():
    try:
        return bigquery.Client()
    except Exception as e:
        logger.error(f"BQ client failed: {e}")
        return None


def fetch_prompt_chunks(client, prompt_id):
    query = """
    SELECT chunk_order, chunk_file
    FROM `ctoteam.prism_prompt_catalog.prompt_chunks`
    WHERE prompt_uid = @prompt_id OR prompt_uid = CONCAT('vertexai:', @prompt_id)
    ORDER BY chunk_order ASC
    """
    job_config = bigquery.QueryJobConfig(
        query_parameters=[bigquery.ScalarQueryParameter("prompt_id", "STRING", prompt_id)]
    )
    try:
        rows = list(client.query(query, job_config=job_config).result())
        return "\n".join([row["chunk_file"] for row in rows]) if rows else ""
    except Exception as e:
        logger.error(f"Chunk fetch failed: {e}")
        return ""


def call_grok_43_reasoning(prompt_text, json_mode=False):
    credentials, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
    credentials.refresh(google.auth.transport.requests.Request())
    client = openai.OpenAI(
        base_url="https://aiplatform.googleapis.com/v1/projects/ctoteam/locations/global/endpoints/openapi",
        api_key=credentials.token
    )
    args = {
        "model": "xai/grok-4.3",
        "messages": [{"role": "user", "content": prompt_text}],
        "temperature": 0.2
    }
    if json_mode:
        args["response_format"] = {"type": "json_object"}
    response = client.chat.completions.create(**args)
    return response.choices[0].message.content


def upload_to_gcs(bucket_name, blob_path, content, content_type="text/plain"):
    try:
        client = storage.Client()
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(blob_path)
        if isinstance(content, str):
            blob.upload_from_string(content, content_type=content_type)
        else:
            blob.upload_from_file(content, content_type=content_type)
        return f"gs://{bucket_name}/{blob_path}"
    except Exception as e:
        logger.error(f"GCS upload failed {blob_path}: {e}")
        return None


def log_build_state(client, user_email, prompt_id, run_uuid, phase, status, details=""):
    row = {
        "build_id": run_uuid,
        "prompt_id": f"vertexai:{prompt_id}",
        "user_email": user_email,
        "phase": phase,
        "status": status,
        "details": details,
        "timestamp": datetime.utcnow().isoformat()
    }
    try:
        client.insert_rows_json("ctoteam.prism_sentinel_audit.build_runs", [row])
    except Exception:
        pass  # Graceful
