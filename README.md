[<img src="https://gitlab.com/teleagriculture/community/-/raw/main/teleAgriCulture%20Board%20V2.1/Docu/pictures/vscode.svg" alt="VS Code logo" width="50" height="50">](https://code.visualstudio.com)   &nbsp;   [<img src="https://cdn.platformio.org/images/platformio-logo-xs.fd6e881d.png" alt="PlatformIO logo" height="50">](https://platformio.org) &nbsp; [<img src="https://gitlab.com/teleagriculture/community/-/raw/main/teleAgriCulture%20Board%20V2.1/Docu/pictures/ESP32-S3.png" alt="ESP32-S3 logo" height="50">](https://www.espressif.com/sites/default/files/documentation/esp32-s3_datasheet_en.pdf)

# TeleAgriCulture Board V2.1

![TeleAgriCulture Board V2.1](https://gitlab.com/teleagriculture/community/-/raw/main/teleAgriCulture%20Board%20V2.1/Docu/pictures/tac_board_V2_1_02.JPG)

_Picture by Daniel Fischer 2024_

A modular, open-source hardware platform for urban agriculture and ecology projects,
built around an **ESP32-S3**. Firmware is a VS Code / PlatformIO project.

> **New here?**
> - **Just got a board?** → jump to [Quick Start](#quick-start-for-board-owners).
> - **Want to build the firmware yourself?** → see [For Developers](#for-developers).

---

## Table of Contents

- [TeleAgriCulture Board V2.1](#teleagriculture-board-v21)
  - [Table of Contents](#table-of-contents)
  - [What is TeleAgriCulture?](#what-is-teleagriculture)
  - [What can you do with the board?](#what-can-you-do-with-the-board)
  - [Quick Start (for board owners)](#quick-start-for-board-owners)
  - [Board Functions](#board-functions)
    - [Navigation](#navigation)
    - [Configuration Mode](#configuration-mode)
    - [Serial Monitor](#serial-monitor)
    - [Upload modes \& LIVE mode](#upload-modes--live-mode)
    - [AP Mode (live dashboard)](#ap-mode-live-dashboard)
    - [SD Card Logging](#sd-card-logging)
  - [Firmware \& OTA Updates](#firmware--ota-updates)
  - [Troubleshooting](#troubleshooting)
  - [For Developers](#for-developers)
    - [Build \& flash from source](#build--flash-from-source)
    - [Platform-specific setup (CLI / no editor needed)](#platform-specific-setup-cli--no-editor-needed)
    - [Credentials \& helper scripts](#credentials--helper-scripts)
    - [Known issue: `ModuleNotFoundError: No module named 'intelhex'`](#known-issue-modulenotfounderror-no-module-named-intelhex)
    - [Architecture \& deep dive](#architecture--deep-dive)
    - [Contributing](#contributing)
  - [Documentation](#documentation)
  - [Implemented Sensors](#implemented-sensors)
  - [Community \& Data API](#community--data-api)

---

## What is TeleAgriCulture?

TeleAgriCulture is a community platform that provides a crowd/cloud data exchange
network to promote a more sustainable engagement with food, agriculture and ecology —
through creative innovation, community engagement and scientific education.

It aims to make environmental sensing technologies and data-visualization tools
accessible to anyone interested in exploring the interactions between plants, animals,
humans and their environments.

## What can you do with the board?

The TeleAgriCulture Board V2.1 is a versatile, customizable board for applications such as:

- **Monitor** soil moisture, temperature, humidity, light intensity and many more
  parameters of your plants or crops (see [Implemented Sensors](#implemented-sensors)).
- **Control** irrigation systems, LED lights, fans or other actuators based on sensor
  data or user input.
- **Connect** via WiFi or LoRaWAN and send/receive data to/from the TeleAgriCulture
  Platform or other services.
- **Create** interactive art installations or educational projects that use
  environmental data as input.

---

## Quick Start (for board owners)

Boards are **flashed with the latest firmware at shipping and ready to use** — no
computer or coding required. (You can later update over the air, see
[Firmware & OTA Updates](#firmware--ota-updates).)

**You need:** a TeleAgriCulture Board V2.1, a micro-USB cable, and optionally some
sensors/actuators. A step-by-step guide with pictures is
[here](https://gitlab.com/teleagriculture/community/-/blob/main/teleAgriCulture%20Board%20V2.1/Docu/setup.md).

1. **Power the board** via micro-USB or a Waveshare Solar Power Manager board.
2. The board opens a WiFi Access Point named after the board's MAC address, so it is
   **unique per board**:
   - **Config Portal AP:** `TAC_config_XXXX` (e.g. `TAC_config_A1B2`) — `XXXX` are 4 hex
     digits from the board's MAC address.
   - **Password:** `enter123`
   - _Older firmware used a static name (`TeleAgriCulture Board`) shared by all boards._
3. **Connect** to that WiFi with your phone or laptop.
4. Your browser is redirected to the board's **Config Portal** (IP `192.168.4.1`).
5. **Step through the setup pages**, choose your settings, and **save**.

> Using **LoRa**? Enter your LoRa credentials on the Config Portal, and make sure the
> board runs the firmware that matches your region / LoRa module
> (see [Firmware & OTA Updates](#firmware--ota-updates)).

---

## Board Functions

### Navigation
- **Move between pages:** use the **BOOT BUTTON** and **SELECT BUTTON**.
- **Wake from deep sleep:** press the **BOOT BUTTON**.

### Configuration Mode
To open the Config Portal again after setup, use either method:
1. **Long press:** hold the **BOOT BUTTON** for more than 5 seconds.
2. **Double reset:** reset the board, wait ~1 second, then reset again.

### Serial Monitor
Available at a baud rate of **115200**.

### Upload modes & LIVE mode
- **WiFi Upload** - JSON https POST + bearer to kits.teleagriculture.org
- **LoRa Upload** — long-range, low-power data transmission.
- **No Upload** — run without sending data; useful for local processing or storage.
- **LIVE Mode (MQTT / OSC)** — stream sensor data in real time over the local network,
  without uploading to the TAC server. Two protocols are supported:
  - **MQTT** — works with Home Assistant, Node-RED and similar tools.
  - **OSC** (Open Sound Control) — UDP-based, popular in Max/MSP, TouchDesigner, Pure Data.

  The send rate is capped at 20 messages per second to avoid flooding the network.

### AP Mode (live dashboard)
When the board is **not** battery-powered, it runs in AP Mode and serves a live
sensor dashboard. Connect to its WiFi:
- **SSID:** `TAC_dash_XXXX` — unique per board (same 4 MAC hex digits as the Config Portal AP).
- **Password:** `enter123`

Then open **192.168.4.1** to view real-time readings from the connected sensors.

> _Older firmware used a static name (`Teleagriculture DB`) shared by all boards._

### SD Card Logging
The board can log data to an SD card connected to the SPI connector. Use any
SPI SD-card module that runs at **3.3 V** (this one works well:
[example module](https://www.amazon.de/dp/B09YYG6BT3?ref=ppx_yo2ov_dt_b_fed_asin_title&th=1)).

1. **Find the SPI connector** on the board:

   ![SPI Connector](https://gitlab.com/teleagriculture/community/-/raw/main/teleAgriCulture%20Board%20V2.1/Docu/pictures/SPI_CON.jpeg)

   _Picture by Daniel Fischer 2024_

2. **Wire the SD-card module** to the SPI connector:

   ![SD Card Reader Module](https://gitlab.com/teleagriculture/community/-/raw/main/teleAgriCulture%20Board%20V2.1/Docu/pictures/SD_CARD-Modul.jpeg)

   _Picture by Daniel Fischer 2024_

   | Module pin | Board pin |
   |------------|-----------|
   | VCC        | VCC       |
   | GND        | GND       |
   | MOSI       | MOSI      |
   | MISO       | MISO      |
   | CS         | CS        |

3. **Format the SD card as FAT32** for compatibility.

---

## Firmware & OTA Updates

Pre-compiled firmware for **over-the-air (OTA) updates** — uploaded via *Board Setup*
on the Config Portal — lives in the [`Firmware/`](Firmware) folder
(current version **v1.93**).

> **If you use LoRa, pick the firmware that matches your region / LoRa module.**
> Each region has its own binary (`firmware_<region>_v<version>.bin`), because the
> LoRaWAN frequency band is compiled in.

---

## Troubleshooting

- **Can't connect to the board's WiFi:** reset the board or move closer to it.
- **Serial Monitor shows nothing/garbage:** confirm the baud rate is **115200**.
- **SD card not recognized:** make sure it is **FAT32** formatted and wired correctly.
- **Battery Mode limitations:** in Battery Mode some features are reduced to save power.

---

## For Developers

This is a **VS Code + PlatformIO** project for the ESP32-S3.
But you can for sure use your favorite IDE VIM/eMACs what ever with the platformio CLI setup

### Build & flash from source
1. Install [VS Code](https://code.visualstudio.com) and the
   [PlatformIO](https://platformio.org) extension, then open this folder.
2. Pick the PlatformIO **environment** for your LoRa region:
   `EU`, `US`, `AU`, `AS`, `JP`, `KR`, `IN` (defined in [`platformio.ini`](platformio.ini)).
3. Build and upload:
   ```bash
   pio run -e EU -t upload      # swap EU for your region
   ```

### Platform-specific setup (CLI / no editor needed)

Prefer the command line? The PlatformIO CLI works the same on every OS — see the
[official install docs](https://docs.platformio.org/en/latest/core/installation/index.html).
The recipes below get you from a clean machine to a flashed board.

<details>
<summary><b>Linux</b> (CLI, no editor needed)</summary>

```bash
# 1. Install dependencies
sudo apt install python3 python3-pip git    # Debian/Ubuntu
sudo pacman -S python python-pip git         # Arch
sudo dnf install python3 python3-pip git    # Fedora

# 2. Install PlatformIO
pip3 install --user platformio
export PATH="$HOME/.local/bin:$PATH"         # add to ~/.bashrc to persist

# 3. USB access (once)
sudo usermod -aG dialout $USER
sudo udevadm control --reload-rules && sudo udevadm trigger
# log out and back in

# 4. Clone & configure
git clone https://github.com/TeleAgriCulture/main.git
cd main
cp include/board_credentials.template.h include/board_credentials.h
nano include/board_credentials.h             # fill in BOARD_ID, API_KEY, ...

# 5. Build & upload (EU region)
pio run -e EU --target upload

# 6. Serial monitor
pio device monitor --baud 115200
```
</details>

<details>
<summary><b>macOS</b> (CLI, no editor needed)</summary>

```bash
# 1. Install Homebrew (if not already installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 2. Install dependencies
brew install python git

# 3. Install PlatformIO
pip3 install --user platformio
export PATH="$HOME/.local/bin:$PATH"         # add to ~/.zshrc to persist

# 4. Clone & configure
git clone https://github.com/TeleAgriCulture/main.git
cd main
cp include/board_credentials.template.h include/board_credentials.h
open -e include/board_credentials.h          # fill in BOARD_ID, API_KEY, ...

# 5. Build & upload (EU region)
pio run -e EU --target upload

# 6. Serial monitor
pio device monitor --baud 115200
```
</details>

<details>
<summary><b>Windows</b> (recommended: VS Code + PlatformIO extension)</summary>

1. Install [VS Code](https://code.visualstudio.com).
2. Open Extensions (`Ctrl+Shift+X`) → search **"PlatformIO IDE"** → Install.
3. Install [Git for Windows](https://git-scm.com/download/win).
4. Open a terminal (Git Bash or the VS Code terminal) and clone:
   ```bash
   git clone https://github.com/TeleAgriCulture/main.git
   ```
5. In VS Code: **File → Open Folder** → select the cloned folder.
6. Copy `include/board_credentials.template.h` → `include/board_credentials.h` and fill in your data.
7. Use the PlatformIO toolbar (bottom bar) to **Build / Upload / Monitor** — `EU` is the default environment.
</details>

> In every case, see **[README_credentials.md](README_credentials.md)** for exactly which
> fields to fill in `board_credentials.h`.

### Credentials & helper scripts
Each board's credentials (API key, LoRaWAN keys, MQTT server) are **compiled into the
firmware** via `include/board_credentials.h`. That file is git-ignored, so you create
it once from the committed template.

See **[README_credentials.md](README_credentials.md)** for the full workflow:
- **Manual** — copy `board_credentials.template.h` → `board_credentials.h`, fill in
  your values, build. (No extra files needed.)
- **Maintainer scripts** — `flash_board.py <KIT_ID>` flashes a specific board, and
  `build_firmware.py` builds the credential-free release binaries (one per region).

### Known issue: `ModuleNotFoundError: No module named 'intelhex'`
If the build fails with this error, install the missing module into PlatformIO's Python:
```bash
# Windows
C:\Users\YOUR_USERNAME\.platformio\penv\Scripts\python.exe -m pip install intelhex

# Linux / macOS
~/.platformio/penv/bin/python -m pip install intelhex
```

### Architecture & deep dive
For the full firmware reference — modular library layout, boot/loop flow, all
configuration flags, power management and the build-flag matrix — see
**[Docu/dev_docu.md](Docu/dev_docu.md)**.

### Contributing
We'd love to hear about your experiences and projects with the board! For source-code
details and contribution info, see [Docu/dev_docu.md](Docu/dev_docu.md#-contributing) or
the online [Docu Page](https://gitlab.com/teleagriculture/community/-/tree/main/teleAgriCulture%20Board%20V2.1/Docu).

---

## Documentation

| Document | What's inside |
|----------|---------------|
| **[Docu/setup.md](Docu/setup.md)** | Illustrated step-by-step board setup (with photos) |
| **[Docu/README.md](Docu/README.md)** | Build steps, board access, main-program overview, adding sensors, wishlist |
| **[Docu/dev_docu.md](Docu/dev_docu.md)** | Full developer reference: architecture, flags, power management, build config |
| **[README_credentials.md](README_credentials.md)** | Setting up credentials and building/flashing firmware |
| **[Docu/calibration_ADS1115.md](Docu/calibration_ADS1115.md)** | Sensor calibration wizard (pH, EC, DO, ORP, soil) |
| **[Docu/API.md](Docu/API.md)** | Reading your data back out of the TeleAgriCulture API |
| **[Schematic](Docu/Schematic_teleAgriculture_Board_v2.1.pdf)** / **[PCB front](Docu/PCB_teleAgriculture_Board_v2.1_front.pdf)** / **[PCB back](Docu/PCB_teleAgriculture_Board_v2.1_back.pdf)** | Hardware schematic and PCB layout (PDF) |

---

## Implemented Sensors

- **ADS1115** — 4-channel 16-bit ADC (I2C 0x48), used for aquaponic probes: ORP, dissolved oxygen, EC, pH
- **BATTERY** — battery voltage read from onboard BATSENS pin
- **BH_1745** — ROHM BH1745NUC RGBC color sensor, outputs Red / Green / Blue / Clear counts (I2C 0x38 / 0x39)
- **BH_1750** — ambient light sensor, lux output (I2C 0x23 / 0x5C)
- **BME_280** — temperature, humidity and barometric pressure (I2C)
- **BMP_280** — temperature and barometric pressure (I2C)
- **BMP_680** — temperature, humidity, pressure and VOC air quality index (I2C)
- **CAP_SOIL** — capacitive soil moisture sensor (analog)
- **CAP_GROOVE** — capacitive groove soil moisture sensor (analog)
- **DFR FLAME** — DFRobot analog flame detection sensor
- **DFR LIGHT** — DFRobot analog ambient light sensor
- **DFR LM35** — DFRobot LM35 analog linear temperature sensor
- **DHT11** — digital temperature and humidity sensor
- **DHT22** — digital temperature and humidity sensor (higher accuracy than DHT11)
- **DS18B20** — 1-Wire waterproof temperature sensor, supports multiple sensors on one bus
- **HEART_RATE** — Gravity Heart Rate Monitor Sensor (SEN0203 based on AD8232), outputs BPM (analog)
- **LEVEL** — analog water level sensor
- **LIS331HH** — 3-axis linear accelerometer, ±6 g full-scale, outputs X / Y / Z in g (I2C 0x18 / 0x19)
- **LTR_390** — UV index and ambient light sensor (I2C 0x53)
- **MultiGasV1** — Grove Multichannel Gas Sensor V1 (I2C 0x04) — H₂, CO, NO₂, NH₃, C₄H₁₀, C₃H₈, CH₄, C₂H₅OH
- **MultiGasV2** — Grove Multichannel Gas Sensor V2 (I2C 0x08) — same gas channels, updated hardware
- **PRE_LVL** — DFRobot throw-in liquid level transmitter (analog pressure-based depth sensor)
- **RTCDS3231** — DS3231 real-time clock module with onboard temperature sensor (I2C 0x68)
- **SERVO** — servo motor output *(control logic not yet implemented)*
- **SHT_21** — temperature and humidity sensor (I2C 0x40)
- **SOUND** — DFRobot Gravity analog sound level meter (dB)
- **SPF_WINDVANE** — SparkFun Weather Meter Kit wind vane, 16-direction ADC lookup, output in degrees
- **SPF_ANEMOMETER** — SparkFun Weather Meter Kit anemometer, pulse counting over 5 s, output in km/h
- **TDS** — analog total dissolved solids sensor (water quality, ppm)
- **UV_DFR** — DFRobot ML8511 analog UV sensor, outputs UV index
- **VEML7700** — high-accuracy ambient light sensor, lux and white light (I2C 0x10)
- **WS2812** — RGB LED strip output *(control logic not yet implemented)*

---

## Community & Data API

Join the community at **https://www.teleagriculture.org** to share your projects and
experiences.

To push data to teleagriculture.org you need a **board ID and API token**. See the
[API documentation](https://gitlab.com/teleagriculture/community/-/blob/e54ab443139c24a1889cc83034cda92408a1d88b/teleAgriCulture%20Board%20V2.1/Docu/API.md)
for how to read your data back out.
