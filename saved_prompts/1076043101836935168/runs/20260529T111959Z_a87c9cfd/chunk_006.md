utions), edges
 (Triggered,UsesPrompt,Follows), and measures (total_cost,avg_latency,total_tokens).
 Now generate Part 2 implementation for real data.
 Tasks:

 1. Inspect and map actual schemas for prompt_versions, prompt_events, prompt_chunks, prompt_attachments, prompts, users, executions.
 2. Produce 06_create_property_graph_real_data.sql using real keys/relations.
 3. Produce 07_real_data_kpi_queries.sql with production KPIs: total/avg cost, latency percentiles, token usage, execution success/failure, chain depth,
   prompt version performance, attachment footprint.

 4. Include validation SQL (08_validation_checks.sql) for null keys, orphan edges, duplicate IDs, and measure sanity.
 5. Keep all SQL BigQuery GoogleSQL-compatible and runnable in US region.”



[MODEL] **Refining Production Readiness**

I'm now focusing on ensuring our BigQuery Property Graph implementation meets production-grade standards, specifically by aligning the schema with established best practices for users, prompts, and execution data. This stage is crucial for scalability and maintainability.

**Validating Schema Details**

I'm now cross-referencing my schema designs with the actual PRISM dataset tables. My focus is on verifying column types and logical structures for `prompt_versions`, `prompt_events`, `prompt_chunks`, and `prompt_attachments` against your established data.

**Mapping Core Entities**

I am currently mapping the core entities of `prompts`, `users`, and `executions` within the real schema. My next step involves detailing the node and edge relationships, ensuring `prompt_uid` serves as a robust key for the `prompts` node.

**Defining Node Keys**

I am currently refining the key strategies for our core entities. For prompts, I'm leaning towards `prompt_uid` as the consistent identifier. For prompt versions, `(prompt_uid, version_number)` appears to be the most logical composite key. I am also considering `run_id` as a primary key for prompt event executions.

**Finalizing Key Selections**

I'm now solidifying key definitions, consolidating `run_id` for executions and cross-referencing `event_id` for prompt events. My focus is on ensuring these align with the PRISM catalog's `run_id` lineage for consistency.

**Leveraging Existing Run IDs**

I've realized the PRISM tables already capture run metadata. My current focus is on constructing a Property Graph schema that directly utilizes these existing `run_id` fields for nodes like `prompt_versions`, treating each run as a distinct snapshot.

**Defining Node Keys**

I am currently refining the key strategies for our core entities. For prompts, I'm leaning towards `prompt_uid` as the consistent identifier. For prompt versions, `(prompt_uid, version_number)` appears to be the most logical composite key. I am also considering `run_id` as a primary key for prompt event executions.

**Finalizing Key Selections**

I'm now solidifying key definitions, consolidating `run_id` for executions and cross-referencing `event_id` for prompt events. My focus is on ensuring these align with the PRISM catalog's `run_id` lineage for consistency.

**Leveraging Existing Run IDs**

I've realized the PRISM tables already capture run metadata. My current focus is on constructing a Property Graph schema that directly utilizes these existing `run_id` fields for nodes like `prompt_versions`, treating each run as a distinct snapshot.

**Establishing Node Keys**

I've decided to use `run_id` as the natural key for `prompt_versions` and composite keys like `(run_id, chunk_id)` for `prompt_chunks`, ensuring these align with existing join conditions. `event_id` is now the definitive key for `prompt_events`.

**Structuring Node Tables**

I am now defining the properties and keys for our core node tables. `prompt_versions` will be keyed by `run_id`, and `prompt_chunks` and `prompt_attachments` by `(run_id, chunk_id)` and `(run_id, attachment_id)` respectively. `prompt_events` will use `event_id`.

**Integrating Measures**

I'm incorporating measures into the schema, calculating total attachment size from `prompt_attachments` and tracking token usage and cost from `prompt_events`, enhancing our analytical capabilities.

