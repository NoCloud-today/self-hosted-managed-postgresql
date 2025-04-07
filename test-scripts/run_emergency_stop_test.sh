#!/bin/bash

TEST_DIRECTORY="./test-volume"
BEFORE=$DOCKER_VOLUME_DIRECTORY
export DOCKER_VOLUME_DIRECTORY=$TEST_DIRECTORY

wait_for_health() {
    local max_attempts=30
    local attempt=0
    echo "Waiting for health check to pass..."
    
    while [ $attempt -lt $max_attempts ]; do
        attempt=$((attempt + 1))

        if curl -s -f http://0.0.0.0:8000/health > /dev/null; then
            echo "Health check passed"
            return 0
        fi
        
        sleep 1
    done
    attempt=0
}

echo "Starting containers..."
docker compose up -d --build

echo "Waiting for containers to be healthy..."
wait_for_health

echo "Creating test database..."
curl -X POST http://0.0.0.0:8000/database/run \
  -H "Content-Type: application/json" \
  -d '{"query": "CREATE database test_database"}'

echo "Creating test table..."
curl -X POST http://0.0.0.0:8000/database/run \
  -H "Content-Type: application/json" \
  -d '{"query": "CREATE table test_table(id bigint)", "database_name": "test_database"}'

echo "Inserting test data..."
curl -X POST http://0.0.0.0:8000/database/run \
  -H "Content-Type: application/json" \
  -d '{"query": "INSERT INTO test_table(id) VALUES (1),(2)", "database_name": "test_database"}'

echo "Performing full backup..."
curl -X POST http://0.0.0.0:8000/backup/full

echo "Stopping postgres container..."
docker compose stop postgres

echo "Deleting postgres data..."
rm -rf $TEST_DIRECTORY/postgres_data/*

echo "Starting postgres container..."
docker compose start postgres

echo "Waiting for postgres to be ready..."
wait_for_health
sleep 20
echo "Performing immediate restore..."
curl -X POST http://0.0.0.0:8000/restore/immediate

echo "Verifying restored data..."
EXPECTED_RESPONSE='{"message":"SQL executed successfully","result":"1\n2"}'
ACTUAL_RESPONSE=$(curl -s -X POST http://0.0.0.0:8000/database/run \
  -H "Content-Type: application/json" \
  -d '{"query": "SELECT * from test_table", "database_name": "test_database"}')

if [ "$ACTUAL_RESPONSE" != "$EXPECTED_RESPONSE" ]; then
    echo "Test failed: Restored data verification failed"
    echo "Expected: $EXPECTED_RESPONSE"
    echo "Got: $ACTUAL_RESPONSE"
    exit 1
fi

echo "Data verification successful"

echo "Cleaning up..."
docker compose down -v
sudo rm -rf $TEST_DIRECTORY

DOCKER_VOLUME_DIRECTORY=$BEFORE

echo "Test completed successfully" 