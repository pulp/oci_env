#!/bin/bash

declare FILENAME="$1"

set -e

mkdir -p /opt/oci_env/db_back/

echo "dumping database to /var/lib/pulp"
pg_dump -U pulp -F c -b -f "/var/lib/pulp/pulp_db.backup" 

echo "archiving /var/lib/pulp to $FILENAME.tar.gz"
tar -czf /opt/oci_env/db_back/$FILENAME.tar.gz -C /var/lib/pulp .