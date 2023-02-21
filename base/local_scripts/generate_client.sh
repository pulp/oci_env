#!/bin/bash

set -e

declare PROJECT=$1
declare LANGUAGE=$2

if [ ! -d "${SRC_DIR}/pulp-openapi-generator/" ]
then
    echo "Please clone github.com/pulp/pulp-openapi-generator into ${pwd}/pulp-openapi-generator/"
    exit 1
fi

echo "Generating ${LANGUAGE}-client for ${PROJECT}."

cd ${SRC_DIR}/pulp-openapi-generator/

export PULP_URL=${API_PROTOCOL}://${API_HOST}:${API_PORT}


CONTAINER_LABEL=$(${COMPOSE_BINARY} container inspect ${COMPOSE_PROJECT_NAME}_pulp_1 | jq -r ".[0].ProcessLabel")
export PULP_MCS_LABEL=${CONTAINER_LABEL#'system_u:system_r:container_t:'}

./generate.sh $PROJECT $LANGUAGE
