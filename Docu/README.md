# teleAgriCulture Board V2.1

[<img src="pictures/vscode.svg" alt="VS Code logo" width="50" height="50">](https://code.visualstudio.com)   &nbsp;   [<img src="https://cdn.platformio.org/images/platformio-logo-xs.fd6e881d.png" alt="PlatformIO logo" height="50">](https://platformio.org) &nbsp; [<img src="pictures/ESP32-S3.png" alt="PlatformIO logo" height="50">](https://www.espressif.com/sites/default/files/documentation/esp32-s3_datasheet_en.pdf)

To build the teleAgriCulture Board V2.1 project follow these steps:

1. Clone the repository to your local machine.
2. Open the project folder (community/teleAgriCulture Board V2.1) in [VS Code](https://code.visualstudio.com) with the [PlatformIO](https://platformio.org) extension installed.
3. Create `/include/board_credentials.h` with your own BoardID, API_KEY and LoRa credentials — copy `include/board_credentials.template.h` and fill in your values. See **[README_credentials.md](../README_credentials.md)** for the full workflow.
4. Choose the matching lora-region environment when you build (`-e EU`, `US`, `AU`, `AS`, `JP`, `KR`, `IN`; see `platformio.ini`).
5. Build and upload the project to your ESP32-S3 board.

Once the project is uploaded to the board, a unique access point is created for each board. The SSID is printed to the Serial Monitor on boot and shown on the TFT display. See the [Accessing the Board](#accessing-the-board) section for details.

<mark>!! to build this project, take care that board_credentials.h is in the include folder (gets ignored by git)</mark>

## Accessing the Board

Each board names its WiFi APs after its MAC address, so they are **unique per board**.
Both SSIDs use `XXXX` = the last 4 hex digits of the MAC, and the password `enter123`:

```
Config Portal AP:  TAC_config_XXXX   (e.g. TAC_config_A3F7)
Dashboard AP:      TAC_dash_XXXX     (e.g. TAC_dash_A3F7)
Password:          enter123
```

The active SSID is printed to the Serial Monitor at boot and shown on the TFT display.
_(Older firmware used static names shared by all boards: `TeleAgriCulture Board` / `Teleagriculture DB`.)_

### Config Portal

Opens automatically on first boot, after a **double-reset**, or by holding the BOOT button for > 5 s.

1. Connect your phone or laptop to `TAC_config_XXXX` / `enter123`
2. A captive portal opens automatically (or navigate to `http://192.168.4.1`)
3. Select your WiFi network, enter credentials, configure upload settings
4. Save — the board reboots and connects to your network

### Dashboard (sensor data + web UI)

During normal operation (when not battery-powered) the board opens the `TAC_dash_XXXX` AP for local access without a router.

| How to connect | Address |
|---|---|
| Via the board's own AP | `http://192.168.4.1` |
| Via your local WiFi (mDNS) | `http://esp32.local` |
| Via your local WiFi (IP) | IP shown on TFT display |

The dashboard shows live sensor readings, uptime, board ID, and upload target.  
It refreshes automatically every 15 seconds.

### Calibration Wizard

Navigate to `/calibrate` on the dashboard address:

```
http://192.168.4.1/calibrate        (via board AP)
http://esp32.local/calibrate        (via local WiFi)
```

Select a sensor and follow the step-by-step wizard. Live ADC readings update every 2 s.  
→ See [calibration_ADS1115.md](calibration_ADS1115.md) for full documentation.

### LIVE Mode (MQTT / OSC)

Configure LIVE mode in the Config Portal under the **LIVE** tab. The board must be connected to your WiFi network.

**MQTT:**
- Set broker IP, port (default 1883), and topic
- Data is published as JSON to `<topic>/<data_name>`
- Compatible with Home Assistant, Node-RED, MQTT Explorer, etc.

**OSC:**
- Set target IP and port
- Each measurement is sent as an individual OSC message: `/tac/<data_name> <value>`
- Compatible with Max/MSP, TouchDesigner, Pure Data, etc.

Rate is capped at **20 sends/second** (50 ms minimum gap).  
LIVE mode does **not** upload to the TAC server — it is local network only.

## Main program

The `main()` function in the `src/main.cpp` file handles the Config Access Point, WiFi, LoRa, load, save, time and display UI. It initializes the board and its sensors and starts the main loop.

The global vector `sensorVector` is used to store connected sensor data. Each element in the vector represents a sensor and contains its measurements. The data name and value for each measurement can be accessed using `sensorVector[i].measurements[j].data_name` and `sensorVector[i].measurements[j].value`, respectively.

In the main loop, the program reads sensor data, updates the display UI and sends data to the server at regular intervals. The board can also enter deep sleep mode to conserve power.

Global vector to store connected Sensor data:
`std::vector<Sensor> sensorVector;`
 
Sensor Data Name: `sensorVector[i].measurements[j].data_name`    --> in order of apperiance (temp, temp1, temp2 ...)
Sensor Value:     `sensorVector[i].measurements[j].value`

## Sensors

The teleAgriCulture Board V2.1 supports a variety of sensors through its connectors. The currently implemented sensors are listed in the `SensorsImplemented` enum in `lib/init_TAC/src/def_Sensors.h`. For the canonical, up-to-date list see **[README.md – Implemented Sensors](../README.md#implemented-sensors)**.

The notes below cover the read-implementation details (I2C addresses, datasheet links):

- BMP_280: A temperature and pressure sensor.
- LEVEL: A water level sensor.
- VEML7700: An ambient light sensor.
- TDS: A total dissolved solids sensor.
- CAP_SOIL: A capacitive soil moisture sensor.
- CAP_GROOVE: A capacitive groove moisture sensor.
- DHT_22: A temperature and humidity sensor.
- DS18B20: A temperature sensor.
- HEART_RATE: Gravity Heart Rate Monitor Sensor (SEN0203 based on AD8232), outputs BPM via ADC
- MULTIGAS: A multi-gas sensor. <mark>`gas.begin(Wire, 0x08);` I2C Address is used<mark>
- MULTIGAS_V1: An older version of the multi-gas sensor. <mark>`multiGasV1.begin(0x04);` I2C Address is used<mark>
- DS3231: A real-time clock module
- BATTERY: Battery level sensed on BATSENS Pin.
- WS2812: An RGB LED strip - <mark>not implemented now.<mark>
- SERVO: A servo motor -<mark>not implemented now.<mark>
- BME_280: A temperature, humidity and pressure sensor.
- SCD4x CO2: Sensirion SCD40 / SCD41 CO₂ + temperature + humidity sensor (I2C 0x62); the firmware auto-detects the variant.
- SOUND: Gravity analog Sound level meter https://wiki.dfrobot.com/Gravity__Analog_Sound_Level_Meter_SKU_SEN0232
- Pressure Level Sensor  https://wiki.dfrobot.com/Throw-in_Type_Liquid_Level_Transmitter_SKU_KIT0139
- ML8511 UV Sensor https://wiki.dfrobot.com/UV_Sensor_v1.0-ML8511_SKU_SEN0175
- LM35 temperature sensor https://wiki.dfrobot.com/DFRobot_LM35_Linear_Temperature_Sensor__SKU_DFR0023_   //not tested now
- DFRobot Analog Ambient Light Sensor https://wiki.dfrobot.com/DFRobot_Ambient_Light_Sensor_SKU_DFR0026   //not tested now

- **ADS1115** *(Advanced — optional analog-sensor expansion module)*: a 4-channel,
  16-bit ADC (I2C 0x48, GAIN_ONE = ±4.096 V, 0.125 mV/bit). It is **not a sensor itself**
  but adds four high-precision analog inputs for the DFRobot Gravity **water-quality
  probes** used in aquaponic / hydroponic systems. The ESP32's own ADC is too noisy for
  these probes, so they are read through the ADS1115. Each channel needs a one-time
  calibration (web wizard at `/calibrate`, stored in `board_cal.json`) — see
  [calibration_ADS1115.md](calibration_ADS1115.md).
  - ADC0: ORP / Redox (mV) — https://wiki.dfrobot.com/Gravity_Analog_ORP_Sensor_PRO_SKU_SEN0464
  - ADC1: DO / Dissolved Oxygen (mg/L) — https://wiki.dfrobot.com/Gravity__Analog_Dissolved_Oxygen_Sensor_SKU_SEN0237
  - ADC2: EC / Conductivity (mS/cm) — https://wiki.dfrobot.com/Gravity__Analog_Electrical_Conductivity_Sensor___Meter_V2__K=1__SKU_DFR0300
  - ADC3: pH — https://wiki.dfrobot.com/Gravity__Analog_pH_Sensor_Meter_Kit_V2_SKU_SEN0161-V2

- BH_1745: ROHM BH1745NUC RGBC color sensor (I2C 0x38 / 0x39) — outputs Red, Green, Blue, Clear as uint16 counts
- SPF_WINDVANE: SparkFun Weather Meter Kit wind vane — reads ADC voltage and maps to 16 compass directions (degrees)
- SPF_ANEMOMETER: SparkFun Weather Meter Kit anemometer — counts pulses over 5 s and returns wind speed in km/h
- LIS331HH: 3-axis linear accelerometer, ±6 g full-scale, outputs X / Y / Z in g (I2C 0x18 / 0x19)



Each sensor has its own reading code in the `include/sensor_Read.hpp` file. Simple I2C sensors use direct Wire communication without extra libraries. The data from the sensors is stored in the `sensorVector` and can be accessed using the `sensorVector[i].measurements[j].value` syntax.

New sensors can be added by following the steps outlined in the [Adding new sensors](#adding-new-sensors) section.

## Adding New Sensors

To add new sensors, follow these steps:

1. In `lib/init_TAC/src/def_Sensors.h` and `def_Sensors.cpp`:
    - Add new `SensorName` to `ENUM SensorsImplemented` (use a name that has no conflicts with your sensor library). Increment `SENSORS_NUM` by 1.
    - Add new sensor to the `proto_sensors` JSON string in `def_Sensors.cpp` (use the same format).
    - Add new `ENUM ValueOrder` if necessary. This also has to be added to the switch in `lora_functions.cpp` (`lora_sendData()`) and to `getValueOrderFromString()` in `def_Sensors.cpp`. (LoRa data gets sent in the format `<ValueOrder ENUM><Value>` for encoding/decoding).
2. In `include/sensor_Read.hpp`:
    - For simple I2C sensors prefer direct Wire reads over adding a library (see BH_1745 or BH_1750 as examples).
    - Add implementation to the following functions corresponding to your sensor type with a case statement using your sensor ENUM:
        - `readI2C_Connectors()`
        - `readADC_Connectors()`
        - `readOneWire_Connectors()`
        - `readI2C_5V_Connector()`
        - `readSPI_Connector()`
        - `readEXTRA_Connectors()`
3. Create a new sensor object at the end of your implementation like: `Sensor newSensor = allSensors[ENUM_SENSOR];` (using the prototype sensor)
4. Add sensor measurement to the newSensor object like: `newSensor.measurements[0].value = value;`
5. Push the new sensor object to the global sensorVector like: `sensorVector.push_back(newSensor);`
6. <mark>Share your success with the community :-) <mark>


## Wishlist

- [x] WPA2 enterprise support
- [x] LoRa regions
- [x] deep sleep
- [x] custom NTP server option
- [x] include CA root certificates
- [x] EduRoam WPA3 support (tested at Kunstuni Linz and JKU Linz)
- [x] support for alternative I2C adresses
- [x] data upload intervall based on UI
- [x] display data in the browser (just in NO BATTERY MODE)
- [ ] powermanagment field tests
- [x] implement DS3231 RTC
- [x] implement BH1745 RGBC color sensor
- [x] implement SparkFun Weather Meter Kit (wind vane + anemometer)
- [x] timestamp in WiFi JSON payload
- [x] LIVE mode rate limiter (20 sends/sec)
- [ ] implement WS2812 LED function and control logic
- [ ] implement Servo function and control logic
- [~] sensor calibration option — web wizard for pH, EC, DO, ORP, soil (in development, see [calibration_ADS1115.md](calibration_ADS1115.md))

### Hardware

- [ ] LiPo Charger circuit on board
- [ ] Grove I2C Connector
- [ ] USB-C Connector

for technical questions you can write me an email: artdanion at gmail.com

 

## Implemented Sensors

- ADS1115 (optional analog-sensor expansion — 4-ch 16-bit ADC, I2C 0x48: ORP, DO, EC, pH)
- BATTERY (battery voltage on the BATSENS pin)
- BH_1745 (Pimoroni / ROHM BH1745NUC RGBC color sensor, I2C 0x38 / 0x39)
- BH_1750
- BME_280
- BMP_280
- BMP_680
- CAP_SOIL (capacitive soil moisture, analog)
- CAP_GROOVE (capacitive groove moisture, analog)
- DFR FLAME
- DFR LIGHT
- DFR LM35
- DHT11
- DHT22
- DS18B20
- HEART_RATE (Gravity Heart Rate Monitor Sensor SEN0203 based on AD8232)
- LEVEL (analog water level sensor)
- LIS331HH (3-axis accelerometer ±6 g, X/Y/Z in g, I2C 0x18 / 0x19)
- LTR_390
- MultiGasV1
- MultiGasV2
- PRE_LVL (DFRobot throw-in liquid-level / pressure depth transmitter, analog)
- RTCDS3231
- SCD4x (Sensirion SCD40 / SCD41 CO₂ + temperature + humidity, I2C 0x62)
- SERVO (servo output — control logic not yet implemented)
- SHT_21
- SOUND (DFRobot Gravity analog sound level meter, dBA)
- SPF_WINDVANE (SparkFun Weather Meter Kit — wind direction via ADC, 16 compass directions)
- SPF_ANEMOMETER (SparkFun Weather Meter Kit — wind speed via pulse counting, km/h)
- TDS
- UV_DFR (DFRobot ML8511 analog UV sensor, UV index)
- VEML7700
- WS2812 (RGB LED strip output — control logic not yet implemented)

## Sensor Calibration

Selected sensors support in-firmware calibration via the web interface. Navigate to `http://<board-ip>/calibrate` to open the calibration wizard.

| Sensor group | Method | Status |
|---|---|---|
| pH, EC, DO, ORP | ADS1115 module required — web wizard with live readings | In development |
| Soil moisture (CAP_SOIL) | 2-point dry/wet via analog pin | Available |

Calibration values are saved to `/board_cal.json` on SPIFFS and loaded on every boot. Factory defaults are used if no calibration has been performed — behaviour is identical to earlier firmware versions.

→ Full documentation, formulas, buffer solutions and troubleshooting: **[calibration_ADS1115.md](calibration_ADS1115.md)**

## WiFi Data Upload

The board sends a single HTTP POST request to the TAC backend after every measurement cycle.

### Endpoint

```
POST https://kits.teleagriculture.org/api/kits/{boardID}/measurements
Content-Type: application/json
Authorization: Bearer {API_KEY}
```

`boardID` and `API_KEY` are set in `/include/board_credentials.h`.

### Payload structure

The payload is a **flat JSON object** — one key per measurement, plus an optional timestamp.

```json
{
  "temp":        23.45,
  "press":       1013.25,
  "alt":         210.3,
  "hum":         58.1,
  "TDS":         312.0,
  "mois":        67.0,
  "Battery":     3.87,
  "time":        "2025-06-01 14:32:05 CEST"
}
```

- All values are **floats, rounded to 2 decimal places**.
- **NaN values are silently dropped** — if a sensor fails, its key is absent.
- `"time"` requires a valid time source (NTP, RTC, or HTTP header sync). Absent if time is unavailable.
- If the same measurement type appears more than once (e.g. two temperature sensors), subsequent keys are suffixed: `temp`, `temp1`, `temp2`, …

### Complete field reference

| Key | Unit | Source sensor(s) |
|-----|------|-----------------|
| `temp` | °C | BMP280, BME280, BME680, DS18B20, DHT22, DHT11, SHT21, LM35, SCD40/SCD41 |
| `hum` | % | BME280, BME680, DHT22, DHT11, SHT21, SCD40/SCD41 |
| `press` | hPa | BMP280, BME280, BME680 |
| `alt` | m | BMP280, BME280, BME680 |
| `resist` | kΩ | BME680 (gas resistance) |
| `lux` | lx | VEML7700, BH1750, BH1745 |
| `ambient` | lx | VEML7700 (white channel) |
| `UV Int.` | mW/cm² | ML8511 UV sensor |
| `UV Index` | mW/cm² | LTR390 |
| `Light int.` | lx | DFRobot ambient light |
| `red` / `green` / `blue` / `clear` | raw counts | BH1745 RGBC |
| `height` | mm | Water level sensor |
| `TDS` | ppm | TDS sensor |
| `mois` | % or raw | CAP_SOIL (%), CAP_GROOVE (raw ADC) |
| `Battery` | V | Battery voltage (BATSENS pin) |
| `ORP` | mV | ADS1115 ch0 — ORP probe |
| `DO` | mg/L | ADS1115 ch1 — dissolved oxygen |
| `EC` | mS/cm | ADS1115 ch2 — conductivity |
| `PH` | pH | ADS1115 ch3 — pH probe |
| `CO` | ppm | MultiGas / MultiGas V1 |
| `NO2` | ppm | MultiGas / MultiGas V1 |
| `NH3` | ppm | MultiGas V1 |
| `CH4` | ppm | MultiGas V1 |
| `H2` | ppm | MultiGas V1 |
| `C3H8` | ppm | MultiGas V1 (propane) |
| `C4H10` | ppm | MultiGas V1 (butane) |
| `C2H5OH` | ppm | MultiGas V1 (ethanol) |
| `co2` | ppm | SCD40 / SCD41 (SCD4x CO₂ sensor) |
| `Sound lvl` | dBA | DFRobot sound level meter |
| `Pressure lvl` | mm | Throw-in liquid level transmitter |
| `flame` | V | DFRobot flame sensor |
| `wind_dir` | deg | SparkFun wind vane (0–360°, 16 steps) |
| `wind_spd` | km/h | SparkFun anemometer |
| `BPM` | bpm | Gravity Heart Rate Monitor Sensor (SEN0203) |
| `time` | string | Timestamp — `"YYYY-MM-DD HH:MM:SS TZ"` |

## LIVE Mode (MQTT / OSC)

LIVE mode streams sensor data in real time over the local network — it does **not** upload to the TAC server. Two protocols are supported:

- **MQTT**: publish/subscribe broker protocol, compatible with Home Assistant, Node-RED, etc.
- **OSC** (Open Sound Control): UDP-based, popular in Max/MSP, TouchDesigner, Pure Data, etc.

The rate is capped at **20 sends per second** (50 ms minimum gap) to avoid flooding the network.
