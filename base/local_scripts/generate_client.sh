#!/bin/bash

set -e

declare PROJECT=$1

if [ ! -d "../pulp-openapi-generator/" ] 
then
    echo "Please clone github.com/pulp/pulp-openapi-generator into ../pulp-openapi-generator/"
    exit 1
fi

echo "Generating client for ${PROJECT}."

cd ../pulp-openapi-generator/

export PULP_URL=${API_PROTOCOL}://${API_HOST}:${API_PORT}

if [ $COMPOSE_BINARY = "podman-compose" ]
then

    CONTAINER_LABEL=$(podman container inspect ${COMPOSE_PROJECT_NAME}_pulp_1 | jq -r ".[0].ProcessLabel")
    export PULP_MCS_LABEL=${CONTAINER_LABEL#'system_u:system_r:container_t:'}

    CONTAINER_LABEL=$(podman container inspect ${COMPOSE_PROJECT_NAME}_pulp_1 | jq -r ".[0].ProcessLabel")
    export PULP_MCS_LABEL=${CONTAINER_LABEL#'system_u:system_r:container_t:'}

fi

./generate.sh $PROJECT python
