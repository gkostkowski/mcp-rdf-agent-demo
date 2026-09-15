# Local Infrastructure

`docker-compose.yaml` defines the local services. GraphDB data lives in the
Compose-managed `graphdb-data` volume; it is not stored in the working tree.

GraphDB 11.5.0 requires a license. Request a GraphDB Free license and place it
at `infra/graphdb/graphdb.license`. This path is ignored by Git and is mounted
read-only into GraphDB; do not commit or share the license file.

Start GraphDB and open Workbench at <http://127.0.0.1:7200>:

```bash
make up
```

Load the version-controlled sources into a fresh `library-demo` repository:

```bash
make graphdb-load
```

This command deletes the complete repository before recreating it. It places
`vocab/ontology/library_full.owl` and `vocab/library-cv.ttl` in
`http://library-demo.com/graph/vocab`, and `data/library-xs.ttl` in
`http://library-demo.com/graph/data`. Normal service restarts do not reload
data.

Check the running repository after loading:

```bash
make graphdb-smoke
```

Stop services with `make down`. `make down-volumes` is destructive and removes
the persisted GraphDB data volume after confirmation.
