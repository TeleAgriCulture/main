#!/usr/bin/env python3
"""
flash_board.py - Flash a TeleAgriculture board with the credentials of a Kit ID.

Looks up the given Kit ID, renders include/board_credentials.template.h into
include/board_credentials.h with the board's credentials, then builds & uploads
the firmware with PlatformIO using the LoRa region of that board as the build
environment.

Credentials come from:
    --source csv   Boards_List.csv next to this script (default)
    --source api   the web app, using a flashing token from the admin panel
                   (Kits > tick boards > Create flashing token). The app
                   records each flash.

Usage:
    python flash_board.py <KIT_ID> [options]

Examples:
    python flash_board.py 1014                 # build + upload board 1014
    python flash_board.py 1014 --port COM7     # pin the serial port
    python flash_board.py 1014 --env US        # override the LoRa region/env
    python flash_board.py 1014 --erase         # full chip erase, then flash (see note)
    python flash_board.py 1014 --no-upload     # only generate header + build
    python flash_board.py 1014 --dry-run       # show what would happen, do nothing

    # from the web app (token via env var only, keeps it out of shell history)
    set TAC_FLASH_TOKEN=tacf_...                          (Windows cmd)
    $env:TAC_FLASH_TOKEN="tacf_..."                       (PowerShell)
    export TAC_FLASH_TOKEN=tacf_...                       (macOS/Linux)
    python flash_board.py 1014 --source api --api-url https://<app host>
    (or set TAC_API_URL instead of --api-url)

Re-flashing a board with a DIFFERENT Kit ID:
    The board stores its config (boardID, API key, WiFi, sensors) in flash
    (SPIFFS + NVS). A normal upload does NOT touch those partitions, so the
    OLD stored boardID overrides the newly compiled one at runtime - the board
    keeps its previous identity. Use --erase to wipe stored config first so the
    new Kit ID actually takes effect (this also clears the saved WiFi network).
"""

import argparse
import csv
import json
import os
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CSV_PATH = ROOT / "Boards_List.csv"
TEMPLATE_PATH = ROOT / "include" / "board_credentials.template.h"
HEADER_PATH = ROOT / "include" / "board_credentials.h"

DEFAULT_MQTT_IP = "158.255.212.248"

# env vars for --source api
TOKEN_ENV = "TAC_FLASH_TOKEN"
API_URL_ENV = "TAC_API_URL"

# CSV LoRa-Region label -> PlatformIO env name (see platformio.ini)
REGION_TO_ENV = {
    "EU": "EU",
    "US": "US",
    "AU": "AU",
    "AUS": "AU",
    "AS": "AS",
    "ASIA": "AS",
    "JP": "JP",
    "KR": "KR",
    "IN": "IN",
    "IND": "IN",
}

# logical field name -> set of possible CSV column headers (matched case/space-insensitively)
FIELD_ALIASES = {
    "kit_id": ["kit id", "kitid"],
    "name": ["name in the app", "name"],
    "api_key": ["api key", "apikey"],
    "region": ["lora region", "region"],
    "appeui": ["otaa_appeui"],
    "deveui": ["otaa_deveui"],
    "appkey": ["otaa_appkey"],
    "mqtt_ip": ["mqtt_server_ip", "mqtt server ip"],
}


def clean(value):
    """Strip whitespace and the leading Excel text-marker apostrophe."""
    if value is None:
        return ""
    return value.strip().lstrip("'").strip()


def build_column_map(header):
    """Map our logical field names to the actual column index in the CSV."""
    norm = [clean(h).lower() for h in header]
    colmap = {}
    for field, aliases in FIELD_ALIASES.items():
        for alias in aliases:
            if alias in norm:
                colmap[field] = norm.index(alias)
                break
    missing = {"kit_id", "api_key"} - colmap.keys()
    if missing:
        sys.exit(f"ERROR: CSV is missing required column(s): {', '.join(missing)}")
    return colmap


def load_board(kit_id):
    """Return merged credential dict for kit_id, or exit with an error."""
    if not CSV_PATH.exists():
        sys.exit(f"ERROR: {CSV_PATH.name} not found next to this script.")

    # latin-1 never raises on odd bytes; board names may contain non-UTF8 chars.
    with open(CSV_PATH, "r", encoding="latin-1", newline="") as fh:
        rows = list(csv.reader(fh))
    if not rows:
        sys.exit("ERROR: Boards_List.csv is empty.")

    colmap = build_column_map(rows[0])

    def cell(row, field):
        idx = colmap.get(field)
        if idx is None or idx >= len(row):
            return ""
        return clean(row[idx])

    # A Kit ID may be spread over several rows (name/key in one, LoRa data in
    # another). Merge: for each field keep the first non-empty value found.
    merged = {}
    found = False
    for row in rows[1:]:
        if cell(row, "kit_id") != str(kit_id):
            continue
        found = True
        for field in FIELD_ALIASES:
            if not merged.get(field):
                merged[field] = cell(row, field)

    if not found:
        sys.exit(f"ERROR: Kit ID {kit_id} not found in {CSV_PATH.name}.")
    if not merged.get("api_key"):
        sys.exit(f"ERROR: Kit ID {kit_id} has no API key in the CSV.")
    return merged


