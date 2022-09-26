#!/bin/bash

declare PROJECT="$1"

set -e

cd "/src/$PROJECT/"

echo "Setting up venv for testing"
VENVPATH=/tmp/gng_testing
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
export HUB_API_ROOT="http://localhost:5001/api/galaxy/"

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
