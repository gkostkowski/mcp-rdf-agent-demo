from datetime import datetime, timezone
from pathlib import Path

from rdflib import Dataset, Graph, Literal, Namespace, RDF, URIRef
from rdflib.namespace import XSD

from library_demo.queries.templates import load_overdue_loans_query


DATA_FILE = Path(__file__).parents[3] / "data/library-xs.ttl"
DATA_GRAPH = URIRef("http://library-demo.com/graph/data")
DATA = Namespace("http://library-demo.com/data#")
LIB = Namespace("http://library-demo.com/ontology#")
DCTERMS = Namespace("http://purl.org/dc/terms/")
PERSON = Namespace("http://www.w3.org/ns/person#")
AS_OF = datetime(2026, 9, 15, tzinfo=timezone.utc)


def execute_query(query: str) -> Graph:
    dataset = Dataset(default_union=True)
    dataset.graph(DATA_GRAPH).parse(DATA_FILE, format="turtle")
    return dataset.query(
        query,
        initBindings={
            "library_name": Literal("Central Library"),
            "as_of": Literal(AS_OF),
        },
    ).graph


def assert_overdue_loan_projection(result: Graph) -> None:
    loan = DATA.aliceCentralLoanOverdue

    assert set(result.subjects(RDF.type, LIB.Loan)) == {loan}
    assert (loan, LIB.loanedCopy, DATA.copy1) in result
    assert (
        loan,
        LIB.dueAt,
        Literal("2026-08-15T23:59:59", datatype=XSD.dateTime),
    ) in result
    assert not list(result.objects(loan, LIB.returnedAt))
    assert (DATA.copy1, LIB.bookCopyId, Literal("COPY-001")) in result
    assert (
        DATA.bookEdition1,
        LIB.title,
        Literal("Knowledge Graphs in Practice"),
    ) in result
    assert (DATA.alice, DCTERMS.identifier, Literal("user-alice")) in result
    assert (DATA.alice, PERSON.fullName, Literal("Alice Adams")) in result


def test_packaged_overdue_loans_query_constructs_complete_projection() -> None:
    assert_overdue_loan_projection(execute_query(load_overdue_loans_query()))
