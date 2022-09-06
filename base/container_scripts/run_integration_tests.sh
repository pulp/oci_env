#!/bin/bash

declare PROJECT=$1
declare MODE=$2
declare TEST=$3
declare BUILD=$4

CONTENTAPPROVAL=$(cat /src/oci_env/.compose.env | grep PULP_GALAXY_REQUIRE_CONTENT_APPROVAL) 
if [[ $CONTENTAPPROVAL != "PULP_GALAXY_REQUIRE_CONTENT_APPROVAL=true" ]]; then
    echo "The integration tests will not run correctly unless you set PULP_GALAXY_REQUIRE_CONTENT_APPROVAL=true"
    exit 1
fi

export HUB_USE_MOVE_ENDPOINT="true"
export HUB_API_ROOT=http://localhost:5001/api/automation-hub/

source /src/${OCI_ENV_DIRECTORY}/base/container_scripts/configure_pulp_smash.sh

# Stop pulp services
SERVICES=$(s6-rc -a list | egrep ^pulp)
echo "$SERVICES" | xargs -I {} s6-rc -d change {}

# Reset db and run migrations
yes yes | pulpcore-manager reset_db --user postgres
/etc/init/postgres-prepare

# Restart services
echo "$SERVICES" | xargs -I {} s6-rc -u change {}
s6-rc -u change nginx

# Load data
pulpcore-manager shell_plus < src/$PROJECT/dev/common/setup_test_data.py

cd /src/$PROJECT/

test_settings=$(case $MODE in
    (standalone) echo "not cloud_only and not community_only and not rbac_roles";;
    (standalone-rbac) echo "rbac_roles";;
    (standalone-community) echo "community_only";;
    (standalone-ldap) echo "standalone_only and ldap";;
    (insights) echo "not standalone_only and not community_only and not rbac_roles";;
esac)

if [[ $TEST != "" ]]; then # specific test
    pytest --capture=no -k "$TEST" -v galaxy_ng/tests/integration
elif [[ $BUILD != "" ]]; then # galaxy_ng build (standalone, standalone-rbac, standalone-community, standalone-ldap, insights)
    pytest --capture=no -m "$test_settings" -v galaxy_ng/tests/integration
elif [[ $MODE != "" ]]; then # run tests with mark decorator (-m)
    pytest --capture=no -m "$MODE" -v galaxy_ng/tests/integration
else 
    pytest --capture=no -v galaxy_ng/tests/integration
fi
