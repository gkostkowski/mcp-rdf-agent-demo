from datetime import datetime, timezone
from unittest.mock import Mock, call, patch

import pytest
from SPARQLWrapper import RDFXML
from SPARQLWrapper.SPARQLExceptions import SPARQLWrapperException
from rdflib import Graph, Literal

from library_demo.adapters.graphdb.client import GraphDBClient, GraphDBClientError


ENDPOINT_URL = "http://graphdb.example.test/repositories/library"
CONSTRUCT_QUERY = "CONSTRUCT { ?subject ?predicate ?object } WHERE { ?subject ?predicate ?object }"
LIBRARY_NAME = "Central Library"
AS_OF = datetime(2026, 9, 1, 12, tzinfo=timezone.utc)
BINDINGS = {"library_name": LIBRARY_NAME, "as_of": AS_OF}
INJECTION_LIKE_LIBRARY_NAME = 'Central Library" } UNION { ?subject ?predicate ?object'


@patch("library_demo.adapters.graphdb.client.SPARQLWrapper")
def test_construct_executes_the_supplied_query_and_returns_its_graph(
    sparql_wrapper: Mock,
) -> None:
    expected_graph = Graph()
    wrapper = sparql_wrapper.return_value
    wrapper.queryAndConvert.return_value = expected_graph

    result = GraphDBClient(ENDPOINT_URL).construct(CONSTRUCT_QUERY, BINDINGS)

    assert result is expected_graph
    sparql_wrapper.assert_called_once_with(ENDPOINT_URL)
    wrapper.setQuery.assert_called_once_with(CONSTRUCT_QUERY)
    wrapper.addParameter.assert_has_calls(
        [
            call("$library_name", Literal(LIBRARY_NAME).n3()),
            call("$as_of", Literal(AS_OF).n3()),
        ]
    )
    wrapper.setReturnFormat.assert_called_once_with(RDFXML)


@patch("library_demo.adapters.graphdb.client.SPARQLWrapper")
def test_construct_wraps_sparqlwrapper_failures(sparql_wrapper: Mock) -> None:
    wrapper = sparql_wrapper.return_value
    wrapper.queryAndConvert.side_effect = SPARQLWrapperException("GraphDB is unavailable")

    with pytest.raises(GraphDBClientError, match="GraphDB is unavailable"):
        GraphDBClient(ENDPOINT_URL).construct(CONSTRUCT_QUERY, BINDINGS)


@patch("library_demo.adapters.graphdb.client.SPARQLWrapper")
def test_construct_wraps_transport_failures_with_the_original_cause(
    sparql_wrapper: Mock,
) -> None:
    wrapper = sparql_wrapper.return_value
    transport_error = OSError("Connection refused")
    wrapper.queryAndConvert.side_effect = transport_error

    with pytest.raises(GraphDBClientError, match="Connection refused") as error:
        GraphDBClient(ENDPOINT_URL).construct(CONSTRUCT_QUERY, BINDINGS)

    assert error.value.__cause__ is transport_error


@patch("library_demo.adapters.graphdb.client.SPARQLWrapper")
def test_construct_rejects_non_graph_conversion_results(sparql_wrapper: Mock) -> None:
    wrapper = sparql_wrapper.return_value
    wrapper.queryAndConvert.return_value = {"results": {}}

    with pytest.raises(GraphDBClientError, match="rdflib.Graph"):
        GraphDBClient(ENDPOINT_URL).construct(CONSTRUCT_QUERY, BINDINGS)


@patch("library_demo.adapters.graphdb.client.SPARQLWrapper")
def test_construct_binds_injection_like_library_name_as_a_single_rdf_literal(
    sparql_wrapper: Mock,
) -> None:
    wrapper = sparql_wrapper.return_value
    wrapper.queryAndConvert.return_value = Graph()

    GraphDBClient(ENDPOINT_URL).construct(
        CONSTRUCT_QUERY, {"library_name": INJECTION_LIKE_LIBRARY_NAME}
    )

    wrapper.addParameter.assert_called_once_with(
        "$library_name", Literal(INJECTION_LIKE_LIBRARY_NAME).n3()
    )
