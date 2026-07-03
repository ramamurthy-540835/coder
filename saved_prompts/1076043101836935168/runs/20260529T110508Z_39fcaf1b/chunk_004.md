ecreate a Neo4j-like experience directly in BigQuery.

**Defining Graph Structure**

I am now solidifying the graph schema, mapping `User` to `Execution` via a `TRIGGERED` relationship and `Execution` to `Prompt` with an `OF_PROMPT` edge. I'm also considering `Prompt` to `Prompt` chains for sequential LLM interactions.

**Refining Relationship Logic**

I am now clarifying the relationships between my graph entities. I'm moving away from a simple `PromptLineage` and opting for `Execution_Transitions` to link `execution_id` to `next_execution_id`, which better represents agent chaining. I'm also establishing `Prompt_Executions` to connect `prompt_id` to `execution_id`.



[MODEL] **Exploring BigQuery Graph Measures**

I'm currently focused on how measures are defined within BigQuery property graphs, specifically noting their placement within the `PROPERTIES(...)` clause of `NODE TABLES` and `EDGE TABLES` and the syntax involving `MEASURE()` and aggregate functions.

**Understanding Graph Measure Access**

My focus has shifted to how measures are accessed. I've learned that direct pattern matching with GQL isn't possible; instead, I must use `GRAPH_EXPAND` and the `AGG` function. This handles measure aggregation and automatically manages grain-locking for deduplication.

**Addressing Fan-Out Multiplication**

I've identified a critical bug where fan-out operations, particularly with measures, can lead to double-counting. My current effort is focused on understanding the precise mechanisms causing this row multiplication and developing strategies to mitigate it.

**Resolving Fan-Out Duplication**

I've discovered that joining user, execution, and prompt tables duplicates cost and latency, leading to incorrect aggregations. My current focus is on how BigQuery Property Graphs and grain-locked measures, evaluated top-down, will natively resolve this fan-out issue by preventing row multiplication.

**Implementing Native Measures**

I am now focusing on the practical implementation of native measures within BigQuery Property Graphs. My current work involves defining and creating these measures, specifically `total_cost` and `avg_latency`, directly on the `executions` node table using the `MEASURE()` function.

**Defining Graph Measures**

I am currently defining grain-locked measures directly on the `executions` node table. This includes `total_cost`, `avg_latency`, and `total_tokens`, utilizing the `MEASURE()` function with aggregate operations.

**Implementing Grain-Locked Measures**

I'm now implementing grain-locked measures directly on the `executions` node table, defining `total_cost`, `avg_latency`, and `total_tokens` using the `MEASURE()` function and aggregate operations.

**Leveraging Primary Keys**

I'm now focused on how BigQuery's query engine utilizes defined primary keys on node tables, like `execution_id` for `executions`, to inherently resolve the fan-out problem by preventing row multiplication even with complex graph traversals.



[MODEL] # Enterprise Knowledge Fabric & BigQuery Measures for AI Operations
## Implementing Neo4j-like Graph Analytics with Native BigQuery Measures

**Document Version:** 1.0  
**Date:** May 29, 2026  
**Author(s):** Mastech Digital - GCP - Studio Team  

---

### 1. Introduction & Concept: Replicating the "Neo4j Experience"

In a native graph database like Neo4j, you think of data as connected networks: an AI agent runs a series of sequential **Prompts** (version lineage), triggering multi-step **Executions** (agent chains), initiated by specific **Users**. You write Cypher queries to traverse these paths, trace dependencies, and evaluate pipeline latency. 

Replicating this in a traditional cloud data warehouse often leads to two major bottlenecks:
1. **The Fan-Out / Double-Counting Bug:** Because a single User triggers an Execution chain that references multiple Prompts, joining these tables duplicates metrics (e.g., multiplying the execution `cost` or `tokens` across every path), leading to false metric aggregations.
2. **Heavy ETL Overhead:** Exporting BigQuery tables to an external Neo4j instance just to run graph analytics adds pipeline latency, storage duplication, and security governance risks.

