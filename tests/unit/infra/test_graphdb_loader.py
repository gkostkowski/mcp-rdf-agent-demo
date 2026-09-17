from pathlib import Path


ROOT = Path(__file__).parents[3]
LOADER_SCRIPT = ROOT / "infra/graphdb/load-graphdb.sh"
ONTOLOGY_FILE = ROOT / "vocab/ontology/library.ttl"
ONTOLOGY_IRI = "http://library-demo.com/ontology#core"


def test_graphdb_loader_uses_the_tracked_core_ontology() -> None:
    loader = LOADER_SCRIPT.read_text(encoding="utf-8")

    assert ONTOLOGY_FILE.is_file()
    assert 'readonly ONTOLOGY_FILE="vocab/ontology/library.ttl"' in loader
    assert ONTOLOGY_IRI in loader
