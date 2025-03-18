#!/bin/bash
set -e
echo "Stopping PostgreSQL..."
su pgbackrest -c "ssh -o postgres@postgres \"sudo pg_ctl -D /var/lib/postgres/data/pgdata -l logfile stop\"" || {
    echo "Failed to stop PostgreSQL"
    exit 1
}
