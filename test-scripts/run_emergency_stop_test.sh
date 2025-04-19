#!/bin/bash

wait_for_health() {
    local max_attempts=30
    local attempt=0
    echo "Waiting for health check to pass..."
    while [ $attempt -lt $max_attempts ]; do
        attempt=$((attempt + 1))

        if curl -s -f http://0.0.0.0:8000/health > /dev/null; then
            curl -s -f http://0.0.0.0:8000/health
            echo "Health check passed"
            return 0
        fi

        sleep 1
    done
}

start_containers(){
  echo "Starting containers..."
  docker compose -f compose.s3.yml up  -d --wait
  docker compose -f compose.yml up -d --build

  echo "Waiting for containers to be healthy..."
  wait_for_health
}
prepare_test_database() {
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

verify_that_database_could_accept_write_transactions(){
  echo "Inserting data for testing that database could accept write transactions..."
  curl -X POST http://0.0.0.0:8000/database/run \
    -H "Content-Type: application/json" \
    -d '{"query": "INSERT INTO test_table(id) VALUES (3),(4)", "database_name": "test_database"}'
}
insert_data_which_should_not_be_in_recovery(){
  echo "Inserting test data, which should not be in restored data..."
  curl -X POST http://0.0.0.0:8000/database/run \
    -H "Content-Type: application/json" \
    -d '{"query": "INSERT INTO test_table(id) VALUES (5),(6)", "database_name": "test_database"}'
}
verify_restore_second(){
  echo "Verifying restored data..."
  EXPECTED_RESPONSE='{"message":"SQL executed successfully","result":"1\n2\n3\n4"}'
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
create_immediate_restore(){
  echo "Performing immediate restore..."
  curl -X POST http://0.0.0.0:8000/restore/immediate
}
create_pitr_restore(){
  echo "Performing pitr restore..."
  curl -X POST http://0.0.0.0:8000/restore/immediate?timestamp="$1"
}
delete_postgres_container(){
  echo "Killing postgres container"
  docker kill postgres
  echo "Removing all from directory $DOCKER_VOLUME_DIRECTORY/postgres_data"
  ls "$DOCKER_VOLUME_DIRECTORY/postgres_data"
  sudo rm -rf "$DOCKER_VOLUME_DIRECTORY/postgres_data"
  echo "After removing: "
  ls -a "$DOCKER_VOLUME_DIRECTORY"

  docker start postgres

  sleep 20
}
cleanup(){
  echo "Cleaning up..."
  docker compose logs postgres
  docker compose logs backup-manager

  docker compose -f compose.yml down -v
  docker compose -f compose.s3.yml down -v
  sudo rm -rf "./test-volume"

}

pitr_incr_backup_test(){
  start_containers
  prepare_test_database
  echo "Performing full backup..."
  curl -X POST http://0.0.0.0:8000/backup/incr
  delete_postgres_container
  verify_restore
  verify_that_database_could_accept_write_transactions
  curl -X POST http://0.0.0.0:8000/backup/incr
  sleep 3
  TIME_TO_RESTORE=$(date +%s)
  sleep 3
  insert_data_which_should_not_be_in_recovery
  create_pitr_restore $TIME_TO_RESTORE
  verify_restore_second
  cleanup
}
pitr_diff_backup_test(){
  start_containers
  prepare_test_database
  echo "Performing full backup..."
  curl -X POST http://0.0.0.0:8000/backup/diff
  delete_postgres_container
  verify_restore
  verify_that_database_could_accept_write_transactions
  curl -X POST http://0.0.0.0:8000/backup/full
  sleep 3
  TIME_TO_RESTORE=$(date +%s)
  sleep 3
  insert_data_which_should_not_be_in_recovery
  create_pitr_restore $TIME_TO_RESTORE
  verify_restore_second
  cleanup
}
pitr_full_backup_test(){
  start_containers
  prepare_test_database
  echo "Performing full backup..."
  curl -X POST http://0.0.0.0:8000/backup/full
  delete_postgres_container
  verify_restore
  verify_that_database_could_accept_write_transactions
  curl -X POST http://0.0.0.0:8000/backup/incr
  sleep 3
  TIME_TO_RESTORE=$(date +%s)
  sleep 3
  insert_data_which_should_not_be_in_recovery
  create_pitr_restore $TIME_TO_RESTORE
  verify_restore_second
  cleanup
}
pitr_to_empty_cluster(){
  start_containers
  echo "Performing incr backup..."
  curl -X POST http://0.0.0.0:8000/backup/incr
  sleep 3
  TIME_TO_RESTORE=$(date +%s)
  sleep 3
  create_pitr_restore $TIME_TO_RESTORE
  prepare_test_database
  verify_restore
  cleanup
}
if [ $# -eq 0 ]; then
    echo "Error: Please provide a test type"
    echo "Available test types:"
    echo "  pitr-incr - Point-in-time recovery with incremental backup"
    echo "  pitr-diff - Point-in-time recovery with differential backup"
    echo "  pitr-full - Point-in-time recovery with full backup"
    echo "  pitr-empty - Point-in-time recovery in empty cluster"
    exit 1
fi

BEFORE=$DOCKER_VOLUME_DIRECTORY
export DOCKER_VOLUME_DIRECTORY="./test-volume"
cleanup
case "$1" in
    "pitr-incr")
        pitr_incr_backup_test
        ;;
    "pitr-diff")
        pitr_diff_backup_test
        ;;
    "pitr-empty")
        pitr_to_empty_cluster
        ;;
    "pitr-full")
        pitr_full_backup_test
        ;;
    *)
        echo "Error: Unknown test type '$1'"
        echo "Available test types:"
        echo "  pitr-incr - Point-in-time recovery with incremental backup"
        echo "  pitr-diff - Point-in-time recovery with differential backup"
        echo "  pitr-full - Point-in-time recovery with full backup"
        echo "  pitr-empty - Point-in-time recovery in empty cluster"
        exit 1
        ;;
esac
echo "Test completed successfully"
DOCKER_VOLUME_DIRECTORY=$BEFORE