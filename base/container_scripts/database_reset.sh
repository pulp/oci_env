#!/bin/bash

# stop pulp services
SERVICES=$(s6-rc -a list | grep -E ^pulp)
echo "$SERVICES" | xargs -I {} s6-rc -d change {}

# reset the db and run migrations
pulpcore-manager reset_db --no-input --user postgres
/etc/init/postgres-prepare

# restart the servicees
echo "$SERVICES" | xargs -I {} s6-rc -u change {}
s6-rc -u change nginx
bash /src/oci_env/.compiled/init.sh
