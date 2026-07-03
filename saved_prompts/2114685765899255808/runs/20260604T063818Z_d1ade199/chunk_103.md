 product
steward-inventory@gpc.comprojects/ekf/locations/us/keyRings/ekf-ring/cryptoKeys/inventory-keycategoryProduct Category
High-level classification of the product
steward-inventory@gpc.comprojects/ekf/locations/us/keyRings/ekf-ring/cryptoKeys/inventory-keyorder_idOrder Identifier
Unique identifier for a customer order
steward-orders@gpc.comprojects/ekf/locations/us/keyRings/ekf-ring/cryptoKeys/orders-keyorder_dateOrder Date
The date and time when the order was placed
steward-orders@gpc.comprojects/ekf/locations/us/keyRings/ekf-ring/cryptoKeys/orders-keysensitivity_levelGovernance Sensitivity Tag
The classification level of data sensitivity for governance
steward-governance@gpc.comprojects/ekf/locations/us/keyRings/ekf-ring/cryptoKeys/governance-key
BigQuery Graph / Spanner Graph LineageLive queryable graph structure showing entity relationships and data lineage flows.
Graph EntitiesCustomer [customers]
Spanner Graph Node
Order [transactions]
Spanner Graph Node
Product [products]
Spanner Graph Node
Supplier
Spanner Graph Node
Region
Spanner Graph Node
Traversed RelationshipsCustomer [customers]PLACED

Order [transactions]
Order [transactions]CONTAINS

Product [products]
Product [products]SOURCED_FROM

Supplier
SupplierLOCATED_IN

Region
Ingestion Pipeline
Healthy
Operational
All requested backend endpoints responded successfully.
Active Metadata Catalogs
1 datasets
ekf
9 tables
BigLake Feeds
ekf_biglake_feed
PARQUET · gs://ekf-biglake-feed/pos_transactions/
projects/ctoteam/locations/us-central1/connections/ekf-biglake-conn
active
EKF Staged Data
live
gs://ekf-biglake-feed/
customer_export.csv
9.8 KB
gs://ekf-biglake-feed/unload/customers/year=2026/month=05/customer_export.csv
22/05/26, 10:37 pm
CSV
1 file staged10-Phase Execution TimelinePhase 1: Ingestion Foundation
completed
Model: grok-fast
Phase 2: BigQuery Integration
completed
Model: gemini-flash
Phase 3: Metadata Modeling
completed
Model: gemini-3.5-flash
Phase 4: Data Quality Rules
completed
Model: gemini-flash
Phase 5: Security Governance Design
completed
Model: gemini-3.5-flash
Phase 6: CI/CD Deployment
completed
Model: gemini-flash
Phase 7: Testing Automation
completed
Model: grok-fast
Phase 8: Documentation & Runbooks
completed
Model: grok-fast
Phase 9: Advanced Analytics
completed
Model: gemini-flash
Phase 10: BigLake Federated Storage + Next.js Frontend
completed
Model: gemini-flashInteractive Action ConsoleValidate any live asset from the catalog against governance requirements.
Quick Templates
ekf · customers
ekf · transactions
ekf · customer_lifetime_value
Dataset
ekf
Table
Select table…
customers
products
transactions
ekf_biglake_feed
customer_lifetime_value
customer_order_frequency
daily_aov
daily_total_sales
top_products
Sensitivity Level
internal
public
confidential
restricted
pii
Validate Asset
dataset=ekf
table=customers
sensitivity=internal
Compliance Result: ✓ Compliant
Tables in ekf(9)
customers
products
transactions
ekf_biglake_feed
customer_lifetime_value
customer_order_frequency
daily_aov
daily_total_sales
top_productsEKF AI Agent Chat ConsoleMetadata Catalog Agent v3.0
Natural language queries across the full EKF catalog, security posture, and lineage graph.
user@ekf:~$ Show lineage flows
▶ SecurityGovernanceAgent · intent: lineage_query
Traversed the live BigQuery Graph / Spanner Graph structure showing entity relationships: Customer [customers] -> PLACED -> Order [transactions] -> CONTAINS -> Product [products] -> SOURCED_FROM -> Supplier -> LOCATED_IN -> Region.
Traversed Graph Lineage Relationships:
Customer [customers]PLACED
Order [transactions]
Order [transactions]CONTAINS
Product [products]
Product [products]SOURCED_FROM
Supplier
SupplierLOCATED_IN
Region
confidence: 95%
tokens: 120
latency: 350ms
model: gemini-3.5-flash
Query Agent
Find confidential datasets
Show security policies
Show lineage flows
Show analytics insights



