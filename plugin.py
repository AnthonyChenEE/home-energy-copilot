import json, requests

# Load configuration
CONFIG_PATH = "config.json"
with open(CONFIG_PATH, "r") as f:
    config = json.load(f)

IFTTT_KEY = config.get("IFTTT_KEY")
DEVICE_TOPICS = config.get("DEVICE_TOPICS")

def send_ifttt_event(event_name, value1=None, value2=None):
    url = f"https://maker.ifttt.com/trigger/{event_name}/with/key/{IFTTT_KEY}"
    payload = {"value1": value1, "value2": value2}
    response = requests.post(url, json=payload)
    print(f"Sent {event_name} with {value1}, {value2} - Status: {response.status_code}")

def handle_command(command, args=None):
    if command == "optimize_energy":
        print("Optimizing energy usage based on price schedule...")
        send_ifttt_event("optimize_energy")
    elif command == "turn_on_device":
        device = args.get("device")
        send_ifttt_event("turn_on_device", device)
        print(f"{device} turned ON.")
    elif command == "turn_off_device":
        device = args.get("device")
        send_ifttt_event("turn_off_device", device)
        print(f"{device} turned OFF.")
    else:
        print(f"Unknown command: {command}")

# Main entry point for testing
if __name__ == "__main__":
    print("Home Energy Copilot started. Waiting for commands...")
    while True:
        cmd = input("Command: ").strip()
        if cmd in ["exit", "quit"]:
            break
        handle_command(cmd, {"device": "lamp"})