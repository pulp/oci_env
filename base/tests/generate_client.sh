#!/bin/bash

set -e

declare PROJECT=$1

if [ ! -d "../pulp-openapi-generator/" ] 
then
    echo "Please clone github.com/pulp/pulp-openapi-generator into ../pulp-openapi-generator/"
    exit 1
fi

cd ../pulp-openapi-generator/

export PULP_URL=http://localhost:5001
# export PULP_API_ROOT=/pulp/api/v3/

./generate.sh $PROJECT python
