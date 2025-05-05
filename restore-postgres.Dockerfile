FROM woblerr/pgbackrest:${BACKREST_VERSION}

RUN apt-get update -y \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y \
        apt-utils \
        postgresql-${PG_VERSION} \
        postgresql-contrib-${PG_VERSION} \
        openssh-server \
        rsyslog \
    && apt-get autoremove -y \
    && apt-get autopurge -y \
    && rm -rf /var/lib/apt/lists/*

COPY --chmod=755 --chown=${BACKREST_USER}:${BACKREST_GROUP} ./postgres/scripts/pg_prepare.sh /var/lib/postgresql/pg_prepare.sh
COPY --chmod=640 --chown=${BACKREST_USER}:${BACKREST_GROUP} ./postgres/config/postgresql.conf /etc/postgresql/${PG_VERSION}/main/postgresql.conf
COPY --chmod=640 --chown=${BACKREST_USER}:${BACKREST_GROUP} ./postgres/config/pg_hba.conf /etc/postgresql/${PG_VERSION}/main/pg_hba.conf
COPY --chmod=640 --chown=${BACKREST_USER}:${BACKREST_GROUP} ./postgres/config/pgbackrest.conf /etc/pgbackrest/pgbackrest.conf

