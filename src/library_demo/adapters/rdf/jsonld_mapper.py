"""Map framed overdue-loan JSON-LD into dictionaries.

OVERDUE_LOAN_CONTEXT maps RDF predicates to short JSON-LD terms. OVERDUE_LOAN_FRAME
tells PyLD which related nodes to embed so the mapper can flatten one overdue-loan
result.
"""

import json
from datetime import datetime, timezone

from pyld import jsonld
from rdflib import Graph


LIBRARY = "http://library-demo.com/ontology#"
DCTERMS = "http://purl.org/dc/terms/"
PERSON = "http://www.w3.org/ns/person#"
XSD = "http://www.w3.org/2001/XMLSchema#"

# Maps RDF predicates to the short terms used by the JSON-LD mapper.
OVERDUE_LOAN_CONTEXT = {
    "@vocab": LIBRARY,
    "loaned_copy": {"@id": f"{LIBRARY}loanedCopy", "@type": "@id"},
    "due_at": {"@id": f"{LIBRARY}dueAt", "@type": f"{XSD}dateTime"},
    "membership": {"@id": f"{LIBRARY}madeUnderMembership", "@type": "@id"},
    "book_copy_id": f"{LIBRARY}bookCopyId",
    "book": {"@id": f"{LIBRARY}represents", "@type": "@id"},
    "book_title": f"{LIBRARY}title",
    "borrower": {"@id": f"{LIBRARY}belongsToBorrower", "@type": "@id"},
    "borrower_id": f"{DCTERMS}identifier",
    "borrower_name": f"{PERSON}fullName",
}

# Embeds overdue-loan related nodes needed for flattening the result.
OVERDUE_LOAN_FRAME = {
    "@context": OVERDUE_LOAN_CONTEXT,
    "@type": "Loan",
    "loaned_copy": {
        "@embed": "@always",
        "book_copy_id": {},
        "book": {"@embed": "@always", "book_title": {}},
    },
    "due_at": {},
    "membership": {
        "@embed": "@always",
        "borrower": {
            "@embed": "@always",
            "borrower_id": {},
            "borrower_name": {},
        },
    },
}


def _utc_datetime(value: str) -> datetime:
    """Parse an offset-aware timestamp as UTC."""
    due_at = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if due_at.utcoffset() is None:
        raise ValueError("due_at must include an explicit UTC offset")
    return due_at.astimezone(timezone.utc)


def map_overdue_loans(graph: Graph) -> list[dict[str, object]]:
    """Map overdue-loan RDF data to flat result dictionaries."""
    json_ld_document = json.loads(graph.serialize(format="json-ld"))
    framed_document = jsonld.frame(json_ld_document, OVERDUE_LOAN_FRAME)
    compacted_document = jsonld.compact(framed_document, OVERDUE_LOAN_CONTEXT)
    loans = compacted_document.get("@graph", [compacted_document])

    return sorted(
        [
            {
                "loan_id": loan["@id"],
                "book_copy_id": loan["loaned_copy"]["book_copy_id"],
                "book_title": loan["loaned_copy"]["book"]["book_title"],
                "borrower_id": loan["membership"]["borrower"]["borrower_id"],
                "borrower_name": loan["membership"]["borrower"]["borrower_name"],
                "due_at": _utc_datetime(loan["due_at"]),
            }
            for loan in loans
        ],
        key=lambda loan: str(loan["loan_id"]),
    )