backend       execution.md     models.json        src
bigquery      fastapi.log      path           terraform
cloudbuild.yaml   frontend       prompt_requirements.json tests
config       knowledge       prompts
docs        launch_model.sh    README.md
(.venv-vllm) appadmin@chn-mit-genai-dq1:~/projects/Ram_Projects/DiracDelta/ekf$ ls -l knowledge/
total 24096
-rw-rw-r-- 1 appadmin appadmin   9699 Apr 17 09:25 knowledge_base_generator.py
-rw-rw-r-- 1 appadmin appadmin  11771 Apr 13 07:35 knowledge_base.json
drwxrwxr-x 7 appadmin appadmin   4096 Mar 23 05:21 mhh-adept-solution-value-based-care-feature-vbc_agents
-rw-rw-r-- 1 appadmin appadmin 24636798 Apr 17 03:27 mhh-adept-solution-value-based-care-feature-vbc_agents.zip
drwxrwxr-x 2 appadmin appadmin   4096 Apr 20 09:54 Rules
drwxrwxr-x 2 appadmin appadmin   4096 Apr 17 05:49 schemas
(.venv-vllm) appadmin@chn-mit-genai-dq1:~/projects/Ram_Projects/DiracDelta/ekf$
  
i ahe added a few expaoce n knowfor teh use of adept only promt is d for te chaiag efirs teh u aspr te adeapt by tmastech

n no vbc we have copes for the use no vnc i really now nd to vbc hre th i seh retail so we ne dto crefullt ghiv eeh prmt i nly ne dto pick and g eteh skin for the




───────────────────────────────────────────────────────────────────────────────────────────────────

diff>









^C again to exit
───────────────────────────────────────────────────────────────────────────────────────────────────

diff>









^C KeyboardInterrupt
^C
 
 ne dto pus to git

lets do a research  theentperprise knwoleege graph and identay all te featur that are promosied and see what we have done

