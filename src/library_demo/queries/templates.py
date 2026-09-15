from importlib.resources import files


QUERY_PACKAGE = "library_demo.queries"
OVERDUE_LOANS_QUERY = "overdue_loans.sparql"


def load_overdue_loans_query() -> str:
    """Load the packaged developer-authored overdue-loans query."""
    return files(QUERY_PACKAGE).joinpath(OVERDUE_LOANS_QUERY).read_text(encoding="utf-8")
