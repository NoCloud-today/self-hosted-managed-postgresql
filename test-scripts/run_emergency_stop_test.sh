#!/bin/bash

wait_for_health() {
    local max_attempts=30
    local attempt=0
    echo "Waiting for health check to pass..."
    timeout 120s sh -c 'while [ "`docker inspect -f {{.State.Health.Status}} backup-manager`" != "healthy" ]; do     sleep 2; done'
}

start_containers(){
  echo "Starting containers..."
  docker compose -f compose.s3.yml up  -d --wait --force-recreate
  docker compose -f compose.yml up -d --build --force-recreate

  echo "Waiting for containers to be healthy..."
  wait_for_health
}
prepare_test_database() {
  echo "Creating test database..."
  curl --location --request POST 'http://0.0.0.0:8000/database?database_name=testdb'
  echo "Creating test table..."
  curl -X POST http://0.0.0.0:8000/database/run \
    -H "Content-Type: application/json" \
    -d '{"query": "CREATE table test_table(id bigint)", "database_name": "testdb"}'

  echo "Inserting test data..."
  curl -X POST http://0.0.0.0:8000/database/run \
    -H "Content-Type: application/json" \
    -d '{"query": "INSERT INTO test_table(id) VALUES (1),(2)", "database_name": "testdb"}'
}

verify_that_database_could_accept_write_transactions(){
  echo "Inserting data for testing that database could accept write transactions..."
  curl -X POST http://0.0.0.0:8000/database/run \
    -H "Content-Type: application/json" \
    -d '{"query": "INSERT INTO test_table(id) VALUES (3),(4)", "database_name": "testdb"}'
}
insert_data_which_should_not_be_in_recovery(){
  echo "Inserting test data, which should not be in restored data..."
  curl -X POST http://0.0.0.0:8000/database/run \
    -H "Content-Type: application/json" \
    -d '{"query": "INSERT INTO test_table(id) VALUES (5),(6)", "database_name": "testdb"}'
}
verify_restore_second(){
  echo "Verifying restored data..."
  EXPECTED_RESPONSE='{"message":"SQL executed successfully","result":[[1],[2],[3],[4]]}'
  ACTUAL_RESPONSE=$(curl -s -X POST http://0.0.0.0:8000/database/run \
    -H "Content-Type: application/json" \
    -d '{"query": "SELECT * from test_table", "database_name": "testdb"}')

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
  EXPECTED_RESPONSE='{"message":"SQL executed successfully","result":[[1],[2]]}'
  ACTUAL_RESPONSE=$(curl -s -X POST http://0.0.0.0:8000/database/run \
    -H "Content-Type: application/json" \
    -d '{"query": "SELECT * from test_table", "database_name": "testdb"}')

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
  docker network ls
  curl -X POST http://0.0.0.0:8000/restore/immediate
}
create_pitr_restore(){
  echo "Performing pitr restore..."
  docker network ls
  curl -X POST http://0.0.0.0:8000/restore/time?timestamp="$1"
}
delete_postgres_container(){
  echo "Killing postgres container"
  docker kill pg

  docker run --rm -v self-hosted-postgresql-management_postgres_data:/volume busybox sh -c "rm -rf /volume/*"

  docker start pg

  timeout 40s sh -c 'while [ "`docker inspect -f {{.State.Health.Status}} pg`" != "healthy" ]; do     sleep 2; done'
  docker network ls
  curl -X POST http://0.0.0.0:8000/restore/existing

}
cleanup(){
  echo "Cleaning up..."
  docker compose logs pg
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
  create_immediate_restore

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