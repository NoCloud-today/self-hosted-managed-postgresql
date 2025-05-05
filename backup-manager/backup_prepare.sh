#!/usr/bin/env bash
set -e
PG_CLUSTER="main"
initialize_stanza(){
  echo "Stanza does not exist, creating new"
  pgbackrest --log-level-console=info --stanza=$PG_CLUSTER stanza-create
}
if  ! pgbackrest info | grep -q "stanza: $PG_CLUSTER"; then
    initialize_stanza
fi
if  pgbackrest info | grep -q "status: error"; then
    echo "No backup exists, creating backup"
    pgbackrest --log-level-console=info  backup --type=full --stanza=$PG_CLUSTER --repo 1
    pgbackrest --log-level-console=info  backup --type=full --stanza=$PG_CLUSTER --repo 2
fi

uvicorn app.src.main:app --host 0.0.0.0 --port 8000 --log-config log_config.json

