#!/bin/bash

set -x
set -eu

whoami

declare FILENAME="$1"
declare MIGRATE="${2-0}"

# wait until s6-rc is able to lock
set +e
for x in $(seq 1 20); do
    echo "${x} checking if s6-rc -a can make locks ..."
    OUTPUT=$(s6-rc -a list)
    if [ $? -eq 0 ]; then
        echo "s6-rc -a list is ready"
        break
    else
        echo "s6-rc -a list is not ready: $?"
        sleep 1
    fi
done

# now we need to wait till pulp services register
for x in $(seq 1 20); do
    echo "${x} waiting for pulp services to register"
    PULP_SERVICES_COUNT=$(s6-rc -a list | grep -E ^pulp | wc -l)
    if  [ "$PULP_SERVICES_COUNT" -gt 0 ]; then
        echo "found ${PULP_SERVICES_COUNT} total pulp services running, continuing"
        break
    fi
    echo "found ${PULP_SERVICES_COUNT} total pulp services running, waiting"
    sleep 1
done

# turn error breaks back on
set -e

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
