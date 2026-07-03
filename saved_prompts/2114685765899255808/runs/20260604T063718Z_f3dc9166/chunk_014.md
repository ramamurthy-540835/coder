VCXv1QXswx0mgIOvd2NeL9z7wdGP89r6QAgJzPSev34/l+6GaSlIp6gYFYaLG+tOdhxd+DFJ+63EuLNT53a/Zn8sIpvB+Bz0W7a+I3OyF6P6+PvHPVs4PIGRwDGN6x1aRmH1yuJQErH2pEtDD849Jfq7l3XPhHfK9cTOlWl/BvMrnI1ZDeQ8bkKUZetrbX3uEPyGRHdAvbhSkJJG1cYSrm322oWK88wwOHCx3bHMZii+CHwrLsI9xxxH4r7fShk6M/F0lMbFdKLhLktvXD92WG8os3qcWKb4oPPp1httMz523R9B/UyIPdBp3t1Ld6Vkpb4DObDNG8SLFcq2DIjpzfdtyvwGm9z+G+gHcQsmwYKz7FCUGsTv/T2CPsdJqBp/NAmC7h+DzTGzzKaddtJtweU/kDk0JYVgUrhGZh3Vn4VVAlCssnRJb50KhRLlEIba0kBuxPAUlXG6xaCM0x4E5o6UaIp6gli5J4S4tfygjHoAuOf4pQJ11X/g/fREDU5gcC3PKbqgyQoEFod+AF/GGydJoBkIREr070VLURQ/nd35ynrU1d0CK8M6mHZbL1lBsopeR/f9hIzWlfzsKf/sKHzuAZYcWx52wAUo1v68eOXxNdxlR04osT2MmmAPFoeNoHjHJG1AZrouS1WGqbkxD6hSLNJiP2NgBcA+S+/w8kW4Uq2Ty782EJu9gI/CiDtvxOOlog4A/IMLNZ4dPHhIz0nX+WTQCflbjU4Wj5Lc1S7WWzWL2F4cpWOQPUWnO18lPjjZjlSdeTSdPvfb/qKGTCLdAp02UWNQhxLGIf2/tmtUPxwtQubzDKgSEJljBkfEP1sLW6zm6fjonWbs8eQHwIgZIUidvB99ZS2wTWsQoLWc8o7uzLk7TkCwC/TNx/jz0KOZKSrQUR2j47A=="
                }
              ]
            }
          ],
          "tools": [
            {
              "googleSearch": {}
            }
          ],
          "safetySettings": [
            {
              "category": "HARM_CATEGORY_HATE_SPEECH",
              "threshold": "OFF"
            },
            {
              "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
              "threshold": "OFF"
            },
            {
              "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
              "threshold": "OFF"
            },
            {
              "category": "HARM_CATEGORY_HARASSMENT",
              "threshold": "OFF"
            }
          ],
          "generationConfig": {
            "temperature": 1,
            "topP": 0.95,
            "maxOutputTokens": 65535,
            "thinkingConfig": {
              "thinkingLevel": "MEDIUM"
            }
          }
        }
      },
      "executions": [
        {
          "arguments": {
            "token": {
              "partList": {}
            },
            "location": {
              "partList": {}
            },
            "project": {
              "partList": {}
            },
            "prompt_id": {
              "partList": {}
            },
            "url": {
              "partList": {}
            },
            "out": {
              "partList": {}
            }
          }
        }
      ],
      "apiSchemaVersion": "1.0.0"
    }
  },
  "metadataArtifact": "projects/1035117862188/locations/us-central1/metadataStores/default/artifacts/d8195c44-d0de-41b1-a8c0-0940f4d79c84",
  "modelReference": "projects/ctoteam/locations/global/publishers/google/models/gemini-3.5-flash"
}

[USER] 

(None)
(venv) appadmin@chn-mit-genai-dq1:~/projects/Ram_Projects/DiracDelta/gcloud_run$ SO WE MAY NEED TO IMPVE ALSO https://console.cloud.google.com/agent-platform/studio/saved-prompts/locations/us-central1/2114685765899255808?model=gemini-3.5-flash&project=ctoteam CAN WE DOUBLE CHECXK WE HAVE TO PARSE IT PROPERLY



