#!/bin/bash

declare PROJECT=$1

set -e

export XDG_CONFIG_HOME=/src/oci_env/base/tests/

cd /src/$PROJECT/

black --check --diff .
flake8 --config flake8.cfg
[ ! -x .ci/scripts/extra_linting.sh ] || .ci/scripts/extra_linting.sh
