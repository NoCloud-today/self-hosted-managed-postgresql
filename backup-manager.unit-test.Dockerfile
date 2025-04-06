FROM python:3.12


RUN apt-get update && apt-get install -y \
    python3-pip \
    postgresql-client

COPY backup-manager/app/ /app

WORKDIR /app
RUN  pip install --no-cache-dir -r requirements.txt
RUN chmod +x scripts/*.sh
ENTRYPOINT  pytest -v --cov=src/services --cov-report=term-missing