**Defining Edge Relationships**

I'm now detailing the edge relationships, specifically how `prompt_events` connects to `users` via `user_id`, which I've decided to include in `prompt_versions`. I'm also mapping the `ContainsChunk` edge from `prompt_versions` to `prompt_chunks`.

**Mapping Event Lineage**

I am now defining the `NextEvent` edge, creating a self-referencing relationship on `prompt_events` using `parent_event_id` to capture the precise event flow and lineage, which is a significant development for modeling dynamic execution paths.

**Structuring Graph Edges**

I am now defining the structure of edge tables, including how `prompt_chunks` and `prompt_attachments` naturally serve as edge representations connecting to `prompt_versions` using `run_id`. I am also mapping `prompt_events` to `users` and `prompt_versions` as relevant edges.

**Refining Event Flow Edges**

I'm now defining the `NextEvent` edge, establishing a self-referencing relationship on `prompt_events` via `parent_event_id` to accurately capture dynamic event flow and lineage. This is a critical step in modeling complex execution paths.

**Querying Graph Measures**

I am now focusing on how to effectively query the measures within the property graph. My immediate concern is ensuring that the queries using `GRAPH_EXPAND` and standard SQL are syntactically precise and correctly aggregate measures like failure rates and attachment footprints.

**Validating Graph Logic**

I am now generating validation queries to ensure data integrity, specifically checking for null keys, orphaned edges, duplicate IDs, and verifying that calculated graph measures align perfectly with native SQL aggregations. This phase is critical for robust production readiness.



[MODEL] This implementation guide delivers **Part 2** of the Enterprise Knowledge Fabric & BigQuery Measures integration for the PRISM Prompt Lakehouse. 

We will transition the conceptual graph model from Part 1 into a production-grade framework aligned to your actual physical tables (`prompt_versions`, `prompt_events`, `prompt_chunks`, `prompt_attachments`, `prompts`, `users`, `executions`) in the `ctoteam.prism_prompt_catalog` dataset.

---

### Production Graph Architecture Map

Our production graph explicitly models the life cycle of a prompt run. A user triggers a prompt template version, which decomposes into chunks, pulls dynamic attachments, and undergoes step-by-step executions (events).

```
          [users]
             ^
       (TriggeredBy)
             |
     [prompt_versions] ---- (HasAttachment) ----> [prompt_attachments]
             |
             +------------- (ContainsChunk) ----> [prompt_chunks]
             |
             +------------- (GeneratedEvent) ---> [prompt_events] -- (FollowsEvent) --> [prompt_events]
```

*   **Grain-Locked Measures** prevent double-counting of attachment footprints, chunk weights, and execution latency across paths when joined to recursive event chains.

---

### 1. `06_create_property_graph_real_data.sql`

This script declares the property graph directly over your real PRISM schema. It defines schema-level metrics (measures) locked to the grains of your event logging and storage tables.