[MODEL] **Analyzing API Response**

I'm now examining the raw JSON returned from the REST API. My focus is on understanding the structure of this data, specifically the 'name' field and its initial components.

**Discovering Nested Structure**

I've identified that the prompt structure isn't a top-level key. Instead, it's deeply embedded within the `metadata.text` field as a JSON string. This requires an additional parsing step.

**Confirming Serialization Method**

I've confirmed that the prompt structure is indeed serialized as a JSON-encoded string within the `metadata.text` field. I'm now investigating the structure under `promptApiSchema`, noting the `multimodalPrompt` key with its camelCase convention.

**Locating System Instructions**

I've confirmed the presence of `systemInstructionGcsUri` within `promptApiSchema`. Now, I'm investigating the parsed `metadata.text` JSON for a `system_instruction` or `systemInstruction` key nested within `structured_prompt.prompt_message`.

**Parsing Nested Data**

I'm now actively parsing the `metadata.text` field, recognizing it contains a JSON string. My current effort is directed at examining the keys within this nested structure, specifically searching for system instruction-related fields.

**Refining Parsing Logic**

I'm now focused on developing a resilient parsing strategy, anticipating variations. This involves carefully inspecting the nested structure within `metadata.text`, specifically looking for `system_instruction` and `contents` keys to extract system and user prompts.

**Extracting User Prompts**

I'm now extracting user prompt segments from the nested `contents` array, joining them with newlines. My current task involves completing this extraction and preparing to integrate the system instruction.

**Integrating System Instructions**

I'm currently working on combining the extracted system instruction with the user prompt, ensuring proper formatting. If the initial parsing of `metadata.text` fails, I'm ready to leverage the `promptApiSchema` as a fallback.

**Confirming Final Structure**

I've confirmed the logic is robust, handling both standard and multimodal prompts by parsing `metadata.text` or falling back to `promptApiSchema`. I'm now reviewing the extracted user prompt text, which unexpectedly contains our full debug chat history.

**Identifying Root Cause**

I've realized the core schema is split: a JSON-serialized string in `data["metadata"]["text"]` (camelCase) and `data["promptApiSchema"]` (snake_case). This explains the parsing complexities encountered.

**Resolving Schema Ambiguity**

I've identified two distinct schema paths for prompt data: one within `data["metadata"]["text"]` (camelCase) and another in `data["promptApiSchema"]` (snake_case). My current focus is on implementing a unified parsing strategy to handle both gracefully.

**Unifying Schema Handling**

I've pinpointed two schema structures: one is a camelCase JSON string within `data["metadata"]["text"]`, the other is snake_case in `data["promptApiSchema"]`. My current objective is to develop a unified parsing approach to manage both these data formats effectively.

**Synthesizing Prompt Data**

I'm now combining the system instructions with the user prompt parts I've extracted. My current objective is to ensure this integrated prompt is correctly formatted before further processing.

**Combining Prompt Segments**

I'm now merging the system instructions with the user prompt components I've gathered. My focus is on ensuring the final, unified prompt is accurately structured for the next stages of processing.

**Assembling Final Prompt**

I'm now merging extracted system instructions with user prompt segments. My current goal is to ensure the fully integrated prompt is accurately structured for subsequent processing, preparing the markdown file.



[MODEL] Excellent find! Seeing the raw JSON output is incredibly helpful. 

### Why the previous parser didn't catch the prompt text
As your JSON dump reveals, the Agent Platform / Vertex AI API structures prompt data in two parallel ways:
1. **Pathway 1 (Serialized JSON String):** The `metadata` object contains a field named `"text"`, which is a **serialized JSON string** containing the full `structured_prompt` structure.
2. **Pathway 2 (Nested Dictionary):** The API exposes a camelCase schema under `promptApiSchema` -> `multimodalPrompt` -> `promptMessage`.

