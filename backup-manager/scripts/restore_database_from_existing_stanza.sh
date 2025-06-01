#!/bin/bash
set -e

./stop.sh

./run_container.sh "pgbackrest --stanza=main --log-level-console=info --delta --recovery-option=recovery_target=immediate --target-action=promote --type=immediate restore"

./start.sh

pgbackrest --log-level-console=info backup --type=full --stanza=main --repo=1
pgbackrest --log-level-console=info backup --type=full --stanza=main --repo=2
