-- Step 1: Create the schema for the prompt catalog if it doesn't exist.
CREATE SCHEMA IF NOT EXISTS prism_prompt_catalog;

-- Step 2: Create the base tables for the graph nodes.
-- The PRIMARY KEY constraints, while not enforced, provide metadata for the graph engine.

-- Table for users who initiate prompt executions.
CREATE OR REPLACE TABLE `prism_prompt_catalog.users` (
    user_id     INT64 NOT NULL,
    user_name   STRING,
    PRIMARY KEY (user_id) NOT ENFORCED
);

-- Table for the prompt templates.
CREATE OR REPLACE TABLE `prism_prompt_catalog.prompts` (
    prompt_id   INT64 NOT NULL,
    prompt_name STRING,
    version     STRING,
    PRIMARY KEY (prompt_id) NOT ENFORCED
);

-- Table for execution events, which serves as the central "fact" table.
-- It includes metrics and foreign keys to model relationships.
CREATE OR REPLACE TABLE `prism_prompt_catalog.executions` (
    execution_id        INT64 NOT NULL,
    user_id             INT64,          -- Foreign key to users
    prompt_id           INT64 NOT NULL, -- Foreign key to prompts
    next_execution_id   INT64,          -- Self-referencing key for agent chains
    latency_ms          INT64,
    tokens_used         INT64,
    cost                FLOAT64,
    PRIMARY KEY (execution_id) NOT ENFORCED
);
