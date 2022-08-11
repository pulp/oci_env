#!/bin/bash

set -e

declare PROJECT=$1

cd /src/pulp-openapi-generator/$PROJECT-client

pip install -e .