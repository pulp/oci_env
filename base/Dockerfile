ARG BASE_IMAGE=ghcr.io/pulp/pulp-ci-centos9:latest
FROM $BASE_IMAGE

# configure S6 to use env variables
ENV S6_KEEP_ENV=1

COPY dev_requirements.txt /dev_requirements.txt

COPY switch_python /usr/bin/switch_python
ARG PYTHON_VERSION=3.11
RUN switch_python "$PYTHON_VERSION"

RUN pip3 install -r dev_requirements.txt

RUN dnf -y install gettext

COPY settings.py /etc/pulp/settings.py
COPY s6-rc.d/oci-env-prepare/ /etc/s6-overlay/s6-rc.d/oci-env-prepare/
COPY s6-rc.d/oci-env-profiles /etc/s6-overlay/s6-rc.d/oci-env-profiles/
RUN cd /etc/s6-overlay/s6-rc.d/user/contents.d && touch oci-env-prepare oci-env-profiles

# Modify postgres so it starts after oci-env gets a chance to initialize the plugins from source
COPY s6-rc-modifications/postgres-prepare/dependencies.d /etc/s6-overlay/s6-rc.d/postgres-prepare/dependencies.d

COPY utils.sh /utils.sh