```sql
-- =====================================================================
-- Artifact: 06_create_property_graph_real_data.sql
-- Purpose: Defines the Enterprise Property Graph and Native Measures over
--          the physical production tables of the PRISM Prompt Lakehouse.
-- Dataset: ctoteam.prism_prompt_catalog
-- =====================================================================

CREATE OR REPLACE PROPERTY GRAPH `ctoteam.prism_prompt_catalog.prompt_execution_graph`
NODE TABLES (
  -- 1. Users Node Table
  `ctoteam.prism_prompt_catalog.users`
    KEY (user_id)
    PROPERTIES (user_id, user_name, user_role),

  -- 2. Master Prompts Node Table
  `ctoteam.prism_prompt_catalog.prompts`
    KEY (prompt_id)
    PROPERTIES (prompt_id, prompt_name, category),

  -- 3. Prompt Versions Node Table (SCD Type 2 snapshot granularity)
  `ctoteam.prism_prompt_catalog.prompt_versions`
    KEY (run_id)
    PROPERTIES (prompt_uid, version_number, run_id, repeat_mode, is_current, status, valid_from, valid_to),

  -- 4. Chunks Node Table
  `ctoteam.prism_prompt_catalog.prompt_chunks`
    KEY (run_id, chunk_id)
    PROPERTIES (run_id, chunk_id, chunk_type, size_bytes),

  -- 5. Attachments Node Table (Carries dynamic multimodel storage measures)
  `ctoteam.prism_prompt_catalog.prompt_attachments`
    KEY (run_id, attachment_id)
    PROPERTIES (
      run_id, 
      attachment_id, 
      mime_type, 
      gcs_uri, 
      size_bytes,
      -- Measure: Tracks storage weight per version without path duplication
      MEASURE(SUM(size_bytes)) AS total_attachment_size_bytes,
      MEASURE(COUNT(attachment_id)) AS total_attachments_count
    ),

  -- 6. Events Node Table (The operational engine of the execution)
  `ctoteam.prism_prompt_catalog.prompt_events`
    KEY (event_id)
    PROPERTIES (
      event_id,
      run_id,
      parent_event_id,
      event_type,
      status,
      latency_ms,
      tokens_used,
      cost,
      -- Measures: System KPI Aggregations grain-locked to the unique event level
      MEASURE(SUM(cost)) AS total_cost,
      MEASURE(AVG(latency_ms)) AS avg_latency_ms,
      MEASURE(SUM(tokens_used)) AS total_tokens_used,
      MEASURE(COUNT(event_id)) AS event_count,
      MEASURE(COUNTIF(status = 'FAILED')) AS failed_event_count
    )
)
EDGE TABLES (
  -- Edge: User triggered a version run
  `ctoteam.prism_prompt_catalog.prompt_versions` AS TriggeredBy
    SOURCE KEY (run_id) REFERENCES `ctoteam.prism_prompt_catalog.prompt_versions` (run_id)
    DESTINATION KEY (user_id) REFERENCES `ctoteam.prism_prompt_catalog.users` (user_id),

  -- Edge: Version run instantiated a specific Prompt Master Record
  `ctoteam.prism_prompt_catalog.prompt_versions` AS InstantiatedFrom
    SOURCE KEY (run_id) REFERENCES `ctoteam.prism_prompt_catalog.prompt_versions` (run_id)
    DESTINATION KEY (prompt_id) REFERENCES `ctoteam.prism_prompt_catalog.prompts` (prompt_id),

  -- Edge: Version contains prompt text components (Chunks)
  `ctoteam.prism_prompt_catalog.prompt_chunks` AS ContainsChunk
    SOURCE KEY (run_id) REFERENCES `ctoteam.prism_prompt_catalog.prompt_versions` (run_id)
    DESTINATION KEY (run_id, chunk_id) REFERENCES `ctoteam.prism_prompt_catalog.prompt_chunks` (run_id, chunk_id),

  -- Edge: Version run loaded GCS dynamic files (Multimodal Attachments)
  `ctoteam.prism_prompt_catalog.prompt_attachments` AS HasAttachment
    SOURCE KEY (run_id) REFERENCES `ctoteam.prism_prompt_catalog.prompt_versions` (run_id)
    DESTINATION KEY (run_id, attachment_id) REFERENCES `ctoteam.prism_prompt_catalog.prompt_attachments` (run_id, attachment_id),

  -- Edge: Version execution workflow generated operational events
  `ctoteam.prism_prompt_catalog.prompt_events` AS GeneratedEvent
    SOURCE KEY (run_id) REFERENCES `ctoteam.prism_prompt_catalog.prompt_versions` (run_id)
    DESTINATION KEY (event_id) REFERENCES `ctoteam.prism_prompt_catalog.prompt_events` (event_id),

  -- Edge: Lineage transition modeling sequential dependency (e.g. LLM chain transitions)
  `ctoteam.prism_prompt_catalog.prompt_events` AS FollowsEvent
    SOURCE KEY (parent_event_id) REFERENCES `ctoteam.prism_prompt_catalog.prompt_events` (event_id)
    DESTINATION KEY (event_id) REFERENCES `ctoteam.prism_prompt_catalog.prompt_events` (event_id)
);
```

