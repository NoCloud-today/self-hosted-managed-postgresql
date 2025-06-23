#!/bin/bash
set -e

CONTAINER_COMMAND=$1
if [ -z "$CONTAINER_COMMAND" ]; then
    echo "Error: Target command is required"
    exit 1
fi

docker network ls
docker run --rm \
  --network=self-hosted-postgresql-management_backup-network \
  --user root \
  --entrypoint bash \
  -e PG_VERSION="$PG_VERSION" \
  -e PG_CLUSTER="main" \
  -e "BACKREST_HOST_TYPE=tls" \
  -e BACKREST_UID="$BACKREST_UID" \
  -e BACKREST_GID="$BACKREST_GID" \
  -e CONTAINER_COMMAND="$CONTAINER_COMMAND" \
  -v "self-hosted-postgresql-management_postgres_data:/var/lib/postgresql/${PG_VERSION}/main" \
  "andrewbolotsky/pg-pgbackrest:$BACKREST_VERSION" \
  -c "
    echo \"CONTAINER_COMMAND: \$CONTAINER_COMMAND\" && \
    /var/lib/postgresql/pg_prepare.sh \"\$CONTAINER_COMMAND\"
  "