"""Window alert: tells you when it's a good time to open the windows, and
reminds you to close them when it gets cold or rain is coming.

Runs from GitHub Actions every 15 min. Python 3.12 + requests only.
Env vars: MODE (auto|notify_me|announce), DRY_RUN=1, FORCE_TEST=1,
          TEST_HOME (main|<name>|all, for FORCE_TEST),
          VOICEMONKEY_TOKEN, VOICEMONKEY_DEVICE, NOTIFYME_ACCESS_CODE,
          VOICEMONKEY_CHIME, ALERT_LANG (en|fr, your own home), ALL_SECRETS (JSON of all repo secrets; each
          HOME_<NAME> secret is one more Echo home (docs/echo.html), each PHONE_<NAME> secret one more
          home without an Echo that gets phone pushes through ntfy (docs/phone.html))
"""
import hashlib
import json
import os
import sys
import time
from datetime import datetime, time as dtime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import requests

from flair import REASONS, build_message, norm_lang

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
    "display_seconds": 60,         # spoken mode: how long the text stays on the Echo Show screen
    "sunny_cloud_max": 40,         # cloud cover % under this (daytime) = sunny, sun jokes allowed
}
STATE_FILE = Path(__file__).parent / "state.json"
API = "https://api.open-meteo.com/v1/forecast"
VM_URL = "https://api-v3.voicemonkey.io/announce"
NM_URL = "https://api.notifymyecho.com/v1/NotifyMe"
NTFY_URL = "https://ntfy.sh/"


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
def fetch_weather(cfg=CONFIG, tries=3, timeout=15) -> dict:
    params = {
        "latitude": cfg["lat"], "longitude": cfg["lon"], "timezone": cfg["tz"],
        "current": "temperature_2m,relative_humidity_2m,dew_point_2m,"
                   "precipitation,wind_speed_10m,cloud_cover,is_day",
        "hourly": "temperature_2m,precipitation_probability,precipitation",
        "forecast_hours": 3,  # this hour + next 2
    }
    last = None
    for attempt in range(tries):
        try:
            r = requests.get(API, params=params, timeout=timeout)
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
                # sun jokes only when the sun is really out right now
                "sunny": bool(c.get("is_day")) and (c.get("cloud_cover") or 0) < cfg["sunny_cloud_max"],
            }
        except Exception as e:  # noqa: BLE001
            last = e
            if attempt < tries - 1:
                time.sleep(2 ** attempt)
    raise RuntimeError(f"Open-Meteo failed after {tries} tries: {last}")

def answer(w: dict, now_local: datetime, lang="en", cfg=CONFIG, rng=None) -> str:
    """Spoken reply to "should I open the windows?": same rules as the alert,
    except the time-of-day slots (you asked, so the time is always fine)."""
    lang = norm_lang(lang)
    r = REASONS[lang]
    ok, checks = evaluate(now_local, w, cfg)
    failed = [k for k, v in checks.items() if not v and k != "time"]
    if not failed:
        kw = {"rng": rng} if rng else {}
        title, body = build_message(now_local.date(), w, spoken=True, lang=lang, **kw)
        return r["yes"].format(title=title, body=body)
    keys = []
    for k in failed:
        if k == "temp":
            keys.append("too_cold" if w["temp"] < cfg["temp_min"] else "too_hot")
        elif k == "humidity":
            keys.append("too_damp" if w["humidity"] > cfg["hum_max"] else "too_dry")
        elif k in r:
            keys.append(k)
    if "no_precip" in keys and "no_rain_soon" in keys:
        keys.remove("no_rain_soon")  # raining now says enough
    vals = {"t": f"{w['temp']:.0f}", "h": f"{w['humidity']:.0f}", "d": f"{w['dew_point']:.0f}",
            "w": f"{w['wind']:.0f}", "m": f"{w['min_temp_soon']:.0f}"}
    why = r["and"].join(r[k].format(**vals) for k in keys[:2])  # top 2 reasons, short to hear
    return r["no"].format(why=why)


# ----------------------------------------------------------------- HOMES ---
def anon_id(raw: str, prefix: str = "h") -> str:
    """Private id for a home: a hash of its secret code, never its name. The repo and its
    logs are public, so names and towns must never show up in state.json or run logs."""
    return f"{prefix}-" + hashlib.sha256(raw.encode()).hexdigest()[:10]


def aliases(key: str, name: str) -> set:
    """Names that pick this home in a test run (kept in memory only, never printed)."""
    short = key.split("_", 1)[1].lower()
    return {short, str(name).lower(), "p-" + short}


