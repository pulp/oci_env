#!/bin/bash

declare PACKAGE="$1"

if [[ $PACKAGE == "pulp_file" || ${PACKAGE} == "pulp_certguard" ]]
then
    declare PACKAGE="pulpcore"
fi

set -e

export XDG_CONFIG_HOME=/opt/scripts/

cd "/src/$PACKAGE/"

black --check --diff .

if [[ -f flake8.cfg ]];
then
    flake8 --config flake8.cfg "${PACKAGE}"
else
    flake8
fi

[ ! -x .ci/scripts/extra_linting.sh ] || .ci/scripts/extra_linting.sh
