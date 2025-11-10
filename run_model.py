import requests
import subprocess
import sys
import time

BASE_URL = "https://molybdous-tatyana-proximately.ngrok-free.dev"
# BASE_URL = "http://127.0.0.1:5000"  # Change to ngrok URL when ready

CONTAINER_NAME = "ollama-gh"
MODEL_NAME = "qwen:0.5b"

def get_prompt():
    """Fetches a new prompt from the remote server."""
    try:
        print(f"Fetching prompt from {BASE_URL}/get_prompt...")
        response = requests.get(f"{BASE_URL}/get_prompt")
        response.raise_for_status() # Raises an error for bad responses (4xx, 5xx)
        
        prompt = response.text
        if not prompt.strip():
            print("no pending job...")
            return
        print(f"Received prompt: '{prompt}'")
        return prompt

    except requests.exceptions.RequestException as e:
        print(f"Error fetching prompt: {e}")

def run_ollama(prompt):
    """
    Runs the prompt against the Ollama container, captures output,
    and returns the combined, filtered result.
    """
    print(f"Running prompt against model '{MODEL_NAME}' in container '{CONTAINER_NAME}'...")
    
    command = [
        "docker", "exec", CONTAINER_NAME,
        "ollama", "run", MODEL_NAME, prompt, "--verbose"
    ]
    
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        
        stdout = result.stdout
        stderr = result.stderr

        # --- Filter stderr to remove junk before "total duration:" ---
        filter_key = "total duration:"
        stats_index = stderr.find(filter_key)
        
        if stats_index != -1:
            filtered_stderr = stderr[stats_index:]
        else:
            filtered_stderr = stderr # Fallback if key isn't found

        print("\n--- Model Output (from stdout) ---")
        print(stdout)
        print("----------------------------------")
        
        print("\n--- Verbose Stats (filtered stderr) ---")
        print(filtered_stderr)
        print("-----------------------------------")

        # --- Combine stdout and filtered stderr ---
        combined_output = f"{stdout}\n{filtered_stderr}"
        return combined_output

    except subprocess.CalledProcessError as e:
        print(f"Error running 'docker exec': {e}", file=sys.stderr)
        print(f"Stderr: {e.stderr}", file=sys.stderr)
        return "error"
    except FileNotFoundError:
        print("Error: 'docker' command not found. Is Docker installed and in the PATH?", file=sys.stderr)
        return "error"

def send_results(prompt, result_text):
    """Sends the combined result back to the server."""
    endpoint = f"{BASE_URL}/return_results"
    # The server reads the prompt from the queue file, so we only need to send the result.
    payload = {
        "result": result_text
    }
    
    try:
        print(f"Sending results to {endpoint}...")
        response = requests.post(
            endpoint,
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        print("Results sent successfully.")
    except requests.exceptions.RequestException as e:
        print(f"Error sending results: {e}", file=sys.stderr)


end_at = time.time() + 3600

from datetime import datetime
print("Ending at:", datetime.fromtimestamp(end_at).strftime("%A, %d %B %Y at %I:%M:%S %p"))

while time.time() < end_at:
    prompt_to_run = get_prompt()
    if prompt_to_run:
        combined_output = run_ollama(prompt_to_run)
        send_results(prompt_to_run, combined_output)
    time.sleep(5)
