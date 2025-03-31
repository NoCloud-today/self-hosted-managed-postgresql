# Self hosted PostgreSQL management


## How to start?

1. Generate SSH keys:
   ```bash
   ssh-keygen -t rsa -b 4096 -f ssh_keys/id_rsa_postgres
   ssh-keygen -t rsa -b 4096 -f ssh_keys/id_rsa_backup_manager
   ```
2. Create `certs` directory and make certificates 
   ```bash
   mkdir -p certs
   openssl genpkey -algorithm RSA -out certs/private.key -pkeyopt rsa_keygen_bits:2048
   openssl req -new -x509 -key certs/private.key -out certs/public.crt -days 3650 -subj "/CN=minio"
   ```
2. Run docker-compose.yml