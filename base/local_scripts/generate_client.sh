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

./generate.sh $PROJECT python
