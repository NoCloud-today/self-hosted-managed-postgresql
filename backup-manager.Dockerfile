FROM ubuntu:latest

WORKDIR /app

RUN apt-get update && apt-get install -y \
    perl \
    pgbackrest=2.50-1build2 \
    python3 \
    python3-pip \
    cron \
    openssh-client \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /root/.ssh && \
    chown root:root /root/.ssh && \
    chmod 700 /root/.ssh

RUN apt-get update && \
    apt-get install -y openssh-server sudo && \
    mkdir /var/run/sshd && chmod 0755 /var/run/sshd

COPY backup-manager/config/pgbackrest.conf /etc/pgbackrest/pgbackrest.conf

RUN adduser pgbackrest
RUN mkdir -p -m 700 /home/pgbackrest/.ssh
RUN chown pgbackrest:pgbackrest /home/pgbackrest/.ssh
RUN chown pgbackrest:pgbackrest /var/log/pgbackrest
USER pgbackrest
COPY --chown=pgbackrest:pgbackrest ssh_keys/id_rsa_backup_manager /home/pgbackrest/.ssh/id_rsa
COPY --chown=pgbackrest:pgbackrest ssh_keys/id_rsa_backup_manager.pub /home/pgbackrest/.ssh/id_rsa.pub
RUN chmod 600 /home/pgbackrest/.ssh/id_rsa && \
    chmod 644 /home/pgbackrest/.ssh/id_rsa.pub

COPY --chown=pgbackrest:pgbackrest ssh_keys/id_rsa_postgres.pub /home/pgbackrest/.ssh/authorized_keys

RUN eval $(ssh-agent) && \
    ssh-add /home/pgbackrest/.ssh/id_rsa
USER root
RUN chown pgbackrest:pgbackrest /home/pgbackrest/.ssh
RUN chmod 600 /home/pgbackrest/.ssh/authorized_keys
RUN sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config && \
    sed -i 's/#PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config && \
    sed -i 's/#PubkeyAuthentication yes/PubkeyAuthentication yes/' /etc/ssh/sshd_config

RUN mkdir -p /home/pgbackrest/.ssh && \
    echo "Host postgres\n\tStrictHostKeyChecking no\n\tUserKnownHostsFile=/dev/null" > /home/pgbackrest/.ssh/config && \
    chown -R pgbackrest:pgbackrest /home/pgbackrest/.ssh && \
    chmod 600 /home/pgbackrest/.ssh/config

EXPOSE 22
COPY backup-manager/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt --break-system-packages
COPY backup-manager .

COPY backup-manager/crontab /etc/cron.d/backup-cron
RUN chmod 0644 /etc/cron.d/backup-cron && \
    crontab /etc/cron.d/backup-cron

COPY backup-manager/scripts/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
