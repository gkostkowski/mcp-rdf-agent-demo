from datetime import datetime, timezone

from library_demo.models.overdue_loans_result import OverdueLoansResult
from library_demo.queries.templates import render_overdue_loans
from library_demo.services.ports import GraphConstructor, GraphResultMapper



def get_overdue_loans(
    library_name: str,
    as_of: datetime | None,
    *,
    graph_client: GraphConstructor,
    result_mapper: GraphResultMapper,
) -> OverdueLoansResult:
    """Return overdue loans held by the specified library at a UTC instant."""
    normalized_library_name = " ".join(library_name.split())
    resolved_as_of = _resolve_as_of(as_of)
    query = render_overdue_loans(normalized_library_name, resolved_as_of)
    graph = graph_client.construct(query)
    items = result_mapper(graph)

    return OverdueLoansResult(
        library_name=normalized_library_name,
        as_of=resolved_as_of,
        items=items,
    )


def _resolve_as_of(as_of: datetime | None) -> datetime:
    if as_of is None:
        return datetime.now(timezone.utc)
    if as_of.tzinfo is not timezone.utc:
        raise ValueError("as_of must be a timezone-aware UTC datetime")
    return as_of
