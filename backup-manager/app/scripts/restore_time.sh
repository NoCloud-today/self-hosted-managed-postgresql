#!/bin/bash
set -e

TARGET_TIME="$1"

if [ -z "$TARGET_TIME" ]; then
    echo "Error: Target timestamp is required"
    exit 1
fi

FORMATTED_TIME=$(date -d "$TARGET_TIME" "+%Y-%m-%d %H:%M:%S+00")

./stop.sh
sleep 2

ssh -t postgres@postgres "pgbackrest --stanza=main --log-level-console=info --type=time \"--target=${FORMATTED_TIME}\" --target-action=promote --delta restore"
sleep 2

./start.sh
