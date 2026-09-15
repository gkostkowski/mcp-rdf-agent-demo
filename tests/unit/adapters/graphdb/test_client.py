from unittest.mock import Mock, patch

import pytest
from SPARQLWrapper import RDFXML
from SPARQLWrapper.SPARQLExceptions import SPARQLWrapperException
from rdflib import Graph

from library_demo.adapters.graphdb.client import GraphDBClient, GraphDBClientError


ENDPOINT_URL = "http://graphdb.example.test/repositories/library"
CONSTRUCT_QUERY = "CONSTRUCT { ?subject ?predicate ?object } WHERE { ?subject ?predicate ?object }"


@patch("library_demo.adapters.graphdb.client.SPARQLWrapper")
def test_construct_executes_the_supplied_query_and_returns_its_graph(
    sparql_wrapper: Mock,
) -> None:
    expected_graph = Graph()
    wrapper = sparql_wrapper.return_value
    wrapper.queryAndConvert.return_value = expected_graph

    result = GraphDBClient(ENDPOINT_URL).construct(CONSTRUCT_QUERY)

    assert result is expected_graph
    sparql_wrapper.assert_called_once_with(ENDPOINT_URL)
    wrapper.setQuery.assert_called_once_with(CONSTRUCT_QUERY)
    wrapper.setReturnFormat.assert_called_once_with(RDFXML)


@patch("library_demo.adapters.graphdb.client.SPARQLWrapper")
def test_construct_wraps_sparqlwrapper_failures(sparql_wrapper: Mock) -> None:
    wrapper = sparql_wrapper.return_value
    wrapper.queryAndConvert.side_effect = SPARQLWrapperException("GraphDB is unavailable")

    with pytest.raises(GraphDBClientError, match="GraphDB is unavailable"):
        GraphDBClient(ENDPOINT_URL).construct(CONSTRUCT_QUERY)


@patch("library_demo.adapters.graphdb.client.SPARQLWrapper")
def test_construct_wraps_transport_failures_with_the_original_cause(
    sparql_wrapper: Mock,
) -> None:
    wrapper = sparql_wrapper.return_value
    transport_error = OSError("Connection refused")
    wrapper.queryAndConvert.side_effect = transport_error

    with pytest.raises(GraphDBClientError, match="Connection refused") as error:
        GraphDBClient(ENDPOINT_URL).construct(CONSTRUCT_QUERY)

    assert error.value.__cause__ is transport_error


@patch("library_demo.adapters.graphdb.client.SPARQLWrapper")
def test_construct_rejects_non_graph_conversion_results(sparql_wrapper: Mock) -> None:
    wrapper = sparql_wrapper.return_value
    wrapper.queryAndConvert.return_value = {"results": {}}

    with pytest.raises(GraphDBClientError, match="rdflib.Graph"):
        GraphDBClient(ENDPOINT_URL).construct(CONSTRUCT_QUERY)
