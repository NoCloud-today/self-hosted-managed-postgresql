#!/bin/bash
set -e

TARGET_TIME="$1"

if [ -z "$TARGET_TIME" ]; then
    echo "Error: Target timestamp is required"
    exit 1
fi

./stop.sh
sleep 2

su pgbackrest -c 'ssh  postgres@postgres "sudo rm -rf /var/lib/postgresql/16/main/*"'

if [ -z "$TARGET_TIME" ]; then
    pgbackrest --stanza=main --log-level-console=info --delta restore
else
    pgbackrest --stanza=main --log-level-console=info --delta --recovery-option="recovery_target_time=${TARGET_TIME}" restore
fi

./start.sh


