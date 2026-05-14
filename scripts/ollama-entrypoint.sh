#!/bin/sh
set -eu

MODEL="${LLM_MODEL:-${OLLAMA_MODEL:-gemma4:26b}}"

ollama serve &
OLLAMA_PID="$!"

attempts=0
until ollama list >/dev/null 2>&1; do
  attempts=$((attempts + 1))
  if [ "$attempts" -gt 60 ]; then
    echo "Ollama did not become ready in time." >&2
    kill "$OLLAMA_PID" >/dev/null 2>&1 || true
    exit 1
  fi
  sleep 2
done

if [ -n "$MODEL" ]; then
  echo "Ensuring Ollama model is available: $MODEL"
  ollama pull "$MODEL"
fi

wait "$OLLAMA_PID"
