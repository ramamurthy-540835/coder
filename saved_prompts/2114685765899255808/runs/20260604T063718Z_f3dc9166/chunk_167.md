ecoded_text[:15000] + "\n\n[... Truncated for token optimization and response speed ...]"
        return decoded_text
    except Exception as e:
        return "[Failed to decode text: " + str(e) + "]"

# 2. LOCAL PYTHON PARSER (Recursive cleaner: strips images, decodes and truncates plain text logs)
print("\nExtracting plain text contents locally to prevent payload bloat and 400 errors...")

def clean_node(node):
    if isinstance(node, dict):
        # Check if this dictionary itself is an inline data block
        has_mime = "mime_type" in node or "mimeType" in node or "mime" in node
        if "data" in node and has_mime:
            mime = node.get("mime_type") or node.get("mimeType") or node.get("mime") or ""
            raw_data = node["data"]
            if mime == "text/plain" and raw_data:
                node["data"] = decode_base64_text(raw_data)
            else:
                size = len(raw_data) if raw_data else 0
                node["data"] = f"<stripped_base64_payload_of_mime_{mime}_size_{size}_bytes>"
        
        # Recurse through all other keys
        for key, value in list(node.items()):
            if key == "text" and isinstance(value, str):
                try:
                    nested_json = json.loads(value)
                    node[key] = json.dumps(clean_node(nested_json))
                except Exception:
                    pass
            else:
                node[key] = clean_node(value)
    elif isinstance(node, list):
        return [clean_node(item) for item in node]
    return node

cleaned_data = clean_node(data)
Path("saved_prompts/raw_clean_" + prompt_id + ".json").write_text(json.dumps(cleaned_data, indent=2))
print("Saved cleaned metadata to saved_prompts/raw_clean_" + prompt_id + ".json")

# 3. Use Gemini 2.5 Flash to dynamically generate the optimized prompt
print("\nInvoking Gemini on clean text to generate aligned markdown prompt...")

