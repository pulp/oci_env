#!/bin/bash

# the operation will error out unless all services are stopped
ls /var/run/s6/services | egrep ^pulp | xargs -I {} s6-svc -d /var/run/s6/services/{}

# wipe the database non-interactive
yes yes | pulpcore-manager reset_db --user postgres
