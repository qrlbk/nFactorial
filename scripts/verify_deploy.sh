#!/usr/bin/env bash
# Usage: ./scripts/verify_deploy.sh https://your-app.vercel.app [https://api.onrender.com]
set -euo pipefail

FRONTEND="${1:?Frontend URL (e.g. https://your-app.vercel.app)}"
API="${2:-}"

FRONTEND="${FRONTEND%/}"

echo "==> Health via Vercel proxy: ${FRONTEND}/api/health"
curl -fsS "${FRONTEND}/api/health" | head -c 500
echo ""

if [[ -n "$API" ]]; then
  API="${API%/}"
  echo "==> Direct API health: ${API}/health"
  curl -fsS "${API}/health" | head -c 500
  echo ""
fi

echo "==> Frontend page (HTTP status)"
code=$(curl -sS -o /dev/null -w "%{http_code}" "${FRONTEND}/en")
echo "GET ${FRONTEND}/en → ${code}"
[[ "$code" == "200" ]] || { echo "Expected 200"; exit 1; }

echo "OK — deployment checks passed."
