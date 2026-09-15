from typing import Protocol


class ConstructedGraph(Protocol):
    """Opaque graph data passed from a constructor to a result mapper."""


class GraphConstructor(Protocol):
    def construct(self, query: str) -> ConstructedGraph:
        """Execute a CONSTRUCT query and return its RDF graph."""


class GraphResultMapper(Protocol):
    def __call__(self, graph: ConstructedGraph) -> list[dict[str, object]]:
        """Map an RDF graph to a query-specific result projection."""
