#!/usr/bin/env bash
set -e
PG_CLUSTER="main"

/entrypoint.sh "echo"

chown -R ${BACKREST_USER}:${BACKREST_GROUP} /var/run

initialize_stanza(){
  echo "Stanza does not exist, creating new stanza"
  su "${BACKREST_USER}" <<'EOF'
  PG_CLUSTER="main"
  pgbackrest --log-level-console=info --stanza=$PG_CLUSTER stanza-create
EOF
}
if  ! pgbackrest info | grep -q "stanza: $PG_CLUSTER"; then
    initialize_stanza
fi
if  pgbackrest info | grep -q "status: error"; then
    echo "No backup exists, creating backup in stanza"
    su "${BACKREST_USER}" <<'EOF'
    PG_CLUSTER="main"
    pgbackrest --log-level-console=info  backup --type=full --stanza=$PG_CLUSTER --repo 1
    pgbackrest --log-level-console=info  backup --type=full --stanza=$PG_CLUSTER --repo 2
EOF
fi
chmod -R 777 /app/.web

chown -R ${BACKREST_USER}:${BACKREST_GROUP} /app
echo "Starting reflex server"
su "${BACKREST_USER}" <<'EOF'
    redis-server --daemonize yes && \
    exec reflex run --env prod --loglevel info
EOF


