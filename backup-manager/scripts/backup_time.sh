#!/bin/bash
set -e

pgbackrest --log-level-console=info  backup --type=incr --stanza=main
