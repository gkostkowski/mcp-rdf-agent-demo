from datetime import datetime, timezone

import pytest
from fastmcp import Client

from library_demo.adapters.graphdb.client import GraphDBClientError
from library_demo.models.overdue_loans_result import OverdueLoansResult


CENTRAL_LIBRARY = "Central Library"
WEST_LIBRARY = "West Library"
AS_OF = datetime(2026, 9, 1, 12, tzinfo=timezone.utc)
LANGFLOW_UTC_AS_OF = "2026-09-15 21:08:11 UTC"
EXPECTED_LANGFLOW_UTC_AS_OF = datetime(2026, 9, 15, 21, 8, 11, tzinfo=timezone.utc)
OVERDUE_ITEMS = [
    {
        "loan_id": "loan-1",
        "book_copy_id": "COPY-001",
        "book_title": "Knowledge Graphs in Practice",
        "borrower_id": "user-alice",
        "borrower_name": "Alice Adams",
        "due_at": datetime(2026, 8, 15, 23, 59, 59, tzinfo=timezone.utc),
    }
]
SERVICE_UNAVAILABLE_MESSAGE = "The overdue-loans service is unavailable."
SECRET_ENDPOINT = "http://graphdb.internal:7200/repositories/secret-library"
ORIGINAL_ERROR = "connection refused while reading loan data"
GRAPHDB_ENDPOINT = "http://graphdb:7200/repositories/library-demo"


class FakeGraph:
    pass


class FakeGraphClient:
    def __init__(self) -> None:
        self.graph = FakeGraph()

    def construct(self, query: str, bindings: dict[str, str | datetime]) -> FakeGraph:
        return self.graph


class FailingGraphClient:
    def construct(self, query: str, bindings: dict[str, str | datetime]) -> FakeGraph:
        raise GraphDBClientError(f"{SECRET_ENDPOINT}: {ORIGINAL_ERROR}")


class FakeResultMapper:
    def __init__(self, items: list[dict[str, object]]) -> None:
        self._items = items

    def __call__(self, graph: FakeGraph) -> list[dict[str, object]]:
        return self._items


@pytest.fixture
def mcp_server():
    from library_demo.entrypoints.mcp import create_mcp_server

    return create_mcp_server(
        graph_client=FakeGraphClient(),
        result_mapper=FakeResultMapper(OVERDUE_ITEMS),
    )


@pytest.mark.anyio
async def test_advertises_only_the_overdue_loans_tool(mcp_server) -> None:
    async with Client(mcp_server) as client:
        tools = await client.list_tools()

    assert [tool.name for tool in tools] == ["get_overdue_loans"]


@pytest.mark.anyio
async def test_overdue_loans_schema_requires_library_name_and_makes_as_of_optional(
    mcp_server,
) -> None:
    async with Client(mcp_server) as client:
        tools = await client.list_tools()

    schema = tools[0].inputSchema
    assert schema["required"] == ["library_name"]
    assert schema["properties"]["library_name"]["type"] == "string"
    assert schema["properties"]["as_of"]["default"] is None


@pytest.mark.anyio
async def test_get_overdue_loans_returns_a_structured_pydantic_result(mcp_server) -> None:
    async with Client(mcp_server) as client:
        response = await client.call_tool(
            "get_overdue_loans",
            {"library_name": CENTRAL_LIBRARY, "as_of": AS_OF.isoformat()},
        )

    result = OverdueLoansResult.model_validate(response.structured_content)
    assert result.library_name == CENTRAL_LIBRARY
    assert result.as_of == AS_OF
    assert result.items[0].book_copy_id == "COPY-001"


@pytest.mark.anyio
async def test_get_overdue_loans_accepts_the_langflow_utc_datetime_format(
    mcp_server,
) -> None:
    async with Client(mcp_server) as client:
        response = await client.call_tool(
            "get_overdue_loans",
            {"library_name": CENTRAL_LIBRARY, "as_of": LANGFLOW_UTC_AS_OF},
        )

    result = OverdueLoansResult.model_validate(response.structured_content)
    assert result.as_of == EXPECTED_LANGFLOW_UTC_AS_OF


@pytest.mark.anyio
async def test_get_overdue_loans_returns_an_empty_structured_pydantic_result() -> None:
    from library_demo.entrypoints.mcp import create_mcp_server

    server = create_mcp_server(
        graph_client=FakeGraphClient(),
        result_mapper=FakeResultMapper([]),
    )

    async with Client(server) as client:
        response = await client.call_tool(
            "get_overdue_loans",
            {"library_name": WEST_LIBRARY, "as_of": AS_OF.isoformat()},
        )

    result = OverdueLoansResult.model_validate(response.structured_content)
    assert result.library_name == WEST_LIBRARY
    assert result.items == []


@pytest.mark.anyio
async def test_get_overdue_loans_rejects_a_request_without_library_name(mcp_server) -> None:
    async with Client(mcp_server) as client:
        response = await client.call_tool_mcp("get_overdue_loans", {"as_of": AS_OF.isoformat()})

    assert response.isError is True


@pytest.mark.anyio
async def test_graphdb_failure_is_sanitized_for_mcp_callers() -> None:
    from library_demo.entrypoints.mcp import create_mcp_server

    server = create_mcp_server(
        graph_client=FailingGraphClient(),
        result_mapper=FakeResultMapper(OVERDUE_ITEMS),
    )

    async with Client(server) as client:
        response = await client.call_tool_mcp(
            "get_overdue_loans",
            {"library_name": CENTRAL_LIBRARY, "as_of": AS_OF.isoformat()},
        )

    assert response.isError is True
    assert SERVICE_UNAVAILABLE_MESSAGE in str(response.content)
    assert SECRET_ENDPOINT not in str(response.content)
    assert ORIGINAL_ERROR not in str(response.content)


@pytest.mark.anyio
async def test_production_factory_reads_the_graphdb_endpoint(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import library_demo.entrypoints.mcp as mcp

    received_endpoints: list[str] = []

    class RecordedGraphDBClient:
        def __init__(self, endpoint: str) -> None:
            received_endpoints.append(endpoint)

    monkeypatch.setenv("GRAPHDB_ENDPOINT", GRAPHDB_ENDPOINT)
    monkeypatch.setattr(mcp, "GraphDBClient", RecordedGraphDBClient)

    server = mcp.create_production_mcp_server()

    assert received_endpoints == [GRAPHDB_ENDPOINT]
    assert list(await server.get_tools()) == ["get_overdue_loans"]


def test_main_starts_streamable_http_on_the_runtime_host_and_port(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import library_demo.entrypoints.mcp as mcp

    run_calls: list[dict[str, object]] = []

    class FakeServer:
        def run(self, **kwargs: object) -> None:
            run_calls.append(kwargs)

    monkeypatch.setattr(mcp, "create_production_mcp_server", FakeServer)

    mcp.main()

    assert run_calls == [
        {
            "transport": "streamable-http",
            "host": "0.0.0.0",
            "port": 8000,
        }
    ]
