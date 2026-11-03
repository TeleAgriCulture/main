# Board Credentials & Flashing

Each board's credentials (API key, LoRaWAN OTAA keys, MQTT server) are **compiled
into the firmware** at build time via `include/board_credentials.h`.

That file is **git-ignored** so real credentials never end up in the repository.
You create it once from the committed template
[`include/board_credentials.template.h`](include/board_credentials.template.h).

There are two ways to do this.

---

## A) Manual — for external developers (no CSV needed)

1. Copy the template to the real header:

   ```powershell
   Copy-Item include/board_credentials.template.h include/board_credentials.h
   ```
   (bash/macOS/Linux: `cp include/board_credentials.template.h include/board_credentials.h`)

2. Open `include/board_credentials.h` and replace every `__PLACEHOLDER__`
   with your own values (the comments next to each line show the expected format).
   If you don't use LoRaWAN, leave the `OTAA_*` placeholders as zeros.

3. Build & upload, choosing your LoRa region as the PlatformIO environment:

   ```powershell
   pio run -e EU -t upload      # or US / AU / AS / JP / KR / IN
   ```

That's it — your `board_credentials.h` stays local and is never committed.

---

## B) Automatic — maintainers with `Boards_List.csv`

If you have the (non-public) `Boards_List.csv`, the helper script does everything
— look up the Kit ID, fill the header, pick the right region env, build and flash:

```powershell
python flash_board.py 1014              # build + upload board 1014
python flash_board.py 1014 --port COM7  # pin the serial port
python flash_board.py 1014 --env US     # override the LoRa region / env
python flash_board.py 1050 --erase      # re-flash with a NEW Kit ID (wipes stored config)
python flash_board.py 1014 --no-upload  # generate header + build only
python flash_board.py 1014 --dry-run    # show the plan, change nothing
```

The script regenerates `include/board_credentials.h` on every run, so don't keep
manual edits there if you also use the script.

> **Re-flashing a board with a different Kit ID?** You must use `--erase`, or the
> board's stored config overrides the new ID at runtime. See the full walkthrough,
> plus how to open the PlatformIO terminal on Mac/Windows, in
> [`README_flashing.md`](README_flashing.md).

### Without the CSV — a flashing token from the web app

An admin can create a flashing token in the web app's admin panel
(Kits → tick the boards → Create flashing token). The script then fetches each
board's credentials from the app instead of `Boards_List.csv`, and the app
records the flash:

```powershell
$env:TAC_FLASH_TOKEN="tacf_..."          # env var only, keeps it out of shell history
python flash_board.py 1014 --source api --api-url https://<app host>
```

A token only works for the boards it was made for, and expires after a few hours.

---

## Release firmware (credential-free, one binary per region)

To build the public per-region firmware **without** any board's credentials:

```powershell
python build_firmware.py             # all regions: EU US AU AS JP KR IN
python build_firmware.py EU US       # only selected regions
python build_firmware.py --dry-run   # show the plan, build nothing
```

This renders a **generic** `board_credentials.h` (boardID 1000, placeholder API
key, zeroed OTAA keys), then builds each region. `copyFirmware.py` writes the
results to `Firmware/firmware_<region>_v<version>.bin`.

How credentials are kept out of the release binaries:

- `build_firmware.py` always renders the generic header first, so no real
  credentials are ever compiled into the release firmware.
- `flash_board.py` sets `TAC_SKIP_RELEASE_COPY=1`, so a board-specific flash
  does **not** overwrite the binaries in `Firmware/`.
- A plain `pio run -e <region>` still copies to `Firmware/` (unchanged) — but it
  uses whatever credentials are currently in `board_credentials.h`, so use
  `build_firmware.py` when you want a clean release.

## Notes

- `pio` must be on your PATH. The easiest way is the **PlatformIO terminal** in
  VS Code, or run PlatformIO commands from the PlatformIO IDE.
- Region → environment mapping lives in [`platformio.ini`](platformio.ini)
  (`[env:EU]`, `[env:US]`, …) and in `flash_board.py`.
- `board_credentials.h` and `Boards_List.csv` are intentionally git-ignored.
