#!/bin/bash
set -e

ssh postgres@postgres 'pgbackrest info --output=json'
