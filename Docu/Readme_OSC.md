# LIVE OSC Mode

## Overview

TeleAgriCulture supports a low-latency LIVE mode for real-time sensor streaming. In LIVE mode, sensor values can be transmitted either via MQTT or OSC (Open Sound Control).

OSC mode is intended for interactive applications such as Processing, TouchDesigner, Max/MSP, Pure Data, multimedia installations, and real-time data visualization.

---

## Configuration

1. Open the TeleAgriCulture configuration portal.
2. Select **LIVE** as the upload mode.
3. Select **OSC** as the live output type.
4. Enter:

   * **OSC IP** – IP address or hostname of the receiving computer.
   * **OSC Port** – UDP port used by the receiver.
5. Use **continouese upload** to get data as soon sensor data is avaiable
6. Save the configuration and reboot the device.

---

## Network Requirements

* The TeleAgriCulture board must be connected to WiFi.
* The receiving application must be reachable through the network.
* In most cases, the board and the receiving computer should be connected to the same local network.
* OSC uses UDP and does not require an MQTT broker.

---

## OSC Address Structure

OSC messages are generated automatically using:

```
<OSC Topic>/<Board ID>/<Measurement Name>
```

Example:

```
OSC Topic: /TAC
Board ID : 1234
```

Results in OSC addresses such as:

```
/TAC/1234/temp
/TAC/1234/hum
/TAC/1234/press
/TAC/1234/acc_x
/TAC/1234/acc_y
/TAC/1234/acc_z
/TAC/1234/BPM
```

The final measurement names depend on the sensors configured on the board.

---

## Sensor Values

Each OSC message contains a single floating-point value.

Example:

```
Address: /TAC/1234/temp
Value:   21.56
```

---

## Notes

* Battery measurements are not transmitted in LIVE OSC mode.
* Values are rounded to two decimal places before transmission.
* Hostnames are supported in addition to numeric IP addresses.
* OSC messages are sent immediately according to the configured sensor update rate.

---

## Example Applications

* Processing
* TouchDesigner
* Max/MSP
* Pure Data
* Custom OSC receivers
* Interactive art installations
* Environmental sensing visualizations