def load_homes(env=os.environ) -> list:
    """Your own home ("main", from the usual secrets) plus one home per
    HOME_<NAME> secret. Each HOME_ secret holds the code from setup.html.
    Compact keys (setup page): n name, p [lat, lon], z timezone (default
    America/Toronto), l lang (en|fr), c Notify Me code, t Voice Monkey token,
    d Voice Monkey device, m mode (default: auto with c, announce without).
    Old long keys (name, lat, lon, tz, notifyme, vm_token, vm_device, mode, lang)
    still work. lang picks the language of every title, joke and spoken line."""
    homes = [{
        "id": "main", "name": "main",
        "lat": CONFIG["lat"], "lon": CONFIG["lon"], "tz": CONFIG["tz"],
        "notifyme": env.get("NOTIFYME_ACCESS_CODE", ""),
        "vm_token": env.get("VOICEMONKEY_TOKEN", ""),
        "vm_device": env.get("VOICEMONKEY_DEVICE", ""),
        "chime": env.get("VOICEMONKEY_CHIME", ""),
        "mode": env.get("MODE") or CONFIG["mode_default"],
        "lang": norm_lang((env.get("ALERT_LANG") or "en").lower()),
    }]
    try:
        secrets = json.loads(env.get("ALL_SECRETS") or "{}")
    except ValueError:
        secrets = {}
    for key in sorted(secrets):
        if key.startswith(("PHONE_", "GHOME_")):   # GHOME_ = first name of PHONE_, still read
            home = _phone_home(key, secrets[key])
            if home:
                homes.append(home)
            continue
        if not key.startswith("HOME_"):
            continue
        hid = key[5:].lower()
        try:
            h = json.loads(secrets[key])
            g = lambda short, long, d="": h.get(short, h.get(long, d))  # noqa: E731
            lat, lon = h["p"] if "p" in h else (h["lat"], h["lon"])
            nm = g("c", "notifyme")
            home = {
                "id": anon_id(secrets[key]), "name": str(g("n", "name") or hid),
                "lat": float(lat), "lon": float(lon),
                "tz": g("z", "tz") or CONFIG["tz"],
                "notifyme": nm,
                "vm_token": g("t", "vm_token"), "vm_device": g("d", "vm_device"),
                "chime": h.get("chime", ""),
                "mode": g("m", "mode") or ("auto" if nm or "lat" in h else "announce"),
                "lang": norm_lang(str(g("l", "lang") or "en").lower()),
            }
            home["aliases"] = aliases(key, home["name"])
            ZoneInfo(home["tz"])  # fail now, not mid-run
        except Exception:  # noqa: BLE001  (never print the secret, its name or its town)
            print(f"ERROR {anon_id(str(secrets[key]))}: not a valid home code, skipped.", file=sys.stderr)
            continue
        homes.append(home)
    return homes


def _phone_home(key: str, raw: str):
    """A PHONE_<NAME> secret (docs/phone.html): the no-Echo fallback. Every alert
    goes to the phone as an ntfy push (any phone; MacroDroid can read it aloud).
    Keys: n name, p [lat, lon], l lang, z timezone (default America/Toronto),
    g ntfy topic. Id is "p-<name>" so it never clashes with an Echo home."""
    try:
        h = json.loads(raw)
        lat, lon = h["p"]
        topic = str(h["g"])
        if not topic or "/" in topic:
            raise ValueError("bad topic")
        home = {
            "id": anon_id(raw, "p"), "name": str(h.get("n") or key.split("_", 1)[1].lower()),
            "lat": float(lat), "lon": float(lon), "tz": h.get("z") or CONFIG["tz"],
            "ntfy": topic, "notifyme": "", "vm_token": "", "vm_device": "", "chime": "",
            "mode": "push", "lang": norm_lang(str(h.get("l") or "fr").lower()),
        }
        home["aliases"] = aliases(key, home["name"])
        ZoneInfo(home["tz"])
    except Exception:  # noqa: BLE001  (never print the secret itself)
        print(f"ERROR {anon_id(str(raw), 'p')}: not a valid phone home code, skipped.", file=sys.stderr)
        return None
    return home


def home_cfg(home: dict) -> dict:
    return {**CONFIG, "lat": home["lat"], "lon": home["lon"], "tz": home["tz"]}


# ------------------------------------------------------------- SENDING ---
def _notify_me(title, text, code):
    r = requests.get(NM_URL, timeout=15, params={
        "notification": text,
        "title": title,  # the title is what shows on the Echo itself
        "accessCode": code,
    })
    r.raise_for_status()


def _announce(title, text, token, device, chime=""):
    payload = {
        "token": token,
        "device": device,
        "speech": f"{title}. {text}",
        "text_display": f"{title}\n{text}",  # shown on the Echo Show screen
        "display_seconds": CONFIG["display_seconds"],
    }
    chime = chime or CONFIG["chime"]
    if chime:
        payload["chime"] = chime
    r = requests.post(VM_URL, timeout=15, json=payload)
    r.raise_for_status()


def _ntfy(title, text, topic, kind="open"):
    """Phone push through ntfy.sh. JSON publish so accents in the title are safe.
    No emoji tags: phones set to read alerts aloud (MacroDroid) would speak them."""
    r = requests.post(NTFY_URL, timeout=15, json={
        "topic": topic, "title": title, "message": text,
        "priority": 4 if kind in ("rain", "cold") else 3,  # close reminders buzz a bit more
    })
    r.raise_for_status()


