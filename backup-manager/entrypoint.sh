#!/bin/bash

touch /var/log/app.log

service ssh restart

su backup-manager -c 'ssh-keyscan -H postgres >> /home/backup-manager/.ssh/known_hosts'

service cron restart

tail -f /var/log/app.log & exec su backup-manager -c "uvicorn app.src.main:app --host 0.0.0.0 --port 8000 --log-config log_config.json" >> /var/log/app.log 2>&1