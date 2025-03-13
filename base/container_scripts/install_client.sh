#!/bin/bash

set -e

declare PROJECT="$1"

cd "/src/pulp-openapi-generator/$PROJECT-client"

# Editable installs are currently broken for the new client
pip install .
