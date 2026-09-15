# Library Demo

Library Demo is a toy multi-library system that demonstrates controlled AI-agent access to RDF data in GraphDB. It supports a library administrator asking for overdue loans and borrower loan history through a Langflow agent and FastMCP tools.

## Target Architecture

```text
Administrator -> Langflow agent -> FastMCP tool -> fixed SPARQL CONSTRUCT
    -> GraphDB -> RDFLib graph -> JSON-LD -> Pydantic result -> agent
```

The agent selects a business tool and supplies its schema-defined arguments. It does not generate SPARQL or receive ontology implementation details. FastMCP returns structured facts only; the agent writes the natural-language response.

## Capabilities

- List open loans overdue at a requested library, with an optional UTC `as_of` timestamp.
- Retrieve active and historical loans for a borrower account identifier, such as `user-alice`.
- Retain late-fee calculation as a planned follow-up after the two query capabilities are working.

For this proof of concept, library names are treated as unique after normalization. The overdue query is scoped to the library holding the book copy.

## Repository structure

- `data/`: deterministic library fixture data.
- `vocab/`: generated ontology and controlled vocabulary artefacts.
- `docs/conceptual-model/`: source conceptual model and diagrams.
- `infra/`: Docker Compose and GraphDB loader. See [infra/README.md](infra/README.md) for local GraphDB setup.
- `src/`: Python application package, added according to the implementation plan.
- `workflow/`: version-controlled exported Langflow flows and agent assets.
- `docs/superpowers/plans/2026-09-15-library-mcp-demo.md`: approved implementation plan.

## Development Boundaries

- Queries are developer-authored SPARQL `CONSTRUCT` templates against `http://library-demo.com/graph/data`.
- User and agent values are rendered as RDF literals, never interpolated into SPARQL directly.
- Query-specific Pydantic DTOs are the MCP contract; they do not mirror the full ontology.
- The Python package follows `models`, `adapters`, `services`, and `entrypoints` boundaries.

## Documentation

- [GraphDB local infrastructure](infra/README.md)
- [Library MCP implementation plan](docs/superpowers/plans/2026-09-15-library-mcp-demo.md)
