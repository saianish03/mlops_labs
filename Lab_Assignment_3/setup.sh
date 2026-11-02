#!/bin/bash
# One-time setup: make folders and tell Docker which user id to use.
set -e

mkdir -p ./logs ./output
echo "AIRFLOW_UID=$(id -u)" > .env

echo "Setup done. Next: docker compose build && docker compose up -d"
