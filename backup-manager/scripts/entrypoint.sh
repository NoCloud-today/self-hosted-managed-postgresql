#!/bin/bash

service ssh restart

su backup-manager -c 'ssh-keyscan -H postgres >> /home/backup-manager/.ssh/known_hosts'


su backup-manager "service cron start"

exec su backup-manager -c "uvicorn app.main:app --host 0.0.0.0 --port 8000"