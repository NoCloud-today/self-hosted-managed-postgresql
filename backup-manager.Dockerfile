ARG BACKREST_VERSION="2.54.2"
FROM woblerr/pgbackrest:${BACKREST_VERSION}

WORKDIR /app

RUN apt-get update -y \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y \
        python3 \
        nano \
        python3-pip \
        postgresql-${PG_VERSION} \
        postgresql-contrib-${PG_VERSION} \
        cron \
        curl \
    && apt-get autoremove -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN  curl -fsSL https://get.docker.com -o get-docker.sh &&\
     sh get-docker.sh


COPY --chmod=600 --chown=${BACKREST_USER}:${BACKREST_GROUP} ./certs/pgbackrest /etc/pgbackrest/cert
COPY --chmod=755 --chown=${BACKREST_USER}:${BACKREST_GROUP} ./backup-manager/backup_prepare.sh /home/pgbackrest/backup_prepare.sh
COPY --chmod=755 --chown=${BACKREST_USER}:${BACKREST_GROUP} backup-manager .

RUN cd app && pip install --no-cache-dir -r requirements.txt --break-system-packages

RUN chmod -R 755 /app && \
    chown -R ${BACKREST_USER}:${BACKREST_GROUP} /app/ &&  \
    chmod +x /app/app/scripts/*

RUN usermod -a -G docker $BACKREST_USER && chown -R ${BACKREST_USER}:${BACKREST_GROUP} /var/run
ENTRYPOINT ["/entrypoint.sh"]
