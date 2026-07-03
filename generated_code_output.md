File: agents/prompt_id_coder_agent.py
```python
#!/usr/bin/env python3
"""
PRISM Coder Agent - Prompt-ID Coding Agent
Fetches saved prompts from Vertex AI Dataset API, extracts content deterministically,
prepares a local prompt package, and launches Aider automatically.
"""

import argparse
import base64
from datetime import datetime
import json
import logging
import os
import subprocess
import sys
import urllib.error
import urllib.request

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)


def get_gcp_project() -> str:
    """Attempts to get the active GCP project, falling back to 'ctoteam'."""
    try:
        res = subprocess.run(
            ["gcloud", "config", "get-value", "project"],
            capture_output=True,
            text=True,
            check=True
        )
        project = res.stdout.strip()
        if project:
            return project
    except Exception:
        pass
    return "ctoteam"


def get_access_token() -> str:
    """Retrieves GCP access token using gcloud CLI with fallback options."""
    try:
        res = subprocess.run(
            ["gcloud", "auth", "print-access-token"],
            capture_output=True,
            text=True,
            check=True
        )
        return res.stdout.strip()
    except Exception:
        pass

    try:
        res = subprocess.run(
            ["gcloud", "auth", "application-default", "print-access-token"],
            capture_output=True,
            text=True,
            check=True
        )
        return res.stdout.strip()
    except Exception:
        logging.error("Authentication failed. Please run the following commands to authenticate:")
        print("\n  gcloud auth login --no-launch-browser", file=sys.stderr)
        print("  gcloud auth application-default login --no-launch-browser", file=sys.stderr)
        print("  gcloud config set project ctoteam\n", file=sys.stderr)
        sys.exit(1)


def fetch_dataset(project_id: str, location: str, prompt_id: str, token: str) -> dict:
    """Fetches the dataset from Vertex AI Dataset API."""
    url = f"https://us-central1-aiplatform.googleapis.com/v1/projects/{project_id}/locations/{location}/datasets/{prompt_id}"
    logging.info(f"Fetching dataset from: {url}")
    
    req = urllib.request.Request(url)
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Content-Type", "application/json")
    
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        err_msg = e.read().decode("utf-8")
        logging.error(f"HTTP Error {e.code}: {err_msg}")
        raise RuntimeError(f"Failed to fetch dataset: {err_msg}") from e
    except Exception as e:
        logging.error(f"Unexpected error fetching dataset: {e}")
        raise


def extract_content(data: dict) -> tuple[str, str, list[str]]:
    """
    Deterministically extracts system instructions, text content, and binary placeholders
    from the raw dataset JSON.
    """
    system_parts = []
    text_parts = []
    binary_placeholders = []

    def traverse(val, current_key=None):
        if isinstance(val, dict):
            # Check for inlineData / attachment structure
            mime_type = val.get("mimeType") or val.get("mime_type")
            data_bytes = val.get("data") or val.get("inlineData")
            if mime_type and data_bytes:
                if isinstance(data_bytes, dict) and "data" in data_bytes:
                    mime_type = data_bytes.get("mimeType", mime_type)
                    data_bytes = data_bytes.get("data")
                
                if isinstance(data_bytes, str):
                    if "text" in mime_type:
                        try:
                            decoded = base64.b64decode(data_bytes).decode("utf-8")
                            text_parts.append(decoded)
                        except Exception as e:
                            text_parts.append(f"[Failed to decode text attachment: {e}]")
                    else:
                        binary_placeholders.append(f"[Binary Attachment: {mime_type} ({len(data_bytes)} base64 chars)]")
                return

            for k, v in val.items():
                if k in {"name", "metadataSchemaUri", "createTime", "updateTime", "etag", "labels"}:
                    continue
                if k in {"systemInstruction", "system_instruction", "system-instruction"}:
                    if isinstance(v, str):
                        system_parts.append(v)
                    elif isinstance(v, (dict, list)):
                        temp_text, temp_sys, temp_bin = [], [], []
                        traverse_sub(v, temp_text, temp_sys, temp_bin)
                        system_parts.extend(temp_text)
                        system_parts.extend(temp_sys)
                else:
                    traverse(v, k)
        elif isinstance(val, list):
            for item in val:
                traverse(item, current_key)
        elif isinstance(val, str):
            if val.strip():
                text_parts.append(val)

    def traverse_sub(val, t_parts, s_parts, b_placeholders):
        if isinstance(val, dict):
            for k, v in val.items():
                traverse_sub(v, t_parts, s_parts, b_placeholders)
        elif isinstance(val, list):
            for item in val:
                traverse_sub(item, t_parts, s_parts, b_placeholders)
        elif isinstance(val, str):
            if val.strip():
                t_parts.append(val)

    traverse(data)
    
    # Clean up and join
    system_instruction = "\n".join(system_parts).strip()
    if not system_instruction:
        system_instruction = "You are PRISM Coder Agent, an enterprise software engineering agent."
    
    # Filter out duplicate text parts to keep output clean
    unique_text_parts = []
    for part in text_parts:
        part_stripped = part.strip()
        if part_stripped and part_stripped not in unique_text_parts:
            unique_text_parts.append(part_stripped)
    
    extracted_text = "\n\n".join(unique_text_parts)
    return system_instruction, extracted_text, binary_placeholders


def build_prompt_package(
    project_id: str,
    location: str,
    prompt_id: str,
    raw_data: dict,
    system_instruction: str,
    extracted_text: str,
    binary_placeholders: list[str]
) -> str:
    """Creates the local prompt package directory and files."""
    output_dir = os.path.join("saved_prompts", prompt_id)
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. raw.json
    with open(os.path.join(output_dir, "raw.json"), "w", encoding="utf-8") as f:
        json.dump(raw_data, f, indent=2)
        
    # 2. system.md
    with open(os.path.join(output_dir, "system.md"), "w", encoding="utf-8") as f:
        f.write(f"# System Instruction\n\n{system_instruction}\n")
        
    # 3. extracted_content.txt
    with open(os.path.join(output_dir, "extracted_content.txt"), "w", encoding="utf-8") as f:
        f.write(extracted_text)
        if binary_placeholders:
            f.write("\n\n### Attachments\n")
            for placeholder in binary_placeholders:
                f.write(f"- {placeholder}\n")
                
    # 4. chunk_001.md
    with open(os.path.join(output_dir, "chunk_001.md"), "w", encoding="utf-8") as f:
        f.write(extracted_text)
        if binary_placeholders:
            f.write("\n\n### Attachments\n")
            for placeholder in binary_placeholders:
                f.write(f"- {placeholder}\n")
                
    # 5. master.md & final_assembled.md
    master_content = f"""# Master: {prompt_id}

- **ID:** {prompt_id}
- **Project:** {project_id}
- **Chunks:** 1

## Chunks

- `chunk_001.md`

## Use

```
aider saved_prompts/{prompt_id}/master.md
aider saved_prompts/{prompt_id}/chunk_001.md
```

============================================================
# CONTENT

---
## Chunk 1

=== SYSTEM ===
{system_instruction}

=== USER ===
{extracted_text}
"""
    if binary_placeholders:
        master_content += "\n### Attachments\n" + "\n".join(f"- {p}" for p in binary_placeholders) + "\n"

    with open(os.path.join(output_dir, "master.md"), "w", encoding="utf-8") as f:
        f.write(master_content)
        
    with open(os.path.join(output_dir, "final_assembled.md"), "w", encoding="utf-8") as f:
        f.write(master_content)
        
    # 6. index.json
    index_data = {
        "prompt_id": prompt_id,
        "project_id": project_id,
        "location": location,
        "extracted_at": datetime.utcnow().isoformat() + "Z",
        "files": [
            "raw.json",
            "system.md",
            "extracted_content.txt",
            "master.md",
            "chunk_001.md",
            "final_assembled.md",
            "index.json"
        ]
    }
    with open(os.path.join(output_dir, "index.json"), "w", encoding="utf-8") as f:
        json.dump(index_data, f, indent=2)
        
    logging.info(f"Successfully built prompt package in: {output_dir}")
    return os.path.join(output_dir, "master.md")


def launch_aider(master_path: str):
    """Launches Aider using start_aider.sh."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    
    aider_script = os.path.join(project_root, "start_aider.sh")
    if not os.path.exists(aider_script):
        logging.error(f"start_aider.sh not found at {aider_script}. Skipping execution.")
        return
        
    aider_cmd = ["./start_aider.sh", "gemini-flash", master_path]
    logging.info(f"Launching Aider: {' '.join(aider_cmd)}")
    
    try:
        subprocess.run(aider_cmd, cwd=project_root, check=True)
    except subprocess.CalledProcessError as e:
        logging.error(f"Aider execution failed with exit code {e.returncode}")
        sys.exit(e.returncode)


def main():
    parser = argparse.ArgumentParser(description="PRISM Coder Agent - Saved Prompt Runner")
    parser.add_argument("--prompt-id", required=True, help="Vertex AI Dataset / Prompt ID")
    parser.add_argument("--project-id", default=get_gcp_project(), help="GCP Project ID")
    parser.add_argument("--location", default="us-central1", help="GCP Region/Location")
    parser.add_argument("--run-aider", action="store_true", help="Automatically run Aider after extraction")
    
    args = parser.parse_args()
    
    token = get_access_token()
    
    try:
        raw_data = fetch_dataset(args.project_id, args.location, args.prompt_id, token)
        system_instruction, extracted_text, binary_placeholders = extract_content(raw_data)
        
        master_path = build_prompt_package(
            project_id=args.project_id,
            location=args.location,
            prompt_id=args.prompt_id,
            raw_data=raw_data,
            system_instruction=system_instruction,
            extracted_text=extracted_text,
            binary_placeholders=binary_placeholders
        )
        
        if args.run_aider:
            launch_aider(master_path)
            
    except Exception as e:
        logging.error(f"Execution failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
```

