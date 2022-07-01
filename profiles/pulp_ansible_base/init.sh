#!/bin/bash

set -e

cmd_stdin_prefix() {
  "$@"
}

cmd_prefix() {
  "$@"
}

source /src/pulp_ansible/.github/workflows/scripts/post_before_script.sh