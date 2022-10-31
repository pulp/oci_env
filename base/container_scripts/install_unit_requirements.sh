#!/bin/bash

set -e

declare PROJECT=$1

if [ ! -d "/src/$PROJECT/" ]
then
    echo "Please clone $PROJECT into ../$PROJECT/"
    exit 1
fi

pip install git+https://github.com/pulp/pulp-smash.git

cd "/src/$PROJECT/"

if [[ -f unittest_requirements.txt ]]; then
    pip install -r unittest_requirements.txt
fi
