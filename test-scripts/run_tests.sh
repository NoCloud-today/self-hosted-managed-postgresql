#!/bin/bash

set -e
echo "Starting test environment..."
bash run_unit_tests.sh
TEST_EXIT_CODE=$?
if [  -$TEST_EXIT_CODE -ne 0 ]; then
  echo "Unit tests failed"
  exit $TEST_EXIT_CODE
fi
bash run_integration_tests.sh
TEST_EXIT_CODE=$?
if [  -$TEST_EXIT_CODE -ne 0 ]; then
  echo "Integration tests failed"
  exit $TEST_EXIT_CODE
fi
bash run emergency_stop_test.sh
TEST_EXIT_CODE=$?
if [  -$TEST_EXIT_CODE -ne 0 ]; then
  echo "Emergency postgres stop test failed"
  exit $TEST_EXIT_CODE
fi