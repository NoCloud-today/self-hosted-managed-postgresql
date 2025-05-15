#!/bin/bash
set -e

TARGET_TIME="$1"

if [ -z "$TARGET_TIME" ]; then
    echo "Error: Target timestamp is required"
    exit 1
fi

./stop.sh

echo "Running pgbackrest point in time recovery"
./run_container.sh "pgbackrest --stanza=main --log-level-console=info --type=time \"--target=${TARGET_TIME}\" --target-action=promote --delta restore"
sleep 2

./start.sh