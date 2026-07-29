#!/bin/bash

declare PACKAGE="$1"
declare PROJECT="${PACKAGE//-/_}"

set -e

if [[ ${PACKAGE} == "pulp_file" || ${PACKAGE} == "pulp_certguard" ]]
then
    declare PACKAGE="pulpcore"
fi

cd "/src/${PACKAGE}/"

function check_pytest () {
    sudo -u pulp -E type pytest || {
        cat << EOF

ERROR: pytest is not installed

This usually means the functional test requirements failed to install. Check that
functest_requirements.txt exists for the plugin and that "oci-env test -p PLUGIN
functional" completed the install step successfully.
EOF
        exit 1
    }
}

function check_client () {
    sudo -u pulp -E python3 -c "import pulpcore.client.${PROJECT}" || {
        cat << EOF

ERROR: pulpcore.client.${PROJECT} is missing.

This usually means you did not run "oci-env generate-client ${PROJECT}" before
running the functional test command.
EOF
        exit 1
    }
}

check_pytest
check_client

sudo -u pulp -E pytest -r sx --rootdir=/var/lib/pulp --color=yes --pyargs "${PROJECT}.tests.functional" "${@:2}"
