#!/bin/bash

declare PACKAGE="$1"

if [ $PACKAGE == "pulp_file" ]
then
    declare PACKAGE="pulpcore"
fi

declare PROJECT="${PACKAGE//-/_}"

set -e

cd "/src/$PACKAGE/"

sudo -u pulp -E PULP_DATABASES__default__USER=postgres pytest -r sx --color=yes --pyargs "$PROJECT.tests.unit" "${@:2}"
