#!/bin/bash
set -e

ssh postgres@postgres "pgbackrest --log-level-console=info backup --type=diff --stanza=main"
