#!/bin/bash

declare PACKAGE="$1"
declare PROJECT="${PACKAGE//-/_}"

set -e

function check_pytest () {
    sudo -u pulp -E type pytest || {
        cat << EOF

ERROR: pytest is not installed

This usually means you did not include the "-i" flag with the oci-env "test"
subcommand. The first invocation of functional tests needs "-i" to install the
test requirements (inc. pytest). After the requirements are installed, "-i" can
be dropped from further runs on the same container instance.
EOF
        exit 1
    }
}

function check_client () {
    sudo -u pulp -E python3 -c "import pulpcore.client.${PROJECT}" || {
        cat << EOF

ERROR: pulpcore.client.${PROJECT} is missing.

This usually means you did not run "oci-env generate-client -i ${PROJECT}" before
running the functional test command. It could also mean you did not pass the "-i"
flag to the "generate-client" subcommand which would have created the client, but
not install it into the appropriate location.
EOF
        exit 1
    }
}

source "/opt/oci_env/base/container_scripts/configure_pulp_smash.sh"

cd "/src/$PACKAGE/"

check_pytest
check_client

sudo -u pulp -E pytest -r sx --rootdir=/var/lib/pulp --color=yes --pyargs "$PROJECT.tests.functional" "${@:2}"
