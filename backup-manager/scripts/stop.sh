#!/bin/bash
set -e
echo "Stopping PostgreSQL..."
if su pgbackrest -c "ssh postgres@postgres 'pg_isready'" >/dev/null 2>&1; then
    echo "PostgreSQL is running, stopping PostgreSQL..."
    su pgbackrest -c "ssh -t postgres@postgres '/usr/lib/postgresql/16/bin/pg_ctl -D /var/lib/postgresql/16/main stop'" || {
        echo "Failed to stop PostgreSQL"
        exit 1
    }
else
    echo "PostgreSQL is not running, skipping stop operation"
fi