list teh scope or ekf as per gcp and we are ned to have main doamins (inductr verift i te to add and what to be retail is polit or wew ecan addmroe thina  we ahave lets mhave teh minc or teh all the gbos of teh mastech digital lisk eh from teh retaik ti hhetalcare, manufactureming , banking and weha twe hed to haev teh featr teh secure way aid i love to thave e more agentsic wauy like micorsoft azureadf  azu datafactir ui expeicne in teh e 


[Attached File: image/jpeg, Size: 388568 bytes]


 also the alowed one agg=pprved on e


[Attached File: image/jpeg, Size: 342844 bytes]


 i wil upalod teh maste digital logo also

   frontend/next-env.d.ts
    frontend/node_modules/
    knowledge/
    mock_customer_data.csv
    scripts/list_vertex_models.py

nothing added to commit but untracked files present (use "git add" to track)
Enumerating objects: 181, done.
Counting objects: 100% (181/181), done.
Delta compression using up to 4 threads
Compressing objects: 100% (146/146), done.
Writing objects: 100% (175/175), 22.98 KiB | 522.00 KiB/s, done.
Total 175 (delta 116), reused 0 (delta 0), pack-reused 0
remote: Resolving deltas: 100% (116/116), completed with 4 local objects.
To https://github.com/ramamurthy-540835/ekf.git
  8ad4f98..96a7095 master -> master
appadmin@chn-mit-genai-dq1:~/projects/Ram_Projects/DiracDelta/ekf$ pwd
/home/appadmin/projects/Ram_Projects/DiracDelta/ekf
appadmin@chn-mit-genai-dq1:~/projects/Ram_Projects/DiracDelta/ekf$ ls -la
total 2532
drwxrwxr-x 23 appadmin appadmin  4096 May 25 01:25 .
drwxrwxr-x 8 appadmin appadmin  4096 May 22 02:33 ..
drwxr-xr-x 2 appadmin appadmin  4096 May 22 08:17 .agents
-rw-rw-r-- 1 appadmin appadmin 2292555 May 25 01:52 .aider.chat.history.md
-rw-rw-r-- 1 appadmin appadmin   78 May 21 02:41 .aiderignore
-rw-rw-r-- 1 appadmin appadmin  96722 May 25 01:41 .aider.input.history
-rw-rw-r-- 1 appadmin appadmin  4937 May 19 08:52 AIDER_QUICK_REF.md
drwxr-xr-x 2 appadmin appadmin  4096 May 25 01:33 .aider.tags.cache.v4
-rw-rw-r-- 1 appadmin appadmin  8173 May 21 10:23 architecture.md
drwxrwxr-x 7 appadmin appadmin  4096 May 22 18:39 backend
-rw-rw-r-- 1 appadmin appadmin  2443 May 25 02:03 .backend_start.log
drwxrwxr-x 7 appadmin appadmin  4096 May 22 08:26 bigquery
drwxrwxr-x 2 appadmin appadmin  4096 May 22 18:56 .claude
-rw-rw-r-- 1 appadmin appadmin  4126 May 22 07:12 cloudbuild.yaml
drwxr-xr-x 2 appadmin appadmin  4096 May 22 08:17 .codex
drwxrwxr-x 2 appadmin appadmin  4096 May 22 06:08 config
drwxrwxr-x 2 appadmin appadmin  4096 May 22 08:21 docs
-rw-rw-r-- 1 appadmin appadmin  2909 May 21 04:06 EKF_AIDER_PROMPTS.md
-rw-rw-r-- 1 appadmin appadmin  12090 May 19 08:52 EKF_QUICK_START.md
-rw-rw-r-- 1 appadmin appadmin  1400 May 21 08:57 .env.local
-rw-rw-r-- 1 appadmin appadmin  3968 May 21 10:16 execution.md
-rw-rw-r-- 1 appadmin appadmin   66 May 21 01:13 fastapi.log
drwxrwxr-x 5 appadmin appadmin  4096 May 22 18:53 frontend
drwxrwxr-x 8 appadmin appadmin  4096 May 25 01:53 .git
-rw-rw-r-- 1 appadmin appadmin   69 May 21 12:01 .gitignore
drwxrwxr-x 5 appadmin appadmin  4096 Apr 20 09:53 knowledge
-rwxrwxr-x 1 appadmin appadmin  3921 May 22 04:07 launch_model.sh
drwxrwxr-x 2 appadmin appadmin  4096 May 25 01:33 logs
-rw-rw-r-- 1 appadmin appadmin  10059 May 22 17:06 mock_customer_data.csv
-rw-rw-r-- 1 appadmin appadmin  1439 May 21 12:04 models.json
drwxrwxr-x 3 appadmin appadmin  4096 May 20 13:05 path
-rw-rw-r-- 1 appadmin appadmin  2175 May 22 15:47 prompt_requirements.json
drwxrwxr-x 14 appadmin appadmin  4096 May 22 18:44 prompts
drwxrwxr-x 3 appadmin appadmin  4096 May 22 06:23 .pytest_cache
-rw-rw-r-- 1 appadmin appadmin  2791 May 22 08:21 README.md
-rw-rw-r-- 1 appadmin appadmin   155 May 22 06:40 requirements.txt
drwxrwxr-x 5 appadmin appadmin  4096 May 23 11:37 scripts
drwxrwxr-x 3 appadmin appadmin  4096 May 21 06:22 src
drwxrwxr-x 5 appadmin appadmin  4096 May 22 13:23 terraform
drwxrwxr-x 3 appadmin appadmin  4096 May 22 15:47 tests
drwxrwxr-x 5 appadmin appadmin  4096 May 20 03:00 .venv
drwxrwxr-x 5 appadmin appadmin  4096 May 20 03:35 .venv-vllm
appadmin@chn-mit-genai-dq1:~/projects/Ram_Projects/DiracDelta/ekf$
 w
hic foelr i wil uplaod teh logo and filename

appadmin@chn-mit-genai-dq1:~/projects/Ram_Projects/DiracDelta/ekf/frontend$ mkdir public
appadmin@chn-mit-genai-dq1:~/projects/Ram_Projects/DiracDelta/ekf/frontend$ cd public/
appadmin@chn-mit-genai-dq1:~/projects/Ram_Projects/DiracDelta/ekf/frontend/public$ ls
mastech_logo.jpg
appadmin@chn-mit-genai-dq1:~/projects/Ram_Projects/DiracDelta/ekf/frontend/public$ ls -la
total 20
drwxrwxr-x 2 appadmin appadmin 4096 May 25 02:09 .
drwxrwxr-x 6 appadmin appadmin 4096 May 25 02:08 ..
-rw-rw-r-- 1 appadmin appadmin 10684 May 19 05:29 mastech_logo.jpg
appadmin@chn-mit-genai-dq1:~/projects/Ram_Projects/DiracDelta/ekf/frontend/public$ file mastech_logo.jpg
mastech_logo.jpg: JPEG image data, JFIF standard 1.01, resolution (DPI), density 300x300, segment length 16, baseline, precision 8, 400x130, components 3
appadmin@chn-mit-genai-dq1:~/projects/Ram_Projects/DiracDelta/ekf/frontend/public$
 
oke onow lets go te ful pomt as per th eabpo e yj pay pf yje mayhch


[Attached File: image/jpeg, Size: 310816 bytes]


look the bakfgroud color o adeapt an d 


[Attached File: image/jpeg, Size: 290164 bytes]



[Attached File: image/jpeg, Size: 290164 bytes]


 it hu dthat taht also


[Attached File: image/jpeg, Size: 104428 bytes]


 wene dto remove teh word adf as that the e apr ui expoer i explai dto bring so thnothi do wthe adf in this alo we ne dto 
*** System restart required ***
Last login: Sun May 24 23:16:18 2026 from 10.100.10.23
cd appadmin@chn-mit-genai-dq1:~$ cd projects/Ram_Projects/DiracDelta/
appadmin@chn-mit-genai-dq1:~/projects/Ram_Projects/DiracDelta$ cd ekf/
appadmin@chn-mit-genai-dq1:~/projects/Ram_Projects/DiracDelta/ekf$ ls
AIDER_QUICK_REF.md EKF_AIDER_PROMPTS.md logs           requirements.txt
architecture.md   EKF_QUICK_START.md  mock_customer_data.csv  scripts
backend       execution.md     models.json        src
bigquery      fastapi.log      path           terraform
cloudbuild.yaml   frontend       prompt_requirements.json tests
config       knowledge       prompts
docs        launch_model.sh    README.md
appadmin@chn-mit-genai-dq1:~/projects/Ram_Projects/DiracDelta/ekf$
have a
 agent SERPAPI_KEY ia de din .env.locl we ne dto ahev aagent taht can bring teh rnew knwol eampe; drwxrwxr-x 7 appadmin appadmin   4096 Mar 23 05:21 mhh-adept-solution-value-based-care-feature-vbc_agents
-rw-rw-r-- 1 appadmin appadmin 24636798 Apr 17 03:27 mhh-adept-solution-value-based-care-feature-vbc_agents.zip
drwxrwxr-x 2 appadmin appadmin   4096 Apr 20 09:54 Rules
drwxrwxr-x 2 appadmin appadmin   4096 Apr 17 05:49 schemas
appadmin@chn-mit-genai-dq1:~/projects/Ram_Projects/DiracDelta/ekf/knowledge$ cat knowledge_base.json
{
 "metadata": {
  "version": "1.0",
  "generated_at": "2026-04-13T07:35:59.371005",
  "source": "pa_assets/",
  "api_provider": "Google Gemini",
  "total_documents": 1,
  "total_policies": 3
 },
 "documents": [
  {
   "document_name": "Benefits.pdf",
   "document_type": "other",
   "summary": "Benefit design guide outlining eligibility, coverage limits, and cost-sharing provisions for ophthalmology services related to diabetic retinopathy screening and monitoring (e.g., CPT 92250) for Medicare Advantage and Commercial plans.",
   "key_policies": [
    {
     "policy_id": "BD-OPH-2025-V1",
     "title": "Medicare Advantage Plans - Diabetic Retinopathy Screening",
     "coverage_status": "CONDITIONAL",
     "cpt_codes": [
      "92250"
     ],
     "icd_codes": [],
     "requirements": [
      "Member must have a documented diagnosis of diabetes mellitus.",
      "Services must meet CMS preventive guidelines.",
      "Limited to one (1) routine screening per calendar year.",
      "Additional imaging permitted only with clinical change documentation.",
      "Prior authorization required only for services listed in the PA Requirements List.",
      "Must be billed with appropriate ICD-10 diagnosis codes."
     ]
    },
    {
     "policy_id": "BD-OPH-2025-V1",
     "title": "Commercial Plans - Diabetic Retinopathy Screening",
     "coverage_status": "CONDITIONAL",
     "cpt_codes": [
      "92250"
     ],
     "icd_codes": [],
     "requirements": [
      "Limited to one (1) screening per 12 months; duplicate imaging may be denied.",
      "Prior authorization and Step Therapy may apply based on specific plan design.",
      "Site-of-care requirements and Network restrictions may apply."
     ]
    },
    {
     "policy_id": "BD-OPH-2025-V1",
     "title": "Non-Covered Services",
     "coverage_status": "NOT_COVERED",
     "cpt_codes": [
      "92250"
     ],
     "icd_codes": [],
     "requirements": [
      "Routine screening without a qualifying diagnosis of diabetes.",
      "Services exceeding frequency limits without documented medical necessity.",
      "Out-of-network services without explicit prior authorization.",
      "Experimental or investigational imaging modalities."
     ]
    }
   ]
  }
 ],
 "policies": [
  {
   "policy_id": "L33795",
   "title": "Spinal Cord Stimulation",
   "document_source": "LCD_L33795_Spinal_Cord_Stimulation_Novitas_JH.json",
   "cpt_codes": [
    "63650",
    "63655",
    "63685",
    "63688",
    "63661",
    "63663"
   ],
   "icd_codes": [
    "M54.50",
    "M54.51",
    "M54.59",
    "M54.4",
    "G54.4",
    "M96.1",
    "G90.521",
    "