---

### 2. `07_real_data_kpi_queries.sql`

This script provides robust analytical queries covering cost analysis, latency distributions, multimodal storage profiles, and chain-of-thought dependencies.

```sql
-- =====================================================================
-- Artifact: 07_real_data_kpi_queries.sql
-- Purpose: Evaluates production KPIs using GQL pattern matching and
--          dynamic grain-locked measures via the GRAPH_EXPAND TVF.
-- =====================================================================

-- ---------------------------------------------------------------------
-- KPI 1: Cost & Latency Performance by Active Prompt Version
-- Resolves SCD Type 2 active tracking using native event measures.
-- ---------------------------------------------------------------------
SELECT 
  v_prompt_uid AS prompt_uid,
  v_version_number AS version,
  AGG(ev_total_cost) AS total_execution_cost,
  AGG(ev_avg_latency_ms) AS average_latency_ms,
  AGG(ev_total_tokens_used) AS aggregated_token_footprint
FROM GRAPH_EXPAND('ctoteam.prism_prompt_catalog.prompt_execution_graph')
WHERE v_is_current = TRUE -- Filters only for the active SCD Type 2 version
GROUP BY 1, 2
ORDER BY total_execution_cost DESC;

-- ---------------------------------------------------------------------
-- KPI 2: Execution Success vs. Failure Rate per Prompt Template
-- Measures LLM reliability natively without multi-join logic.
-- ---------------------------------------------------------------------
SELECT 
  p_prompt_name AS prompt_template_name,
  v_version_number AS version,
  AGG(ev_event_count) AS total_executions,
  AGG(ev_failed_event_count) AS failed_executions,
  ROUND(SAFE_DIVIDE(AGG(ev_failed_event_count), AGG(ev_event_count)) * 100, 2) AS failure_rate_percentage
FROM GRAPH_EXPAND('ctoteam.prism_prompt_catalog.prompt_execution_graph')
GROUP BY 1, 2
ORDER BY failure_rate_percentage DESC;

-- ---------------------------------------------------------------------
-- KPI 3: Multimodal Payload Footprint Impact on Pipeline Latency
-- Checks if massive GCS attachments trigger high event latency.
-- ---------------------------------------------------------------------
SELECT 
  v_run_id AS execution_run_id,
  AGG(att_total_attachment_size_bytes) AS attachment_payload_bytes,
  AGG(ev_avg_latency_ms) AS average_run_latency_ms
FROM GRAPH_EXPAND('ctoteam.prism_prompt_catalog.prompt_execution_graph')
GROUP BY 1
HAVING attachment_payload_bytes IS NOT NULL
ORDER BY attachment_payload_bytes DESC;

-- ---------------------------------------------------------------------
-- KPI 4: Chain-of-Thought (CoT) Event Chaining Traversal (Structural)
-- Traces execution chains and calculates execution delays between steps.
-- ---------------------------------------------------------------------
SELECT * FROM GRAPH_TABLE(
  `ctoteam.prism_prompt_catalog.prompt_execution_graph`
  MATCH (ev1:prompt_events)-[chain:FollowsEvent]->(ev2:prompt_events)
  COLUMNS (
    ev1.run_id AS run_id,
    ev1.event_id AS initial_event_id,
    ev1.event_type AS initial_step,
    ev2.event_id AS downstream_event_id,
    ev2.event_type AS downstream_step,
    (ev2.latency_ms - ev1.latency_ms) AS execution_delta_ms
  )
)
ORDER BY execution_delta_ms DESC
LIMIT 50;
```

---

### 3. `08_validat