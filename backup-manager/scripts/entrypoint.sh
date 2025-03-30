#!/bin/bash

service ssh restart

su pgbackrest -c 'ssh-keyscan -H postgres >> /home/pgbackrest/.ssh/known_hosts'

su pgbackrest -c 'pgbackrest --stanza=main info' | cat

if [ ! -d "/var/lib/pgbackrest" ] || [ -z "$(ls -A "/var/lib/pgbackrest" 2>/dev/null)" ]; then
    echo "Stanza does not exist, creating new"
    su pgbackrest -c "pgbackrest --log-level-console=info --stanza=main stanza-create"
    su pgbackrest -c "pgbackrest --log-level-console=info  backup --type=full --stanza=main"
fi

service cron start

exec su pgbackrest -c "uvicorn app.main:app --host 0.0.0.0 --port 8000"