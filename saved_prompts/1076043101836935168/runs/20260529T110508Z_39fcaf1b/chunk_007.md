GRAPH_EXPAND('ctoteam.prism_prompt_catalog.prompt_execution_graph')
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

### 3. `08_validation_checks.sql`

This script serves as your diagnostic test suite. It flags logical schema errors, orphan edges, and tests that native graph measures match classic SQL aggregate calculations.

```sql
-- =====================================================================
-- Artifact: 08_validation_checks.sql
-- Purpose: Ensures the graph and measures framework is accurate and logical.
-- =====================================================================

-- ---------------------------------------------------------------------
-- TEST 1: Detect Duplicate Primary Keys (Node Key Violations)
-- ---------------------------------------------------------------------
SELECT 'Duplicate Versions' AS assertion, run_id, COUNT(*) AS count
FROM `ctoteam.prism_prompt_catalog.prompt_versions` GROUP BY 2 HAVING count > 1
UNION ALL
SELECT 'Duplicate Events' AS assertion, CAST(event_id AS STRING), COUNT(*) AS count
FROM `ctoteam.prism_prompt_catalog.prompt_events` GROUP BY 2 HAVING count > 1;

-- ---------------------------------------------------------------------
-- TEST 2: Orphan Edge Identification (Referential Integrity Check)
-- Identifies edges pointing to node references that do not exist.
-- ---------------------------------------------------------------------
SELECT 
  'Orphan Event-to-Run Reference' AS validation_failure, 
  e.event_id AS identifier 
FROM `ctoteam.prism_prompt_catalog.prompt_events` e
LEFT JOIN `ctoteam.prism_prompt_catalog.prompt_versions` v ON e.run_id = v.run_id
WHERE v.run_id IS NULL

UNION ALL

SELECT 
  'Orphan Attachment-to-Run Reference' AS validation_failure, 
  CAST(a.attachment_id AS STRING) AS identifier 
FROM `ctoteam.prism_prompt_catalog.prompt_attachments` a
LEFT JOIN `ctoteam.prism_prompt_catalog.prompt_versions` v ON a.run_id = v.run_id
WHERE v.run_id IS NULL;

-- ---------------------------------------------------------------------
-- TEST 3: Measure Sanity Validation Check
-- Confirms that the native measures evaluated inside GRAPH_EXPAND 
-- match conventional SQL calculations down to the exact decimal.
-- ---------------------------------------------------------------------
WITH GraphMeasures AS (
  SELECT 
    v_run_id AS run_id,
    AGG(ev_total_cost) AS graph_cost,
    AGG(ev_total_tokens_used) AS graph_tokens
  FROM GRAPH_EXPAND('ctoteam.prism_prompt_catalog.prompt_execution_graph')
  GROUP BY 1
),
ClassicSQLMeasures AS (
  SELECT 
    run_id,
    SUM(cost) AS sql_cost,
    SUM(tokens_used) AS sql_tokens
  FROM `ctoteam.prism_prompt_catalog.prompt_events`
  GROUP BY 1
)
SELECT 
  g.run_id,
  g.graph_cost,
  c.sql_cost,
  g.graph_tokens,
  c.sql_tokens,
  (g.graph_cost - c.sql_cost) AS cost_discrepancy,
  (g.graph_tokens - c.sql_tokens) AS token_discrepancy
FROM GraphMeasures g
JOIN ClassicSQLMeasures c ON g.run_id = c.run_id
WHERE (g.graph_cost - c.sql_cost) != 0 OR (g.graph_tokens - c.sql_tokens) != 0;
```

---

### 4. Part 2 Operational Status Report

With the execution of Part 2, your **Enterprise Knowledge Fabric** architecture is fully complete:

| Component | Status | Location | Native Capability |
| :--- | :--- | :--- | :--- |
| **06_create_property_graph_real_data.sql** | Prepared | BQ SQL | Generates the structural framework mapping your physical tables (`prompt_versions`, `prompt_events`, etc.). |
| **07_real_data_kpi_queries.sql** | Prepared | BQ GQL | Tracks reliability, multimodal payloads, and recursive chain trajectories using Graph-native SQL. |
| **08_validation_checks.sql** | Prepared | BQ SQL | Asserts referential and measure integrity across all catalog relationships. |

### How to Run:
1. Copy the code block from `06_create_property_graph_real_data.sql` and run it in the BigQuery Workspace console.
2. Run your validation scripts (`08_validation_checks.sql`) to ensure no orphan logs exist from previous tests.
3. Call the queries in `07_real_data_kpi_queries.sql` to verify active measures performance metrics.