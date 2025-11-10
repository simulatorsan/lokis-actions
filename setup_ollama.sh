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
  
  echo "Waiting for Ollama service inside the container to be ready..."
  # Wait by running 'ollama list' inside the container until it succeeds.
  until docker exec $CONTAINER_NAME ollama list >/dev/null 2>&1; do
    echo "Waiting for ollama service in $CONTAINER_NAME..."
    sleep 2
  done
  
  echo "Ollama container is up."
fi

# 2. Pull the model using 'docker exec'
echo "Pulling model '$MODEL_TO_PULL'..."
docker exec $CONTAINER_NAME ollama pull $MODEL_TO_PULL

# 3. pip installs
echo "Installing python libraries"
pip3 install requests

echo "Model pull complete."
echo "--- Script Finished ---"

