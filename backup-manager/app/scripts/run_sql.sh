#!/bin/bash

if [ "$#" -lt 2 ]; then
    echo "Usage: $0 <database_name> <sql_query>"
    exit 1
fi

DATABASE_NAME=$1
SQL_QUERY=$2
echo "OUTPUT:"
PGPASSWORD=$POSTGRES_PASSWORD psql -d "$DATABASE_NAME" \
   -c "$SQL_QUERY" \
   -U postgres \
   -h pg-tls \
   --quiet \
   --no-psqlrc \
   --no-align \
   --tuples-only \
   --field-separator=","

if [ $? -ne 0 ]; then
    exit 1
fi