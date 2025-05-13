#!/usr/bin/env bash
set -e

start_database_foreground(){
  pg_ctlcluster "${PG_VERSION}" ${PG_CLUSTER} start --foreground
}
start_database(){
  pg_ctlcluster "${PG_VERSION}" ${PG_CLUSTER} start
}
stop_database(){
  pg_ctlcluster "${PG_VERSION}" ${PG_CLUSTER} stop
}
create_backup(){
  pgbackrest --log-level-console=info  backup --type=full --stanza=$PG_CLUSTER --repo 1
  pgbackrest --log-level-console=info  backup --type=full --stanza=$PG_CLUSTER --repo 2
}
recover_database(){
  echo "Stanza exist, recover from existing stanza"
  pgbackrest --stanza=main --log-level-console=info --delta --recovery-option=recovery_target=immediate --target-action=promote --type=immediate restore
  echo "Starting database after recovery"
  start_database
  echo "Creating first backup"
  create_backup
  echo "Stopping database after creating first backup"
  stop_database
}
initialize_database(){
  echo "Cluster ${PG_VERSION}/${PG_CLUSTER} does not exist. Creating..."
  SECRET_FILE=etc/postgresql/$PG_VERSION/$PG_CLUSTER/secret.txt
  echo "$POSTGRES_PASSWORD" > "$SECRET_FILE"
  /usr/lib/postgresql/"$PG_VERSION"/bin/initdb -D "$PG_DATA" --pwfile="$SECRET_FILE"

  rm $PG_DATA/postgresql.conf $PG_DATA/pg_hba.conf
  cp /etc/postgresql/$PG_VERSION/$PG_CLUSTER/postgresql.conf $PG_DATA/postgresql.conf
  cp /etc/postgresql/$PG_VERSION/$PG_CLUSTER/pg_hba.conf $PG_DATA/pg_hba.conf
}
prepare_database(){
  # if there are existing stanza - trying to restore from it, else - creating database from scratch
  if pgbackrest info | grep -q "stanza: main"; then
    echo "Stanza exist, trying to restore from it"
    recover_database
  else
    echo "Initializing database"
    initialize_database
  fi
}

PG_CLUSTER="main"
PG_DATA="/var/lib/postgresql/${PG_VERSION}/${PG_CLUSTER}"
PG_VERSION_FILE="/var/lib/postgresql/$PG_VERSION/$PG_CLUSTER/PG_VERSION"
# check if database doesn't initialize
if [ ! -s "$PG_VERSION_FILE" ]; then
  whoami
  chown "${BACKREST_USER}":"${BACKREST_GROUP}" "$PG_DATA"
  chmod -R 750 "$PG_DATA"
  ls -la $PG_DATA
  prepare_database
fi
echo "Giving permissions for data directories for BACKREST_USER"
chown "${BACKREST_USER}":"${BACKREST_GROUP}" "$PG_DATA"
chmod -R 750 "$PG_DATA"

echo "Starting database"
start_database

LOG_FILE="/var/log/postgresql/postgresql-${PG_VERSION}-${PG_CLUSTER}.log"
echo "Tailing PostgreSQL logs from: $LOG_FILE"
tail -F "$LOG_FILE"