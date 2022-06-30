#!/bin/bash

set -o nounset
set -o errexit
set -o pipefail

readonly WITH_MIGRATIONS="${WITH_MIGRATIONS:-0}"
readonly WITH_DEV_INSTALL="${WITH_DEV_INSTALL:-0}"
readonly DEV_SOURCE_PATH="${DEV_SOURCE_PATH:-}"
readonly LOCK_REQUIREMENTS="${LOCK_REQUIREMENTS:-1}"
readonly WAIT_FOR_MIGRATIONS="${WAIT_FOR_MIGRATIONS:-0}"
readonly ENABLE_SIGNING="${ENABLE_SIGNING:-0}"
readonly PULP_GALAXY_DEPLOYMENT_MODE="${PULP_GALAXY_DEPLOYMENT_MODE:-}"


log_message() {
    echo "$@" >&2
}

install_local_deps() {
    local src_path_list
    IFS=':' read -ra src_path_list <<< "$DEV_SOURCE_PATH"

    for item in "${src_path_list[@]}"; do
        src_path="/src/${item}"
        if [[ -d "$src_path" ]]; then
            log_message "Installing path ${item} in editable mode."

            if [[ "${LOCK_REQUIREMENTS}" -eq "1" ]]; then
                pip3 install --no-cache-dir --no-deps --editable "$src_path" >/dev/null
            else
                pip3 install --no-cache-dir --editable "$src_path" >/dev/null
            fi

        else
            log_message "WARNING: Source path ${item} is not a directory."
        fi
    done
}

setup_signing_keyring() {
    log_message "Setting up signing keyring."
    export KEY_FINGERPRINT=$(gpg --show-keys --with-colons --with-fingerprint /tmp/ansible-sign.key | awk -F: '$1 == "fpr" {print $10;}' | head -n1)
    export KEY_ID=${KEY_FINGERPRINT: -16}
    gpg --batch --no-default-keyring --keyring /etc/pulp/certs/galaxy.kbx --import /tmp/ansible-sign.key &>/dev/null
    echo "${KEY_FINGERPRINT}:6:" | gpg --batch --no-default-keyring --keyring /etc/pulp/certs/galaxy.kbx --import-ownertrust &>/dev/null
}

setup_repo_keyring() {
    # run after a short delay, otherwise the django-admin command hangs
    sleep 30
    STAGING_KEYRING=$(django-admin shell -c "from pulp_ansible.app.models import AnsibleRepository;print(AnsibleRepository.objects.get(name='staging').keyring)" 2>/dev/null || true)
    if [[ "${STAGING_KEYRING}" != "/etc/pulp/certs/galaxy.kbx" ]]; then
        log_message "Setting keyring for staging repo"
        django-admin set-repo-keyring --repository staging --keyring /etc/pulp/certs/galaxy.kbx -y
    else
        log_message "Keyring is already set for staging repo."
    fi
    PUBLISHED_KEYRING=$(django-admin shell -c "from pulp_ansible.app.models import AnsibleRepository;print(AnsibleRepository.objects.get(name='published').keyring)" 2>/dev/null || true)
    if [[ "${PUBLISHED_KEYRING}" != "/etc/pulp/certs/galaxy.kbx" ]]; then
        log_message "Setting keyring for published repo"
        django-admin set-repo-keyring --repository published --keyring /etc/pulp/certs/galaxy.kbx -y
    else
        log_message "Keyring is already set for published repo."
    fi
}

setup_signing_service() {
    log_message "Setting up signing service."
    export KEY_FINGERPRINT=$(gpg --show-keys --with-colons --with-fingerprint /tmp/ansible-sign.key | awk -F: '$1 == "fpr" {print $10;}' | head -n1)
    export KEY_ID=${KEY_FINGERPRINT: -16}
    gpg --batch --import /tmp/ansible-sign.key &>/dev/null
    echo "${KEY_FINGERPRINT}:6:" | gpg --import-ownertrust &>/dev/null

    HAS_SIGNING=$(django-admin shell -c 'from pulpcore.app.models import SigningService;print(SigningService.objects.filter(name="ansible-default").count())' 2>/dev/null || true)
    if [[ "$HAS_SIGNING" -eq "0" ]]; then
        log_message "Creating signing service. using key ${KEY_ID}"
        django-admin add-signing-service ansible-default /var/lib/pulp/scripts/collection_sign.sh ${KEY_ID} 2>/dev/null || true
    else
        log_message "Signing service already exists."
    fi
}

create_super_user() {
    pulpcore-manager createsuperuser --no-input --email admin@example.com
}

$1