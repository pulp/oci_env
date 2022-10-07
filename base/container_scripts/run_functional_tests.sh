#!/bin/bash

declare PROJECT="$1"

set -e

source "/opt/oci_env/base/container_scripts/configure_pulp_smash.sh"

cd "/src/$PROJECT/"

sudo -u pulp -E pytest -r sx --rootdir=/var/lib/pulp --color=yes --pyargs "$PROJECT.tests.functional" "${@:2}"
