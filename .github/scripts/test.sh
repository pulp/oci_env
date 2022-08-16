#!/bin/bash

# set -e

oci-env compose build
oci-env compose up -d

sleep 100

oci-env generate-client -i
oci-env test -i -p pulp_file functional
oci-env test -p pulp_file functional -k test_generic_list

oci-env compose logs