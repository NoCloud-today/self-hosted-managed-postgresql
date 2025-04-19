#!/bin/bash

start_database(){
  su postgres -c "/usr/lib/postgresql/16/bin/pg_ctl -D /var/lib/postgresql/16/main \
    -l /var/log/postgresql/postgresql.log \
    -o '-c config_file=/etc/postgresql/16/main/postgresql.conf' \
    start"
}
stop_database(){
  su postgres -c '/usr/lib/postgresql/16/bin/pg_ctl -D /var/lib/postgresql/16/main stop'
}
recover_database(){
  start_database
  stop_database
  echo "Stanza exist, recover from existing stanza"
  su postgres -c "pgbackrest --stanza=main --log-level-console=info --delta --recovery-option=recovery_target=immediate --target-action=promote --type=immediate restore"
  echo "Starting database after recovery"
  start_database
  echo "Creating first backup"
  su postgres -c "pgbackrest --log-level-console=info  backup --type=full --stanza=main"
}
initialize_database(){
  chown postgres:postgres /var/lib/postgresql/16/main
  su postgres -c "/usr/lib/postgresql/16/bin/initdb -D /var/lib/postgresql/16/main"
  if su postgres -c "pgbackrest info" | grep -q "stanza: main"; then
    recover_database
  else
    start_database
  fi
}
initialize_stanza(){
  echo "Stanza does not exist, creating new"
  su postgres -c "pgbackrest --log-level-console=info --stanza=main stanza-create"
}
service ssh restart

mkdir -p /var/log/postgresql
chown postgres:postgres /var/log/postgresql

if [ ! -s "/var/lib/postgresql/16/main/PG_VERSION" ]; then
  initialize_database
else
  start_database
fi


su postgres -c "psql -c \"ALTER USER postgres WITH PASSWORD '${POSTGRES_PASSWORD:-postgres}';\""
if  ! su postgres -c "pgbackrest info" | grep -q "stanza: main"; then
    initialize_stanza
fi
if  su postgres -c "pgbackrest info" | grep -q "status: error"; then
    echo "No backup exists, creating backup"
    su postgres -c "pgbackrest --log-level-console=info  backup --type=full --stanza=main"
fi
tail -f /var/log/postgresql/postgresql.log

