#!/bin/bash

set -e

declare PROJECT="$1"

if [ ! -d "/src/$PROJECT/" ]
then
    echo "Please clone $PROJECT into ../$PROJECT/"
    exit 1
fi

cd "/src/$PROJECT/"

if [[ -f lint_requirements.txt ]]; then
    pip3 install -r lint_requirements.txt
fi
