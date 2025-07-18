#!/bin/bash
TEST_DIRECTORY="./test-volume"
BEFORE=$DOCKER_VOLUME_DIRECTORY
export DOCKER_VOLUME_DIRECTORY=$TEST_DIRECTORY

docker compose  -f compose.s3.yml up --wait --build  --force-recreate
docker compose  -f compose.yml up --wait --build  --force-recreate

timeout 300s sh -c 'while [ "`docker inspect -f {{.State.Health.Status}} backup-manager`" != "healthy" ]; do     sleep 2; done'
docker compose  -f compose.test.yml up --abort-on-container-exit --force-recreate --build
TEST_EXIT_CODE=$?
DOCKER_VOLUME_DIRECTORY=$BEFORE
sudo rm -rf $TEST_DIRECTORY

docker logs pg
docker logs backup-manager
docker compose -f compose.yml down -v
docker compose -f compose.test.yml down -v
docker compose -f compose.s3.yml down -v
echo "Cleaning up test environment..."
exit $TEST_EXIT_CODE