#!/bin/bash
set -e

DB_NAME="$1"

./stop.sh
sleep 2

if [ -z "$DB_NAME" ]; then
    ssh -t postgres@postgres "pgbackrest --stanza=main --log-level-console=info --type=immediate --target-action=promote --delta restore";
else
    ssh -t postgres@postgres "pgbackrest --stanza=main --db-include=${DB_NAME} --log-level-console=info --type=immediate --target-action=promote --delta restore";
fi

sleep 2
./start.sh
