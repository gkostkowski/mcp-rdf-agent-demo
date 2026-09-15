from datetime import datetime, timezone

from pytest_bdd import given, scenarios, then, when

from library_demo.services.overdue_loans import get_overdue_loans


CENTRAL_LIBRARY = "Central Library"
WEST_LIBRARY = "West Library"
AS_OF = datetime(2026, 9, 1, 12, tzinfo=timezone.utc)
CENTRAL_LIBRARY_ITEMS = [
    {
        "loan_id": "loan-1",
        "book_copy_id": "COPY-001",
        "book_title": "Knowledge Graphs in Practice",
        "borrower_id": "user-alice",
        "borrower_name": "Alice Adams",
        "due_at": datetime(2026, 8, 15, 23, 59, 59, tzinfo=timezone.utc),
    }
]

scenarios("../features/library_queries.feature")


class FakeGraphClient:
    def construct(self, query: str) -> "FakeGraph":
        return FakeGraph()


class FakeResultMapper:
    def __init__(self, items: list[dict[str, object]]) -> None:
        self._items = items

    def __call__(self, graph: "FakeGraph") -> list[dict[str, object]]:
        return self._items


class FakeGraph:
    pass


@given("Central Library has Alice's overdue COPY-001 loan", target_fixture="items")
def central_library_items() -> list[dict[str, object]]:
    return CENTRAL_LIBRARY_ITEMS


@given("West Library has no overdue loans", target_fixture="items")
def west_library_items() -> list[dict[str, object]]:
    return []


@when(
    "an administrator requests Central Library overdue loans", target_fixture="result"
)
def request_central_library_overdue_loans(items: list[dict[str, object]]):
    return get_overdue_loans(
        CENTRAL_LIBRARY,
        AS_OF,
        graph_client=FakeGraphClient(),
        result_mapper=FakeResultMapper(items),
    )


@when("an administrator requests West Library overdue loans", target_fixture="result")
def request_west_library_overdue_loans(items: list[dict[str, object]]):
    return get_overdue_loans(
        WEST_LIBRARY,
        AS_OF,
        graph_client=FakeGraphClient(),
        result_mapper=FakeResultMapper(items),
    )


@then("the overdue result includes Alice Adams and COPY-001")
def result_includes_central_library_loan(result) -> None:
    assert result.items[0].borrower_name == "Alice Adams"
    assert result.items[0].book_copy_id == "COPY-001"


@then("the overdue result has no items")
def result_has_no_items(result) -> None:
    assert result.items == []
