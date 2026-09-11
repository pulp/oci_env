#!/bin/bash

set -e

declare PROJECT=$1
declare LANGUAGE=$2
declare CONTAINER_NAME=$3  # e.g, oci_env_pulp_1
declare API_VERSION="${4:-v3}" # e.g. v3
echo "generate_client ${API_VERSION}"

if [ ! -d "${SRC_DIR}/pulp-openapi-generator/" ]
then
    echo "Please clone github.com/pulp/pulp-openapi-generator into ${SRC_DIR}/pulp-openapi-generator/"
    exit 1
fi

echo "Generating ${LANGUAGE}-client for ${PROJECT}."

cd "${SRC_DIR}/pulp-openapi-generator/"

export PULP_URL="${API_PROTOCOL}://${API_HOST}:${API_PORT}"


CONTAINER_LABEL=$("${COMPOSE_BINARY}" container inspect "${CONTAINER_NAME}" | jq -r ".[0].ProcessLabel")
export PULP_MCS_LABEL="${CONTAINER_LABEL#'system_u:system_r:container_t:'}"

if [ -x ./gen-client.sh ]
then
    if [ "${PROJECT}" = "pulpcore" ]
    then
        COMPONENT="core"
    else
        COMPONENT="${PROJECT#pulp_}"
    fi

    API_SPEC="$(mktemp "${PWD}/api-spec.XXXXXX.json")"
    cleanup() {
        rm -f "${API_SPEC}"
    }
    trap cleanup EXIT

    API_ROOT="${PULP_API_ROOT:-/pulp/}"
    API_ROOT="/${API_ROOT#/}"
    API_ROOT="${API_ROOT%/}/"
    API_URL="${API_PROTOCOL}://${API_HOST}:${API_PORT}${API_ROOT}api/${API_VERSION}/"
    echo "retrieving api.json for version ${API_VERSION}"
    RETRY_COUNT=0
    until curl --fail-with-body -k -o "${API_SPEC}" \
        "${API_URL}docs/api.json?bindings&component=${COMPONENT}"
    do
        if [ "${RETRY_COUNT}" -eq 10 ]
        then
            exit 1
        fi
        sleep 2
        RETRY_COUNT=$((RETRY_COUNT + 1))
    done

    ./gen-client.sh "${API_SPEC}" "${COMPONENT}" "${LANGUAGE}" "${PROJECT}"
elif [ -x ./generate.sh ]
then
    ./generate.sh "${PROJECT}" "${LANGUAGE}" "${API_VERSION}"
else
    echo "pulp-openapi-generator must provide gen-client.sh or generate.sh" >&2
    exit 1
fi
