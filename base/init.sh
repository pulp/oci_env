#!/bin/bash

pulpcore-manager createsuperuser --no-input --email admin@example.com || true

if ! grep -q "install_phelpers.sh" /root/.bashrc
then
  echo "source /opt/oci_env/base/container_scripts/install_phelpers.sh" >> /root/.bashrc
fi

# Configure sudo
echo 'Defaults    secure_path = /sbin:/bin:/usr/sbin:/usr/bin:/usr/local/bin:/usr/local/sbin' > /etc/sudoers.d/secure_path
echo 'Defaults    env_keep += "DJANGO_SETTINGS_MODULE PULP_SETTINGS XDG_CONFIG_HOME"' > /etc/sudoers.d/preserve_env

# Add user pulp to sudoers so tests can use sudo
# !pam_acct_mgmt is needed in containers where the pulp user lacks a /etc/shadow entry
printf '%s\n' '%wheel ALL=(ALL) NOPASSWD: ALL' 'Defaults !pam_acct_mgmt' > /etc/sudoers.d/nopasswd
usermod -aG wheel pulp && echo 'Adding the pulp user to the wheel group...'
