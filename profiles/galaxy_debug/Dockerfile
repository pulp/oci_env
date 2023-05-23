FROM localhost/oci_env/pulp:base

RUN find /etc/s6* -name "postgres*" | grep -v prepare | xargs rm -rf
RUN rm -f /etc/s6-overlay/s6-rc.d/postgres-prepare/dependencies.d/postgresql
RUN rm -f /etc/s6-overlay/s6-rc.d/postgres-prepare/dependencies.d/postgresql-init
RUN rm -f /etc/s6-overlay/s6-rc.d/postgres-prepare/dependencies.d/postgres-init

COPY postgres-prepare /etc/init/postgres-prepare
