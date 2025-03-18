#!/bin/bash
set -e
echo "Starting PostgreSQL..."
su pgbackrest -c "ssh postgres@postgres \"sudo pg_ctl -D /var/lib/postgres/data/pgdata -l logfile start\"" || {
    echo "Failed to start PostgreSQL"
    exit 1
}