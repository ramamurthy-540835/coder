"""GCS helper adapters for PRISM agent tools."""

from __future__ import annotations

from typing import Any


def upload_to_gcs(bucket_name: str, blob_path: str, content: str | bytes, content_type: str = "text/plain") -> str | None:
    """Upload content to a GCS blob and return the resulting gs:// URI."""
    try:
        from google.cloud import storage  # imported lazily to keep module import light
    except ImportError as exc:
        raise RuntimeError("google-cloud-storage is required for GCS uploads.") from exc

    try:
        client = storage.Client()
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(blob_path)
        if isinstance(content, bytes):
            blob.upload_from_string(content, content_type=content_type)
        else:
            blob.upload_from_string(content, content_type=content_type)
        return f"gs://{bucket_name}/{blob_path}"
    except Exception as exc:
        raise RuntimeError(f"Failed to upload to GCS {bucket_name}/{blob_path}: {exc}") from exc


def download_gcs_text_file(bucket_name: str, path: str) -> str:
    """Download a text blob from GCS. Return empty string if missing."""
    try:
        from google.cloud import storage  # imported lazily
    except ImportError as exc:
        raise RuntimeError("google-cloud-storage is required for GCS downloads.") from exc

    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(path)
    if not blob.exists():
        return ""
    return blob.download_as_text()


def fetch_latest_run_metadata(bucket_name: str, prompt_id: str) -> dict[str, Any]:
    """Fetch latest run metadata from GCS."""
    meta_path = f"saved-prompts/{prompt_id}/gold/latest.json"
    payload = download_gcs_text_file(bucket_name, meta_path)
    if not payload:
        raise FileNotFoundError(f"Latest pointer not found at gs://{bucket_name}/{meta_path}")
    return _safe_load_json(payload)


def _safe_load_json(payload: str) -> dict[str, Any]:
    import json

    parsed = json.loads(payload)
    if isinstance(parsed, dict):
        return parsed
    raise ValueError(f"Expected JSON object for metadata, got {type(parsed)!r}")
