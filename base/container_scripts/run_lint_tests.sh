#!/bin/bash

declare PACKAGE="$1"

if [ $PACKAGE == "pulp_file" ]
then
    declare PACKAGE="pulpcore"
fi

declare PROJECT="${PACKAGE//-/_}"

set -e

export XDG_CONFIG_HOME=/opt/scripts/

cd "/src/$PACKAGE/"

black --check --diff .

if [[ -f flake8.cfg ]];
then
    flake8 --config flake8.cfg "$PROJECT"
else
    flake8
fi

[ ! -x .ci/scripts/extra_linting.sh ] || .ci/scripts/extra_linting.sh
