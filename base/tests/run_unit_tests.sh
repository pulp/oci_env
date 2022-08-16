#!/bin/bash

declare PROJECT=$1

set -e

export XDG_CONFIG_HOME=/opt/settings/

cd /src/oci_env/
source ./config_loader.sh

mkdir -p /opt/settings/pulp_smash/

cat > /opt/settings/pulp_smash/settings.json <<EOF
{
  "hosts": [
    {
      "hostname": "${API_HOST}",
      "roles": {
        "api": {
          "port": ${API_PORT},
          "scheme": "${API_PROTOCOL}",
          "service": "nginx",
          "verify": false
        },
        "content": {
          "port": ${API_PORT},
          "scheme": "${API_PROTOCOL}",
          "service": "pulp_content_app",
          "verify": false
        },
        "pulp resource manager": {},
        "pulp workers": {},
        "redis": {},
        "shell": {
          "transport": "local"
        }
      }
    }
  ],
  "pulp": {
    "auth": [
      "${DJANGO_SUPERUSER_USERNAME}",
      "${DJANGO_SUPERUSER_PASSWORD}"
    ],
    "selinux enabled": false,
    "version": "3"
  }
}
EOF

cd /src/$PROJECT/

# django test creates a new temporary database so this
# permission is required to avoid an error
psql -U postgres -c 'ALTER USER pulp CREATEDB;'

pulpcore-manager test -v3 $PROJECT.tests.unit.${@:2}
