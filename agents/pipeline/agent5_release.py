import os
import logging
import shutil
import tempfile

from .shared import upload_to_gcs, log_build_state

logger = logging.getLogger(__name__)

class Agent5_ReleaseManager:
    def package(self, client, user_email, prompt_id, run_uuid, project_payload, stack):
        logger.info("[AGENT 5] Packaging & GCS Release...")
        base_dir = tempfile.mkdtemp()
        files = project_payload.get("files", {})

        for rel_path, content in files.items():
            full_path = os.path.join(base_dir, rel_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(content)

        zip_path = f"{base_dir}.zip"
        shutil.make_archive(base_dir, 'zip', base_dir)

        with open(zip_path, "rb") as f:
            zip_uri = upload_to_gcs("agentproject", f"prompts/{prompt_id}/{run_uuid}/04_package/full_project.zip", f, "application/zip")

        # Cleanup
        shutil.rmtree(base_dir, ignore_errors=True)
        os.unlink(zip_path)

        # Telemetry
        log_build_state(client, user_email, prompt_id, run_uuid, "RELEASE", "SUCCESS", zip_uri)
        return zip_uri
