"""Window alert: tells you when it's a good time to open the windows, and
reminds you to close them when it gets cold or rain is coming.

Runs from GitHub Actions every 15 min. Python 3.12 + requests only.
Env vars: MODE (auto|notify_me|announce), DRY_RUN=1, FORCE_TEST=1,
          VOICEMONKEY_TOKEN, VOICEMONKEY_DEVICE, NOTIFYME_ACCESS_CODE,
          VOICEMONKEY_CHIME
"""
import json
import os
import sys
import time
from datetime import datetime, time as dtime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import requests

from flair import build_message

# ---------------------------------------------------------------- CONFIG ---
CONFIG = {
    "lat": 45.76,
    "lon": -73.82,
    "tz": "America/Toronto",
    # When an "open the windows" alert may fire (max ONE per day):
    "weekday_slots": [dtime(12, 0), dtime(17, 0)],  # Mon-Fri, noon and 5pm
    "slot_minutes": 30,            # each slot stays open this long (covers cron delays)
    "weekend_start": dtime(8, 0),  # Sat/Sun: any time in this window
    "weekend_end": dtime(20, 0),
    # Conditions to open:
    "temp_min": 15.0,              # C, inclusive
    "temp_max": 22.0,              # C, inclusive
    "hum_min": 30.0,               # %, inclusive
    "hum_max": 65.0,               # %, inclusive
    "dew_max": 15.0,               # C, strictly under
    "wind_max": 30.0,              # km/h, strictly under
    "optimal_temp": 18.0,          # at or above this = optimal, alert is also spoken
    # "Close the windows" reminder:
    "cold_close": 13.0,            # close if now or within ~2h it drops below this (C)
    "rain_prob_close": 50,         # close if rain chance in next ~2h reaches this (%)
    "close_from": dtime(7, 0),     # only send close reminders inside these hours
    "close_until": dtime(23, 0),
    "mode_default": "auto",        # auto = silent ping always, spoken too if optimal
    "indoor_margin": 2.0,          # FUTURE HOOK: outside must be this much cooler than inside
    "chime": "",                   # spoken mode: sound before speech (or VOICEMONKEY_CHIME)
}
STATE_FILE = Path(__file__).parent / "state.json"
API = "https://api.open-meteo.com/v1/forecast"
VM_URL = "https://api-v3.voicemonkey.io/announce"
NM_URL = "https://api.notifymyecho.com/v1/NotifyMe"


# ------------------------------------------------------- PURE DECISION LOGIC
def in_alert_window(now: datetime, cfg=CONFIG) -> bool:
    """Weekdays: only the noon and 5pm slots. Weekends: the daytime window."""
    t = now.time()
    if now.weekday() < 5:
        for start in cfg["weekday_slots"]:
            begin = datetime.combine(now.date(), start)
            end = begin + timedelta(minutes=cfg["slot_minutes"])
            if begin.time() <= t < end.time():
                return True
        return False
    return cfg["weekend_start"] <= t < cfg["weekend_end"]


def is_optimal(w: dict, cfg=CONFIG) -> bool:
    return w["temp"] >= cfg["optimal_temp"]


def close_reason(w: dict, cfg=CONFIG):
    """Return "rain", "cold" or None."""
    if w["precip"] > 0 or w["rain_soon"]:
        return "rain"
    if w["temp"] < cfg["cold_close"] or w["min_temp_soon"] < cfg["cold_close"]:
        return "cold"
    return None


def evaluate(now_local: datetime, w: dict, cfg=CONFIG, indoor_temp=None):
    """Return (ok, checks): is it a good moment to open the windows?"""
    checks = {
        "time": in_alert_window(now_local, cfg),
        "temp": cfg["temp_min"] <= w["temp"] <= cfg["temp_max"],
        "humidity": cfg["hum_min"] <= w["humidity"] <= cfg["hum_max"],
        "dew_point": w["dew_point"] < cfg["dew_max"],
        "no_precip": w["precip"] == 0,
        "no_rain_soon": not w["rain_soon"],
        "not_getting_cold": w["min_temp_soon"] >= cfg["cold_close"],
        "wind": w["wind"] < cfg["wind_max"],
    }
    # FUTURE HOOK: indoor sensor. Pass indoor_temp and the rule becomes
    # "outside at least indoor_margin C cooler than inside".
    if indoor_temp is not None:
        checks["cooler_than_inside"] = w["temp"] <= indoor_temp - cfg["indoor_margin"]
    return all(checks.values()), checks


def next_state(state: dict, today: str, ok: bool, closing):
    """One open alert per day. A close reminder only follows an open alert.
    Returns (new_state, action) with action in {None, "open", "close"}."""
    s = dict(state)
    if s.get("day") != today:        # new day: forget yesterday's open windows
        s["day"], s["open"] = today, False
    if s["open"] and closing:
        s["open"] = False
        return s, "close"
    if ok and s.get("last_alert") != today:
        s["last_alert"], s["open"] = today, True
        return s, "open"
    return s, None


