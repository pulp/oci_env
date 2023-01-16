#!/bin/bash
set -e

# stop pulp services
SERVICES=$(s6-rc -a list | grep -E ^pulp)
echo "$SERVICES" | xargs -I {} s6-rc -d change {}

# reset the db and run migrations
dropdb --user postgres pulp
dropuser --user postgres pulp
/etc/init/postgres-prepare

# restart the servicees
echo "$SERVICES" | xargs -I {} s6-rc -u change {}
s6-rc -u change nginx
bash /utils.sh run_profile_init_scripts