system_instruction = (
    "You are an expert prompt engineer. You are given a raw JSON representation of a saved prompt dataset "
    "from the Google Gemini Enterprise Agent Platform (Vertex AI). Your task is to analyze this raw JSON, "
    "find the system instructions and user chat messages/prompts, clean them up, align them properly, and "
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
                    "text": "Here is the cleaned JSON representation of the saved prompt dataset:\n\n" + json.dumps(cleaned_data, indent=2)
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

# Try stable, active Gemini 2.5 Flash
models_config_list = [
    {"name": "gemini-2.5-flash", "loc": "us-central1"},
    {"name": "gemini-2.5-flash-lite", "loc": "us-central1"}
]

generation_success = False
generated_prompt = ""

for item in models_config_list:
    model_name = item["name"]
    model_loc = item["loc"]
    gemini_url = "https://" + location + "-aiplatform.googleapis.com/v1/projects/" + project + "/locations/" + model_loc + "/publishers/google/models/" + model_name + ":generateContent"
    print("Trying generation with model:", model_name, "at location:", model_loc)
    
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
            print("Success! Prompt generated successfully using", model_name)
            break
    else:
        print("Model", model_name, "failed with status", gen_response.status_code)

if not generation_success:
    print("\nERROR: Failed to generate prompt.")
    exit(1)

# Clean up any accidental ```markdown fences if the model output them despite instructions
if generated_prompt.startswith("```markdown"):
    generated_prompt = generated_prompt[11:]
elif generated_prompt.startswith("```"):
    generated_prompt = generated_prompt[3:]
if generated_prompt.endswith("```"):
    generated_prompt = generated_prompt[:-3]
generated_prompt = generated_prompt.strip()

# 4. Save the dynamically generated prompts
Path("saved_prompts/assembled_prompt.md").write_text(generated_prompt)
Path("saved_prompts/" + prompt_id + ".md").write_text(generated_prompt)

print("Successfully generated: saved_prompts/assembled_prompt.md")
print("Successfully generated: saved_prompts/" + prompt_id + ".md")
print("\n--- DYNAMIC PROMPT PREVIEW ---")
print(generated_prompt[:1500])
print("------------------------------")
EOF
```

---

### Step 2: Run the Script
Now run the script inside your active virtual environment:
```bash
python3 agents/read_saved_prompt.py
```

[USER] except subprocess.CalledProcessError:
EOFnt("------------------------------")")pts/" + prompt_id + ".md")mpt)espite instructions=60) "/lo
(venv) appadmin@chn-mit-genai-dq1:~/projects/Ram_Projects/DiracDelta/gcloud_run$ python3 agents/read_saved_prompt.py
Successfully retrieved user access token.
Fetching saved prompt dataset from REST API...
Dataset Fetch Status Code: 200
Saved raw metadata to saved_prompts/raw_7562985783854891008.json

Extracting plain text contents locally to prevent payload bloat and 400 errors...
Saved cleaned metadata to saved_prompts/raw_clean_7562985783854891008.json

Invoking Gemini on clean text to generate aligned markdown prompt...
Trying generation with model: gemini-2.5-flash at location: us-central1
Generation Status Code: 400
Model gemini-2.5-flash failed with status 400
Trying generation with model: gemini-2.5-flash-lite at location: us-central1
Generation Status Code: 400
Model gemini-2.5-flash-lite failed with status 400

ERROR: Failed to generate prompt.
(venv) appadmin@chn-mit-genai-dq1:~/projects/Ram_Projects/DiracDelta/gcloud_run$

suee gemin 3.5 flash

[MODEL] **Investigating Generation Failures**

I'm encountering persistent `400` errors when attempting to generate the aligned markdown prompt using the `gemini-2.5-flash` model. This is hindering my progress in producing the desired output.

**Debugging Prompt Structures**

I'm now digging into the specifics of the 400 error by examining the JSON payload sent to `gemini-2.5-flash-lite`. I'm investigating potential structural issues with the `contents`, `systemInstruction`, and `generationConfig` fields, as the Vertex AI REST API documentation for `v1` may offer clarification.



[MODEL] **Exploring System Instruction Format**

I'm currently examining the `systemInstruction` field within the payload. My focus is on its structure, specifically how the `parts` array and its nested `text` objects are organized and populated. This detailed inspection is key to understanding how to best utilize and parse this information.

**Debugging API Response Structure**

I'm investigating why `gemini-2.5-flash` returned a 400 error. My current hypothesis centers on the `systemInstruction` format, specifically the `parts` array and its `text` objects. I need to confirm if my Python script's JSON structure matches the expected Vertex AI v1 REST API format. I'll print the exact error message to pinpoint the discrepancy.

**Reducing Token Count**

My recent attempts to generate aligned markdown prompts have been hitting a 400 error due to excessive token counts. Even after cleaning metadata and reducing file size, the input tokens still vastly exceed the limit. I'm now investigating how the `raw_7562985783854891008.json` and `extracted_content.txt` files contribute to this bloat.

**Investigating File Size**

I'm perplexed because `raw_clean_7562985783854891008.json` hasn't shrunk at all, remaining a massive 21.2 MB. I'm re-examining my `clean_node` function, specifically how it handles `text/plain` data. I'm also wondering if keys within the `metadata` field, if they contain JSON but aren't explicitly named "text", are being overlooked.

**Discovering Schema Structure**

I've discovered that `promptApiSchema` is a dictionary within `metadata`. The substantial size indicates it holds base64 encoded data. I'm now investigating why my `clean_node` function, which correctly handles "text" fields, might have missed this nested structure.

**Refining Nested JSON Handling**

I'm digging into the nuances of my `clean_node` function. It successfully handles nested JSON within `text` fields, but it seems to miss structures like `promptApiSchema`. My current focus is on how it recurses into lists and dictionaries, specifically ensuring it can correctly process dictionary values that aren't explicitly "text" and might contain base64 encoded data.

**Identifying Data Structure Flaws**

I'm re-evaluating my `clean_node` function's recursion. It appears it's not correctly traversing dictionaries where the relevant data isn't directly under a "text" key, specifically when encountering `"inlineData"`. This means nested base64 content is being missed.

**Correcting Recursion Logic**

I'm identifying a flaw in my recursive dictionary traversal. It correctly processes `"text"` fields but fails to handle dictionaries where the data, like `"inlineData"`, isn't directly under a `"text"` key, specifically when dealing with camelCase keys such as `"mimeType"`. This is preventing the extraction of base64 content.

**Refining Recursion**

I'm revisiting my recursive function's handling of dictionaries. It correctly targets `"text"` fields but is missing nested data like `"inlineData"` when it's not directly under a `"text"` key. My current focus is on ensuring it properly traverses these structures and correctly updates the `"data"` field before iterating through the dictionary items.

**Fixing List Handling**

My recursive function was creating a new list when encountering list nodes instead of modifying them in place, thus failing to strip unnecessary data. I'm now adjusting the logic to ensure lists are processed correctly and the overall structure is modified as intended.

**Fixing Dictionary Traversal**

I'm addressing an issue where my recursive function wasn't correctly handling dictionaries when encountering data not directly under a "text" key. Specifically, it seems to be missing `"inlineData"` and is not properly processing the `"data"` field before iterating through dictionary items. I'm refining the logic to ensure these nested structures are correctly identified and processed.

**Identifying Text Source**

I've realized the large text content in `extracted_content.txt` isn't coming from `inline_data` attachments as I'd suspected. Instead, it's directly present within the `part["text"]` fields of the prompt structure. This clarifies where the bulk of the input data originates.

**Finding Text Source**

I've confirmed that the extensive text content originates directly from `part["text"]` fields, not `inline_data`. My `clean_node` function wasn't targeting these plain text strings, explaining why they weren't being processed for size reduction. The large file size was due to unstripped JPEG base64 data within metadata fields.

**Revising Data Stripping Logic**

I'm rethinking my data stripping process. My `has_mime` check is correctly identifying nodes, and the subsequent modification of `"data"` should occur. However, the iteration loop is immediately processing the original base64 string before the modified data is fully integrated, leading to JPEGs not being stripped as expected.

**Correcting List Return Value**

I've identified a critical flaw: when my `clean_node` function processes a list, it creates and returns a *new* list rather than modifying the existing one in place. This means the returned, cleaned list isn't properly replacing the original data structure, leaving the large files intact. I am adjusting this list handling.

**Adjusting List Modification**

I'm refining how my `clean_node` function handles lists. It was incorrectly creating and returning a new list instead of modifying the existing one in place, causing the original, oversized data structure to remain unchanged. I'm now ensuring that list elements are properly processed and the overall structure is updated correctly.

**Revising Recursive Logic**

I'm re-examining my recursive function's handling of dictionary keys. While it correctly modifies `"data"` and `"mimeType"` when `"inlineData"` is present, I'm questioning if the subsequent iteration over `inlineData`'s keys might be overwriting the intended stripping of base64 data by re-assigning the original, unstripped value.

**Revising JSON Loading Logic**

I'm re-evaluating the `metadata.text` field and the conditional JSON loading. While my code correctly identifies `"text"` keys with string values, I'm questioning if the cleaning and re-serialization process is actually modifying the data, given the persistent large file size. This suggests the cleaning might not be effectively reducing the byte count.

**Confirming File Identity**

I've discovered that `raw_clean` and `raw` are byte-for-byte identical. This baffling result, despite a log message claiming successful cleaning and saving to under 50KB, leads me to suspect the script may have been truncated or an older version ran, effectively overwriting the cleaned file with the original data.

**Correcting List Mutation**

I've realized my `clean_node` function returns a *new* list when processing lists, rather than modifying the original in place. This means the cleaning operation doesn't actually alter the data structure that gets saved. I'm adjusting the list handling to ensure in-place modification.

**Revising Exception Handling**

I've identified that the `try-except` block around JSON processing is too broad. If `json.loads` or `clean_node` fails, the original `value` is silently passed over, preventing any cleaning or updating. I'm adjusting this to ensure errors don't bypass necessary data transformations.

**Fixing Silent Errors