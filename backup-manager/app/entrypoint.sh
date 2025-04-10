#!/bin/bash

touch /var/log/app.log

service ssh restart

su backup-manager -c 'ssh-keyscan -H postgres >> /home/backup-manager/.ssh/known_hosts'

service cron start
crontab -u backup-manager /app/app/crontab

tail -f /var/log/app.log & exec su backup-manager -c "uvicorn src.main:app --host 0.0.0.0 --port 8000" >> /var/log/app.log 2>&1