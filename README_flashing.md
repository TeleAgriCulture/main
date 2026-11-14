# Flashing Boards by Kit ID — `flash_board.py`

> ## ⚠️ MAINTAINERS ONLY: needs a board's credentials
>
> `flash_board.py` needs one of two things:
>
> - the non-public **`Boards_List.csv`** in the project root. It holds every board's
>   API key and LoRaWAN OTAA keys, so it is git-ignored and never shared publicly.
>   Admins download it from the kits site's admin panel (Kits, tick the boards,
>   download);
> - or a **flashing token** from the kits site's admin panel, which fetches the
>   credentials for the boards it was made for (see
>   [Without the CSV](#without-the-csv-a-flashing-token)).
>
> **External developers with neither:** follow the **manual** path in
> [`README_credentials.md`](README_credentials.md) instead (copy the template, fill
> in your own values, `pio run -e EU -t upload`).

`flash_board.py` looks up a Kit ID in `Boards_List.csv` (or asks the kits site),
fills `include/board_credentials.h` with that board's credentials, picks the right
LoRa region, then builds and uploads, all in one command.

---

## 1. Open a terminal that knows `pio`

PlatformIO's command line (`pio`) only exists inside PlatformIO's own
environment. A plain terminal (zsh / PowerShell) does **not** know it by default.

### Easiest — the PlatformIO terminal in VS Code (Mac & Windows, no setup)

1. Open the Command Palette:
   - **Mac:** `Cmd + Shift + P`
   - **Windows:** `Ctrl + Shift + P`
2. Type **`PlatformIO: New Terminal`** and press Enter.
3. A terminal opens that already knows `pio` and `python`. Run all commands below
   in **that** terminal.

> The little PlatformIO **ant-head icon** in the VS Code Activity Bar also has
> *"PlatformIO Core CLI"* under *Quick Access → Miscellaneous*, which does the same.

### Optional — make `pio` work in any terminal

**Mac (zsh):**
```bash
echo 'export PATH="$PATH:$HOME/.platformio/penv/bin"' >> ~/.zshrc
source ~/.zshrc
```
On Mac, run the script with **`python3`** (plain `python` usually doesn't exist):
```bash
python3 flash_board.py 1014
```

**Windows (PowerShell):** the PlatformIO installer normally adds `pio` to PATH
already; if not, use the VS Code PlatformIO terminal above. Use `python` on Windows.

---

## 2. Flash a board

Run from the project root (where `flash_board.py` and `Boards_List.csv` live).
Replace `1014` with the Kit ID you want.

```bash
python flash_board.py 1014                 # build + upload board 1014
python flash_board.py 1014 --env US        # override the LoRa region/env
python flash_board.py 1014 --no-upload     # generate header + build only
python flash_board.py 1014 --dry-run       # show the plan, change nothing
```

The script rewrites `include/board_credentials.h` on every run, so **don't keep
manual edits there** if you also use the script.

### Without the CSV: a flashing token

An admin creates a token in the kits site's admin panel (Kits, tick the boards,
**Create flashing token**). It is shown once, works only for those boards, and
expires after a few hours (8 by default). Put it in an environment variable, never
on the command line, so it stays out of your shell history:

```powershell
# Windows (PowerShell)
$env:TAC_FLASH_TOKEN="tacf_..."
python flash_board.py 1014 --source api --api-url https://kits.teleagriculture.org
```

```bash
# Mac (zsh)
export TAC_FLASH_TOKEN="tacf_..."
python3 flash_board.py 1014 --source api --api-url https://kits.teleagriculture.org
```

Set `TAC_API_URL` to skip `--api-url`. Every other option above works the same.
After a successful upload the script tells the kits site the board was flashed,
with the region it built, whether you used `--erase`, and the firmware commit. The
admin panel then shows when each board was last flashed. If that report fails, the
script prints a warning; the board is still flashed.

The script refuses a plain `http://` address (except a local test server), because
anyone on the network could read the token.

### Picking the serial port

First just try without a port — auto-detect works in almost all cases.
If the board isn't found, list the ports and pass one explicitly:

```bash
pio device list
```

- **Mac:** the port looks like `/dev/cu.usbmodem1101` or `/dev/cu.usbserial-XXXX`.
  Use the `/dev/cu.*` name, **not** `/dev/tty.*`.
- **Windows:** the port looks like `COM7`.

```bash
python flash_board.py 1014 --port /dev/cu.usbmodem1101   # Mac
python flash_board.py 1014 --port COM7                   # Windows
```

> **Mac USB note:** the board is an ESP32-S3 with native USB, so **no driver is
> needed**. Use the socket labelled **USB** (not UART). If the upload won't start,
> put the board in flashing mode by hand: hold **BOOT**, briefly tap **RESET**,
> release BOOT, then re-run the command.

---

## 3. ⚠️ Re-flashing a board with a DIFFERENT Kit ID — you MUST erase first

This is the easiest mistake to make, so read it carefully.

The board keeps its settings (boardID, API key, WiFi network, sensor config,
calibration) in flash — in the **SPIFFS** filesystem (`/board_config.json`,
`/connectors.json`, `/board_cal.json`) and in **NVS** (WiFi credentials). A normal
upload replaces **only the program**, and leaves those partitions untouched.

At every boot the firmware **loads the stored config and overwrites the
compiled-in values** — including the boardID. So:

> If you flash a configured board with a new Kit ID **without erasing**, the old
> stored boardID/API key/WiFi win at runtime. The board keeps its **previous
> identity** and the new ID silently does nothing.

To actually switch a board to a new ID, wipe the stored config with `--erase`:

```bash
python flash_board.py 1050 --erase
```

`--erase` runs a full chip erase before flashing, so SPIFFS **and** the saved WiFi
network are cleared and the new Kit ID truly takes effect. On the next boot the
board has no stored config, so it reopens the WiFi/sensor **config portal** for
fresh setup.

| Situation | Command |
|-----------|---------|
| First-time flash of a blank board | `python flash_board.py 1014` |
| Re-flash same board, **same** ID (firmware update) | `python flash_board.py 1014` |
| Re-flash a board with a **different** ID | `python flash_board.py 1050 --erase` |

> Equivalent manual erase if you prefer: `pio run -e EU -t erase` then flash.

---

## Notes

- Region → environment mapping lives in [`platformio.ini`](platformio.ini)
  (`[env:EU]`, `[env:US]`, …) and in `flash_board.py`.
- `board_credentials.h` and `Boards_List.csv` are intentionally git-ignored.
- A board flash sets `TAC_SKIP_RELEASE_COPY=1`, so it does **not** overwrite the
  credential-free release binaries in `Firmware/`. For clean public release
  firmware, use `build_firmware.py` (see [`README_credentials.md`](README_credentials.md)).
