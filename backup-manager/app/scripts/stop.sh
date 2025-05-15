#!/bin/bash
set -e
echo "Stopping PostgreSQL..."

if docker ps --format '{{.Names}}' | grep -q '^pg$'; then
    echo "Container is running, exec stopping cluster"
    docker stop pg
fi