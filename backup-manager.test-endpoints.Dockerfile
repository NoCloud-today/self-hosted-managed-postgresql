FROM python:3.12


RUN apt-get update && apt-get install -y \
    python3-pip \
    postgresql-client
COPY backup-manager-test/tests /tests

WORKDIR /tests

RUN pip install --no-cache-dir -r requirements.txt
ENTRYPOINT pytest .