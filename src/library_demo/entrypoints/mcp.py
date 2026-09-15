import logging
import os
from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastmcp import FastMCP
from fastmcp.exceptions import ToolError
from pydantic import BeforeValidator

from library_demo.adapters.graphdb.client import GraphDBClient, GraphDBClientError
from library_demo.adapters.rdf.jsonld_mapper import map_overdue_loans
from library_demo.models.overdue_loans_result import OverdueLoansResult
from library_demo.services.overdue_loans import get_overdue_loans as get_overdue_loans_service
from library_demo.services.ports import GraphConstructor, GraphResultMapper


LOGGER = logging.getLogger(__name__)
MCP_SERVER_NAME = "library-demo"
OVERDUE_LOANS_TOOL_NAME = "get_overdue_loans"
MCP_TRANSPORT = "streamable-http"
MCP_HOST = "0.0.0.0"
MCP_PORT = 8000
GRAPHDB_ENDPOINT_ENVIRONMENT_VARIABLE = "GRAPHDB_ENDPOINT"
SERVICE_UNAVAILABLE_MESSAGE = "The overdue-loans service is unavailable."
UTC_SUFFIX = " UTC"
UTC_ISO_OFFSET = "+00:00"


def _parse_langflow_utc_datetime(value: object) -> object:
    """Translate Langflow's terminal UTC suffix before Pydantic parses the datetime."""
    if isinstance(value, str) and value.endswith(UTC_SUFFIX):
        return f"{value.removesuffix(UTC_SUFFIX)}{UTC_ISO_OFFSET}"
    return value


AsOfDateTime = Annotated[datetime, BeforeValidator(_parse_langflow_utc_datetime)]


def create_mcp_server(
    *, graph_client: GraphConstructor, result_mapper: GraphResultMapper
) -> FastMCP:
    """Create the MCP server with the supplied overdue-loan collaborators."""
    server = FastMCP(MCP_SERVER_NAME)

    @server.tool(name=OVERDUE_LOANS_TOOL_NAME)
    def get_overdue_loans(
        library_name: str, as_of: AsOfDateTime | None = None
    ) -> OverdueLoansResult:
        """Retrieve overdue loans held by a library at an optional UTC instant."""
        if as_of is not None and as_of.utcoffset() == timedelta(0):
            as_of = as_of.astimezone(timezone.utc)
        try:
            return get_overdue_loans_service(
                library_name,
                as_of,
                graph_client=graph_client,
                result_mapper=result_mapper,
            )
        except GraphDBClientError as error:
            LOGGER.exception(
                "GraphDB unavailable while retrieving overdue loans",
                extra={"mcp_tool": OVERDUE_LOANS_TOOL_NAME},
            )
            raise ToolError(SERVICE_UNAVAILABLE_MESSAGE) from error

    return server


def create_production_mcp_server() -> FastMCP:
    """Create the MCP server with its GraphDB and RDF adapter implementations."""
    endpoint = os.environ[GRAPHDB_ENDPOINT_ENVIRONMENT_VARIABLE]
    return create_mcp_server(
        graph_client=GraphDBClient(endpoint),
        result_mapper=map_overdue_loans,
    )


def main() -> None:
    """Run the Streamable HTTP MCP server for the container runtime."""
    create_production_mcp_server().run(
        transport=MCP_TRANSPORT,
        host=MCP_HOST,
        port=MCP_PORT,
    )
