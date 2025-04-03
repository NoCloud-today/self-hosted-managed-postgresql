#!/bin/bash

if [ "$#" -lt 2 ]; then
    echo "Usage: $0 <database_name> <sql_query>"
    exit 1
fi

DATABASE_NAME=$1
SQL_QUERY=$2
ssh postgres@postgres << EOF
  echo "OUTPUT:"
  psql -d "$DATABASE_NAME" \
       -c "$SQL_QUERY" \
       --quiet \
       --no-psqlrc \
       --no-align \
       --tuples-only \
       --field-separator=","
EOF

if [ $? -ne 0 ]; then
    exit 1
fi