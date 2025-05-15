#!/usr/bin/env bash
set -e

start_database_foreground(){
  pg_ctlcluster "${PG_VERSION}" ${PG_CLUSTER} -o '-c config_file=/etc/postgresql/16/main/postgresql.conf -c hba_file=/etc/postgresql/16/main/pg_hba.conf' start --foreground
}
start_database(){
  pg_ctlcluster "${PG_VERSION}" ${PG_CLUSTER} -o '-c config_file=/etc/postgresql/16/main/postgresql.conf -c hba_file=/etc/postgresql/16/main/pg_hba.conf' start
}
stop_database(){
  pg_ctlcluster "${PG_VERSION}" ${PG_CLUSTER} stop
}
create_backup(){
  su "${BACKREST_USER}" <<'EOF'
  pgbackrest --log-level-console=info  backup --type=full --stanza=$PG_CLUSTER --repo 1
  pgbackrest --log-level-console=info  backup --type=full --stanza=$PG_CLUSTER --repo 2
EOF
}
recover_database(){
  su "${BACKREST_USER}" <<'EOF'
  echo "Stanza exist, recover from existing stanza"
  pgbackrest --stanza=main --log-level-console=info --delta --recovery-option=recovery_target=immediate --target-action=promote --type=immediate restore
EOF
  echo "Starting database after recovery"
  start_database
  echo "Creating first full backup after restore"
  create_backup
  echo "Stopping database after creating first backup"
  stop_database
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
  echo "Database is prepared"
}
run_in_database_mode(){
  echo "Giving permissions for data directories for BACKREST_USER"
  chown "${BACKREST_USER}":"${BACKREST_GROUP}" "$PG_DATA"
  chmod -R 750 "$PG_DATA"
  echo "Starting database"
  start_database
  timeout 30s sh -c 'until pg_isready; do sleep 1; done'
  psql -U postgres -d postgres -c "ALTER USER postgres WITH PASSWORD '${POSTGRES_PASSWORD}';"

  LOG_FILE="/var/log/postgresql/postgresql-${PG_VERSION}-${PG_CLUSTER}.log"
  echo "Tailing PostgreSQL logs from: $LOG_FILE"
  tail -F "$LOG_FILE"
}
run_in_recovery_mode(){
  chown "${BACKREST_USER}":"${BACKREST_GROUP}" "$PG_DATA"
  chmod -R 750 "$PG_DATA"
  echo "Restarting database"
  start_database
  echo "Start database is completed"
  timeout 30s sh -c 'until pg_isready; do sleep 1; done'
  stop_database
  echo "Stop database is completed"
  su "${BACKREST_USER}" -c "$1"
}
if [ $# -eq 0 ]; then
  ./entrypoint.sh "echo"
  run_in_database_mode
elif [ $# -eq 1 ]; then
  ./entrypoint.sh "echo"
  echo "Running in recovery mode with command: $1"
  run_in_recovery_mode "$1"
else
  echo "Error: Invalid number of arguments"
  echo "Usage:"
  echo "  $0              - Run in database mode"
  echo "  $0 <command>    - Run in recovery mode with specified command"
  exit 1
fi