class ApiError(Exception):
    def __init__(self, status, message):
        super().__init__(message)
        self.status = status
        self.message = message


def api_request(method, url, token, body=None):
    """Call the web app. Returns the decoded JSON, or raises ApiError with the app's own message."""
    data = json.dumps(body).encode("utf-8") if body is not None else None
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}
    if data is not None:
        headers["Content-Type"] = "application/json"
    request = urllib.request.Request(url, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as err:
        try:
            message = json.loads(err.read().decode("utf-8")).get("message")
        except (ValueError, AttributeError):
            message = None
        raise ApiError(err.code, message or f"HTTP {err.code} {err.reason}")
    except urllib.error.URLError as err:
        raise ApiError(None, f"could not reach {url}: {err.reason}")


def api_settings(args):
    """The app's base URL and the flashing token, or exit explaining what is missing."""
    token = os.environ.get(TOKEN_ENV, "").strip()
    if not token:
        sys.exit(
            f"ERROR: --source api needs a flashing token in the {TOKEN_ENV} environment variable.\n"
            "       Create one in the admin panel: Kits, tick the boards, Create flashing token."
        )

    base = (args.api_url or os.environ.get(API_URL_ENV, "")).strip().rstrip("/")
    if not base:
        sys.exit(f"ERROR: --source api needs --api-url or the {API_URL_ENV} environment variable.")

    # token is a bearer credential -> https only, except a local dev server
    parsed = urllib.parse.urlparse(base)
    local = parsed.hostname in ("localhost", "127.0.0.1", "::1")
    if parsed.scheme != "https" and not (parsed.scheme == "http" and local):
        sys.exit(f"ERROR: the app URL must start with https:// (got {base}).")

    return base, token


def load_board_from_api(kit_id, base, token):
    """Same dict as load_board(), fetched from the app instead of the CSV."""
    try:
        data = api_request("GET", f"{base}/api/provisioning/kits/{kit_id}", token)
    except ApiError as err:
        sys.exit(f"ERROR: the app refused Kit ID {kit_id}: {err.message}")

    # same field names as FIELD_ALIASES; null = empty CSV cell (script defaults apply)
    board = {
        field: "" if data.get(field) is None else str(data.get(field)).strip()
        for field in FIELD_ALIASES
    }
    if not board.get("api_key"):
        sys.exit(f"ERROR: the app returned no API key for Kit ID {kit_id}.")
    return board


def firmware_version():
    """This repo's short commit, with -dirty for uncommitted changes, or None."""
    try:
        sha = subprocess.run(
            ["git", "-C", str(ROOT), "rev-parse", "--short", "HEAD"],
            capture_output=True, text=True, check=True,
        ).stdout.strip()
        dirty = subprocess.run(
            ["git", "-C", str(ROOT), "status", "--porcelain", "--untracked-files=no"],
            capture_output=True, text=True, check=True,
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return None
    return f"{sha}-dirty" if dirty else sha or None


def report_flash(base, token, kit_id, env, erased):
    """Tell the app the upload finished. Never fails the flash: the board is already done."""
    body = {
        "erased": erased,
        "env": env if env in set(REGION_TO_ENV.values()) else None,
        "firmware": firmware_version(),
    }
    try:
        api_request("POST", f"{base}/api/provisioning/kits/{kit_id}/flashed", token, body)
        print("   Logged : the app has recorded this flash")
    except ApiError as err:
        print(f"  ! Flashed, but the app did not record it: {err.message}")


def resolve_env(region, override):
    if override:
        return override
    key = (region or "").upper()
    if not key:
        print(f"  ! No LoRa region set -> defaulting to env 'EU'.")
        return "EU"
    env = REGION_TO_ENV.get(key)
    if not env:
        sys.exit(f"ERROR: Unknown LoRa region '{region}'. Use --env to set it manually.")
    return env


def render_header(board):
    if not TEMPLATE_PATH.exists():
        sys.exit(f"ERROR: template not found: {TEMPLATE_PATH}")
    text = TEMPLATE_PATH.read_text(encoding="utf-8")

    appeui = board.get("appeui") or ""
    # CSV stores APPEUI as "0"; LMIC expects a 16-hex-digit string.
    if appeui in ("", "0"):
        appeui = "0000000000000000"
    deveui = board.get("deveui") or "0000000000000000"
    appkey = board.get("appkey") or "00000000000000000000000000000000"
    mqtt_ip = board.get("mqtt_ip") or DEFAULT_MQTT_IP

    replacements = {
        "__BOARD_ID__": str(board["kit_id"]),
        "__API_KEY__": board["api_key"],
        "__OTAA_APPEUI__": appeui,
        "__OTAA_DEVEUI__": deveui,
        "__OTAA_APPKEY__": appkey,
        "__MQTT_SERVER_IP__": mqtt_ip,
    }
    for token, value in replacements.items():
        text = text.replace(token, value)

    leftover = [t for t in replacements if t in text]
    if leftover:
        sys.exit(f"ERROR: unreplaced placeholder(s) remain: {leftover}")

    HEADER_PATH.write_text(text, encoding="utf-8")


def main():
    ap = argparse.ArgumentParser(description="Flash a TAC board by Kit ID.")
    ap.add_argument("kit_id", help="Kit ID from Boards_List.csv, e.g. 1014")
    ap.add_argument("--port", help="Serial upload port (e.g. COM7). Default: PIO autodetect.")
    ap.add_argument("--env", help="Override PlatformIO env / LoRa region (EU, US, AU, AS, JP, KR, IN).")
    ap.add_argument("--erase", action="store_true",
                    help="Full chip erase before flashing. Wipes stored config + WiFi so a "
                         "different Kit ID actually takes effect (required when re-flashing a "
                         "board with a new ID).")
    ap.add_argument("--no-upload", action="store_true", help="Generate header and build, but do not upload.")
    ap.add_argument("--dry-run", action="store_true", help="Show the plan without touching files or flashing.")
    ap.add_argument("--source", choices=("csv", "api"), default="csv",
                    help="Where the credentials come from: Boards_List.csv (default) or the web app.")
    ap.add_argument("--api-url",
                    help=f"The web app's address for --source api, e.g. https://example.org. "
                         f"Default: the {API_URL_ENV} environment variable.")
    args = ap.parse_args()

    if args.source == "api":
        base, token = api_settings(args)
        board = load_board_from_api(args.kit_id, base, token)
    else:
        board = load_board(args.kit_id)
    env = resolve_env(board.get("region"), args.env)

    print(f"== Kit {args.kit_id}: {board.get('name') or '(no name)'} ==")
    print(f"   Source : {'web app' if args.source == 'api' else CSV_PATH.name}")
    print(f"   Region : {board.get('region') or '(none)'}  ->  PlatformIO env '{env}'")
    print(f"   DEVEUI : {board.get('deveui') or '(none)'}")
    print(f"   MQTT   : {board.get('mqtt_ip') or DEFAULT_MQTT_IP}")
    print(f"   Port   : {args.port or 'autodetect'}")
    print(f"   Erase  : {'YES - wipes stored config + WiFi' if args.erase else 'no'}")

    target = "build (no upload)" if args.no_upload else "upload"
    if args.dry_run:
        if args.erase:
            print(f"-- dry-run: would run PlatformIO target 'erase' --")
        print(f"-- dry-run: would render header and run PlatformIO target '{target}' --")
        return

    render_header(board)
    print(f"   Wrote  : {HEADER_PATH.relative_to(ROOT)}")

    # A board flash bakes in real credentials - do NOT let copyFirmware.py
    # overwrite the credential-free release binaries in Firmware/.
    child_env = os.environ.copy()
    child_env["TAC_SKIP_RELEASE_COPY"] = "1"

    def run_pio(cmd):
        print(f"-- running: {' '.join(cmd)}")
        try:
            return subprocess.run(cmd, env=child_env).returncode
        except FileNotFoundError:
            sys.exit("ERROR: 'pio' not found. Run from a terminal where PlatformIO is on PATH "
                     "(or use the PlatformIO IDE terminal).")

    # Full chip erase first, so stale stored config can't override the new Kit ID.
    if args.erase:
        erase_cmd = ["pio", "run", "-e", env, "-t", "erase"]
        if args.port:
            erase_cmd += ["--upload-port", args.port]
        rc = run_pio(erase_cmd)
        if rc != 0:
            sys.exit(rc)

    cmd = ["pio", "run", "-e", env]
    if not args.no_upload:
        cmd += ["-t", "upload"]
        if args.port:
            cmd += ["--upload-port", args.port]

    rc = run_pio(cmd)

    # record real uploads only; the CSV path never talks to the app
    if rc == 0 and args.source == "api" and not args.no_upload:
        report_flash(base, token, args.kit_id, env, args.erase)

    sys.exit(rc)


if __name__ == "__main__":
    main()