# ------------------------------------------------------------------- I/O ---
def fetch_weather(cfg=CONFIG) -> dict:
    params = {
        "latitude": cfg["lat"], "longitude": cfg["lon"], "timezone": cfg["tz"],
        "current": "temperature_2m,relative_humidity_2m,dew_point_2m,"
                   "precipitation,wind_speed_10m",
        "hourly": "temperature_2m,precipitation_probability,precipitation",
        "forecast_hours": 3,  # this hour + next 2
    }
    last = None
    for attempt in range(3):
        try:
            r = requests.get(API, params=params, timeout=15)
            r.raise_for_status()
            j = r.json()
            c, h = j["current"], j["hourly"]
            probs = [p or 0 for p in h["precipitation_probability"]]
            rain = [p or 0 for p in h["precipitation"]]
            return {
                "temp": c["temperature_2m"], "humidity": c["relative_humidity_2m"],
                "dew_point": c["dew_point_2m"], "precip": c["precipitation"],
                "wind": c["wind_speed_10m"],
                "min_temp_soon": min(t for t in h["temperature_2m"] if t is not None),
                "rain_soon": max(probs) >= cfg["rain_prob_close"] or sum(rain) >= 0.2,
            }
        except Exception as e:  # noqa: BLE001
            last = e
            time.sleep(2 ** attempt)
    raise RuntimeError(f"Open-Meteo failed after 3 tries: {last}")


def _notify_me(title, text):
    r = requests.get(NM_URL, timeout=15, params={
        "notification": text,
        "title": title,  # the title is what shows on the Echo itself
        "accessCode": os.environ["NOTIFYME_ACCESS_CODE"],
    })
    r.raise_for_status()


def _announce(title, text):
    payload = {
        "token": os.environ["VOICEMONKEY_TOKEN"],
        "device": os.environ["VOICEMONKEY_DEVICE"],
        "speech": f"{title}. {text}",
    }
    chime = os.environ.get("VOICEMONKEY_CHIME") or CONFIG["chime"]
    if chime:
        payload["chime"] = chime
    r = requests.post(VM_URL, timeout=15, json=payload)
    r.raise_for_status()


def send(mode: str, title: str, text: str, speak: bool):
    """auto: silent ping always, plus spoken when `speak` (if Voice Monkey is set up).
    notify_me: silent only. announce: spoken only."""
    if mode not in ("auto", "notify_me", "announce"):
        raise ValueError(f"unknown MODE {mode!r}")
    if mode in ("auto", "notify_me") and os.environ.get("NOTIFYME_ACCESS_CODE"):
        _notify_me(title, text)
    voice_ready = os.environ.get("VOICEMONKEY_TOKEN") and os.environ.get("VOICEMONKEY_DEVICE")
    if mode == "announce" or (mode == "auto" and speak and voice_ready):
        _announce(title, text)


def load_state() -> dict:
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {"day": "", "open": False, "last_alert": "", "heartbeat": ""}


def main() -> int:
    dry = os.environ.get("DRY_RUN") == "1"
    mode = os.environ.get("MODE") or CONFIG["mode_default"]
    now = datetime.now(ZoneInfo(CONFIG["tz"]))
    today = now.strftime("%Y-%m-%d")

    try:
        w = fetch_weather()
    except RuntimeError as e:
        print(f"ERROR {e}. No alert sent.", file=sys.stderr)
        return 1

    spoken_text = mode == "announce"
    title, msg = build_message(now.date(), w, spoken=spoken_text)

    if os.environ.get("FORCE_TEST") == "1":
        print(f"FORCE_TEST mode={mode} title={title!r} msg={msg!r} dry={dry}")
        if not dry:
            send(mode, title, msg, speak=True)
        return 0

    state = load_state()
    ok, checks = evaluate(now, w)
    reason = close_reason(w)
    new, action = next_state(state, today, ok, reason)
    if action == "close" and not (CONFIG["close_from"] <= now.time() < CONFIG["close_until"]):
        action = None  # too early or late for a reminder; state already cleared

    print(f"{now:%Y-%m-%d %H:%M} ok={ok} action={action} reason={reason} "
          f"optimal={is_optimal(w)} weather={w} checks={checks}")

    if dry:
        print("DRY_RUN: nothing sent, state not saved.")
        return 0

    if action == "open":
        send(mode, title, msg, speak=is_optimal(w))
    elif action == "close":
        c_title, c_msg = build_message(now.date(), w, close=reason)
        send(mode, c_title, c_msg, speak=True)

    if today != new.get("heartbeat"):
        new["heartbeat"] = today  # one commit/day keeps the cron from auto-disabling
    if new != state:
        STATE_FILE.write_text(json.dumps(new, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
