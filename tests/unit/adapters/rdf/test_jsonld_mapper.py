from datetime import datetime, timezone
from pathlib import Path

from rdflib import Graph, Literal, Namespace
from rdflib.namespace import XSD

from library_demo.adapters.rdf.jsonld_mapper import map_overdue_loans


FIXTURE_FILE = Path(__file__).parents[3] / "fixtures" / "overdue_loans.ttl"
EXPECTED_DUE_AT = datetime(2026, 8, 15, 23, 59, 59, tzinfo=timezone.utc)
DATA = Namespace("http://library-demo.com/data#")
LIBRARY = Namespace("http://library-demo.com/ontology#")
TIMEZONELESS_DUE_AT = Literal("2026-08-15T23:59:59", datatype=XSD.dateTime)


def test_map_overdue_loans_returns_no_loans_for_an_empty_graph() -> None:
    assert map_overdue_loans(Graph()) == []


def test_map_overdue_loans_maps_the_complete_overdue_projection() -> None:
    graph = Graph().parse(FIXTURE_FILE, format="turtle")

    assert map_overdue_loans(graph) == [
        {
            "loan_id": "http://library-demo.com/data#aliceCentralLoanOverdue",
            "book_copy_id": "COPY-001",
            "book_title": "Knowledge Graphs in Practice",
            "borrower_id": "user-alice",
            "borrower_name": "Alice Adams",
            "due_at": EXPECTED_DUE_AT,
        }
    ]


def test_map_overdue_loans_interprets_a_timezone_less_due_at_as_utc() -> None:
    graph = Graph().parse(FIXTURE_FILE, format="turtle")
    graph.remove((DATA.aliceCentralLoanOverdue, LIBRARY.dueAt, None))
    graph.add((DATA.aliceCentralLoanOverdue, LIBRARY.dueAt, TIMEZONELESS_DUE_AT))

    assert map_overdue_loans(graph)[0]["due_at"] == EXPECTED_DUE_AT
