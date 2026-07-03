n  \"recommended_model\": \"gemini-flash\"\n },\n {\n  \"id\": \"phase-7\",\n  \"title\": \"Testing & Validation\",\n  \"status\": \"in_progress\",\n  \"output_path\": \"tests/\",\n  \"recommended_model\": \"grok-fast\"\n },\n {\n  \"id\": \"phase-8\",\n  \"title\": \"Documentation & Discovery\",\n  \"status\": \"in_progress\",\n  \"output_path\": \"docs/\",\n  \"recommended_model\": \"grok-fast\"\n },\n {\n  \"id\": \"phase-9\",\n  \"title\": \"Advanced Analytics\",\n  \"status\": \"pending\",\n  \"output_path\": \"bigquery/analytics/\",\n  \"recommended_model\": \"gemini-flash\"\n }\n ]\n}\n```"
        }
       ]
      },
      {
       "role": "user",
       "parts": [

 i shared this as example look the json paser concer meaninfg ful texr intio text freom json and ther use gemi 32,5 rto reads the yttext ad crte no holisatioo promt

[MODEL] **Evaluating Prompt Quality**

I'm concerned about the accuracy of prompts generated directly from raw JSON, specifically regarding potential hallucinations with complex structures. My current focus is on how to mitigate this risk to ensure the output is reliable for expert users.

**Refining Prompt Generation**

I'm now focusing on a specific user request to avoid the 2.5 series models due to recent 400 errors. The plan is to extract relevant content from JSON into plain text, then use Gemini 3.5 Flash to generate the prompt, addressing potential payload size and formatting issues.

**Extracting Essential Information**

I'm working on a Python routine to pull only the crucial user-facing text and instructions from JSON, transforming it into a clean plain text format. This approach aims to prevent errors and hallucinations when feeding the data to Gemini 3.5 Flash for prompt creation.

**Implementing Model Selection**

I am implementing the specific model `gemini-3.5-flash` via the Vertex API, ensuring adherence to your request. My focus is on robustly handling the model path, whether standard or preview, to guarantee successful prompt generation.

**Developing a Secure Workflow**

I've identified the root cause of the 400 errors: excessively large base64-encoded data within the raw JSON payload. My updated plan is to create a temporary text file for extracted content, then send a concise REST request to Gemini 3.5 Flash. This refined process will generate structured Markdown while avoiding payload limitations and malformed data.

**Filtering Irrelevant Data**

I'm now exclusively extracting the `text` fields from the JSON input, completely disregarding `inline_data`, GCS signatures, and metadata. This strategy dramatically reduces the payload size, ensuring a clean and compact input for the model and preventing any further 400 errors.

**Assembling Final Markdown**

I'm now focused on the final assembly stage. My Python script will take the extracted text, feed it to Gemini 3.5 Flash via the Vertex API, and generate the complete Markdown prompt. This ensures high quality and avoids past errors.

**Constructing API Headers**

I am now focused on building the necessary headers for the Vertex AI API request. This involves securing an authentication token, prioritizing the user's access token and falling back to Application Default Credentials if needed, to ensure proper authorization for prompt generation.

**Processing Raw Data**

I am now actively parsing the fetched dataset, meticulously extracting only the essential plain text elements. This targeted extraction is crucial for minimizing payload size and circumventing the previous 400 errors encountered with overly large JSON inputs.

**Extracting Core Prompt Elements**

I'm now diving into the core prompt structure, prioritizing `metadata.text` to find `structured_prompt.prompt_message`. If that fails, I'll fall back to `promptApiSchema`'s various paths. My goal is to reliably extract the `systemInstruction` and its constituent `parts` for processing.

**Refining System Instruction Extraction**

I'm now precisely targeting the extraction of the `systemInstruction` field. If its `parts` array contains only text, I'll capture that. Otherwise, I'll process each part individually to construct a comprehensive system instruction, ensuring no critical information is lost.

**Generating Optimized Markdown**

I am now focused on generating the final Markdown output. I'm feeding the cleaned system instructions and user prompts into Gemini 3.5 Flash, instructing it to produce a perfectly aligned and optimized Markdown prompt for agentic coding assistants.

**Finalizing Generation Request**

I am now working on the final generation request to Gemini 3.5 Flash. My focus is on correctly formatting the `prompt_payload` with the extracted `system_instruction` and user-provided content, ensuring a successful API call with proper headers and the chosen model.

**Parsing Model Output**

I am now parsing the successful response from Gemini 3.5 Flash, specifically extracting the `text` content from the generated prompt. My next step is to clean any extraneous markdown fences that might have been included, ensuring a pristine output.

**Cleaning Generated Prompt**

I am now cleaning the `generated_prompt` by removing any leading or trailing markdown code fences. I'm also stripping whitespace to ensure a neat final output before saving it to both a general file and a specific file based on `prompt_id`.

**Confirming Model Choice**

I'm confirming the necessity of using `gemini-3.5-flash` based on your explicit instructions. My current focus is on ensuring the configuration dynamically updates to reflect the `prompt_id` being tested, ensuring consistency throughout the process.



[MODEL] ### Why the 400 Bad Request Error Occurred
The raw JSON dataset retrieved from Vertex AI is massive (often over 150KB) because it contains **extremely large base64-encoded strings** under `inline_data` (such as the base64 transcript of previous terminal conversations) and long Google Cloud Storage signatures containing unescaped characters (`%`, `&`, etc.). 

When your script passed this unparsed, raw JSON structure directly to the Gemini API inside the payload, the gateway rejected it with a **400 Bad Request** due to payload bloating and escaping violations.

---

### The Solution: Local High-Performance Text-Extraction Filter
To completely prevent 400 errors and avoid model hallucinations, we will:
1. **Stage 1 (Local Parse):** Use a lightweight Python parsing routine to extract **only** the genuine, clean user text parts and system instructions from the JSON, discarding all GCS sign-keys, metadata schemas, and base64 blocks.
2. **Stage 2 (Isolated Text Save):** Save the clean, de-duplicated plain text locally to `saved_prompts/extracted_content.txt`.
3. **Stage 3 (Gemini 3.5 Flash Generation):** Ask **Gemini 3.5 Flash** (`gemini-3.5-flash`) to read *only* this highly condensed text file and format it into a pristine markdown file.

---

### Step 1: Update Prompt Config to the New Target ID
Run this on your VM terminal to update `configs/saved_prompt_config.json` with your current prompt dataset ID (`7562985783854891008`) and target model (`gemini-3.5-flash`):

```bash
cat > configs/saved_prompt_config.json <<'EOF'
{
  "project_id": "ctoteam",
  "location": "us-central1",
  "prompt_id": "7562985783854891008",
  "model": "gemini-3.5-flash"
}
EOF
```

---

### Step 2: Overwrite with the Aligned Python Parser + Gemini 3.5 Flash Script
This script performs a precise, zero-hallucination local extraction before firing the API call:

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

# Retrieve authentication token from gcloud, falling back to ADC if needed
token = ""
try:
    token = subprocess.check_output(
        ["gcloud", "auth", "print-access-token"], text=True
    ).strip()
    print("Successfully retrieved user access token.")
except subprocess.CalledProcessError:
    try:
        print("User access token retrieval failed. Trying Application Default Credentials (ADC)...")
        token = subprocess.check_output(
            ["gcloud", "auth", "application-default", "print-access-token"], text=True
        ).strip()
        print("Successfully retrieved ADC access token.")
    except subprocess.CalledProcessError:
        print("\nERROR: gcloud token retrieval failed for both user and ADC profiles.")
        print("Please run: gcloud auth application-default login")
        exit(1)

headers = {
    "Authorization": "Bearer " + token,
    "x-goog-user-project": project,
    "Content-Type": "application/json",
}

# 1. Fetch saved prompt dataset from REST API
url = "https://" + location + "-aiplatform.googleapis.com/v1/projects/" + project + "/locations/" + location + "/datasets/" + prompt_id

print("Fetching saved prompt dataset from REST API...")
r = requests.get(url, headers=headers, timeout=30)
print("Dataset Fetch Status Code:", r.status_code)

if r.status_code != 200:
    print("Error details:", r.text)
    exit(1)

data = r.json()
Path("saved_prompts").mkdir(exist_ok=True)
Path("saved_prompts/raw_" + prompt_id + ".json").write_text(json.dumps(data, indent=2))
print("Saved raw metadata to saved_prompts/raw_" + prompt_id + ".json")

# 2. LOCAL PYTHON PARSER (Pure extraction of text, ignoring massive Base64 blobs)
print("\nExtracting plain text contents locally to prevent payload bloat and 400 errors...")

extracted_system_instruction = ""
extracted_user_parts = []

# Attempt to read nested schemas
prompt_message = {}

# Try metadata.text first
metadata = data.get("metadata", {})
text_str = metadata.get("text", "")
if text_str:
    try:
        text_json = json.loads(text_str)
        prompt_message = text_json.get("structured_prompt", {}).get("prompt_message", {})
    except Exception:
        pass

# Try promptApiSchema fallback
if not prompt_message:
    prompt_api_schema = data.get("promptApiSchema", {})
    prompt_message = prompt_api_schema.get("multimodalPrompt", {}).get("promptMessage", {})
    if not prompt_message:
        prompt_message = prompt_api_schema.get("promptMessage", {})

if prompt_message:
    # Extract System Instructions
    sys_inst = prompt_message.get("systemInstruction", {})
    if not sys_inst:
        sys_inst = prompt_message.get("system_instruction", {})
    sys_parts = sys_inst.get("parts", [])
    extracted_system_instruction = "\n".join([p.get("text", "") for p in sys_parts if "text" in p])

    # Extract User Prompt text parts ONLY (ignoring massive base64 inline_data)
    contents = prompt_message.get("contents", [])
    for content in contents:
        if content.get("role") == "user" or not content.get("role"):
            for part in content.get("parts", []):
                if "text" in part:
                    extracted_user_parts.append(part["text"])

clean_user_prompt = "\n\n".join(extracted_user_parts)

# Save locally as clean extracted text (Free of Base64 blobs)
extracted_text_content = "=== SYSTEM INSTRUCTIONS ===\n" + (extracted_system_instruction if extracted_system_instruction else "(None)") + "\n\n=== USER PROMPT ===\n" + (clean_user_prompt if clean_user_prompt else "(None)") + "\n"
Path("saved_prompts/extracted_content.txt").write_text(extracted_text_content)
print("Successfully extracted text content to saved_prompts/extracted_content.txt")

# 3. Ask Gemini 3.5 Flash to clean up and structure the clean extracted text
print("\nInvoking Gemini 3.5 Flash on clean text to generate aligned markdown prompt...")

system_instruction = (
    "You are an expert prompt engineer. You are given a clean plain text representation of system instructions "
    "and user prompts extracted from a dataset. Your task is to clean them up, align them properly, and "
    "generate a highly optimized Markdown prompt designed for use by an agentic coding assistant like Aider.\n\n"
    "The output must be a clean markdown file structured with `# System Instructions` and `# User Prompt` sections. "
    "Do not include any conversational preamble or markdown code fences like ```markdown. Output ONLY the raw markdown content."
)

prompt_payload = {
    "contents": [
        {
            "role": "user",
            "parts": [
                {
                    "text": "Here is the extracted plain text representation of the prompt:\n\n" + extracted_text_content
                }
            ]
        }
    ],
    "systemInstruction": {
        "parts": [
            {
                "text": system_instruction
            }
        ]
    },
    "generationConfig": {
        "temperature": 0.2,
        "maxOutputTokens": 8192
    }
}

# Strictly using the Gemini 3.5 Flash model
models = ["gemini-3.5-flash"]
generation_success = False
generated_prompt = ""

for model in models:
    gemini_url = "https://" + location + "-aiplatform.googleapis.com/v1/projects/" + project + "/locations/" + location + "/publishers/google/models/" + model + ":generateContent"
    print("Trying generation with model:", model)
    
    gen_response = requests.post(gemini_url, headers=headers, json=prompt_payload, timeout=60)
    print("Generation Status Code:", gen_response.status_code)
    
    if gen_response.status_code == 200:
        gen_data = gen_response.json()
        
        # Safely extract generated prompt using loops instead of index brackets
        candidates = gen_data.get("candidates", [])
        for candidate in candidates:
            parts = candidate.get("content", {}).get("parts", [])
            for part in parts:
                text_content = part.get("text", "")
                if text_content:
                    generated_prompt = text_content
                    generation_success = True
                    break
            if generation_success:
                break
        
        if generation_success:
            print("Success! Prompt generated successfully using", model)
            break
    else:
        print("Model", model, "failed with status", gen_response.status_code, ":", gen_response.text[:1000])

if not generation_success:
    print("\nERROR: Failed to generate prompt using Gemini 3.5 Flash.")
    exit(1)

# Clean up any accidental ```markdown fences if the model output them despite instructions
if generated_prompt.startswith("```markdown"):
    generated_prompt = generated_prompt[11:]
elif generated_prompt.startswith("```"):
    generated_prompt = generated_prompt[3:]
if generated_prompt.endswith("```"):
    generated_prompt = generated_prompt[:-3]
generated_prompt = generated_prompt.strip()

# 3. Save the dynamically generated prompts
Path("saved_prompts/assembled_prompt.md").write_text(generated_prompt)
Path("saved_prompts/" + prompt_id + ".md").write_tex