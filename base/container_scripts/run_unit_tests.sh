#!/bin/bash

declare PACKAGE="$1"
declare PROJECT="${PACKAGE//-/_}"

set -e

source "/opt/oci_env/base/container_scripts/configure_pulp_smash.sh"

cd "/src/$PACKAGE/"

sudo -u pulp -E PULP_DATABASES__default__USER=postgres pytest -r sx --color=yes --pyargs "$PROJECT.tests.unit" "${@:2}"
