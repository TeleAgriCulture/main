Firmware updates can be uploaded to the board over WiFi.

1. Connect to the board's WiFi: `TAC_config_XXXX` (`XXXX` is the last 4 hex digits of the board's MAC address), password `enter123`.
2. In the Config Portal, open Board Setup and choose Upload Firmware.
3. Upload the file for your region: EU_868, US_CAN_915, AUS_915, ASIA_923, JP_923, KR_920 or IND_866. The wrong region's file stops LoRa from working.

After uploading, enter the board credentials (Kit ID, API Key) and, for LoRa, the LoRa credentials (DevEUI, AppEUI, AppKey) again in Board Setup.
