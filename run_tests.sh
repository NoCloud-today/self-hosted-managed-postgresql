#!/bin/bash

set -e
echo "Starting test environment..."
bash test-scripts/run_unit_tests.sh
TEST_EXIT_CODE=$?
if [  -$TEST_EXIT_CODE -ne 0 ]; then
  echo "Unit tests failed"
  exit $TEST_EXIT_CODE
fi
bash test-scripts/run_e2e_tests.sh
TEST_EXIT_CODE=$?
if [  -$TEST_EXIT_CODE -ne 0 ]; then
  echo "e2e tests failed"
  exit $TEST_EXIT_CODE
fi
bash test-scripts/run_emergency_stop_test.sh pitr-full
bash test-scripts/run_emergency_stop_test.sh pitr-diff
bash test-scripts/run_emergency_stop_test.sh pitr-incr
bash test-scripts/run_emergency_stop_test.sh pitr-empty

TEST_EXIT_CODE=$?
if [  -$TEST_EXIT_CODE -ne 0 ]; then
  echo "Emergency postgres stop test failed"
  exit $TEST_EXIT_CODE
fi