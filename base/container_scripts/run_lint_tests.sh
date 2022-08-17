#!/bin/bash

declare PROJECT=$1

set -e

export XDG_CONFIG_HOME=/opt/scripts/

cd /src/$PROJECT/

black --check --diff .

if [[ -f flake8.cfg ]];
then
    flake8 --config flake8.cfg $PROJECT
else
    flake8
fi

[ ! -x .ci/scripts/extra_linting.sh ] || .ci/scripts/extra_linting.sh
