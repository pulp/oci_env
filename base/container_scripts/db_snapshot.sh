#!/bin/bash

declare FILENAME="$1"

set -e

mkdir -p /opt/oci_env/db_backup/

echo "dumping database to /var/lib/pulp"
pg_dump -U pulp -F c -b -f "/var/lib/pulp/pulp_db.backup"

echo "backing up /etc/pulp/certs"
rm -rf /var/lib/pulp/certs/ || true
cp -r /etc/pulp/certs/ /var/lib/pulp/certs/

echo "archiving /var/lib/pulp to $FILENAME.tar.gz"
tar -czf /opt/oci_env/db_backup/$FILENAME.tar.gz -C /var/lib/pulp .