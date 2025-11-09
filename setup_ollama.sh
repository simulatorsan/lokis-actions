#!/bin/bash
set -e # Exit immediately if a command exits with a non-zero status.

# --- Configuration ---
CONTAINER_NAME="ollama-gh"
HOST_PORT="11435"
MODEL_TO_PULL="qwen:0.5b"
API_URL="http://localhost:$HOST_PORT"

# --- Logic ---
echo "--- Ollama Setup Script ---"

# 1. Check if container is already running
if [ "$(docker ps -q -f "name=$CONTAINER_NAME" -f "status=running")" ]; then
  echo "Container '$CONTAINER_NAME' is already running on port $HOST_PORT. Skipping start."
else
  echo "Container '$CONTAINER_NAME' not found or not running. Starting it..."
  
  # Attempt to remove any stopped container with the same name first
  docker rm $CONTAINER_NAME || true
  
  echo "Starting $CONTAINER_NAME container on host port $HOST_PORT..."
  docker run -d -p $HOST_PORT:11434 \
    --name $CONTAINER_NAME \
    ollama/ollama
  
  echo "Waiting for Ollama API to be ready at $API_URL..."
  until curl --fail --silent --output /dev/null $API_URL; do
    echo "Waiting..."
    sleep 1
  done
  
  echo "Ollama container is up."
fi

# 2. Pull the model
echo "Pulling model '$MODEL_TO_PULL'..."
curl $API_URL/api/pull -d '{
  "name": "'"$MODEL_TO_PULL"'"
}'
echo "Model pull complete."
echo "--- Script Finished ---"
