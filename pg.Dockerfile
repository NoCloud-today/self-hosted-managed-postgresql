ARG BACKREST_VERSION="2.54.2"
ARG PG_VERSION="16"
FROM woblerr/pgbackrest:${BACKREST_VERSION}
ARG PG_VERSION
ENV BACKREST_USER="postgres" \
    BACKREST_GROUP="postgres" \
    PG_VERSION="${PG_VERSION}" \
    PG_CLUSTER="main"

RUN apt-get update -y \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y \
        curl \
        gnupg \
        lsb-release \
    && curl https://www.postgresql.org/media/keys/ACCC4CF8.asc | gpg --dearmor -o /etc/apt/trusted.gpg.d/postgresql.gpg \
    && echo "deb http://apt.postgresql.org/pub/repos/apt/ $(lsb_release -cs)-pgdg main" \
        > /etc/apt/sources.list.d/pgdg.list
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

RUN mkdir -p -m 700 \
        /var/lib/postgresql/.ssh \
    && chown -R ${BACKREST_USER}:${BACKREST_GROUP} \
        /var/lib/postgresql/.ssh

COPY --chmod=600 --chown=${BACKREST_USER}:${BACKREST_GROUP} ./certs/pgbackrest /etc/pgbackrest/cert

RUN chown -R ${BACKREST_USER}:${BACKREST_GROUP} /var/lib/postgresql/$PG_VERSION/$PG_CLUSTER && chmod -R 750 "/var/lib/postgresql/$PG_VERSION/$PG_CLUSTER"
ENTRYPOINT ["/entrypoint.sh"]
