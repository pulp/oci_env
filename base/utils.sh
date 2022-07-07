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
            # the oci images expect all the pulp binaries to land in /usr/local/bin/, not the default /usr/bin/
                pip3 install --prefix /usr/local/ --no-cache-dir --no-deps --editable "$src_path" >/dev/null
            else
                pip3 install --prefix /usr/local/ --no-cache-dir --editable "$src_path" >/dev/null
            fi

            nginx_config="${src_path}/${item}/app/webserver_snippets/nginx.conf"

            # use cp since ln doesn't work on mounted files
            if [[ -f $nginx_config ]]; then
                cp "${nginx_config}" "/etc/nginx/pulp/${item}.conf"
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