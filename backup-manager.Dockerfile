FROM ubuntu:24.04

WORKDIR /app

RUN apt-get update && apt-get install -y \
    python3 \
    nano \
    python3-pip \
    cron \
    openssh-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /root/.ssh && \
    chown root:root /root/.ssh && \
    chmod 700 /root/.ssh

RUN apt-get update && \
    apt-get install -y openssh-server sudo && \
    mkdir /var/run/sshd && chmod 0755 /var/run/sshd


RUN adduser backup-manager
RUN mkdir -p -m 700 /home/backup-manager/.ssh
RUN chown backup-manager:backup-manager /home/backup-manager/.ssh
USER backup-manager
COPY --chown=backup-manager:backup-manager ssh_keys/id_rsa_backup_manager /home/backup-manager/.ssh/id_rsa
COPY --chown=backup-manager:backup-manager ssh_keys/id_rsa_backup_manager.pub /home/backup-manager/.ssh/id_rsa.pub
RUN chmod 600 /home/backup-manager/.ssh/id_rsa && \
    chmod 644 /home/backup-manager/.ssh/id_rsa.pub

COPY --chown=backup-manager:backup-manager ssh_keys/id_rsa_postgres.pub /home/backup-manager/.ssh/authorized_keys

RUN eval $(ssh-agent) && \
    ssh-add /home/backup-manager/.ssh/id_rsa
USER root
RUN chown backup-manager:backup-manager /home/backup-manager/.ssh
RUN chmod 600 /home/backup-manager/.ssh/authorized_keys
RUN sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config && \
    sed -i 's/#PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config && \
    sed -i 's/#PubkeyAuthentication yes/PubkeyAuthentication yes/' /etc/ssh/sshd_config

RUN mkdir -p /home/backup-manager/.ssh && \
    echo "Host postgres\n\tStrictHostKeyChecking no\n\tUserKnownHostsFile=/dev/null" > /home/backup-manager/.ssh/config && \
    chown -R backup-manager:backup-manager /home/backup-manager/.ssh && \
    chmod 600 /home/backup-manager/.ssh/config

COPY backup-manager .
RUN cd app && pip install --no-cache-dir -r requirements.txt --break-system-packages

RUN chmod -R 755 /app && \
    chown -R backup-manager:backup-manager /app/ &&  \
    chmod +x /app/app/scripts/*
COPY backup-manager/app/crontab /etc/cron.d/backup-cron
RUN chmod 0644 /etc/cron.d/backup-cron && \
    crontab /etc/cron.d/backup-cron
COPY /backup-manager/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
