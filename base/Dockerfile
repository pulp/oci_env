FROM ghcr.io/pulp/pulp-ci-centos:latest

RUN pip3 install pulpcore

COPY settings.py /etc/pulp/settings.py
COPY init/000-a-src-install /etc/cont-init.d/000-a-src-install
COPY init/001-admin-user /etc/cont-init.d/001-admin-user
COPY utils.sh /utils.sh

# TODO update the base image to make auto reload configurable via env var
# overwrite services to allow for auto reload.
COPY services /etc/services.d