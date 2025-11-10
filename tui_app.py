import requests
import chalk

BASE_URL = "http://127.0.0.1:5000"  # Flask server URL

# Check if the server is running
if requests.get(f"{BASE_URL}/").text != "ok":
    raise RuntimeError("Server not running or returned unexpected response.")

while True:
    # Use colored 'Prompt' label (chalk.green)
    prompt = input(chalk.green("Prompt:") + " ")
    if prompt == "/bye":
        print(chalk.cyan("Goodbye!"))
        break

    # Send prompt to server via POST with JSON body
    response = requests.post(
        f"{BASE_URL}/get_response",
        json={"prompt": prompt},
        headers={"Content-Type": "application/json"}
    )
    if response.status_code == 200:
        server_response = response.text
        if server_response.lower() == "none":
            server_response = "Server didn't respond"
        print(chalk.yellow("Response:") + " " + server_response + "\n")
    else:
        print(chalk.red(f"Error: {response.status_code} - {response.text}\n"))