**The Solution:** GoogleSQL natively supports **Property Graphs** and **BigQuery Measures**. By building a property graph directly over your `prism_prompt_catalog` dataset, you get:
*   **Neo4j-style path syntax:** Querying transitions using declarative graph pattern matching (`MATCH`).
*   **Grain-Locked Measures:** Standardized aggregate calculations defined directly at the node schema level. When traversing paths, BigQuery dynamically deduplicates node keys to ensure metrics like "Total LLM Cost" or "Average Chain Latency" are calculated correctly, completely eliminating the fan-out double-counting bug.

---

### 2. The `prism_prompt_catalog` Graph Data Model

To demonstrate this architecture, we will map three primary entities (Nodes) and three interactions (Edges) inside the `prism_prompt_catalog` dataset.

```
       [users] 
          |
     (TriggeredBy)
          v
    [executions] -- (NextStepInChain) --> [executions] (Agent loops)
          |
   (InstantiatedFrom)
          v
      [prompts]
```

#### Graph Nodes (Entities)
*   **`users`**: The developers or end-users initiating LLM requests.
*   **`prompts`**: The versioned prompt templates stored in the catalog.
*   **`executions`**: The granular API execution calls (storing `latency_ms`, `tokens_used`, and `cost`).

#### Graph Edges (Relationships)
*   **`TriggeredBy`**: Connects a `user` to an `execution` ($1:N$).
*   **`InstantiatedFrom`**: Connects an `execution` to the specific template `prompt` it used ($N:1$).
*   **`NextStepInChain`**: Connects an `execution` to a subsequent `execution` ($1:1$ or $1:N$ mapping a multi-step agent trajectory/chain).

---

### 3. Step 1: Base Schema DDL Setup

Run the following SQL in BigQuery to build the physical tables for the catalog. Note the use of `PRIMARY KEY` (even though unenforced, this metadata is consumed by the graph engine to define unique entities).

```sql
CREATE SCHEMA IF NOT EXISTS `prism_prompt_catalog`;

-- 1. Users Table
CREATE OR REPLACE TABLE `prism_prompt_catalog.users` (
    user_id     INT64 NOT NULL,
    user_name   STRING NOT NULL,
    user_role   STRING,
    PRIMARY KEY (user_id) NOT ENFORCED
);

-- 2. Prompts Table (Templates)
CREATE OR REPLACE TABLE `prism_prompt_catalog.prompts` (
    prompt_id   INT64 NOT NULL,
    prompt_name STRING NOT NULL,
    version     STRING NOT NULL,
    category    STRING,
    PRIMARY KEY (prompt_id) NOT ENFORCED
);

-- 3. Executions Table (The fact table containing transactional metrics)
CREATE OR REPLACE TABLE `prism_prompt_catalog.executions` (
    execution_id        INT64 NOT NULL,
    user_id             INT64,
    prompt_id           INT64 NOT NULL,
    parent_execution_id INT64, -- For self-referencing step-by-step chains
    latency_ms          INT64,
    tokens_used         INT64,
    cost                FLOAT64,
    PRIMARY KEY (execution_id) NOT ENFORCED,
    FOREIGN KEY (user_id) REFERENCES `prism_prompt_catalog.users`(user_id) NOT ENFORCED,
    FOREIGN KEY (prompt_id) REFERENCES `prism_prompt_catalog.prompts`(prompt_id) NOT ENFORCED,
    FOREIGN KEY (parent_execution_id) REFERENCES `prism_prompt_catalog.executions`(execution_id) NOT ENFORCED
);
```

---

### 4. Step 2: Creating the Property Graph & Defining Measures

Now, declare the **Property Graph**. In the `PROPERTIES` clause of the `executions` node table, we define the **measures** using the `MEASURE()` keyword. 

These measures lock their aggregation scopes to the primary key of the node table (`execution_id`).

