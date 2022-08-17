#!/bin/bash

declare PROJECT=$1

set -e

source /src/${OCI_ENV_DIRECTORY}/base/container_scripts/configure_pulp_smash.sh

cd /src/$PROJECT/

pytest -r sx --color=yes --pyargs $PROJECT.tests.functional ${@:2}
