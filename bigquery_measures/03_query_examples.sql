-- Example Aggregation Query for the `prompt_execution_graph`

-- This query calculates the total cost and average latency for each prompt
-- by aggregating the properties of matched nodes from the graph.
-- It uses the standard GRAPH_TABLE function with a GROUP BY clause.
SELECT
  prompt_name,
  version,
  COUNT(execution_id) AS number_of_executions,
  SUM(cost) AS total_cost_for_prompt,
  AVG(latency_ms) AS average_latency_for_prompt
FROM GRAPH_TABLE(
  `prism_prompt_catalog.prompt_execution_graph`
  MATCH (p:prompts) <-[:UsesPrompt]- (e:executions)
  COLUMNS (
    p.prompt_name AS prompt_name,
    p.version AS version,
    e.execution_id AS execution_id,
    e.cost AS cost,
    e.latency_ms AS latency_ms
  )
)
GROUP BY
  prompt_name,
  version
ORDER BY
  total_cost_for_prompt DESC;
