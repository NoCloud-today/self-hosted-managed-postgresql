#!/bin/bash
set -e

TARGET_TIME="$1"

if [ -z "$TARGET_TIME" ]; then
    echo "Error: Target timestamp is required"
    exit 1
fi

./stop.sh
sleep 2


su pgbackrest -c "ssh -t postgres@postgres 'pgbackrest --stanza=main --log-level-console=info --type=time  \"--target=${TARGET_TIME}\" --delta restore'"


./start.sh




