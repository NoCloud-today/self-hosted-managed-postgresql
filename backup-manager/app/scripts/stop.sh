#!/bin/bash
set -e
echo "Stopping PostgreSQL..."

docker stop pg-tls
