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
        return None # Return None on failure
    except FileNotFoundError:
        print("Error: 'docker' command not found. Is Docker installed and in the PATH?", file=sys.stderr)
        return None # Return None on failure

def send_results(prompt, result_text):
    """Sends the prompt and the combined result back to the server."""
    endpoint = f"{BASE_URL}/return_results"
    payload = {
        "prompt": prompt,
        "result": result_text
    }
    
    try:
        print(f"Sending results to {endpoint}...")
        response = requests.post(endpoint, json=payload)
        response.raise_for_status()
        print("Results sent successfully.")
    except requests.exceptions.RequestException as e:
        print(f"Error sending results: {e}", file=sys.stderr)

if __name__ == "__main__":
    prompt_to_run = get_prompt()
    if prompt_to_run:
        combined_output = run_ollama(prompt_to_run)
        
        if combined_output:
            send_results(prompt_to_run, combined_output)