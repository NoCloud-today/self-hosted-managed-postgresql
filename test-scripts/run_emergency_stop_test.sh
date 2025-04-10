#!/bin/bash

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

prepare_test_database() {
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
}

verify_restore(){
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
}
wait_for_postgres_container(){
  echo "Waiting for postgres to be ready..."
  sleep 20
}
create_immediate_restore(){
  echo "Performing immediate restore..."
  curl -X POST http://0.0.0.0:8000/restore/immediate
}
create_pitr_restore(){
  echo "Performing pitr restore..."
  curl -X POST http://0.0.0.0:8000/restore/immediate?timestamp="$1"
}
cleanup(){
  echo "Cleaning up..."
  docker compose down -v
  sudo rm -rf "./test-volume"

  echo "Test completed successfully"
}

full_backup_test(){
  prepare_test_database
  echo "Performing full backup..."
  curl -X POST http://0.0.0.0:8000/backup/full

  wait_for_postgres_container
  create_immediate_restore
  verify_restore
  cleanup
}

diff_backup_test(){
  prepare_test_database
  echo "Performing diff backup..."
  curl -X POST http://0.0.0.0:8000/backup/diff

  wait_for_postgres_container
  create_immediate_restore
  verify_restore
  cleanup
}
incr_backup_test(){
  prepare_test_database
  echo "Performing incr backup..."
  curl -X POST http://0.0.0.0:8000/backup/incr

  wait_for_postgres_container
  create_immediate_restore
  verify_restore
  cleanup
}

pitr_incr_backup_test(){
  prepare_test_database
  echo "Performing incr backup..."
  curl -X POST http://0.0.0.0:8000/backup/incr
  TIME_TO_RESTORE=$(date +%s)
  sleep 3
  wait_for_postgres_container
  create_pitr_restore $TIME_TO_RESTORE
  verify_restore
  cleanup
}
pitr_diff_backup_test(){
  prepare_test_database
  echo "Performing incr backup..."
  curl -X POST http://0.0.0.0:8000/backup/diff
  TIME_TO_RESTORE=$(date +%s)
  sleep 3
  wait_for_postgres_container
  create_pitr_restore $TIME_TO_RESTORE
  verify_restore
  cleanup
}
pitr_full_backup_test(){
  prepare_test_database
  echo "Performing incr backup..."
  curl -X POST http://0.0.0.0:8000/backup/full
  TIME_TO_RESTORE=$(date +%s)
  sleep 3
  wait_for_postgres_container
  create_pitr_restore $TIME_TO_RESTORE
  verify_restore
  cleanup
}

if [ $# -eq 0 ]; then
    echo "Error: Please provide a test type"
    echo "Available test types:"
    echo "  full      - Full backup test"
    echo "  diff      - Differential backup test"
    echo "  incr      - Incremental backup test"
    echo "  pitr-incr - Point-in-time recovery with incremental backup"
    echo "  pitr-diff - Point-in-time recovery with differential backup"
    echo "  pitr-full - Point-in-time recovery with full backup"
    exit 1
fi

BEFORE=$DOCKER_VOLUME_DIRECTORY
export DOCKER_VOLUME_DIRECTORY="./test-volume"

case "$1" in
    "full")
        full_backup_test
        ;;
    "diff")
        diff_backup_test
        ;;
    "incr")
        incr_backup_test
        ;;
    "pitr-incr")
        pitr_incr_backup_test
        ;;
    "pitr-diff")
        pitr_diff_backup_test
        ;;
    "pitr-full")
        pitr_full_backup_test
        ;;
    *)
        echo "Error: Unknown test type '$1'"
        echo "Available test types:"
        echo "  full      - Full backup test"
        echo "  diff      - Differential backup test"
        echo "  incr      - Incremental backup test"
        echo "  pitr-incr - Point-in-time recovery with incremental backup"
        echo "  pitr-diff - Point-in-time recovery with differential backup"
        echo "  pitr-full - Point-in-time recovery with full backup"
        exit 1
        ;;
esac

DOCKER_VOLUME_DIRECTORY=$BEFORE