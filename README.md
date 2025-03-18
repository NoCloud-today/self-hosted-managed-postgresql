# Self hosted PostgreSQL management


## How to start?

1. Generate SSH keys:
   ```bash
   ssh-keygen -t rsa -b 4096 -f ssh_keys/id_rsa_postgres
   ssh-keygen -t rsa -b 4096 -f ssh_keys/id_rsa_backup_manager
   ```

2. Run docker-compose.yml