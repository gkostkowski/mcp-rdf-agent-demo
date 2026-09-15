from datetime import datetime
from importlib.resources import files
import re

from rdflib import Literal


QUERY_PACKAGE = "library_demo.queries"
OVERDUE_LOANS_TEMPLATE = "overdue_loans.sparql"
LIBRARY_NAME_PLACEHOLDER = "{{ library_name }}"
AS_OF_PLACEHOLDER = "{{ as_of }}"
PLACEHOLDER_PATTERN = re.compile(
    "|".join(map(re.escape, (LIBRARY_NAME_PLACEHOLDER, AS_OF_PLACEHOLDER)))
)


def render_overdue_loans(library_name: str, as_of: str | datetime) -> str:
    """Render the developer-authored overdue-loans query with RDF literals."""
    template = files(QUERY_PACKAGE).joinpath(OVERDUE_LOANS_TEMPLATE).read_text(
        encoding="utf-8"
    )
    rendered_values = {
        LIBRARY_NAME_PLACEHOLDER: Literal(library_name).n3(),
        AS_OF_PLACEHOLDER: Literal(as_of).n3(),
    }
    return PLACEHOLDER_PATTERN.sub(lambda match: rendered_values[match.group()], template)
