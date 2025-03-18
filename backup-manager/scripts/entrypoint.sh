#!/bin/bash

service ssh restart

su pgbackrest -c 'ssh-keyscan -H postgres >> /home/pgbackrest/.ssh/known_hosts'

if ! su pgbackrest -c 'pgbackrest --stanza=main info >/dev/null 2>&1'; then
    su pgbackrest -c "pgbackrest --log-level-console=info --stanza=main stanza-create"
fi

service cron start

exec su pgbackrest -c "uvicorn app.main:app --host 0.0.0.0 --port 8000"