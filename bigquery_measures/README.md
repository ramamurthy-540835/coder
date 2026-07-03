# BigQuery Property Graph for `prism_prompt_catalog`

This directory contains a set of SQL scripts to implement BigQuery Property Graph analytics directly within Google BigQuery, using native graph and measure capabilities.

The solution is based on a `prism_prompt_catalog` dataset that tracks AI prompt executions, users, and performance metrics.

## Graph Data Model

The graph consists of three main entities (nodes) and three types of relationships (edges):

```
       [users]
          |
     (Triggered)
          |
          v
    [executions] -- (Follows) --> [executions] (Agent chains)
          |
   (UsesPrompt)
          |
          v
      [prompts]
```

*   **Nodes**:
    *   `users`: Individuals who trigger prompt executions.
    *   `prompts`: The prompt templates being executed.
    *   `executions`: The record of a specific prompt run, containing metrics like cost and latency.
*   **Edges**:
    *   `Triggered`: Connects a `user` to an `execution`.
    *   `UsesPrompt`: Connects an `execution` to the `prompt` it used.
    *   `Follows`: A self-referencing edge connecting an `execution` to the next one in a sequence, modeling agent chains.

## SQL Scripts

The implementation is broken down into sequential SQL files:

1.  **`01_create_base_tables.sql`**: Contains the DDL to create the physical BigQuery tables for `users`, `prompts`, and `executions`.
2.  **`02_create_property_graph.sql`**: Contains the `CREATE PROPERTY GRAPH` statement. This script defines the graph schema over the base tables and creates grain-locked **Measures** for `cost`, `latency`, and `tokens` on the `executions` node to ensure accurate aggregations.
3.  **`03_query_examples.sql`**: Provides a standard BigQuery-compatible example query using `GRAPH_TABLE`. It demonstrates how to perform aggregations (e.g., `SUM(cost)`) over matched graph rows using a standard `GROUP BY` clause.
