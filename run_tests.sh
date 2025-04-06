#!/bin/bash

set -e
echo "Starting test environment..."
TEST_DIRECTORY=./test-volume
echo "Running unit tests"
docker build -f "backup-manager.unit-test.Dockerfile" -t backup-manager-unit-test .
docker run --name backup-manager-unit-test-container backup-manager-unit-test || true
TEST_EXIT_CODE=$?
docker rm backup-manager-unit-test-container
echo "Stop running unit tests"
if [  -$TEST_EXIT_CODE -ne 0 ]; then
  echo "Unit tests failed"
  exit $TEST_EXIT_CODE
fi

export DOCKER_VOLUME_DIRECTORY=$TEST_DIRECTORY
BEFORE=$DOCKER_VOLUME_DIRECTORY
DOCKER_VOLUME_DIRECTORY=$BEFORE

docker-compose -f compose.yml -f compose.test.yml up --abort-on-container-exit --force-recreate --build || true
TEST_EXIT_CODE=$?

rm -rf $TEST_DIRECTORY
echo "Cleaning up test environment..."
exit "$TEST_EXIT_CODE"