def send(home: dict, title: str, text: str, speak: bool, kind: str = "open"):
    """auto: silent ping always, plus spoken when `speak` (if Voice Monkey is set up).
    notify_me: silent only. announce: spoken only. push (phone homes): every alert
    goes to the phone, `speak` is ignored. kind: open|rain|cold|test (push icon)."""
    mode = home["mode"]
    if mode == "push":
        _ntfy(title, text, home["ntfy"], kind)
        return
    if mode not in ("auto", "notify_me", "announce"):
        raise ValueError(f"unknown MODE {mode!r}")
    if mode in ("auto", "notify_me") and home["notifyme"]:
        _notify_me(title, text, home["notifyme"])
    voice_ready = home["vm_token"] and home["vm_device"]
    if mode == "announce" or (mode == "auto" and speak and voice_ready):
        _announce(title, text, home["vm_token"], home["vm_device"], home["chime"])


# --------------------------------------------------------------- STATE ---
BLANK = {"day": "", "open": False, "last_alert": ""}


def load_state() -> dict:
    """{"heartbeat": day, "homes": {id: {day, open, last_alert}}}.
    The old one-home file becomes the "main" home."""
    s = json.loads(STATE_FILE.read_text()) if STATE_FILE.exists() else {}
    if "homes" not in s:
        old = {k: s[k] for k in BLANK if k in s}
        s = {"heartbeat": s.get("heartbeat", ""), "homes": {"main": {**BLANK, **old}}}
    return s


# ---------------------------------------------------------------- MAIN ---
def _why(e) -> str:
    """Error type and HTTP status only: request URLs carry access codes and locations."""
    status = getattr(getattr(e, "response", None), "status_code", None)
    return type(e).__name__ + (f" HTTP {status}" if status else "")


def mask_secrets(homes):
    """Hide every code in GitHub's public logs (a HOME_ secret is masked only as a whole)."""
    if os.environ.get("GITHUB_ACTIONS") == "true":
        for h in homes:
            for k in ("notifyme", "vm_token", "vm_device", "ntfy"):
                if h.get(k):
                    print(f"::add-mask::{h[k]}")


def run_home(home: dict, state: dict, dry: bool, force: bool) -> dict:
    """Check one home and alert if needed. Returns that home's new state."""
    cfg = home_cfg(home)
    now = datetime.now(ZoneInfo(cfg["tz"]))
    today = now.strftime("%Y-%m-%d")
    w = fetch_weather(cfg)
    lang = home.get("lang", "en")
    # spoken wording ("19 degrees", not "19 C") also for phones, which may read alerts aloud
    title, msg = build_message(now.date(), w, spoken=home["mode"] in ("announce", "push"), lang=lang)
    tag = f"[{home['id']}]"

    if force:
        print(f"{tag} FORCE_TEST mode={home['mode']} lang={lang} title={title!r} msg={msg!r} dry={dry}")
        if not dry:
            send(home, title, msg, speak=True, kind="test")
        return state

    ok, checks = evaluate(now, w, cfg)
    reason = close_reason(w, cfg)
    new, action = next_state(state, today, ok, reason)
    if action == "close" and not (cfg["close_from"] <= now.time() < cfg["close_until"]):
        action = None  # too early or late for a reminder; state already cleared

    print(f"{tag} {now:%Y-%m-%d %H:%M} ok={ok} action={action} reason={reason} "
          f"optimal={is_optimal(w, cfg)} weather={w} checks={checks}")
    if dry:
        return state

    if action == "open":
        send(home, title, msg, speak=is_optimal(w, cfg))
    elif action == "close":
        c_title, c_msg = build_message(now.date(), w, close=reason, lang=lang)
        send(home, c_title, c_msg, speak=True, kind=reason)
    return new


def main() -> int:
    dry = os.environ.get("DRY_RUN") == "1"
    force = os.environ.get("FORCE_TEST") == "1"
    test_home = (os.environ.get("TEST_HOME") or "main").lower()
    homes = load_homes()
    mask_secrets(homes)
    if force and test_home != "all":
        # pick by the name the person typed (or its secret name); only the private id is printed
        homes = [h for h in homes if test_home == h["id"] or test_home in h.get("aliases", ())]
        if not homes:
            print("ERROR no home with that name.", file=sys.stderr)
            return 1

    state = load_state()
    new = {"heartbeat": state["heartbeat"], "homes": dict(state["homes"])}
    failed = 0
    for home in homes:
        before = state["homes"].get(home["id"], BLANK)
        try:
            new["homes"][home["id"]] = run_home(home, before, dry, force)
        except Exception as e:  # noqa: BLE001  one broken home must not stop the others
            failed += 1
            print(f"ERROR [{home['id']}] {_why(e)}. No alert sent.", file=sys.stderr)

    if dry:
        print("DRY_RUN: nothing sent, state not saved.")
        return 1 if failed else 0

    today = datetime.now(ZoneInfo(CONFIG["tz"])).strftime("%Y-%m-%d")
    if today != new["heartbeat"]:
        new["heartbeat"] = today  # one commit/day keeps the cron from auto-disabling
    if new != state:
        STATE_FILE.write_text(json.dumps(new, indent=2) + "\n")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
