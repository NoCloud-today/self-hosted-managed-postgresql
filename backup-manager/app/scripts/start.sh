#!/bin/bash

docker restart pg

while [ "`docker inspect -f {{.State.Health.Status}} pg`" != "healthy" ]; do     sleep 2; done