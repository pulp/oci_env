#!/bin/bash

declare PROJECT=$1

set -e

source /src/${COMPOSE_PROJECT_NAME}/base/container_scripts/configure_pulp_smash.sh

cd /src/$PROJECT/

PULP_DATABASES__default__USER=postgres pytest -r sx --color=yes --pyargs $PROJECT.tests.unit ${@:2}