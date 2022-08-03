#!/bin/bash

# Loads all the compose configurations

set -o nounset
set -o errexit

if [[ -f '.compose.env' ]]; then
  # export variables from .compose.env but only if the var is not already set.
  eval "$(grep -v '^#' .compose.env | sed -E 's|^(.+)=(.*)$|export \1=${\1:-\2}|g' | xargs -L 1)"
fi

# Supported configs
declare -xr DEV_SOURCE_PATH=${DEV_SOURCE_PATH:-}
declare -xr COMPOSE_PROFILE=${COMPOSE_PROFILE:-}
declare -xr DJANGO_SUPERUSER_USERNAME="${DJANGO_SUPERUSER_USERNAME:-admin}"
declare -xr DJANGO_SUPERUSER_PASSWORD="${DJANGO_SUPERUSER_PASSWORD:-password}"
declare -xr API_HOST="${API_HOST:-localhost}"
declare -xr API_PORT="${API_PORT:-5001}"
declare -xr API_PROTOCOL="${API_PROTOCOL:-http}"
declare -xr NGINX_PORT="${NGINX_PORT:-80}"
declare -xr NGINX_SSL_PORT="${NGINX_SSL_PORT:-443}"


# WIP configs
declare -xr COMPOSE_CONTEXT="${PWD}"
declare -xr LOCK_REQUIREMENTS="${LOCK_REQUIREMENTS:-0}"
declare -xr DEV_IMAGE_SUFFIX="${DEV_IMAGE_SUFFIX:-}"
declare -xr DEV_VOLUME_SUFFIX="${DEV_VOLUME_SUFFIX:-${DEV_IMAGE_SUFFIX}}"
declare -xr COMPOSE_PROJECT_NAME="${COMPOSE_PROJECT_NAME:-oci_env${DEV_IMAGE_SUFFIX:-}}"
