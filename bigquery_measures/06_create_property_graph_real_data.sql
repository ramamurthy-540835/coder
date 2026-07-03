-- Part 2: Real-data conservative graph (BigQuery GoogleSQL)
-- Uses only verified core tables/columns.

CREATE OR REPLACE PROPERTY GRAPH `ctoteam.prism_prompt_catalog.prompt_execution_graph_real`
NODE TABLES (
  `ctoteam.prism_prompt_catalog.users` AS users
    KEY (user_id)
    PROPERTIES (user_id, user_name),

  `ctoteam.prism_prompt_catalog.prompts` AS prompts
    KEY (prompt_id)
    PROPERTIES (prompt_id, prompt_name),

  `ctoteam.prism_prompt_catalog.executions` AS executions
    KEY (execution_id)
    PROPERTIES (
      execution_id,
      user_id,
      prompt_id,
      next_execution_id,
      latency_ms,
      tokens_used,
      cost,
      MEASURE(SUM(cost)) AS total_cost,
      MEASURE(AVG(latency_ms)) AS avg_latency,
      MEASURE(SUM(tokens_used)) AS total_tokens
    )
)
EDGE TABLES (
  `ctoteam.prism_prompt_catalog.executions` AS Triggered
    SOURCE KEY (user_id) REFERENCES users (user_id)
    DESTINATION KEY (execution_id) REFERENCES executions (execution_id),

  `ctoteam.prism_prompt_catalog.executions` AS UsesPrompt
    SOURCE KEY (execution_id) REFERENCES executions (execution_id)
    DESTINATION KEY (prompt_id) REFERENCES prompts (prompt_id),

  `ctoteam.prism_prompt_catalog.executions` AS Follows
    SOURCE KEY (execution_id) REFERENCES executions (execution_id)
    DESTINATION KEY (next_execution_id) REFERENCES executions (execution_id)
);
