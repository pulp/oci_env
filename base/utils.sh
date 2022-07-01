#!/bin/bash

set -o nounset
set -o errexit
set -o pipefail

readonly DEV_SOURCE_PATH="${DEV_SOURCE_PATH:-}"
readonly LOCK_REQUIREMENTS="${LOCK_REQUIREMENTS:-1}"


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

create_super_user() {
    pulpcore-manager createsuperuser --no-input --email admin@example.com
}

$1