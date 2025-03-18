#!/bin/bash

service ssh restart

exec su postgres -c "/usr/lib/postgresql/16/bin/postgres \
    -c config_file=/etc/postgresql/16/main/postgresql.conf \
    -c hba_file=/etc/postgresql/16/main/pg_hba.conf"

