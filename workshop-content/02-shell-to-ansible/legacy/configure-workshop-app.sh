#!/usr/bin/env bash
# Legacy workshop deploy script — intentional candidate for Ansible migration.
# REVIEW: Module 2 owner may replace with a customer-style script; keep path or update Module 3 references.
set -euo pipefail

APP_ROOT="${APP_ROOT:-/var/tmp/workshop-app}"
APP_PORT="${APP_PORT:-8080}"
APP_ENV="${APP_ENV:-dev}"
APP_NAME="${APP_NAME:-workshop-demo}"

mkdir -p "${APP_ROOT}"

{
  echo "port=${APP_PORT}"
  echo "env=${APP_ENV}"
} > "${APP_ROOT}/app.conf"

echo "Configured ${APP_NAME} under ${APP_ROOT}"
