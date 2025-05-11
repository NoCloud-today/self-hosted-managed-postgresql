#!/bin/bash
set -e
echo "Stopping PostgreSQL..."

if docker ps --format '{{.Names}}' | grep -q '^pg$'; then
    echo "Container is running, exec stopping cluster"
    docker exec pg sh -c "pg_ctlcluster \${PG_VERSION} \${PG_CLUSTER} stop" || true
fi