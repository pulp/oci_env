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

            pip3 install --prefix /usr/local/ --no-cache-dir --editable "$src_path" >/dev/null

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

set_nginx_port() {
    echo "setting nginx port"
    # the nginx s6 service copies the file from /nginx/nginx.conf, which overwrites our changes,
    # so we have to change the source file.
    /usr/bin/sed -i s/listen\ 80/listen\ "${NGINX_PORT}"/g /nginx/nginx.conf
    /usr/bin/sed -i s/listen\ 443/listen\ "${NGINX_SSL_PORT}"/g /nginx/ssl_nginx.conf

    # this is the older command. Leaving this in for backwards compatibility for devs that haven't
    # updated their images.
    /usr/bin/sed -i s/listen\ 80/listen\ "${NGINX_PORT}"/g /etc/nginx/nginx.conf
}

init_container() {
    install_local_deps
    set_nginx_port
}

run_profile_init_scripts() {
    bash /opt/oci_env/.compiled/${COMPOSE_PROJECT_NAME}/init.sh
}

$1