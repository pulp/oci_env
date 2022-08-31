FROM ghcr.io/pulp/pulp-ci-centos:latest

# configure S6 to use env variables
ENV S6_KEEP_ENV=1

RUN pip3 install pulpcore django-extensions pulp-smash@git+https://github.com/pulp/pulp-smash.git

COPY settings.py /etc/pulp/settings.py
COPY s6-rc.d/oci-env-prepare/ /etc/s6-overlay/s6-rc.d/oci-env-prepare/
COPY s6-rc.d/oci-env-profiles /etc/s6-overlay/s6-rc.d/oci-env-profiles/
RUN cd /etc/s6-overlay/s6-rc.d/user/contents.d && touch oci-env-prepare oci-env-profiles

# Modify postgres so it starts after oci-env gets a chance to initialize the plugins from source
COPY s6-rc-modifications/postgres-prepare/dependencies /etc/s6-overlay/s6-rc.d/postgres-prepare/dependencies

# Modify pulpcore-api so it auto reloads
COPY s6-rc-modifications/pulpcore-api/run /etc/s6-overlay/s6-rc.d/pulpcore-api/run
COPY utils.sh /utils.sh