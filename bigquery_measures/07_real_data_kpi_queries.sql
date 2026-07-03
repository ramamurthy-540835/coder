-- Part 2: Real-data KPI queries (GRAPH_TABLE only)

-- KPI 1: Cost/tokens/latency by prompt
SELECT
  prompt_name,
  COUNT(execution_id) AS execution_count,
  SUM(cost) AS total_cost,
  SUM(tokens_used) AS total_tokens,
  AVG(latency_ms) AS avg_latency_ms
FROM GRAPH_TABLE(
  `ctoteam.prism_prompt_catalog.prompt_execution_graph_real`
  MATCH (p:prompts) <-[:UsesPrompt]- (e:executions)
  COLUMNS (
    p.prompt_name AS prompt_name,
    e.execution_id AS execution_id,
    e.cost AS cost,
    e.tokens_used AS tokens_used,
    e.latency_ms AS latency_ms
  )
)
GROUP BY prompt_name
ORDER BY total_cost DESC;

-- KPI 2: Average latency by user
SELECT
  user_name,
  COUNT(execution_id) AS execution_count,
  AVG(latency_ms) AS avg_latency_ms
FROM GRAPH_TABLE(
  `ctoteam.prism_prompt_catalog.prompt_execution_graph_real`
  MATCH (u:users) -[:Triggered]-> (e:executions)
  COLUMNS (
    u.user_name AS user_name,
    e.execution_id AS execution_id,
    e.latency_ms AS latency_ms
  )
)
GROUP BY user_name
ORDER BY avg_latency_ms DESC;

-- KPI 3: Two-step chain latency
SELECT
  first_step_id,
  second_step_id,
  first_step_latency,
  second_step_latency,
  (first_step_latency + second_step_latency) AS total_chain_latency
FROM GRAPH_TABLE(
  `ctoteam.prism_prompt_catalog.prompt_execution_graph_real`
  MATCH (e1:executions) -[:Follows]-> (e2:executions)
  COLUMNS (
    e1.execution_id AS first_step_id,
    e1.latency_ms AS first_step_latency,
    e2.execution_id AS second_step_id,
    e2.latency_ms AS second_step_latency
  )
)
ORDER BY total_chain_latency DESC;
