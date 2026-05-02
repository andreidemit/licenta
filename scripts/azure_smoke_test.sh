#!/usr/bin/env bash
set -euo pipefail

FRONTEND_URL="${FRONTEND_URL:-}"
BACKEND_URL="${BACKEND_URL:-}"

if [[ -z "$FRONTEND_URL" || -z "$BACKEND_URL" ]]; then
  echo "Usage: FRONTEND_URL=https://<app>.azurestaticapps.net BACKEND_URL=https://<api>.azurecontainerapps.io $0" >&2
  exit 2
fi

FRONTEND_URL="${FRONTEND_URL%/}"
BACKEND_URL="${BACKEND_URL%/}"

echo "== Backend health =="
curl --fail --silent "${BACKEND_URL}/api/health" | grep -q '"status":"ok"'

echo "== Backend scenarios =="
curl --fail --silent "${BACKEND_URL}/api/scenarios" | grep -q '"scenarios"'

echo "== Frontend routes =="
for route in "/" "/antrenare" "/evaluare" "/rulari" "/comparatie"; do
  curl --fail --silent --location "${FRONTEND_URL}${route}" | grep -q '<div id="root">'
  echo "route ok: ${route}"
done

echo "== CORS preflight =="
curl --fail --silent --output /dev/null \
  -H "Origin: ${FRONTEND_URL}" \
  -H "Access-Control-Request-Method: GET" \
  -X OPTIONS \
  "${BACKEND_URL}/api/health"

echo "Azure smoke checks passed."
