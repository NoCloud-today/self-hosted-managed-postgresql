#!/bin/bash

service ssh restart

mkdir -p /var/log/postgresql
chown postgres:postgres /var/log/postgresql

if [ ! -s "/var/lib/postgresql/16/main/PG_VERSION" ]; then
    chown postgres:postgres /var/lib/postgresql/16/main
    su postgres -c "/usr/lib/postgresql/16/bin/initdb -D /var/lib/postgresql/16/main"
fi

su postgres -c "/usr/lib/postgresql/16/bin/pg_ctl -D /var/lib/postgresql/16/main \
    -l /var/log/postgresql/postgresql.log \
    -o '-c config_file=/etc/postgresql/16/main/postgresql.conf' \
    start"

su postgres -c "psql -c \"ALTER USER postgres WITH PASSWORD '${POSTGRES_PASSWORD:-postgres}';\""
if  ! su postgres -c "pgbackrest info" | grep -q "stanza: main"; then
    echo "Stanza does not exist, creating new"
    /usr/bin/mc alias set minio-s3 https://backup-manager-s3:9000 minioadmin minioadmin --insecure
    /usr/bin/mc mb minio-s3/pgbackrest --ignore-existing --insecure
    /usr/bin/mc anonymous set public minio-s3/pgbackrest --insecure
    su postgres -c "pgbackrest --log-level-console=info --stanza=main stanza-create"
    su postgres -c "pgbackrest --log-level-console=info  backup --type=full --stanza=main"
fi
tail -f /var/log/postgresql/postgresql.log

