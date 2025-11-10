
import json
import time
from pathlib import Path
import os

from flask import Flask, request, jsonify


app = Flask(__name__)

# Create tempfiles directory if it doesn't exist
TEMP_DIR = Path("tempfiles")
TEMP_DIR.mkdir(exist_ok=True)

QUEUE_FILE = TEMP_DIR / "queue.txt"
RESULTS_FILE = TEMP_DIR / "results.jsonl"

# Ensure files exist
QUEUE_FILE.touch()
RESULTS_FILE.touch()


@app.route('/')
def index():
    return "ok"

@app.route('/get_prompt')
def get_prompt():
    # Return the contents of the queue file
    with QUEUE_FILE.open() as f:
        return f.read().strip()

@app.route('/return_results', methods=['POST'])
def return_results():
    data = request.get_json()
    prompt = data.get('prompt')
    result = data.get('result')

    with QUEUE_FILE.open() as f:
        prompt = f.read().strip()

    # Append prompt and result to the results file
    with RESULTS_FILE.open("a") as f:
        user_entry = {"role": "user", "content": prompt}
        assistant_entry = {"role": "assistant", "content": result}
        f.write(json.dumps(user_entry) + "\n")
        f.write(json.dumps(assistant_entry) + "\n")

    return "ok"


@app.route('/get_response', methods=['POST'])
def get_response():
    data = request.get_json()
    prompt = data.get('prompt')

    if not prompt: return
    
    with RESULTS_FILE.open("r") as f:
        initial_line_number = len(f.read().split("\n"))

    with QUEUE_FILE.open("a") as f:
        f.write(prompt + "\n")

    # Poll the results file for the response
    while True:
        with RESULTS_FILE.open("r") as f:
            lines = f.read().split("\n")
            if len(lines) <= initial_line_number+1:  # we should have at least 2 new lines
                time.sleep(1)
                continue
            else:
                lines = lines[initial_line_number:]
                assert len(lines) == 2, "Expected exactly 2 new lines in results file, run only 1 client at a time."
                
        # if the first line in lines matches the prompt, return the second line as response
        user_entry = json.loads(lines[0])
        assistant_entry = json.loads(lines[1])
        response = None
        if user_entry["content"] == prompt:
            response = assistant_entry["content"]
            # Clean up the queue file by making it an empty file again
            with QUEUE_FILE.open("w") as f:
                f.write("")

        return response or "none"


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
