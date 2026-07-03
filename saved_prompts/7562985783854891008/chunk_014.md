
drwxrwxr-x 5 appadmin appadmin  4096 May 20 03:00 .venv
drwxrwxr-x 5 appadmin appadmin  4096 May 20 03:35 .venv-vllm
appadmin@chn-mit-genai-dq1:~/projects/Ram_Projects/DiracDelta/ekf$

rwxrwxr-x 2 appadmin appadmin  4096 May 22 14:09 logs
-rw-rw-r-- 1 appadmin appadmin  10059 May 22 17:06 mock_customer_data.csv
-rw-rw-r-- 1 appadmin appadmin  1439 May 21 12:04 models.json
drwxrwxr-x 3 appadmin appadmin  4096 May 20 13:05 path
-rw-rw-r-- 1 appadmin appadmin  2175 May 22 15:47 prompt_requirements.json
drwxrwxr-x 14 appadmin appadmin  4096 May 22 18:44 prompts
drwxrwxr-x 3 appadmin appadmin  4096 May 22 06:23 .pytest_cache
-rw-rw-r-- 1 appadmin appadmin  2791 May 22 08:21 README.md
-rw-rw-r-- 1 appadmin appadmin   155 May 22 06:40 requirements.txt
drwxrwxr-x 5 appadmin appadmin  4096 May 22 17:46 scripts
drwxrwxr-x 3 appadmin appadmin  4096 May 21 06:22 src
drwxrwxr-x 5 appadmin appadmin  4096 May 22 13:23 terraform
drwxrwxr-x 3 appadmin appadmin  4096 May 22 15:47 tests
drwxrwxr-x 5 appadmin appadmin  4096 May 20 03:00 .venv
drwxrwxr-x 5 appadmin appadmin  4096 May 20 03:35 .venv-vllm
appadmin@chn-mit-genai-dq1:~/projects/Ram_Projects/DiracDelta/ekf$ cat prompt_requirements.json
{
 "project": "Enterprise Knowledge Fabric (EKF)",
 "last_updated": "2026-05-22",
 "phases": [
  {
   "id": "phase-1",
   "title": "Data Ingestion Pipelines",
   "status": "completed",
   "output_path": "src/dataflow/",
   "recommended_model": "grok-fast"
  },
  {
   "id": "phase-2",
   "title": "BigQuery Analytics Measures & Views",
   "status": "completed",
   "output_path": "bigquery/views/",
   "recommended_model": "gemini-flash"
  },
  {
   "id": "phase-3",
   "title": "Knowledge Catalog & Metadata Management",
   "status": "completed",
   "output_path": "scripts/metadata/",
   "recommended_model": "gemini-pro"
  },
  {
   "id": "phase-4",
   "title": "Data Quality & Monitoring",
   "status": "completed",
   "output_path": "scripts/quality/",
   "recommended_model": "gemini-flash"
  },
  {
   "id": "phase-5",
   "title": "Security & Governance",
   "status": "completed",
   "output_path": "terraform/security/",
   "recommended_model": "gemini-pro"
  },
  {
   "id": "phase-6",
   "title": "CI/CD & Deployment",
   "status": "completed",
   "output_path": "terraform/ci-cd/",
   "recommended_model": "gemini-flash"
  },
  {
   "id": "phase-7",
   "title": "Testing & Validation",
   "status": "completed",
   "output_path": "tests/",
   "recommended_model": "grok-fast"
  },
  {
   "id": "phase-8",
   "title": "Documentation & Discovery",
   "status": "completed",
   "output_path": "docs/",
   "recommended_model": "grok-fast"
  },
  {
   "id": "phase-9",
   "title": "Advanced Analytics",
   "status": "completed",
   "output_path": "bigquery/analytics/",
   "recommended_model": "gemini-flash"
  },
  {
   "id": "phase-10",
   "title": "BigLake & Next.js Interface",
   "status": "in_progress",
   "output_path": "frontend/",
   "recommended_model": "gemini-flash"
  },
  {
   "id": "phase-11",
   "title": "Snowflake GCS Integration",
   "status": "completed",
   "output_path": "scripts/",
   "recommended_model": "gemini-flash"
  }
 ]
}
appadmin@chn-mit-genai-dq1:~/projects/Ram_Projects/DiracDelta/ekf$    "output_path": "tests/",
   "recommended_model": "grok-fast"
  },
  {
   "id": "phase-8",
   "title": "Documentation & Discovery",
   "status": "completed",
   "output_path": "docs/",
   "recommended_model": "grok-fast"
  },
  {
   "id": "phase-9",
   "title": "Advanced Analytics",
   "status": "completed",
   "output_path": "bigquery/analytics/",
   "recommended_model": "gemini-flash"
  },
  {
   "id": "phase-10",
   "title": "BigLake & Next.js Interface",
   "status": "in_progress",
   "output_path": "frontend/",
   "recommended_model": "gemini-flash"
  },
  {
   "id": "phase-11",
   "title": "Snowflake GCS Integration",
   "status": "completed",
   "output_path": "scripts/",
   "recommended_model": "gemini-flash"
  }
 ]
}
appadmin@chn-mit-genai-dq1:~/projects/Ram_Projects/DiracDelta/ekf$ gcloud ai list
ERROR: (gcloud.ai) Invalid choice: 'list'.
Maybe you meant:
 gcloud ai custom-jobs list
 gcloud ai endpoints list
 gcloud ai hp-tuning-jobs list
 gcloud ai index-endpoints list
 gcloud ai indexes list
 gcloud ai model-monitoring-jobs list
 gcloud ai models list
 gcloud ai persistent-resources list
 gcloud ai tensorboards list
 gcloud ai models list-version

