from library_demo.queries.templates import load_overdue_loans_query


DATA_GRAPH = "http://library-demo.com/graph/data"


def test_load_overdue_loans_query_loads_developer_authored_query() -> None:
    query = load_overdue_loans_query()

    assert "?library_name" in query
    assert "?as_of" in query


def test_load_overdue_loans_query_has_no_template_placeholders() -> None:
    query = load_overdue_loans_query()

    assert "{{ library_name }}" not in query
    assert "{{ as_of }}" not in query


def test_load_overdue_loans_query_scopes_and_filters_the_overdue_projection() -> None:
    query = load_overdue_loans_query()

    assert f"GRAPH <{DATA_GRAPH}>" in query
    assert "lib:heldByLibrary" in query
    assert "lib:returnedAt" in query
    assert "FILTER NOT EXISTS { ?loan lib:returnedAt ?returned_at . }" in query
    assert "lib:dueAt" in query
    assert "?due_at <" in query
