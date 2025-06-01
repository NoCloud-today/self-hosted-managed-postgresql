FROM python:3.12

WORKDIR /app

COPY backup-manager /app

RUN pip install --no-cache-dir -r requirements.txt --break-system-packages

RUN pip install -e . --no-cache-dir --break-system-packages

RUN chmod +x scripts/*.sh

ENTRYPOINT ["pytest"]