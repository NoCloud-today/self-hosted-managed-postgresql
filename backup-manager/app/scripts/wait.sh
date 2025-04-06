#!/bin/bash
echo "Waiting for PostgreSQL to accept connections..."
max_attempts=30
attempt=0

while [ $attempt -lt $max_attempts ]; do
    if ssh postgres@postgres "pg_isready -q" && \
       ssh postgres@postgres "psql -c 'SELECT pg_is_in_recovery()' | grep -q 'f'"; then
        echo "PostgreSQL is ready and accepting read/write transactions"
        exit 0
    fi

    attempt=$((attempt + 1))
    echo "Attempt $attempt of $max_attempts: PostgreSQL not ready yet..."
    sleep 2
done

echo "PostgreSQL did not become ready in time"
exit 1