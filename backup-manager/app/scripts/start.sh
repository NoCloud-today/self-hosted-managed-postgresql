#!/bin/bash

echo "Starting pg container"
docker start pg

timeout 30s sh -c 'while [ "`docker inspect -f {{.State.Health.Status}} pg`" != "healthy" ]; do     sleep 2; done'