```sql
CREATE OR REPLACE PROPERTY GRAPH `prism_prompt_catalog.PromptCatalogGraph`
NODE TABLES (
  `prism_prompt_catalog.users` 
    KEY (user_id) 
    PROPERTIES (user_id, user_name),
    
  `prism_prompt_catalog.prompts` 
    KEY (prompt_id) 
    PROPERTIES (prompt_id, prompt_name, version),
    
  `prism_prompt_catalog.executions` 
    KEY (execution_id) 
    PROPERTIES (
      execution_id, 
      latency_ms, 
      tokens_used, 
      cost,
      -- Schema-level grain-locked Measures
      MEASURE(SUM(cost)) AS total_cost,
      MEASURE(AVG(latency_ms)) AS avg_latency,
      MEASURE(SUM(tokens_used)) AS total_tokens
    )
)
EDGE TABLES (
  -- Relationship 1: User -> Execution
  `prism_prompt_catalog.executions` AS TriggeredBy
    SOURCE KEY (user_id) REFERENCES users (user_id)
    DESTINATION KEY (execution_id) REFERENCES executions (execution_id),
    
  -- Relationship 2: Execution -> Prompt template
  `prism_prompt_catalog.executions` AS InstantiatedFrom
    SOURCE KEY (execution_id) REFERENCES executions (execution_id)
    DESTINATION KEY (prompt_id) REFERENCES prompts (prompt_id),
    
  -- Relationship 3: Self-referencing Execution Chain (Agentic Paths)
  `prism_prompt_catalog.executions` AS NextStepInChain
    SOURCE KEY (parent_execution_id) REFERENCES executions (execution_id)
    DESTINATION KEY (execution_id) REFERENCES executions (execution_id)
);
```

---

### 5. Step 3: Executing Graph Queries

Once the property graph is defined, you can query it in two ways depending on your use case: **Pattern Matching (GQL)** for structural relationships, and **Graph Expansion (TVF)** for safe metric reporting with measures.

#### Scenario A: The Neo4j Experience (Structural Pattern Matching)
Use the `GRAPH_TABLE` operator and Standard GQL syntax to find multi-step agent loops (e.g., finding instances where `Prompt A` executed and immediately triggered another child execution to resolve a task).

```sql
SELECT * FROM GRAPH_TABLE(
  `prism_prompt_catalog.PromptCatalogGraph`
  -- Replicates Cypher: MATCH (p:prompts)-[]->(e1:executions)-[:NextStepInChain]->(e2:executions)
  MATCH (p:prompts)-[ref:InstantiatedFrom]-(e1:executions)-[chain:NextStepInChain]->(e2:executions)
  COLUMNS (
    p.prompt_name,
    p.version,
    e1.execution_id AS first_step_id,
    e2.execution_id AS second_step_id,
    e2.latency_ms AS step_2_latency
  )
)
ORDER BY step_2_latency DESC;
```

#### Scenario B: Querying Measures Safely (Resolving the Fan-Out Double-Counting Bug)
To run aggregation queries across your graph relations, you must use the `GRAPH_EXPAND` table-valued function (TVF) to create a flattened view. 

Within this select list, you wrap your measure columns in the `AGG()` function. Because of the grain-locked definition on the property graph, **BigQuery deduplicates your executions table behind the scenes before aggregating**, even if multiple paths or joins duplicated the execution rows.

```sql
SELECT 
  prompts_prompt_name,
  prompts_version,
  -- Calculate measures safely across any traversed graph relationships
  AGG(executions_total_cost) AS absolute_cost,
  AGG(executions_avg_latency) AS true_average_latency_ms,
  AGG(executions_total_tokens) AS aggregated_tokens
FROM GRAPH_EXPAND('prism_prompt_catalog.PromptCatalogGraph')
GROUP BY 1, 2;
```
*Note: In the output of `GRAPH_EXPAND`, columns are automatically prefixed with their source node/edge labels (e.g., `prompts_prompt_name` and `executions_total_cost`) to prevent naming collisions.*

---

### 6. Architecture Benefits for Mastech Digital Studio

