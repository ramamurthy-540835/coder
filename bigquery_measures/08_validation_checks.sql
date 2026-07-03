-- Part 2: Validation checks (plain SQL + GRAPH_TABLE)

-- Check 1: duplicate keys
SELECT 'duplicate_users' AS check_name, CAST(user_id AS STRING) AS key_value, COUNT(*) AS n
FROM `ctoteam.prism_prompt_catalog.users`
GROUP BY user_id
HAVING COUNT(*) > 1
UNION ALL
SELECT 'duplicate_prompts' AS check_name, CAST(prompt_id AS STRING) AS key_value, COUNT(*) AS n
FROM `ctoteam.prism_prompt_catalog.prompts`
GROUP BY prompt_id
HAVING COUNT(*) > 1
UNION ALL
SELECT 'duplicate_executions' AS check_name, CAST(execution_id AS STRING) AS key_value, COUNT(*) AS n
FROM `ctoteam.prism_prompt_catalog.executions`
GROUP BY execution_id
HAVING COUNT(*) > 1;

-- Check 2: orphan references from executions
SELECT 'orphan_user_ref' AS check_name, CAST(e.execution_id AS STRING) AS execution_id
FROM `ctoteam.prism_prompt_catalog.executions` e
LEFT JOIN `ctoteam.prism_prompt_catalog.users` u ON e.user_id = u.user_id
WHERE e.user_id IS NOT NULL AND u.user_id IS NULL
UNION ALL
SELECT 'orphan_prompt_ref' AS check_name, CAST(e.execution_id AS STRING) AS execution_id
FROM `ctoteam.prism_prompt_catalog.executions` e
LEFT JOIN `ctoteam.prism_prompt_catalog.prompts` p ON e.prompt_id = p.prompt_id
WHERE e.prompt_id IS NOT NULL AND p.prompt_id IS NULL
UNION ALL
SELECT 'orphan_next_execution_ref' AS check_name, CAST(e.execution_id AS STRING) AS execution_id
FROM `ctoteam.prism_prompt_catalog.executions` e
LEFT JOIN `ctoteam.prism_prompt_catalog.executions` n ON e.next_execution_id = n.execution_id
WHERE e.next_execution_id IS NOT NULL AND n.execution_id IS NULL;

-- Check 3: graph-vs-sql aggregate sanity (cost per prompt)
WITH graph_cost AS (
  SELECT
    prompt_name,
    SUM(cost) AS graph_total_cost
  FROM GRAPH_TABLE(
    `ctoteam.prism_prompt_catalog.prompt_execution_graph_real`
    MATCH (p:prompts) <-[:UsesPrompt]- (e:executions)
    COLUMNS (
      p.prompt_name AS prompt_name,
      e.cost AS cost
    )
  )
  GROUP BY prompt_name
),
sql_cost AS (
  SELECT
    p.prompt_name,
    SUM(e.cost) AS sql_total_cost
  FROM `ctoteam.prism_prompt_catalog.executions` e
  JOIN `ctoteam.prism_prompt_catalog.prompts` p ON e.prompt_id = p.prompt_id
  GROUP BY p.prompt_name
)
SELECT
  COALESCE(g.prompt_name, s.prompt_name) AS prompt_name,
  g.graph_total_cost,
  s.sql_total_cost,
  (g.graph_total_cost - s.sql_total_cost) AS delta
FROM graph_cost g
FULL OUTER JOIN sql_cost s ON g.prompt_name = s.prompt_name
WHERE g.graph_total_cost IS NULL
   OR s.sql_total_cost IS NULL
   OR (g.graph_total_cost - s.sql_total_cost) != 0;
