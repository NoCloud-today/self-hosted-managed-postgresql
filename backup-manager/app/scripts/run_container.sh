#!/bin/bash
set -e

CONTAINER_COMMAND=$1
if [ -z "$CONTAINER_COMMAND" ]; then
    echo "Error: Target command is required"
    exit 1
fi

docker exec pg sh -c "
    ls /var/lib/postgresql/${PG_VERSION}/main && \
    $CONTAINER_COMMAND
  "