FROM ubuntu:latest

ARG POSTGRES_PASSWORD
ENV POSTGRES_PASSWORD=${POSTGRES_PASSWORD}

RUN apt-get update && apt-get install -y \
    pgbackrest=2.50-1build2 \
    openssh-client \
    postgresql-16 \
    perl \
    wget \
    openssh-server \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p -m 770 /var/log/pgbackrest \
    && chown postgres:postgres /var/log/pgbackrest \
    && mkdir -p /etc/pgbackrest \
    && mkdir -p /etc/pgbackrest/conf.d \
    && mkdir -p -m 770 /var/lib/pgbackrest \
    && chown postgres:postgres /var/lib/pgbackrest

COPY postgres/config/pgbackrest.conf /etc/pgbackrest/pgbackrest.conf
RUN chown postgres:postgres /etc/pgbackrest/pgbackrest.conf \
    && chmod 640 /etc/pgbackrest/pgbackrest.conf

USER postgres
RUN mkdir -p -m 700 /var/lib/postgresql/.ssh

COPY --chown=postgres:postgres ssh_keys/id_rsa_postgres /var/lib/postgresql/.ssh/id_rsa
COPY --chown=postgres:postgres ssh_keys/id_rsa_postgres.pub /var/lib/postgresql/.ssh/id_rsa.pub
RUN chmod 600 /var/lib/postgresql/.ssh/id_rsa && \
    chmod 644 /var/lib/postgresql/.ssh/id_rsa.pub

COPY --chown=postgres:postgres ssh_keys/id_rsa_backup_manager.pub /var/lib/postgresql/.ssh/authorized_keys
RUN chmod 600 /var/lib/postgresql/.ssh/authorized_keys

RUN eval $(ssh-agent) && \
    ssh-add /var/lib/postgresql/.ssh/id_rsa

USER root
RUN chown postgres:postgres /var/lib/postgresql/.ssh && chmod 600 /var/lib/postgresql/.ssh/authorized_keys
RUN sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config && \
    sed -i 's/#PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config && \
    sed -i 's/#PubkeyAuthentication yes/PubkeyAuthentication yes/' /etc/ssh/sshd_config

RUN mkdir /var/run/sshd && \
    chmod 0755 /var/run/sshd

RUN mkdir -p /var/lib/postgresql/.ssh && \
    echo "Host backup-manager\n\tStrictHostKeyChecking no\n\tUserKnownHostsFile=/dev/null" > /var/lib/postgresql/.ssh/config && \
    chown -R postgres:postgres /var/lib/postgresql/.ssh && \
    chmod 600 /var/lib/postgresql/.ssh/config
EXPOSE 22

RUN mkdir -p -m 770 /var/lib/postgresql/16/main && chown postgres:postgres -R /var/lib/postgresql/16/main

USER root
COPY postgres/config/postgresql.conf /etc/postgresql/16/main/postgresql.conf
COPY postgres/config/pg_hba.conf /etc/postgresql/16/main/pg_hba.conf

COPY postgres/scripts/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

RUN wget https://dl.min.io/client/mc/release/linux-amd64/mc && \
    mv mc /usr/bin/mc && \
    chmod +x /usr/bin/mc

RUN mkdir -p /var/lib/postgresql/16/main && \
chown postgres:postgres /var/lib/postgresql/16/main && \
chmod 700 /var/lib/postgresql/16/main


ENTRYPOINT ["/entrypoint.sh"]