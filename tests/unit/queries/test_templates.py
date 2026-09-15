from datetime import datetime, timezone

from rdflib import Literal

from library_demo.queries.templates import render_overdue_loans


LIBRARY_NAME = 'Central Library" } UNION { ?s ?p ?o'
AS_OF = datetime(2026, 9, 1, 12, tzinfo=timezone.utc)
INJECTION_LIKE_AS_OF = '2026-09-01T12:00:00Z" } UNION { ?s ?p ?o'
LIBRARY_NAME_WITH_AS_OF_PLACEHOLDER = "Central {{ as_of }} Library"
DATA_GRAPH = "http://library-demo.com/graph/data"


def test_render_overdue_loans_renders_inputs_as_rdf_literals() -> None:
    query = render_overdue_loans(LIBRARY_NAME, AS_OF)

    assert Literal(LIBRARY_NAME).n3() in query
    assert Literal(AS_OF).n3() in query
    assert "UNION" not in query.replace(Literal(LIBRARY_NAME).n3(), "")


def test_render_overdue_loans_renders_injection_like_as_of_as_an_rdf_literal() -> None:
    query = render_overdue_loans(LIBRARY_NAME, INJECTION_LIKE_AS_OF)

    assert Literal(INJECTION_LIKE_AS_OF).n3() in query
    assert "UNION" not in query.replace(Literal(LIBRARY_NAME).n3(), "").replace(
        Literal(INJECTION_LIKE_AS_OF).n3(), ""
    )


def test_render_overdue_loans_does_not_reprocess_placeholder_in_library_name() -> None:
    query = render_overdue_loans(LIBRARY_NAME_WITH_AS_OF_PLACEHOLDER, AS_OF)

    assert Literal(LIBRARY_NAME_WITH_AS_OF_PLACEHOLDER).n3() in query


def test_render_overdue_loans_substitutes_all_placeholders() -> None:
    query = render_overdue_loans(LIBRARY_NAME, AS_OF)

    assert "{{ library_name }}" not in query
    assert "{{ as_of }}" not in query


def test_render_overdue_loans_scopes_and_filters_the_overdue_projection() -> None:
    query = render_overdue_loans(LIBRARY_NAME, AS_OF)

    assert f"GRAPH <{DATA_GRAPH}>" in query
    assert "lib:heldByLibrary" in query
    assert "lib:returnedAt" in query
    assert "FILTER NOT EXISTS { ?loan lib:returnedAt ?returned_at . }" in query
    assert "lib:dueAt" in query
    assert "?due_at <" in query
