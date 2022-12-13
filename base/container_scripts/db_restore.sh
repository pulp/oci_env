#!/bin/bash
set -eu

declare FILENAME="$1"

# stop pulp services
SERVICES=$(s6-rc -a list | grep -E ^pulp)
echo "$SERVICES" | xargs -I {} s6-rc -d change {}

echo "extracting $FILENAME.tar.gz to /var/lib/pulp"
tar --overwrite -xzf /opt/oci_env/db_backup/$FILENAME.tar.gz -C /var/lib/pulp/

echo "restoring database"
pg_restore --clean -U pulp -d pulp "/var/lib/pulp/pulp_db.backup"

# restart the servicees
echo "$SERVICES" | xargs -I {} s6-rc -u change {}
s6-rc -u change nginx