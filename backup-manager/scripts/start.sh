#!/bin/bash
set -e
echo "Starting PostgreSQL..."
su pgbackrest -c "ssh postgres@postgres  \"/usr/lib/postgresql/16/bin/pg_ctl -D /var/lib/postgresql/16/main -l /var/log/postgresql/postgresql.log -o '-c config_file=/etc/postgresql/16/main/postgresql.conf' start\"" || {
    echo "Failed to start PostgreSQL"
    exit 1
}