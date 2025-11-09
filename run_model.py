import requests
import subprocess
import sys

# --- Configuration ---

# !! IMPORTANT !!
# Replace this with your public URL from ngrok
# (or whatever tunnelling service you use).
BASE_URL = "https://MY_NGROK_URL.ngrok.io"

CONTAINER_NAME = "ollama-gh"
MODEL_NAME = "qwen:0.5b"

def get_prompt():
    """Fetches a new prompt from the remote server."""
    try:
        print(f"Fetching prompt from {BASE_URL}/get_prompt...")
        response = requests.get(f"{BASE_URL}/get_prompt")
        response.raise_for_status() # Raises an error for bad responses (4xx, 5xx)
        
        # Assuming the server returns the prompt as plain text
        prompt = response.text
        print(f"Received prompt: '{prompt}'")
        return prompt

    except requests.exceptions.RequestException as e:
        print(f"Error fetching prompt: {e}", file=sys.stderr)
        return "what colour is the sky"
        # sys.exit(1)

def run_ollama(prompt):
    """Runs the prompt against the Ollama container using 'docker exec'."""
    print(f"Running prompt against model '{MODEL_NAME}' in container '{CONTAINER_NAME}'...")
    
    # This is the command we will run, broken into a list
    command = [
        "docker", "exec", CONTAINER_NAME,
        "ollama", "run", MODEL_NAME, "--verbose", prompt
    ]
    
    try:
        # Run the command, capture its output, and print it
        # We use 'subprocess.run' which is simpler than Popen
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        
        print("\n--- Model Output ---")
        print(result.stdout)
        print("--------------------")

    except subprocess.CalledProcessError as e:
        print(f"Error running 'docker exec': {e}", file=sys.stderr)
        print(f"Stderr: {e.stderr}", file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError:
        print("Error: 'docker' command not found. Is Docker installed and in the PATH?", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    prompt_to_run = get_prompt()
    if prompt_to_run:
        run_ollama(prompt_to_run)