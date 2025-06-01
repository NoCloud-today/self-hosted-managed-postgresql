#!/bin/bash
set -e

pgbackrest --log-level-console=info backup --type=diff --stanza=main --repo=1
