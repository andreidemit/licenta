#!/usr/bin/env bash
set -euo pipefail

PYTHON_BIN="${PYTHON_BIN:-python3}"
IMAGE_NAME="${IMAGE_NAME:-qlearning-backend}"
HOST_PORT="${HOST_PORT:-8000}"

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

cd "$ROOT_DIR"

echo "== Python API tests =="
"$PYTHON_BIN" -m tests.test_web_api

echo "== Python compile check =="
"$PYTHON_BIN" -m compileall -q src web/backend tests

echo "== Frontend build =="
(cd web/frontend && npm run build)

if ! command -v docker >/dev/null 2>&1; then
  echo "Docker CLI is required for image validation." >&2
  exit 1
fi

echo "== Docker build =="
docker build -t "$IMAGE_NAME" .

echo "== Docker run smoke =="
container_id="$(
  docker run -d --rm \
    -p "${HOST_PORT}:8000" \
    -e APP_ENV=production \
    -e HOST=0.0.0.0 \
    -e PORT=8000 \
    -e DATA_ROOT=/app/data \
    -v "${ROOT_DIR}/data:/app/data" \
    "$IMAGE_NAME"
)"

cleanup() {
  docker stop "$container_id" >/dev/null 2>&1 || true
}
trap cleanup EXIT

for _ in {1..30}; do
  if curl --fail --silent "http://127.0.0.1:${HOST_PORT}/api/health" >/dev/null; then
    echo "Backend health check passed."
    exit 0
  fi
  sleep 1
done

echo "Backend health check failed." >&2
docker logs "$container_id" >&2 || true
exit 1
