-- Step 4: Insert sample data into the base tables.
DELETE FROM `prism_prompt_catalog.executions` WHERE TRUE;
DELETE FROM `prism_prompt_catalog.users` WHERE TRUE;
DELETE FROM `prism_prompt_catalog.prompts` WHERE TRUE;

INSERT INTO `prism_prompt_catalog.users` (user_id, user_name) VALUES
  (1, 'Alice'),
  (2, 'Bob');

INSERT INTO `prism_prompt_catalog.prompts` (prompt_id, prompt_name, version) VALUES
  (101, 'Summarizer', 'v1'),
  (102, 'Code Generator', 'v2'),
  (103, 'Sentiment Analysis', 'v1.5');

INSERT INTO `prism_prompt_catalog.executions`
  (execution_id, user_id, prompt_id, next_execution_id, latency_ms, tokens_used, cost)
VALUES
  (1001, 1, 101, 1002, 500, 250, 0.001),
  (1002, 1, 102, NULL, 1200, 800, 0.005),
  (1003, 2, 101, NULL, 450, 200, 0.0008),
  (1004, 1, 103, NULL, 800, 400, 0.002);
