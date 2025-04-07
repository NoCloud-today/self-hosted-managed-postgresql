#!/bin/bash
echo "Running unit tests"
docker build -f "../backup-manager.unit-test.Dockerfile" -t backup-manager-unit-test ..
docker run --name backup-manager-unit-test-container backup-manager-unit-test
TEST_EXIT_CODE=$?
docker rm backup-manager-unit-test-container
echo "Stop running unit tests"
exit $TEST_EXIT_CODE