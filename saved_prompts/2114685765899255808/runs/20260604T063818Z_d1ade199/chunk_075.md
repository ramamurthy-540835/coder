rate an optimized prompt...")

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
                    "text": "Here is the raw JSON representation of the saved prompt dataset:\n\n" + json.dumps(data, indent=2)
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

# Prioritize low-latency 2.5-flash-lite first, fallback to 2.5-flash if needed
models = ["gemini-2.5-flash-lite", "gemini-2.5-flash"]
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
        print("Model", model, "failed with status", gen_response.status_code)

if not generation_success:
    print("\nERROR: Failed to generate prompt with all tried models.")
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
Path("saved_prompts/" + prompt_id + ".md").write_text(generated_prompt)

print("Successfully generated: saved_prompts/assembled_prompt.md")
print("Successfully generated: saved_prompts/" + prompt_id + ".md")
print("\n--- DYNAMIC PROMPT PREVIEW ---")
print(generated_prompt[:1500])
print("------------------------------")
EOF
```

---

### Step 3: Run the Script
Now run the optimized, ultra-fast script inside your active virtual environment:
```bash
python3 agents/read_saved_prompt.py
```

[USER] i am worried iobn the actul qulity of the promprt gebnrewatd from jdson holisibnatioon d_saved_prompt.py^C
(venv) appadmin@chn-mit-genai-dq1:~/projects/Ram_Projects/DiracDelta/gcloud_run$ python3 agents/read_saved_prompt.py
Successfully retrieved user access token.
Fetching saved prompt dataset from REST API...
Dataset Fetch Status Code: 200
Saved raw metadata to saved_prompts/raw_7562985783854891008.json
Invoking low-latency Gemini 2.5 Flash Lite to dynamically parse the JSON dataset and generate an optimized prompt...
Trying generation with model: gemini-2.5-flash-lite
Generation Status Code: 400
Model gemini-2.5-flash-lite failed with status 400
Trying generation with model: gemini-2.5-flash
Generation Status Code: 400
Model gemini-2.5-flash failed with status 400
ERROR: Failed to generate prompt with all tried models.
(venv) appadmin@chn-mit-genai-dq1:~/projects/Ram_Projects/DiracDelta/gcloud_run$

7d1f237b-2470-4088-8730-549afbfab02d-raw_7562985783854891008.txt
so i think we may bned to use python to extact a meanminffulk and save it as text then ask gemin3,5flash to bno dont use 2.5 series
ii has to ibe"
        }
       ]
      },
      {
       "role": "model",
       "parts": [
        {
         "text": "**Analyzing Model Capabilities**\n\nI am currently evaluating the distinctions between the \"gpt-5.3-codex\" and \"Gemini 3.5\" models. My focus is on identifying their respective strengths and weaknesses across various coding tasks, aiming to understand their performance characteristics in detail.\n\n**Highlighting Codex Advantages**\n\nI'm now focusing on articulating exactly where Codex excels over Gemini 3.5, particularly concerning nuanced code-specific challenges. The aim is to provide a direct, compelling answer for a professional audience, showcasing Codex's unique problem-solving capabilities in areas where generalist models falter, such as understanding complex dependency issues during test collection.\n\n",
         "thought": true
        },
        {
         "text": "Here is a technical, high-impact draft you can use for your LinkedIn post:\n\n***\n\n### Why Codex Succeeds on Complex Codebases Where Traditional LLMs Fail \ud83d\ude80\n\nWhen automating test sanitization and CI/CD pipelines in enterprise environments, there is a massive gap between **generating code** and **remediating production-grade integration errors**. \n\nIn our latest optimization run on the **Enterprise Knowledge Fabric (EKF)**, generalist models struggled with persistent runtime blocks, but **Codex** resolved them systematically. Here is the technical breakdown of why Codex succeeds where others hit a wall:\n\n#### 1. Solving \"Collection-Time\" vs. \"Runtime\" Dependency Hell\n* **The Problem:** Generalist LLMs frequently write code that relies on heavy cloud dependencies (like Google Cloud Data Catalog). If those dependencies are missing in the developer's local test environment, `pytest` fails at **import collection time** before a single test can even execute.\n* **The Codex Fix:** Codex automatically recognizes environment gaps and writes defensive collection-time guards:\n ```python\n try:\n   from google.cloud import datacatalog_v1\n except ImportError:\n   datacatalog_v1 = None\n ```\n It then safely mocks downstream instantiations (`datacatalog_v1.DataCatalogClient() if datacatalog_v1 else None`), ensuring the test suite remains portable and fully collectable.\n\n#### 2. Mastering Complex Mock Assertions & Side Effects\n* **The Problem:** Standard AI models often try to fix failing mock assertions (like `mock_log.assert_called_once()`) by blindly changing call counts or gutting logging logic. They fail to realize that secondary processes (such as a missing optional config file throwing a `WARNING`) contaminate global mock call counts.\n* **The Codex Fix:** Codex targets the exact semantic assertion rather than the total count, ensuring robust and deterministic validation:\n ```python\n audit_calls = [\n   c for c in mock_log.call_args_list \n   if len(c.args) > 1 and c.args[0] == 'NOTICE' and 'AUDIT_LOG' in str(c.args[1])\n ]\n assert len(audit_calls) == 1\n ```\n\n#### 3. True Environmental Symbiosis\n* **The Problem:** Traditional models operate in a vacuum. They don't understand that running `pytest` directly might resolve to a global system binary instead of the active virtual environment\u2019s interpreter (`.venv-vllm`).\n* **The Codex Fix:** Codex writes context-aware scripts using `python -m pytest` and dynamic runtime fallback hooks, guaranteeing correct interpreter alignment.\n\n### The Takeaway \ud83d\udca1\nTo build self-healing software pipelines, you need an AI agent that doesn't just read prompt requirements, but systematically analyzes runtime execution trees, imports, and mock scopes. That is the distinct advantage of Codex.\n\n#SoftwareEngineering #AICoding #DevOps #CICD #Python #CloudArchitecture #Codex"
        }
       ]
      },
      {
       "role": "user",
       "parts": [
        {
         "text": "lest move to the next stage 6"
        }
       ]
      },
      {
       "role": "model",
       "parts": [
        {
         "text": "**Advancing to Next Stage**\n\nI've noticed we've successfully stabilized phases 5 and 6, as indicated by the recent commit. This suggests we're ready to proceed to stage 6 as requested.\n\n",
         "thought": true
        },
        {
         "text": "**Analyzing Stage Progression**\n\nI'm reviewing the user's request to advance to \"stage 6,\" cross-referencing it with the `prompt_requirements.json` document. It appears Phase 6, designated as \"CI/CD & Deployment,\" was previously marked as pending but is now showing as completed. I'm clarifying this discrepancy to ensure we proceed correctly.\n\n",
         "thought": true
        },
        {
         "text": "**Analyzing Next Steps**\n\nI've confirmed Phase 6 is finalized and am now shifting focus to Phase 7, \"Testing & Validation,\" to determine our immediate next action.\n\n",
         "thought": true
        },
        {
         "text": "**Executing Next Phase**\n\nI'm currently focused on initiating the next stage of our process. My thoughts are centered on utilizing the `scripts/run_prompt.py` script to advance to Phase 7, building on the previous execution of `scripts/start_aider.sh` with `gemini-flash` for Phase 6.\n\n",
         "thought": true
        },
        {
         "text": "To move to **Phase 7 (Testing & Validation)** using the newly configured dynamic router, execute either of the following commands:\n\n### Method 1: Using the Bash Launcher\n```bash\n./scripts/start_aider.sh gemini-flash phase-7\n```\n\n### Method 2: Running the Python Executor Directly\n```bash\nsource .venv-vllm/bin/activate\npython3 scripts/run_prompt.py phase-7\n```",
         "thoughtSignature": "AY89a191ptiLthaX7uFqzgie5XdWWsRlHN95f1hvXZjzyWLNiU9zmjrcrKYLHjg1i40ZoLrrJDsdo3u1cYnZwSGjSQ+kTAVAFWftc+eQokdxtktw48j2e6U7U7hpQUcYYlEn7vF/IQtm9wJoSKDFoluFTt4UjEt0H78VH9tKHWa6kLfGJLQx70phSa0FIvsaCbRDcFMd6WHB+moIxj5GKx27zX6fh/T1+NJltF9dime4tbyHLhQR4Spb7mDCLrWijmSNXnggLS4NW3+MI6HbKjIei+I2e9yPtVqRIGTDPC8LhQ9XxZ91Rbdq3XkKzG5B2Db2QsImX70YI5O3Yoch8Lafstn3WJTcT9jNdBCJ7qbwdxLlFnJCYIy95/VmrmNAucS1YkHFl6E9Dm8NI8zFLqXabrSqzJSJk/VW4IirbdLMEpNSP34dwbuTpwZAAdRhe1Wbaw1PFgJon5n8BSeG8u5cZXTQDI4kqzYwkuS4Gqs3mO8iceqjSKauY58WYc591bMVkso2LfVqmuuuKRQhOoGJ/rdkdF7hyH5lEiJRH0KjNs8x4BFTXelwPTl8qnzwY9Oi4A9xsdeIK4sx+NE+hlji6Tfnx05n0XhfSaolXyhJdAA/z6D/iddQMYFxKd1KFwH5Xkycb9pSFhUhrBdk0ccfGLQrwWe9Uk3ltkn38ui4ejlmJ+VQlgXNAnjp3k0ifGqQJ7ntJks+rzQlC9GEoQob/2G/04sJdCskD+fzng/y6b6ltnWUa0nP3F0AEjZ10qPPqWmY+E9S+wf5Pf4wKUa1HwUEi4PYA5SAqRD7Lr2kU9BFp+D4sGsNGxtbs/z9tvxaz/Z11sodIdivPI+HCgeXSOa8DNi/WoxeeWrPJxP3K/IRbSgS2Vi1wISMbWNkIrjqYcQIxzePHI2brjXIEblPvmfZFPqc4uyJN65shan3Bq04SgKa8bCxWJnO110bMwHgqsthkNro07I9VClpBwRKc6cmhGL8BDUxTeLAF3eGg745n1Ww2XFhD56SFAarQZJAup6KQ46LSgMmGqUwPztzgXv/K3Y5La/7p/Qwu7H7qeGvgz7kRTWCr4o9oGnAyX3v1BZuFJ0v/vrsnKSicLWl7RnByO3MStNi98hIA3diM21SjKMBVMplnl1TEqRCA4bPvgbf7B+druSvnvhh2M8BsWS/6w+RbV51VCH6OVdmQIxXHQgl4j3/fHHHqkglh1xg3hFw6B551IP0s9wShL58woRYS1MD2pok4BmZ+ejV+AeJzrWUgOjnkoOVH93C6ZgwWo4RWslhQ3VY6cu8ealijaA7YhsXBXV8750ouO6X3KX+21ixPQ=="
        }
       ]
      },
      {
       "role": "user",
       "parts": [
        {
         "text": "no stage 6 is bening"
        }
       ]
      },
      {
       "role": "model",
       "parts": [
        {
         "text": "### prompt_requirements.json\n```json\n{\n \"project\": \"Enterprise Knowledge Fabric (EKF)\",\n \"last_updated\": \"2026-05-21\",\n \"phases\": [\n {\n  \"id\": \"phase-1\",\n  \"title\": \"Data Ingestion Pipelines\",\n  \"status\": \"completed\",\n  \"output_path\": \"src/dataflow/\",\n  \"recommended_model\": \"grok-fast\"\n },\n {\n  \"id\": \"phase-2\",\n  \"title\": \"BigQuery Analytics Measures & Views\",\n  \"status\": \"completed\",\n  \"output_path\": \"bigquery/views/\",\n  \"recommended_model\": \"gemini-flash\"\n },\n {\n  \"id\": \"phase-3\",\n  \"title\": \"Knowledge Catalog & Metadata Management\",\n  \"status\": \"completed\",\n  \"output_path\": \"scripts/metadata/\",\n  \"recommended_model\": \"gemini-pro\"\n },\n {\n  \"id\": \"phase-4\",\n  \"title\": \"Data Quality & Monitoring\",\n  \"status\": \"completed\",\n  \"output_path\": \"scripts/quality/\",\n  \"recommended_model\": \"gemini-flash\"\n },\n {\n  \"id\": \"phase-5\",\n  \"title\": \"Security & Governance\",\n  \"status\": \"completed\",\n  \"output_path\": \"terraform/security/\",\n  \"recommended_model\": \"gemini-pro\"\n },\n {\n  \"id\": \"phase-6\",\n  \"title\": \"CI/CD & Deployment\",\n  \"status\": \"completed\",\n  \"output_path\": \"terraform/ci-cd/\",\n  \"recommended_model\": \"gemini-flash\"\n },\n {\n  \"id\": \"phase-7\",\n  \"title\": \"Testing & Validation\",\n  \"status\": \"in_progress\",\n  \"output_path\": \"tests/\",\n  \"recommended_model\": \"grok-fast\"\n },\n {\n  \"id\": \"phase-8\",\n  \"title\": \"Documentation & Discovery\",\n  \"status\": \"in_progress\",\n  \"output_path\": \"docs/\",\n  \"recommended_model\": \"grok-fast\"\n },\n {\n  \"id\": \"phase-9\",\n  \"title\": \"Advanced Analytics\",\n  \"status\": \"pending\",\n  \"output_path\": \"bigquery/analytics/\",\n  \"recommended_model\": \"gemini-flash\"\n }\n ]\n}\n```"
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

I'm working on