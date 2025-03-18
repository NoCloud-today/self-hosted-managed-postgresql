#!/bin/bash

service ssh restart

mkdir -p /var/log/postgresql
chown postgres:postgres /var/log/postgresql

if [ ! -s "/var/lib/postgresql/16/main/PG_VERSION" ]; then
    su postgres -c "/usr/lib/postgresql/16/bin/initdb -D /var/lib/postgresql/16/main"
fi

su postgres -c "/usr/lib/postgresql/16/bin/pg_ctl -D /var/lib/postgresql/16/main \
    -l /var/log/postgresql/postgresql.log \
    -o '-c config_file=/etc/postgresql/16/main/postgresql.conf' \
    start"

sleep 5

su postgres -c "psql -c \"ALTER USER postgres WITH PASSWORD '${POSTGRES_PASSWORD:-postgres}';\""

tail -f /var/log/postgresql/postgresql.log

