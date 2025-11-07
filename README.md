# Home Energy Copilot – G-Assist Plug-in (EV-Aware)

## Overview

**Home Energy Copilot** is a Project G-Assist plug-in that runs on RTX AI PCs and helps optimize **home energy usage and EV charging** using simple natural-language commands.

The plug-in connects to automation tools like **IFTTT** to control smart devices such as:

- EV charger (`charger`)
- Air conditioner (`ac`)
- Lighting (`lamp`)

It supports **time-of-use (TOU) energy optimization**, scheduling EV charging during low-tariff hours while keeping the logic local and privacy-friendly.

Example use cases:
- “Optimize my home energy usage in eco mode.”
- “Charge my EV only during cheap electricity hours.”
- “Force start EV charging now.”
- “Turn off non-critical devices during peak hours.”

---

## Features

- 🧠 **On-device AI assistant** via NVIDIA Project G-Assist  
- 🔋 **EV-aware charging optimization** (auto / force_on / force_off modes)  
- ⚡ **Time-of-use tariff support** using a configurable low-tariff window  
- 🏠 **Home energy optimization** for non-critical loads (AC, lighting)  
- 🔗 Integration with **IFTTT Webhooks** for easy smart home connectivity  
- 🛠 Simple, extensible Python architecture (single `plugin.py` entry point)

---

## Project Structure

```text
home-energy-copilot/
├── plugin.py         # Main plug-in logic (commands, EV optimization, IFTTT calls)
├── manifest.json     # G-Assist plug-in metadata and command definitions
├── requirements.txt  # Python dependencies
├── config.json       # Configuration: IFTTT key, device names, tariff window
└── README.md         # This file
