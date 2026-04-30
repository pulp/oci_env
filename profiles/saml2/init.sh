#!/bin/bash

set -eu

dnf -y install xmlsec1-openssl
uv pip install djangosaml2

mkdir -p /etc/pulp/certs
pushd /etc/pulp/certs
yes "" | openssl req -nodes -new -x509 -newkey rsa:2048 -days 3650 -keyout saml2-private.key -out saml2-public.crt

chown pulp saml2-private.key saml2-public.crt
popd
