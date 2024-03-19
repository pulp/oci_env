#!/bin/bash

set -e

declare PROJECT=$1

if [ $PROJECT == "pulp_file" ]
then
    declare PROJECT="pulpcore"
fi

if [ ! -d "/src/$PROJECT/" ]
then
    echo "Please clone $PROJECT into ../$PROJECT/"
    exit 1
fi

# pip3 install git+https://github.com/pulp/pulp-smash.git
pip install git+https://github.com/pulp/pulp-smash.git

cd "/src/$PROJECT/"

if [[ -f unittest_requirements.txt ]]; then
    # pip3 install -r unittest_requirements.txt
    pip install -r unittest_requirements.txt
fi