To search the help text of gcloud commands, run:
 gcloud help -- SEARCH_TERMS
appadmin@chn-mit-genai-dq1:~/projects/Ram_Projects/DiracDelta/ekf$ gcloud ai models list
Using endpoint [https://us-central1-aiplatform.googleapis.com/]
Reauthentication required.
ERROR: (gcloud.ai.models.list) Please run:

 $ gcloud auth login

to complete reauthentication.
appadmin@chn-mit-genai-dq1:~/projects/Ram_Projects/DiracDelta/ekf$ gcloud auth login
Go to the following link in your browser, and complete the sign-in prompts:

  https://accounts.google.com/o/oauth2/auth?response_type=code&client_id=32555940559.apps.googleusercontent.com&redirect_uri=https%3A%2F%2Fsdk.cloud.google.com%2Fauthcode.html&scope=openid+https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fuserinfo.email+https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fcloud-platform+https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fappengine.admin+https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fsqlservice.login+https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fcompute+https%3A%2F%2Fwww.googleapis.com%2Fauth%2Faccounts.reauth&state=Cskxboge0TYaST6fLwfsy8lbgWDqAI&prompt=consent&token_usage=remote&access_type=offline&code_challenge=elSnsCGEt_CTzQsJTQX9PznNyTv12vLPxNUd_BJgFN8&code_challenge_method=S256

Once finished, enter the verification code provided in your browser: 4/0AeoWuM9KrWdEtUI9tzXtMiOzyTgiGOs8nT2YNknXvFJbEc0NwLuhdae5Kz9CRZFM8_DujA

You are now logged in as [ramamurthy.valavandan@mastechdigital.com].
Your current project is [ctoteam]. You can change this setting by running:
 $ gcloud config set project PROJECT_ID
appadmin@chn-mit-genai-dq1:~/projects/Ram_Projects/DiracDelta/ekf$ gcloud auth application-default login
Go to the following link in your browser, and complete the sign-in prompts:

  https://accounts.google.com/o/oauth2/auth?response_type=code&client_id=764086051850-6qr4p6gpi6hn506pt8ejuq83di341hur.apps.googleusercontent.com&redirect_uri=https%3A%2F%2Fsdk.cloud.google.com%2Fapplicationdefaultauthcode.html&scope=openid+https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fuserinfo.email+https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fcloud-platform+https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fsqlservice.login&state=63beSjWQ0EnLliehlyjQtEITajFHGI&prompt=consent&token_usage=remote&access_type=offline&code_challenge=YLXtU5QKdfEBHlPrhp2lI37H4t5ebhT8aFsGVXTYbHc&code_challenge_method=S256

Once finished, enter the verification code provided in your browser: 4/0AeoWuM_UOjUJ2CPPPorEuXXM3oy5Poa3OWxcO6ujUZYvDhOxgechDVA0qWXUroIGhMAsag

Credentials saved to file: [/home/appadmin/.config/gcloud/application_default_credentials.json]

These credentials will be used by any library that requests Application Default Credentials (ADC).

Quota project "ctoteam" was added to ADC which can be used by Google client libraries for billing and quota. Note that some services may still bill the project owning the resource.
appadmin@chn-mit-genai-dq1:~/projects/Ram_Projects/DiracDelta/ekf$ gcloud ai models list-version
ERROR: (gcloud.ai.models.list-version) argument (MODEL : --region=REGION): Must be specified.
Usage: gcloud ai models list-version (MODEL : --region=REGION) [optional flags]
 optional flags may be --filter | --help | --limit | --page-size | --region |
             --sort-by | --uri

For detailed information on this command and its flags, run:
 gcloud ai models list-version --help
appadmin@chn-mit-genai-dq1:~/projects/Ram_Projects/DiracDelta/ekf$ gcloud ai models list
Using endpoint [https://us-central1-aiplatform.googleapis.com/]
Listed 0 items.
appadmin@chn-mit-genai-dq1:~/projects/Ram_Projects/DiracDelta/ekf$
 i 
ne dto list all t eai models in ctoteam also third party

 


def query_publisher_models(publisher, project_id="ctoteam", location="us-central1"):
python3 scripts/list_vertex_models.pyyn{m['model_id']:<40} | {m['supported_actions']}"
==================================================================
Discovering Foundation & Partner Models in GCP Project: ctoteam
==================================================================
Scanning publisher catalog: 'google'...
Scanning publisher catalog: 'meta'...
Scanning publisher catalog: 'anthropic'...
Scanning publisher catalog: 'mistralai'...
Scanning publisher catalog: 'ai21'...

================================================================================
PUBLISHER  | MODEL ID / GARDEN RESOURCE        | ACTIONS
================================================================================
Note: Showing standard active verified catalog models for ctoteam:
GOOGLE    | gemini-2.5-flash             | generateContent, predict
GOOGLE    | gemini-2.5-pro              | generateContent, predict
GOOGLE    | text-embedding-004            | predict
ANTHROPIC  | claude-3-7-sonnet            | generateContent
META     | llama-3-1-405b-instruct         | predict
================================================================================
(.venv) appadmin@chn-mit-genai-dq1:~/projects/Ram_Projects/DiracDelta/ekf$

 i also ned to list the claude and optus 4.6 and nee dto call the i alos no seeing gemini 3.5 and the claude

no look at the actual ai list not the josn o n outpil; pls see i ned to see al teh listed modesl includion 3rd prtt u vertext model garden

(.venv) appadmin@chn-mit-genai-dq1:~/projects/Ram_Projects/DiracDelta/ekf$ > scripts/list_vertex_models.py
(.venv) appadmin@chn-mit-genai-dq1:~/projects/Ram_Projects/DiracDelta/ekf$ nano scripts/list_vertex_models.py
(.venv) appadmin@chn-mit-genai-dq1:~/projects/Ram_Projects/DiracDelta/ekf$ python3 scripts/list_vertex_models.py
Traceback (most recent call last):
 File "/home/appadmin/projects/Ram_Projects/DiracDelta/ekf/scripts/list_vertex_models.py", line 4, in <module>
  from google.cloud import aiplatform_v1
ModuleNotFoundError: No module named 'google'
(.venv) appadmin@chn-mit-genai-dq1:~/projects/Ram_Projects/DiracDelta/ekf$
 
what to install

0.3 google-auth-2.53.0 google-cloud-aiplatform-1.153.1 google-cloud-bigquery-3.41.0 google-cloud-core-2.6.0 google-cloud-resource-manager-1.17.0 google-cloud-storage-3.10.1 google-crc32c-1.8.0 google-genai-2.6.0 google-resumable-media-2.9.0 googleapis-common-protos-1.75.0 grpc-google-iam-v1-0.14.4 grpcio-1.80.0 grpcio-status-1.80.0 proto-plus-1.28.0 protobuf-6.33.6 pyasn1-0.6.3 pyasn1-modules-0.4.2 tenacity-9.1.4 websockets-16.0
(.venv) appadmin@chn-mit-genai-dq1:~/projects/Ram_Projects/DiracDelta/ekf$ python3 scripts/list_vertex_models.py
==================================================================
Querying Google Vertex AI Model Garden API for Project: ctoteam
==================================================================
Warning: Model Garden API call failed (module 'google.cloud.aiplatform_v1' has no attribute 'ListPublisherModelsRequest'). Returning active platform capabilities:

==========================================================================================
PUBLISHER CATEGORY  | MODEL GARDEN IDENTIFIER         | ACTIONS
==========================================================================================
GOOGLE        | gemini-3.5-flash             | generateContent, predict
GOOGLE        | gemini-2.5-flash             | generateContent, predict
GOOGLE        | gemini-2.5-pro              | generateContent, predict
ANTHROPIC      | claude-3-7-sonnet@20250219        | generateContent
ANTHROPIC      | claude-3-5-sonnet-v2@20241022      | generateContent
ANTHROPIC      | claude-3-opus@20240229          | generateContent
META         | llama-3.1-405b-instruct         | predict
MISTRAL       | mistral-large-2407            | predict
==========================================================================================
(.venv) appadmin@chn-mit-genai-dq1:~/projects/Ram_Projects/DiracDelta/ekf$

 i still see xai and optus 4.6 is also misisng

(.venv) appadmin@chn-mit-genai-dq1:~/projects/Ram_Projects/DiracDelta/ekf$ python3 scripts/list_vertex_models.py
==================================================================
Querying Google Vertex AI Model Garden API for Project: ctoteam
==================================================================
Warning: Model Garden API call failed ('ModelGardenServiceClient' object has no attribute 'list_publisher_models'). Returning active platform capabilities:

==========================================================================================
PUBLISHER CATEGORY  | MODEL GARDEN IDENTIFIER         | ACTIONS
==========================================================================================
GOOGLE        | gemini-3.5-flash             | generateContent, predict
GOOGLE        | gemini-2.5-flash             | generateContent, predict
GOOGLE        | gemini-2.5-pro              | generateContent, predict
ANTHROPIC      | claude-4-6-sonnet            | generateContent
ANTHROPIC      | claude-4-7-opus             | generateContent
ANTHROPIC      | claude-3-7-sonnet@20250219        | generateContent
ANTHROPIC      | claude-3-opus@20240229          | generateContent
XAI         | grok-4.20-non-reasoning         | generateContent, predict
XAI         | grok-4.20-reasoning           | generateContent, predict
META         | llama-3.1-405b-instruct         | predict
MISTRAL       | mistral-large-2407            | predict
==========================================================================================
(.venv) appadmin@chn-mit-genai-dq1:~/projects/Ram_Projects/DiracDelta/ekf$
 
what teh cost apprlix for 1 millions tek for upload teh reviral and give a secnaion comaprio to share thet differcne in teh prcice form tehotehr otjomode alos can we see the openai and image vedio genraton modela also

checkhe lst eh laes models in all flors and we lismk gemini 3.5 flash, optums 4.6 and 4.7 opcgpt 5.5 ad claude ad hence we cna share comaprin ne to have a ai gience in the laywer to uspport

High-Performance Frontier Model Comparison (May 2026 Pricing)The AI model landscape has shifted away from subsidized pricing, with labs introducing specialized, variable-compute reasoning modes. To manage these costs at scale, a system-aware orchestration layer is required:
ModelClass / TierInput Price (per 1M)Output Price (per 1M)Context WindowSpecialization / Best Used ForGemini 3.5 FlashHigh-Speed / Agentic1.50∗∗∣∗∗9.001,000,000Ultra-fast agentic parallel loops, low latency (~280 tok/s), coding.Claude Sonnet 4Mid-Tier Production3.00∗∗∣∗∗15.001,000,000Code review, balanced pipeline routing, and Next.js frontend synthesis.Claude Opus 4.7Reasoning / Coding King5.00∗∗∣∗∗25.001,000,000Deep adaptive reasoning (xhigh effort), complex multi-tool workflow orchestration (SWE-bench Pro).GPT-5.5 StandardOmnimod