By deploying this pattern on top of the `prism_prompt_catalog` dataset, you establish three key architectural achievements:

1. **Semantic Layer Decoupling:** Measures are no longer buried inside fragile BI tools (like Looker LookML or Tableau formulas) or written repeatedly inside ad-hoc queries. They are defined centrally in the BigQuery schema itself.
2. **Unified Data Lakehouse & Graph:** Downstream components like **Vertex AI Feature Store** can retrieve high-quality, governed graph structures and correct historical aggregations using native SQL queries directly from BigQuery without running separate data pipelines.
3. **No Row Multiplication Security Risks:** When building analytical models (e.g., predicting LLM pricing structures), data scientists can execute highly relational features (e.g., "cost of the preceding 3 executions in this chain") with guaranteed mathematical correctness because of the grain-locked `MEASURE(SUM(cost))` constraint.

[USER] # PRISM Prompt Lakehouse Handoff (Launch Guide)

This document is the operational handoff for running the Prompt Lakehouse pipeline end-to-end.

## Scope

This pipeline does all of the following:
1. Fetches a saved prompt from Vertex AI Dataset API by `prompt_id`.
2. Extracts deterministic prompt content (system/user/model/attachments).
3. Writes local medallion artifacts (bronze/silver/gold).
4. Uploads artifacts to GCS under `saved-prompts/<prompt_id>/...`.
5. Registers run/chunks/attachments/events into BigQuery (`prism_prompt_catalog`) with SCD Type 2 versioning.

## Entry Point

Run this from:
`/home/appadmin/projects/Ram_Projects/DiracDelta/gcloud_run`

```bash
./scripts/extract_store_prompt.sh <PROMPT_ID> [--force]
```

Example:
```bash
./scripts/extract_store_prompt.sh 3381323161097207808 --force
```

## Core Components

- Extraction agent:
 - `agents/gcs_prompt_store.py`
- BigQuery catalog agent:
 - `agents/bigquery_prompt_catalog.py`
- Driver script:
 - `scripts/extract_store_prompt.sh`
- Schema:
 - `sql/prompt_catalog/create_tables.sql`

## Local Artifact Layout

Generated under:
`saved_prompts/<prompt_id>/runs/<run_id>/`

- `bronze/`
 - `raw.json`
 - `source_metadata.json`
- `silver/`
 - `raw_clean.json`
 - `system.md`
 - `user_messages/`
 - `model_messages/`
 - `chunks/chunk_*.md`
 - `attachments/*.json` (metadata)
 - `attachments_raw/*` (binary/text payload files)
 - `final_assembled.md`
- `gold/`
 - `master.md` (default = business-clean)
 - `master_business.md` (system + USER-only)
 - `master_full.md` (system + all messages)
 - `extraction_report.json`
 - `prompt_summary.json`

## GCS Layout

Uploaded under:
`gs://agentproject/saved-prompts/<prompt_id>/`

- `bronze/<run_id>/...`
- `silver/<run_id>/...`
- `gold/<run_id>/...`
- `gold/latest.json`

## BigQuery Tables

Dataset:
`ctoteam.prism_prompt_catalog`

Main tables:
- `prompt_versions` (SCD Type 2)
- `prompt_chunks`
- `prompt_attachments`
- `prompt_events`

Views:
- `latest_runs`
- `extraction_status`
- `chunk_distribution`

## Business Prompt Quality Mode

Current default for downstream coding prompt is business-clean:
- `gold/master.md` == `gold/master_business.md`
- excludes model-response noise
- best default for Gemini 3.5 execution quality

Full archive prompt remains available:
- `gold/master_full.md`

## Attachment Strategy (BigQuery-ready)

For each attachment:
- metadata JSON is saved in `silver/attachments/*.json`
- actual payload file is saved in `silver/attachments_raw/*`
- BigQuery `prompt_attachments.gcs_uri` points to `attachments_raw/...` when available

This enables downstream multimodal workflows over real files.

## Validation Commands

### 1) Check latest version row
```bash
bq query --use_legacy_sql