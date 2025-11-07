import json
import datetime
import requests

CONFIG_PATH = "config.json"


def load_config(path: str = CONFIG_PATH) -> dict:
    """Load configuration from JSON file."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            config = json.load(f)
    except FileNotFoundError:
        raise RuntimeError(
            f"Config file '{path}' not found. Please create it based on config.json template."
        )
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Failed to parse '{path}': {e}")
    return config


config = load_config()
IFTTT_KEY = config.get("IFTTT_KEY")
DEVICE_TOPICS = config.get("DEVICE_TOPICS", {})
TARIFF_CONFIG = config.get("TARIFF_CONFIG", {})


def send_ifttt_event(event_name: str, value1=None, value2=None):
    """
    Trigger an IFTTT Webhook event.

    event_name: Name of the IFTTT event (must match your IFTTT applet).
    value1, value2: Optional payload values.
    """
    if not IFTTT_KEY:
        print("[ERROR] IFTTT_KEY is not set in config.json")
        return

    url = f"https://maker.ifttt.com/trigger/{event_name}/with/key/{IFTTT_KEY}"
    payload = {"value1": value1, "value2": value2}

    try:
        response = requests.post(url, json=payload, timeout=5)
        print(
            f"[INFO] Sent IFTTT event='{event_name}' value1='{value1}' "
            f"status={response.status_code}"
        )
    except requests.RequestException as e:
        print(f"[ERROR] Failed to send IFTTT event '{event_name}': {e}")


class DeviceController:
    """
    High-level controller for home devices (including EV charger).
    """

    def __init__(self, device_topics: dict):
        self.device_topics = device_topics

    def turn_on(self, device_name: str):
        """
        Turn on a device via IFTTT.
        """
        print(f"[ACTION] Turning ON device='{device_name}'")
        # Here device_name is passed to IFTTT; the applet maps this to real device
        send_ifttt_event("turn_on_device", device_name)

    def turn_off(self, device_name: str):
        """
        Turn off a device via IFTTT.
        """
        print(f"[ACTION] Turning OFF device='{device_name}'")
        send_ifttt_event("turn_off_device", device_name)

    def optimize_home_energy(self, mode: str = "eco"):
        """
        Simple home energy optimization:
        - In 'eco' mode, turn off non-critical devices during peak hours.
        - In 'comfort' mode, be less aggressive.
        This is a placeholder for more advanced MPC/optimization.
        """
        now = datetime.datetime.now()
        hour = now.hour
        print(f"[INFO] Running home energy optimization at {hour:02d}:00, mode={mode}")

        low_start = TARIFF_CONFIG.get("LOW_TARIFF_START", 22)
        low_end = TARIFF_CONFIG.get("LOW_TARIFF_END", 7)

        in_low_tariff = (hour >= low_start) or (hour < low_end)

        if mode == "eco":
            if not in_low_tariff:
                # Example: turn off some non-critical devices
                for dev in ["lamp", "ac"]:
                    if dev in self.device_topics:
                        self.turn_off(dev)
                print("[INFO] Eco mode: turned off non-critical devices during peak hours.")
            else:
                print("[INFO] Eco mode: low-tariff period, keeping devices as-is.")
        elif mode == "comfort":
            print("[INFO] Comfort mode: no aggressive actions taken.")
        else:
            print(f"[WARN] Unknown home energy mode='{mode}'")

    def optimize_ev_charging(self, mode: str = "auto"):
        """
        EV charging optimization strategy.

        - 'auto': start charging only during low-tariff hours.
        - 'force_on': immediately start charging.
        - 'force_off': immediately stop charging.
        """
        charger_name = "charger"  # logical name used in config & IFTTT
        now = datetime.datetime.now()
        hour = now.hour

        low_start = TARIFF_CONFIG.get("LOW_TARIFF_START", 22)
        low_end = TARIFF_CONFIG.get("LOW_TARIFF_END", 7)

        in_low_tariff = (hour >= low_start) or (hour < low_end)

        print(
            f"[INFO] EV charging request at {hour:02d}:00, mode={mode}, "
            f"low-tariff window=[{low_start}:00–{low_end}:00)"
        )

        if mode == "force_on":
            self.turn_on(charger_name)
            print("[INFO] EV charging: force_on → charger turned ON.")
            return

        if mode == "force_off":
            self.turn_off(charger_name)
            print("[INFO] EV charging: force_off → charger turned OFF.")
            return

        # auto mode
        if in_low_tariff:
            print("[INFO] EV charging: inside low-tariff window → starting charge.")
            self.turn_on(charger_name)
        else:
            print("[INFO] EV charging: peak hours → delaying charge.")
            self.turn_off(charger_name)


def handle_command(controller: DeviceController, command: str, args: dict | None = None):
    """
    Main command dispatcher used by G-Assist and local debug mode.
    """
    args = args or {}
    print(f"[DEBUG] handle_command command='{command}' args={args}")

    if command == "optimize_energy":
        mode = args.get("mode", "eco")
        controller.optimize_home_energy(mode=mode)

    elif command == "charge_ev":
        mode = args.get("mode", "auto")
        controller.optimize_ev_charging(mode=mode)

    elif command == "turn_on_device":
        device = args.get("device", "lamp")
        controller.turn_on(device)

    elif command == "turn_off_device":
        device = args.get("device", "lamp")
        controller.turn_off(device)

    else:
        print(f"[WARN] Unknown command: {command}")


# ===== Local debug entry point =====
if __name__ == "__main__":
    print("Home Energy Copilot (EV-aware) started. Local debug mode.")
    controller = DeviceController(DEVICE_TOPICS)

    print("Available debug commands: optimize_energy, charge_ev, turn_on_device, turn_off_device")
    print("Type 'exit' or 'quit' to stop.\n")

    while True:
        cmd = input("Command> ").strip()
        if cmd in ("exit", "quit"):
            break

        if cmd == "optimize_energy":
            mode = input("Mode [eco/comfort]> ").strip() or "eco"
            handle_command(controller, "optimize_energy", {"mode": mode})

        elif cmd == "charge_ev":
            mode = input("Mode [auto/force_on/force_off]> ").strip() or "auto"
            handle_command(controller, "charge_ev", {"mode": mode})

        elif cmd in ("turn_on_device", "turn_off_device"):
            dev = input("Device name [lamp/ac/charger]> ").strip() or "lamp"
            handle_command(controller, cmd, {"device": dev})

        else:
            print("[WARN] Unknown debug command. Try: optimize_energy, charge_ev, turn_on_device, turn_off_device")