Because the core data inside `"metadata"` was wrapped in an extra layer of string-serialization (i.e. as a raw string), the previous parser skipped right over it.

---

### Step 1: Overwrite with the Robust Double-Parser
This updated script dynamically tries **both pathways** (de-serializing the `metadata.text` JSON string, and falling back to the nested `promptApiSchema` structure) to guarantee flawless extraction of your prompt details.

Run this command in your VM terminal:
```bash
cat > agents/read_saved_prompt.py <<'EOF'
import json
import subprocess
import requests
from pathlib import Path

# Load configuration
try:
    cfg = json.load(open("configs/saved_prompt_config.json"))
except FileNotFoundError:
    print("Config file configs/saved_prompt_config.json not found.")
    exit(1)

project = cfg["project_id"]
location = cfg["location"]
prompt_id = cfg["prompt_id"]

# Retrieve authentication token from gcloud
try:
    token = subprocess.check_output(
        ["gcloud", "auth", "print-access-token"], text=True
    ).strip()
except subprocess.CalledProcessError:
    print("\nERROR: gcloud token retrieval failed.")
    print("Please run: gcloud auth login --no-launch-browser")
    exit(1)

headers = {
    "Authorization": "Bearer " + token,
    "x-goog-user-project": project,
    "Content-Type": "application/json",
}

# The Vertex AI / Agent Platform dataset endpoint
url = "https://" + location + "-aiplatform.googleapis.com/v1/projects/" + project + "/locations/" + location + "/datasets/" + prompt_id

print("Fetching saved prompt dataset from REST API...")
r = requests.get(url, headers=headers, timeout=30)
print("Status Code:", r.status_code)

if r.status_code != 200:
    print("Error details:", r.text)
    exit(1)

data = r.json()
Path("saved_prompts").mkdir(exist_ok=True)
Path("saved_prompts/raw_" + prompt_id + ".json").write_text(json.dumps(data, indent=2))
print("Saved raw metadata to saved_prompts/raw_" + prompt_id + ".json")

# Parsing variables
system_instruction_text = ""
user_prompt_text = ""

# Pathway 1: Parse the JSON-serialized "text" string inside "metadata"
metadata = data.get("metadata", {})
text_str = metadata.get("text", "")

if text_str:
    try:
        text_json = json.loads(text_str)
        structured_prompt = text_json.get("structured_prompt", {})
        prompt_message = structured_prompt.get("prompt_message", {})
        
        # Extract System Instructions (supports both snake_case and camelCase inside serialized text)
        sys_inst = prompt_message.get("system_instruction", {})
        if not sys_inst:
            sys_inst = prompt_message.get("systemInstruction", {})
        sys_parts = sys_inst.get("parts", [])
        system_instruction_text = "\n".join([p.get("text", "") for p in sys_parts if "text" in p])
        
        # Extract User contents
        contents = prompt_message.get("contents", [])
        user_prompt_parts = []
        for content in contents:
            if content.get("role") == "user" or not content.get("role"):
                for p in content.get("parts", []):
                    if "text" in p:
                        user_prompt_parts.append(p["text"])
        user_prompt_text = "\n".join(user_prompt_parts)
        print("Successfully extracted prompt content from metadata.text JSON string.")
    except Exception as e:
        print("Warning: Failed to parse metadata.text as JSON string:", e)

# Pathway 2 (Fallback): Parse promptApiSchema
if not user_prompt_text and not system_instruction_text:
    prompt_api_schema = data.get("promptApiSchema", {})
    
    # Handle standard nested pathways
    prompt_message = prompt_api_schema.get("multimodalPrompt", {}).get("promptMessage", {})
    if not prompt_message:
        prompt_message = prompt_api_schema.get("promptMessage", {})
        
    if prompt_message:
        sys_parts = prompt_message.get("systemInstruction", {}).get("parts", [])
        system_instruction_text = "\n".join([p.get("text", "") for p in sys_parts if "text" in p])
        
        contents = prompt_message.get("contents", [])
        user_prompt_parts = []
        for content in contents:
            if content.get("role") == "user" or not content.get("role"):
                for p in content.get("parts", []):
                    if "text" in p:
                        user_prompt_parts.append(p["text"])
        user_prompt_text = "\n".join(user_prompt_parts)
        print("Successfully extracted prompt content via promptApiSchema fallback.")

# Assemble Markdown file
assembled_md_content = """# System Instructions
""" + (system_instruction_text if system_instruction_text else "(None)") + """

# User Prompt
""" + (user_prompt_text if user_prompt_text else "(None)") + "\n"

Path("saved_prompts/assembled_prompt.md").write_text(assembled_md_content)
print("Successfully generated: saved_prompts/assembled_prompt.md")
print("\n--- PROMPT PREVIEW ---")
print(assembled_md_content[:1500])
print("----------------------")
EOF
```

