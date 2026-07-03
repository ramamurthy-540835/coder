-- Step 3: Create the Property Graph over the base tables.
-- This defines the semantic layer, including nodes, edges, and measures.

CREATE OR REPLACE PROPERTY GRAPH `prism_prompt_catalog.prompt_execution_graph`
-- Define the node tables using their primary keys.
NODE TABLES (
  `prism_prompt_catalog.users` AS users
    KEY (user_id)
    PROPERTIES (user_id, user_name),

  `prism_prompt_catalog.prompts` AS prompts
    KEY (prompt_id)
    PROPERTIES (prompt_id, prompt_name, version),

  `prism_prompt_catalog.executions` AS executions
    KEY (execution_id)
    PROPERTIES (
      execution_id,
      latency_ms,
      tokens_used,
      cost,
      -- Define grain-locked measures to prevent fan-out bugs during aggregation.
      -- These measures are locked to the `execution_id` of this table.
      MEASURE(SUM(cost)) AS total_cost,
      MEASURE(AVG(latency_ms)) AS avg_latency,
      MEASURE(SUM(tokens_used)) AS total_tokens
    )
)
-- Define the edge tables to model relationships between nodes.
EDGE TABLES (
  -- Relationship 1: User -> Execution
  `prism_prompt_catalog.executions` AS Triggered
    SOURCE KEY (user_id) REFERENCES users (user_id)
    DESTINATION KEY (execution_id) REFERENCES executions (execution_id),

  -- Relationship 2: Execution -> Prompt
  `prism_prompt_catalog.executions` AS UsesPrompt
    SOURCE KEY (execution_id) REFERENCES executions (execution_id)
    DESTINATION KEY (prompt_id) REFERENCES prompts (prompt_id),

  -- Relationship 3: Execution -> Execution (Self-referencing agent chain)
  `prism_prompt_catalog.executions` AS Follows
    SOURCE KEY (execution_id) REFERENCES executions (execution_id)
    DESTINATION KEY (next_execution_id) REFERENCES executions (execution_id)
);
