#!/bin/bash

declare PACKAGE="$1"

if [[ $PACKAGE == "pulp_file" || ${PACKAGE} == "pulp_certguard" ]]
then
    declare PACKAGE="pulpcore"
fi

set -e

export XDG_CONFIG_HOME=/opt/scripts/

cd "/src/$PACKAGE/"

ruff format --check --diff
ruff check

[ ! -x .ci/scripts/extra_linting.sh ] || .ci/scripts/extra_linting.sh
