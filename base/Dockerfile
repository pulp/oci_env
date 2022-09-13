FROM ghcr.io/pulp/pulp-ci-centos:latest

RUN pip3 install pulpcore django-extensions pulp-smash@git+https://github.com/pulp/pulp-smash.git

COPY settings.py /etc/pulp/settings.py
COPY utils.sh /utils.sh

# TODO update the base image to make auto reload configurable via env var
# overwrite services to allow for auto reload.
COPY s6-rc.d /etc/s6-overlay/s6-rc.d
