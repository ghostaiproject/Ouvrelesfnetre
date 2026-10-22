"""Window alert: pings an Amazon Echo when it's a good night to open the windows.

Runs from GitHub Actions every 15 min. Python 3.12 + requests only.
Env vars: MODE (announce|notify_me), DRY_RUN=1, FORCE_TEST=1,
          VOICEMONKEY_TOKEN, VOICEMONKEY_DEVICE, NOTIFYME_ACCESS_CODE
"""
import json
import os
import sys
import time
from datetime import datetime, time as dtime
from pathlib import Path
from zoneinfo import ZoneInfo

import requests

from flair import build_message

# ---------------------------------------------------------------- CONFIG ---
CONFIG = {
    "lat": 45.76,
    "lon": -73.82,
    "tz": "America/Toronto",
    "night_start": dtime(22, 0),   # inclusive
    "night_end": dtime(6, 0),      # exclusive
    "temp_min": 15.0,              # C, inclusive (raise = fewer cold-night alerts)
    "temp_max": 22.0,              # C, inclusive
    "hum_min": 30.0,               # %, inclusive
    "hum_max": 65.0,               # %, inclusive
    "dew_max": 15.0,               # C, strictly under
    "wind_max": 30.0,              # km/h, strictly under
    "rearm_after_misses": 2,       # consecutive bad checks before re-arming
    "close_alert": False,          # also alert when conditions leave range
    "mode_default": "notify_me",   # "announce" (spoken) or "notify_me" (silent glow)
    "indoor_margin": 2.0,          # FUTURE HOOK: outside must be this much cooler than inside
    "chime": "",                   # announce mode only: sound played before speech.
                                   # Or set the VOICEMONKEY_CHIME env var / repo variable.
}
STATE_FILE = Path(__file__).parent / "state.json"
API = "https://api.open-meteo.com/v1/forecast"
VM_URL = "https://api-v3.voicemonkey.io/announce"
NM_URL = "https://api.notifymyecho.com/v1/NotifyMe"


# ------------------------------------------------------- PURE DECISION LOGIC
def in_night_window(now_local: datetime, cfg=CONFIG) -> bool:
    t = now_local.time()
    s, e = cfg["night_start"], cfg["night_end"]
    return t >= s or t < e if s > e else s <= t < e


def evaluate(now_local: datetime, w: dict, cfg=CONFIG, indoor_temp=None):
    """Return (ok, checks) where checks maps condition name -> bool."""
    checks = {
        "night": in_night_window(now_local, cfg),
        "temp": cfg["temp_min"] <= w["temp"] <= cfg["temp_max"],
        "humidity": cfg["hum_min"] <= w["humidity"] <= cfg["hum_max"],
        "dew_point": w["dew_point"] < cfg["dew_max"],
        "no_precip": w["precip"] == 0,
        "wind": w["wind"] < cfg["wind_max"],
    }
    # FUTURE HOOK: indoor sensor. Pass indoor_temp and the rule becomes
    # "outside at least indoor_margin C cooler than inside".
    if indoor_temp is not None:
        checks["cooler_than_inside"] = w["temp"] <= indoor_temp - cfg["indoor_margin"]
    return all(checks.values()), checks


def next_state(state: dict, ok: bool, cfg=CONFIG):
    """Hysteresis: alert once on entry, re-arm after N consecutive misses.
    Returns (new_state, action) with action in {None, "open", "close"}."""
    s = dict(state)
    action = None
    if ok:
        s["misses"] = 0
        if s["armed"]:
            action, s["armed"], s["open"] = "open", False, True
    else:
        s["misses"] = s["misses"] + 1
        if s["open"]:
            action, s["open"] = "close", False
        if s["misses"] >= cfg["rearm_after_misses"]:
            s["armed"] = True
    return s, action


# ------------------------------------------------------------------- I/O ---
def fetch_weather(cfg=CONFIG) -> dict:
    params = {
        "latitude": cfg["lat"], "longitude": cfg["lon"], "timezone": cfg["tz"],
        "current": "temperature_2m,relative_humidity_2m,dew_point_2m,"
                   "precipitation,wind_speed_10m",
    }
    last = None
    for attempt in range(3):
        try:
            r = requests.get(API, params=params, timeout=15)
            r.raise_for_status()
            c = r.json()["current"]
            return {
                "temp": c["temperature_2m"], "humidity": c["relative_humidity_2m"],
                "dew_point": c["dew_point_2m"], "precip": c["precipitation"],
                "wind": c["wind_speed_10m"],
            }
        except Exception as e:  # noqa: BLE001
            last = e
            time.sleep(2 ** attempt)
    raise RuntimeError(f"Open-Meteo failed after 3 tries: {last}")


def send(mode: str, title: str, text: str):
    if mode == "announce":
        payload = {
            "token": os.environ["VOICEMONKEY_TOKEN"],
            "device": os.environ["VOICEMONKEY_DEVICE"],
            "speech": f"{title}. {text}",
        }
        chime = os.environ.get("VOICEMONKEY_CHIME") or CONFIG["chime"]
        if chime:
            payload["chime"] = chime
        r = requests.post(VM_URL, timeout=15, json=payload)
    elif mode == "notify_me":
        r = requests.get(NM_URL, timeout=15, params={
            "notification": text,
            "title": title,  # the title is what shows on the Echo itself
            "accessCode": os.environ["NOTIFYME_ACCESS_CODE"],
        })
    else:
        raise ValueError(f"unknown MODE {mode!r}")
    r.raise_for_status()


def load_state() -> dict:
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {"armed": True, "open": False, "misses": 0, "heartbeat": ""}


def main() -> int:
    dry = os.environ.get("DRY_RUN") == "1"
    mode = os.environ.get("MODE") or CONFIG["mode_default"]
    now = datetime.now(ZoneInfo(CONFIG["tz"]))

    try:
        w = fetch_weather()
    except RuntimeError as e:
        print(f"ERROR {e}. No alert sent.", file=sys.stderr)
        return 1

    spoken = mode == "announce"
    title, msg = build_message(now.date(), w, spoken=spoken)

    if os.environ.get("FORCE_TEST") == "1":
        print(f"FORCE_TEST mode={mode} title={title!r} msg={msg!r} dry={dry}")
        if not dry:
            send(mode, title, msg)
        return 0

    state = load_state()
    ok, checks = evaluate(now, w)
    new, action = next_state(state, ok)
    if action == "close" and not CONFIG["close_alert"]:
        action = None

    print(f"{now:%Y-%m-%d %H:%M} ok={ok} action={action} armed={new['armed']} "
          f"weather={w} checks={checks}")

    if dry:
        print("DRY_RUN: nothing sent, state not saved.")
        return 0

    if action == "open":
        send(mode, title, msg)
    elif action == "close":
        c_title, c_msg = build_message(now.date(), w, close=True)
        send(mode, c_title, c_msg)

    today = now.strftime("%Y-%m-%d")
    if today != new.get("heartbeat"):
        new["heartbeat"] = today  # one commit/day keeps the cron from auto-disabling
    if new != state:
        STATE_FILE.write_text(json.dumps(new, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
