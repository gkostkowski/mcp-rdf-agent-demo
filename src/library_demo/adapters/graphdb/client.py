from rdflib import Graph
from SPARQLWrapper import RDFXML, SPARQLWrapper


class GraphDBClientError(Exception):
    """Raised when GraphDB cannot return an RDF graph for a CONSTRUCT query."""


class GraphDBClient:
    def __init__(self, endpoint_url: str) -> None:
        self._endpoint_url = endpoint_url

    def construct(self, query: str) -> Graph:
        try:
            client = SPARQLWrapper(self._endpoint_url)
            client.setQuery(query)
            client.setReturnFormat(RDFXML)
            result = client.queryAndConvert()
        except Exception as error:
            raise GraphDBClientError(str(error)) from error

        if not isinstance(result, Graph):
            raise GraphDBClientError("GraphDB CONSTRUCT result was not an rdflib.Graph")

        return result