---

### Step 2: Run the Script
Execute the updated python agent:
```bash
python3 agents/read_saved_prompt.py
```

This will cleanly de-serialize the prompt, generate `saved_prompts/assembled_prompt.md` containing your instructions and code, and display a neat terminal preview!

[USER]  cat assembled_prompt.md
# System Instructions
(None)

# User Prompt
77 updates can be applied immediately.
To see these additional updates run: apt list --upgradable

15 additional security updates can be applied with ESM Apps.
Learn more about enabling ESM Apps service at https://ubuntu.com/esm


*** System restart required ***
Last login: Thu May 28 06:30:23 2026 from 10.100.10.49
appadmin@chn-mit-genai-dq1:~$ cd projects/Ram_Projects/DiracDelta/
appadmin@chn-mit-genai-dq1:~/projects/Ram_Projects/DiracDelta$ ls
deepcoder ekf gcloud_run image_gen logs ossa PRISM
appadmin@chn-mit-genai-dq1:~/projects/Ram_Projects/DiracDelta$ cd gcloud_run
appadmin@chn-mit-genai-dq1:~/projects/Ram_Projects/DiracDelta/gcloud_run$ ls
agents bootstrap.sh configs logs   prompts    reports  scripts   tem
apps cloudbuild core  models.json prompt-tracker.json saved_prompts start_aider.sh
appadmin@chn-mit-genai-dq1:~/projects/Ram_Projects/DiracDelta/gcloud_run$ cd /home/appadmin/project
mkdir -p agents configs saved_prompts logs
appadmin@chn-mit-genai-dq1:~/projects/Ram_Projects/DiracDelta/gcloud_run$ cat > configs/saved_prompt_config.json <<'EOF'
{
 "project_id": "ctoteam",
 "location": "us-central1",
 "prompt_id": "3364082818773680128",
 "model": "gemini-3.5-flash"
}
EOF
appadmin@chn-mit-genai-dq1:~/projects/Ram_Projects/DiracDelta/gcloud_run$ cat > agents/read_saved_prompt.py <<'EOF'
import json, subprocess, requests
from pathlib import Path

cfg = json.load(open("configs/saved_prompt_config.json"))
project = cfg["project_id"]
location = cfg["location"]
prompt_id = cfg["prompt_id"]

token = subprocess.check_output(
 ["gcloud", "auth", "print-access-token"], text=True
).strip()

headers = {
 "Authorization": f"Bearer {token}",
 "x-goog-user-project": project,
 "Content-Type": "application/json",
}

candidate_urls = [
 f"https://{location}-aiplatform.googleapis.com/v1/projects/{project}/locations/{location}/prompts/{prompt_id}",
 f"https://{location}-aiplatform.googleapis.com/v1beta1/projects/{project}/locations/{location}/prompts/{prompt_id}",
 f"https://{location}-aiplatform.googleapis.com/v1/projects/{project}/locations/{location}/savedPrompts/{prompt_id}",
 f"https://{location}-aiplatform.googleapis.com/v1beta1/projects/{project}/locations/{location}/EOF print("\nFAILED: No API endpoint worked. Need SDK/API name verification.")
app