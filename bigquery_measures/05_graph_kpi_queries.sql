-- Query 1: Top Prompts by Total Cost
SELECT
  prompt_name,
  version,
  SUM(cost) AS total_cost_for_prompt,
  COUNT(execution_id) AS number_of_executions
FROM GRAPH_TABLE(
  `prism_prompt_catalog.prompt_execution_graph`
  MATCH (p:prompts) <-[:UsesPrompt]- (e:executions)
  COLUMNS (
    p.prompt_name AS prompt_name,
    p.version AS version,
    e.execution_id AS execution_id,
    e.cost AS cost
  )
)
GROUP BY prompt_name, version
ORDER BY total_cost_for_prompt DESC;

-- Query 2: Average Latency by User
SELECT
  user_name,
  AVG(latency_ms) AS avg_user_latency,
  COUNT(execution_id) AS total_executions
FROM GRAPH_TABLE(
  `prism_prompt_catalog.prompt_execution_graph`
  MATCH (u:users) -[:Triggered]-> (e:executions)
  COLUMNS (
    u.user_name AS user_name,
    e.latency_ms AS latency_ms,
    e.execution_id AS execution_id
  )
)
GROUP BY user_name
ORDER BY avg_user_latency DESC;

-- Query 3: Two-step execution chains
SELECT
  first_step_id,
  second_step_id,
  (first_step_latency + second_step_latency) AS total_chain_latency,
  user_name
FROM GRAPH_TABLE(
  `prism_prompt_catalog.prompt_execution_graph`
  MATCH (u:users) -[:Triggered]-> (e1:executions) -[:Follows]-> (e2:executions)
  COLUMNS (
    e1.execution_id AS first_step_id,
    e1.latency_ms AS first_step_latency,
    e2.execution_id AS second_step_id,
    e2.latency_ms AS second_step_latency,
    u.user_name AS user_name
  )
);
