#!/bin/bash

CERTS_DIRECTORY="certs"


mkdir -p $CERTS_DIRECTORY/minio

# generate minio certs
openssl genpkey -algorithm RSA -out $CERTS_DIRECTORY/minio/private.key -pkeyopt rsa_keygen_bits:2048
openssl req -new -x509 -key $CERTS_DIRECTORY/minio/private.key -out $CERTS_DIRECTORY/minio/public.crt -days 3650 -subj "/CN=minio"

mkdir -p $CERTS_DIRECTORY/pgbackrest

# generate pgbackrest certs

cd $CERTS_DIRECTORY/pgbackrest || exit 1

openssl genrsa -out pgbackrest-selfsigned-ca.key 4096

openssl req -new -x509 -extensions v3_ca \
    -days 99999 \
    -subj "/CN=backrest-ca" \
    -key pgbackrest-selfsigned-ca.key \
    -out pgbackrest-selfsigned-ca.crt

openssl x509 -in pgbackrest-selfsigned-ca.crt -text -noout

openssl genrsa -out pgbackrest-selfsigned-server.key 4096

openssl req -new -nodes \
    -out pgbackrest-selfsigned-server.csr \
    -key pgbackrest-selfsigned-server.key \
    -config pgbackrest-selfsigned-server.cnf

openssl x509 -req -extensions v3_req  -CAcreateserial \
    -days 99999 \
    -in pgbackrest-selfsigned-server.csr \
    -CA pgbackrest-selfsigned-ca.crt \
    -CAkey pgbackrest-selfsigned-ca.key \
    -out pgbackrest-selfsigned-server.crt \
    -extfile pgbackrest-selfsigned-server.cnf

openssl x509 -in pgbackrest-selfsigned-server.crt -text -noout

openssl genrsa -out pgbackrest-selfsigned-client.key 4096

openssl req -new -nodes \
    -out pgbackrest-selfsigned-client.csr \
    -key pgbackrest-selfsigned-client.key \
    -config pgbackrest-selfsigned-client.cnf

openssl x509 -req -extensions v3_req -CAcreateserial \
    -days 99999 \
    -in pgbackrest-selfsigned-client.csr \
    -CA pgbackrest-selfsigned-ca.crt \
    -CAkey pgbackrest-selfsigned-ca.key \
    -out pgbackrest-selfsigned-client.crt \
    -extfile pgbackrest-selfsigned-client.cnf

openssl x509 -in pgbackrest-selfsigned-client.crt -text -noout