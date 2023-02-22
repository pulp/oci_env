#!/bin/bash
set -eu

declare FILENAME="$1"
declare MIGRATE="${2-0}"

# stop pulp services
SERVICES=$(s6-rc -a list | grep -E ^pulp)
echo "$SERVICES" | xargs -I {} s6-rc -d change {}

echo "extracting $FILENAME.tar.gz to /var/lib/pulp"
tar --overwrite -xzf /opt/oci_env/db_backup/$FILENAME.tar.gz -C /var/lib/pulp/

# older backups don't have the certs dir
if [ -d "/var/lib/pulp/certs/" ] 
then
    echo "restoring /etc/pulp/certs"
    rm -rf /etc/pulp/certs/
    mv /var/lib/pulp/certs/ /etc/pulp/certs/
    chown -R pulp:pulp  /etc/pulp/certs/
fi


echo "restoring database"

# pg_restore --clean doesn't work with postgres extensions
dropdb --user postgres pulp
su postgres -c "createdb --encoding=utf-8 --locale=en_US.UTF-8 -T template0 -O pulp pulp"
pg_restore -U pulp -d pulp "/var/lib/pulp/pulp_db.backup"

if [[ "$MIGRATE" -eq "1" ]]; then
    pulpcore-manager migrate
fi

# restart the servicees
echo "$SERVICES" | xargs -I {} s6-rc -u change {}
s6-rc -u change nginx