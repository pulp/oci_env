#!/bin/bash

pulpcore-manager createsuperuser --no-input --email admin@example.com || true

if ! pulp --refresh-api status
then
  pulp config create --overwrite --base-url "http://localhost:${NGINX_PORT}" --username "${DJANGO_SUPERUSER_USERNAME}" --password "${DJANGO_SUPERUSER_PASSWORD}"
  if ! grep -q "_PULP_COMPLETE=bash_source pulp" /root/.bashrc
  then
    echo "eval \"\$(LC_ALL=C _PULP_COMPLETE=bash_source pulp)\"" >> /root/.bashrc
  fi
  pulp --refresh-api status
fi
