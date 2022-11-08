#!/bin/bash

# This script is used to test the SFTP profile functionality of the OCI CLI.
# It is intended to be run from the OCI CLI's test suite.
# If you want to run this script locally, run it from the oci_env base directiory with the '--local' option.

set -eu

CONTAINER_RUNTIME="${TEST:-podman}"

ENV_FILE=""
if [ "$(pwd | cut -d'/' -f5)" = "oci_env" ]; then
	ENV_FILE="oci_env/"
fi
ENV_FILE="${ENV_FILE}.github/assets/test_scripts/sftp_${CONTAINER_RUNTIME}.env"

oci-env -e $ENV_FILE compose build
oci-env -e $ENV_FILE compose up -d

oci-env -e $ENV_FILE poll --wait 15 --attempts 30

oci-env -e $ENV_FILE pulp file content upload --file "dev_requirements.txt" --relative-path "dev_requirements.txt"

oci-env -e $ENV_FILE compose down
