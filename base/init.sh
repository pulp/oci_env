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

# Configure sudo
echo 'Defaults    secure_path = /sbin:/bin:/usr/sbin:/usr/bin:/usr/local/bin:/usr/local/sbin' > /etc/sudoers.d/secure_path
echo 'Defaults    env_keep += "DJANGO_SETTINGS_MODULE PULP_SETTINGS XDG_CONFIG_HOME"' > /etc/sudoers.d/preserve_env

# Add user pulp to sudoers so tests can use sudo
echo '%wheel ALL=(ALL) NOPASSWD: ALL' > /etc/sudoers.d/nopasswd
echo 'usermod -a -G wheel pulp'
