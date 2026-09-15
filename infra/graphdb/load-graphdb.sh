#!/bin/sh
set -eu

readonly GRAPHDB_URL="${GRAPHDB_URL:-http://graphdb:7200}"
readonly REPOSITORY_ID="${REPOSITORY_ID:-library-demo}"
readonly REPOSITORY_CONFIG="${REPOSITORY_CONFIG:-/config/repository-config.ttl}"
readonly VOCAB_GRAPH="http://library-demo.com/graph/vocab"
readonly DATA_GRAPH="http://library-demo.com/graph/data"
readonly ONTOLOGY_FILE="vocab/ontology/library_full.owl"
readonly VOCABULARY_FILE="vocab/library-cv.ttl"
readonly DATA_FILE="data/library-xs.ttl"
readonly RETRY_COUNT=60
readonly RETRY_DELAY_SECONDS=2

wait_for_graphdb() {
    attempt=1
    while [ "${attempt}" -le "${RETRY_COUNT}" ]; do
        if curl --fail --silent --show-error "${GRAPHDB_URL}/rest/repositories" >/dev/null; then
            return 0
        fi
        attempt=$((attempt + 1))
        sleep "${RETRY_DELAY_SECONDS}"
    done

    printf '%s\n' "GraphDB did not become reachable at ${GRAPHDB_URL}" >&2
    return 1
}

delete_repository() {
    status_code=$(curl --silent --output /dev/null --write-out '%{http_code}' \
        --request DELETE "${GRAPHDB_URL}/rest/repositories/${REPOSITORY_ID}")

    case "${status_code}" in
        200|202|204|404) return 0 ;;
        *)
            printf '%s\n' "Unable to delete repository ${REPOSITORY_ID}: HTTP ${status_code}" >&2
            return 1
            ;;
    esac
}

create_repository() {
    curl --fail-with-body --silent --show-error \
        --request POST "${GRAPHDB_URL}/rest/repositories" \
        --form "config=@${REPOSITORY_CONFIG};type=text/turtle"
}

start_import() {
    file_path="$1"
    graph_iri="$2"
    payload=$(jq --null-input --arg file "${file_path}" --arg context "${graph_iri}" \
        '{fileNames: [$file], importSettings: {context: $context}}')

    curl --fail-with-body --silent --show-error \
        --request POST "${GRAPHDB_URL}/rest/repositories/${REPOSITORY_ID}/import/server" \
        --header 'Content-Type: application/json' \
        --data "${payload}"
}

wait_for_import() {
    file_path="$1"
    attempt=1
    while [ "${attempt}" -le "${RETRY_COUNT}" ]; do
        response=$(curl --fail-with-body --silent --show-error --get \
            --data-urlencode "name=${file_path}" \
            "${GRAPHDB_URL}/rest/repositories/${REPOSITORY_ID}/import/server")
        status=$(printf '%s' "${response}" | jq --raw-output --arg name "${file_path}" \
            '[.[] | select(.name == $name) | .status] | last // empty')

        case "${status}" in
            DONE|done) return 0 ;;
            ERROR|error)
                printf '%s\n' "GraphDB could not import ${file_path}" >&2
                return 1
                ;;
            NONE|PENDING|pending|IMPORTING|importing|INTERRUPTING|interrupting)
                sleep "${RETRY_DELAY_SECONDS}"
                ;;
            *)
                printf '%s\n' "Unexpected import status for ${file_path}: ${status}" >&2
                return 1
                ;;
        esac
        attempt=$((attempt + 1))
    done

    printf '%s\n' "Timed out importing ${file_path}" >&2
    return 1
}

import_file() {
    file_path="$1"
    graph_iri="$2"
    start_import "${file_path}" "${graph_iri}"
    wait_for_import "${file_path}"
}

smoke_check() {
    query='ASK {
      GRAPH <http://library-demo.com/graph/vocab> {
        <http://library-demo.com/ontology> ?ontologyPredicate ?ontologyObject .
        <http://library-demo.com/ontology#BookCopyAvailabilityStatus> ?vocabularyPredicate ?vocabularyObject
      }
      GRAPH <http://library-demo.com/graph/data> { ?dataSubject ?dataPredicate ?dataObject }
    }'
    response=$(curl --fail-with-body --silent --show-error \
        --header 'Accept: application/sparql-results+json' \
        --data-urlencode "query=${query}" \
        "${GRAPHDB_URL}/repositories/${REPOSITORY_ID}")

    printf '%s' "${response}" | jq --exit-status '.boolean == true' >/dev/null
}

load() {
    wait_for_graphdb
    delete_repository
    create_repository
    import_file "${ONTOLOGY_FILE}" "${VOCAB_GRAPH}"
    import_file "${VOCABULARY_FILE}" "${VOCAB_GRAPH}"
    import_file "${DATA_FILE}" "${DATA_GRAPH}"
    smoke_check
}

case "${1:-load}" in
    load) load ;;
    smoke) wait_for_graphdb && smoke_check ;;
    *)
        printf '%s\n' "Usage: graphdb-loader [load|smoke]" >&2
        exit 64
        ;;
esac
