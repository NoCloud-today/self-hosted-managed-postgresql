#!/bin/bash
set -e

pgbackrest --log-level-console=info backup --type=full --stanza=main --repo=1
