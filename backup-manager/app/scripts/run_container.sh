#!/bin/bash
set -e

CONTAINER_COMMAND=$1
if [ -z "$CONTAINER_COMMAND" ]; then
    echo "Error: Target command is required"
    exit 1
fi

docker run --rm \
  --network=self-hosted-postgresql-management_backup-network \
  --user root \
  --entrypoint bash \
  -e PG_VERSION=$PG_VERSION \
  -v "$POSTGRES_VOLUME_DIRECTORY:/var/lib/postgresql/${PG_VERSION}/main" \
  -v "$POSTGRES_CONFIG:/etc/pgbackrest/" \
  -v "$CERTS_DIRECTORY_FOR_INTERNAL_CONTAINER:/etc/pgbackrest/certs" \
  woblerr/pgbackrest:$BACKREST_VERSION \
  -c "
    $CONTAINER_COMMAND
  "