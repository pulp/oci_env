#!/bin/bash

declare PROJECT="$1"

set -e

cd "/src/$PROJECT/"

echo "Setting up venv for testing"
if [ -n ${CLEAN_VENV} ]; then
    # Clean up the venv only if the caller exported CLEAN_VENV
    # If following TDD practices, cleaning up by default will
    # waste a lot of time.
    VENVPATH=$(mktemp -d /tmp/gng_testing_XXXX)
    rm -rf $VENVPATH
    trap "rm -rf $VENVPATH" EXIT
else
    # Use a consistent path and don't clean up so that tests
    # can run quickly and repeatedly per TDD.
    VENVPATH=/tmp/gng_testing
fi

PIP=${VENVPATH}/bin/pip
if [[ ! -d $VENVPATH ]]; then
    python3 -m venv $VENVPATH
    $PIP install --retries=0 --verbose --upgrade pip wheel
fi
source $VENVPATH/bin/activate
echo "PYTHON: $(which python)"
pip install -r integration_requirements.txt
pip show epdb || pip install epdb

echo "Setting up test data"
pulpcore-manager shell < dev/common/setup_test_data.py

echo "Setting config vars"
API_PREFIX=$(dynaconf get GALAXY_API_PATH_PREFIX)
export HUB_API_ROOT="${API_PROTOCOL}://${API_HOST}:${API_PORT}${API_PREFIX}"

echo "Starting pytest"
pytest \
    --capture=no \
    -m "not cloud_only and not community_only and not rbac_roles" \
    -v $@ \
    --ignore=galaxy_ng/tests/unit \
    --ignore=galaxy_ng/tests/functional \
    galaxy_ng/tests/integration
RC=$?
exit $RC
