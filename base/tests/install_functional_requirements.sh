#!/bin/bash

set -e

declare PROJECT=$1

if [ ! -d "/src/$PROJECT/" ] 
then
    echo "Please clone $PROJECT into ../$PROJECT/"
    exit 1
fi

cd /src/$PROJECT/

pip install -e .
pip install -r functest_requirements.txt

cd /src/pulp-openapi-generator/$PROJECT-client

pip install -e .