File: scripts/run_prompt_id.sh
```bash
#!/usr/bin/env bash
# Reusable VM coding agent runner script.
# Accepts any Google Agent Platform / Vertex AI Studio saved prompt ID,
# extracts the prompt from GCP, prepares a local prompt package, and launches Aider.

set -euo pipefail

if [ -z "${1:-}" ]; then
  echo "Usage: $0 <prompt_id>"
  exit 1
fi

PROMPT_ID="$1"

# Resolve script directory to run python script correctly
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PARENT_DIR="$(dirname "$SCRIPT_DIR")"

echo "=== Starting Prompt ID Coder Agent ==="
echo "Prompt ID: $PROMPT_ID"

python3 "$PARENT_DIR/agents/prompt_id_coder_agent.py" --prompt-id "$PROMPT_ID" --run-aider
```

File: README.md
```markdown
# PRISM Coder Agent - Prompt-ID Runner

A reusable VM coding agent that accepts any Google Agent Platform / Vertex AI Studio saved prompt ID, extracts the prompt from GCP, prepares a local prompt package, and launches Aider automatically using `start_aider.sh`.

## Features

- **Deterministic Extraction**: Extracts prompt content, system instructions, and text/plain attachments without altering the source content.
- **Binary Stripping**: Safely strips binary/image/pdf payloads into descriptive placeholders.
- **Automatic Aider Execution**: Automatically triggers `./start_aider.sh` with the generated master prompt package.
- **Robust Authentication**: Automatically attempts multiple GCP authentication methods with clear fallback instructions.

## Directory Structure

When a prompt is fetched, the following package is generated:
```
saved_prompts/<prompt_id>/
├── raw.json               # Raw API response from Vertex AI
├── system.md              # Extracted system instructions
├── extracted_content.txt  # Extracted user prompt content
├── master.md              # Master prompt file for Aider
├── chunk_001.md           # Main content chunk
├── final_assembled.md     # Assembled prompt package
└── index.json             # Metadata index of the package
```

## Usage

### CLI Execution

Run the wrapper script directly with any prompt ID:

```bash
./scripts/run_prompt_id.sh <prompt_id>
```

Example:
```bash
./scripts/run_prompt_id.sh 2114685765899255808
```

### Python CLI Execution

For more configuration options, run the Python script directly:

```bash
python3 agents/prompt_id_coder_agent.py --prompt-id <prompt_id> --run-aider
```

Options:
- `--prompt-id`: (Required) Vertex AI Dataset / Prompt ID.
- `--project-id`: GCP Project ID (defaults to active gcloud project or `ctoteam`).
- `--location`: GCP Region/Location (defaults to `us-central1`).
- `--run-aider`: Automatically run Aider after extraction.
```