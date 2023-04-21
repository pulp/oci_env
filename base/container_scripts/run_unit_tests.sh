#!/bin/bash

declare PACKAGE="$1"
declare PROJECT="${PACKAGE//-/_}"

set -e

function check_test () {
   [[ -d "${PROJECT}/tests/unit" ]] || {
       echo "Skipping unit tests because they do not seem to exist..."
       pwd
       exit 0
   }
}

source "/opt/oci_env/base/container_scripts/configure_pulp_smash.sh"

cd "/src/$PACKAGE/"

check_test

sudo -u pulp -E PULP_DATABASES__default__USER=postgres pytest -r sx --color=yes --pyargs "$PROJECT.tests.unit" "${@:2}"
