#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_PID=""
FRONTEND_PID=""

cleanup() {
  if [[ -n "${BACKEND_PID}" ]] && ps -p "${BACKEND_PID}" >/dev/null 2>&1; then
    kill "${BACKEND_PID}" >/dev/null 2>&1 || true
  fi
  if [[ -n "${FRONTEND_PID}" ]] && ps -p "${FRONTEND_PID}" >/dev/null 2>&1; then
    kill "${FRONTEND_PID}" >/dev/null 2>&1 || true
  fi
}
trap cleanup EXIT

start_backend() {
  cd "${ROOT_DIR}/backend"

  # Load local environment variables if available
  if [[ -f ".env" ]]; then
    # shellcheck disable=SC2046
    export $(grep -v '^#' .env | xargs)
  fi

  export FLASK_APP="${FLASK_APP:-app:create_app}"
  local port="${FLASK_PORT:-5001}"
  echo "Starting backend (Flask) on port ${port}..."
  flask run --debug --port "${port}"
}

start_frontend() {
  cd "${ROOT_DIR}/frontend"
  local port="${VITE_PORT:-5173}"
  echo "Starting frontend (Vite) on port ${port}..."
  npm run dev -- --host --port "${port}"
}

start_backend &
BACKEND_PID=$!

start_frontend &
FRONTEND_PID=$!

sleep 2
open "http://localhost:${VITE_PORT:-5173}" >/dev/null 2>&1 || true

wait
