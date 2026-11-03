## How to setup the TeleAgriCulture V2.1 board

First connect Power (via USB or Solar Board)

<img src="pictures/board_power.jpg" alt="Board Power" width="400" height="400">

Switch board into Config Mode (new boards start into config mode)

- to enter the Config Mode later (with open Config Portal):
- - press BOOT BUTTON > 5 sec or 
- - Doueble Reset the board (reset, 1, 2, 3, reset again)

<img src="pictures/board_config.jpg" alt="Board Config Mode" width="400" height="400">

Connect to board via WiFi (on your Mobile phone or Notebook)

**WiFi Network Name (SSID):**
- **Config Portal AP**: `TAC_config_XXXX` (e.g. `TAC_config_A1B2`) — unique per board, `XXXX` = last 4 hex digits of the MAC address
- _Older firmware (v1.75 and earlier) used a static SSID on all boards: `TeleAgriCulture Board`_

**Password**: `enter123`

<img src="pictures/board_wifi.jpg" alt="Board WiFi" width="400" height="400">

Config Portal opens automatically or open IP: 192.168.4.1 in a browser (on the device you connected to the Board WiFi)

> **iPhone / iPad (iOS 14+)**
> iOS tries to detect the config portal over HTTPS first, which the board does not support. It falls back to HTTP after a few seconds — the "Login to network" popup will appear, just with a short delay (3–5 s). If the popup does not appear at all, open **Safari** and navigate manually to **`http://192.168.4.1`**. This bypasses the automatic detection entirely and opens the config portal directly.


<img src="pictures/board_config_page.jpg" alt="Board Config Page" width="400" height="400">

Now you can change your board settings (WiFi Network, Upload, Sensors, Timezone...)

If you use the Update Option:

>find the current compiled firmware for OTA upload (Board Setup on the Config Portal) here:
>[current Firmware](../Firmware) (current version 1.96)
>
>**If you are using LORA please choose the right Firmware for your location / lora module**
>and you have to enter your credentials for LoRa on the Config Portal

## Connect your data to the TeleAgriCulture Kits page

<img src="pictures/teleagriculture_kits_page.jpg" alt="TeleAgriCulture Kits Page" width="400" height="400">

- first you need an account on the TeleAgiCulture page. Talk to our admin.
- log in to kits.teleagriculture.org
- click on your kit
- click on configure (Top Right)
- add Sensors, dont change the API-key or Kit-ID (we are sending data verified by this numbers)
- save your settings

**we dont send Sensor or data names. (names use a lot of bytes via Lora transmission)**
**So your Sensor names have to match whats shown on your board (e.g.: temp, temp1, temp2... hum, hum1, ...)**

>**for more info about the source code and if you would like to contribute in the coding goto:**  [Docu Page](README.md)
there is also a section about integrated sensors.


## Implemented Sensors

For a complete list of all implemented sensors with technical details, see [README.md - Implemented Sensors](../README.md#implemented-sensors).

Quick list: ADS1115, BATTERY, BH_1745, BH_1750, BME_280, BMP_280, BMP_680, CAP_SOIL, CAP_GROOVE, DFR FLAME, DFR LIGHT, DFR LM35, DHT11, DHT22, DS18B20, HEART_RATE, LEVEL, LIS331HH, LTR_390, MultiGasV1, MultiGasV2, PRE_LVL, RTCDS3231, SCD4x, SERVO, SHT_21, SOUND, SPF_WINDVANE, SPF_ANEMOMETER, TDS, UV_DFR, VEML7700, WS2812
