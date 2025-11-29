#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/.."
if [ -f .venv/bin/activate ]; then
  source .venv/bin/activate
fi

pip install -r requirements.txt

# Requires prisma CLI available; install with: pip install prisma
prisma generate
prisma migrate deploy

echo "Migrations applied."
