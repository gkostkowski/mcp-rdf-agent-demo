from datetime import datetime, timedelta, timezone

import pytest

import library_demo.services.overdue_loans as overdue_loans
from library_demo.queries.templates import render_overdue_loans


CENTRAL_LIBRARY = "Central Library"
WEST_LIBRARY = "West Library"
AS_OF = datetime(2026, 9, 1, 12, tzinfo=timezone.utc)
CURRENT_UTC = datetime(2026, 9, 2, 9, 30, tzinfo=timezone.utc)
NAIVE_AS_OF = datetime(2026, 9, 1, 12)
NON_UTC_AS_OF = datetime(2026, 9, 1, 12, tzinfo=timezone(timedelta(hours=2)))
ZERO_OFFSET_NON_UTC_AS_OF = datetime(
    2026, 9, 1, 12, tzinfo=timezone(timedelta(0), "GMT")
)
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


class FakeGraphClient:
    def __init__(self) -> None:
        self.graph = FakeGraph()
        self.queries: list[str] = []

    def construct(self, query: str) -> "FakeGraph":
        self.queries.append(query)
        return self.graph


class FakeResultMapper:
    def __init__(self, items: list[dict[str, object]]) -> None:
        self.items = items
        self.graphs: list[FakeGraph] = []

    def __call__(self, graph: "FakeGraph") -> list[dict[str, object]]:
        self.graphs.append(graph)
        return self.items


class FakeGraph:
    pass


class FixedDateTime:
    @classmethod
    def now(cls, tz: timezone) -> datetime:
        assert tz is timezone.utc
        return CURRENT_UTC


def test_get_overdue_loans_returns_complete_central_library_result() -> None:
    graph_client = FakeGraphClient()
    result_mapper = FakeResultMapper(CENTRAL_LIBRARY_ITEMS)

    result = overdue_loans.get_overdue_loans(
        CENTRAL_LIBRARY,
        AS_OF,
        graph_client=graph_client,
        result_mapper=result_mapper,
    )

    assert result.library_name == CENTRAL_LIBRARY
    assert result.as_of == AS_OF
    assert result.items[0].borrower_name == "Alice Adams"
    assert result.items[0].book_copy_id == "COPY-001"
    assert graph_client.queries == [render_overdue_loans(CENTRAL_LIBRARY, AS_OF)]
    assert result_mapper.graphs == [graph_client.graph]


def test_get_overdue_loans_returns_empty_result_for_west_library() -> None:
    graph_client = FakeGraphClient()
    result_mapper = FakeResultMapper([])

    result = overdue_loans.get_overdue_loans(
        WEST_LIBRARY,
        AS_OF,
        graph_client=graph_client,
        result_mapper=result_mapper,
    )

    assert result.library_name == WEST_LIBRARY
    assert result.as_of == AS_OF
    assert result.items == []
    assert graph_client.queries == [render_overdue_loans(WEST_LIBRARY, AS_OF)]


def test_get_overdue_loans_normalizes_library_name_before_rendering_query() -> None:
    graph_client = FakeGraphClient()
    result_mapper = FakeResultMapper([])

    result = overdue_loans.get_overdue_loans(
        " \tCentral\n  Library ",
        AS_OF,
        graph_client=graph_client,
        result_mapper=result_mapper,
    )

    assert result.library_name == CENTRAL_LIBRARY
    assert graph_client.queries == [render_overdue_loans(CENTRAL_LIBRARY, AS_OF)]


def test_get_overdue_loans_uses_explicit_utc_as_of_in_query() -> None:
    graph_client = FakeGraphClient()
    result_mapper = FakeResultMapper([])
    explicit_as_of = datetime(2026, 9, 3, 8, 15, tzinfo=timezone.utc)

    result = overdue_loans.get_overdue_loans(
        CENTRAL_LIBRARY,
        explicit_as_of,
        graph_client=graph_client,
        result_mapper=result_mapper,
    )

    assert result.as_of == explicit_as_of
    assert graph_client.queries == [
        render_overdue_loans(CENTRAL_LIBRARY, explicit_as_of)
    ]


def test_get_overdue_loans_uses_current_utc_when_as_of_is_absent(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    graph_client = FakeGraphClient()
    result_mapper = FakeResultMapper([])
    monkeypatch.setattr(overdue_loans, "datetime", FixedDateTime)

    result = overdue_loans.get_overdue_loans(
        CENTRAL_LIBRARY,
        None,
        graph_client=graph_client,
        result_mapper=result_mapper,
    )

    assert result.as_of == CURRENT_UTC
    assert graph_client.queries == [render_overdue_loans(CENTRAL_LIBRARY, CURRENT_UTC)]


@pytest.mark.parametrize(
    "invalid_as_of",
    (NAIVE_AS_OF, NON_UTC_AS_OF, ZERO_OFFSET_NON_UTC_AS_OF),
)
def test_get_overdue_loans_rejects_non_utc_explicit_as_of(
    invalid_as_of: datetime,
) -> None:
    graph_client = FakeGraphClient()
    result_mapper = FakeResultMapper([])

    with pytest.raises(ValueError, match="timezone-aware UTC"):
        overdue_loans.get_overdue_loans(
            CENTRAL_LIBRARY,
            invalid_as_of,
            graph_client=graph_client,
            result_mapper=result_mapper,
        )

    assert graph_client.queries == []
