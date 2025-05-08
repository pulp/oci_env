#!/bin/bash

declare PACKAGE="$1"
declare PROJECT="${PACKAGE//-/_}"

if [[ ${PACKAGE} == "pulp_file" || ${PACKAGE} == "pulp_certguard" ]]
then
    declare PACKAGE="pulpcore"
fi

set -e

cd "/src/${PACKAGE}/"

sudo -u pulp -E PULP_DATABASES__default__USER=postgres pytest -r sx --color=yes --pyargs "${PROJECT}.tests.unit" "${@:2}"
