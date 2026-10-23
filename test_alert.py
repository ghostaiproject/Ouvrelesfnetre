import json
import random
from datetime import date, datetime
from zoneinfo import ZoneInfo

import alert
from alert import close_reason, evaluate, in_alert_window, is_optimal, next_state
from flair import CLOSE_LINES, WEATHER_LINES, build_message, holiday_for, weather_kind

TZ = ZoneInfo("America/Toronto")
GOOD = {"temp": 19, "humidity": 50, "dew_point": 8, "precip": 0, "wind": 10,
        "min_temp_soon": 17, "rain_soon": False}


def at(h, m=0, day=22):  # Oct 22 2026 = Thursday, Oct 24 = Saturday
    return datetime(2026, 10, day, h, m, tzinfo=TZ)


def test_good_moment_passes():
    assert evaluate(at(12), GOOD)[0]
    assert evaluate(at(17), GOOD)[0]


def test_weekday_slots():
    assert in_alert_window(at(12, 0))
    assert in_alert_window(at(12, 29))
    assert not in_alert_window(at(12, 30))
    assert in_alert_window(at(17, 0))
    assert not in_alert_window(at(17, 30))
    assert not in_alert_window(at(8, 0))
    assert not in_alert_window(at(23, 0))


def test_weekend_window():
    assert in_alert_window(at(8, 0, day=24))
    assert in_alert_window(at(19, 59, day=24))
    assert not in_alert_window(at(7, 59, day=24))
    assert not in_alert_window(at(20, 0, day=24))


def test_temp_edges():
    assert evaluate(at(12), {**GOOD, "temp": 15})[0]
    assert evaluate(at(12), {**GOOD, "temp": 22})[0]
    assert not evaluate(at(12), {**GOOD, "temp": 14.9})[0]
    assert not evaluate(at(12), {**GOOD, "temp": 22.1})[0]


def test_humidity_edges():
    assert evaluate(at(12), {**GOOD, "humidity": 65})[0]
    assert evaluate(at(12), {**GOOD, "humidity": 30})[0]
    assert not evaluate(at(12), {**GOOD, "humidity": 65.1})[0]
    assert not evaluate(at(12), {**GOOD, "humidity": 29.9})[0]


def test_dew_precip_wind():
    assert not evaluate(at(12), {**GOOD, "dew_point": 15})[0]
    assert not evaluate(at(12), {**GOOD, "precip": 0.1})[0]
    assert not evaluate(at(12), {**GOOD, "wind": 30})[0]


def test_no_open_when_rain_or_cold_coming():
    assert not evaluate(at(12), {**GOOD, "rain_soon": True})[0]
    assert not evaluate(at(12), {**GOOD, "min_temp_soon": 12.9})[0]


def test_optimal():
    assert is_optimal({**GOOD, "temp": 18})
    assert not is_optimal({**GOOD, "temp": 17.9})


def test_close_reason():
    assert close_reason(GOOD) is None
    assert close_reason({**GOOD, "rain_soon": True}) == "rain"
    assert close_reason({**GOOD, "precip": 0.3}) == "rain"
    assert close_reason({**GOOD, "temp": 12.9}) == "cold"
    assert close_reason({**GOOD, "min_temp_soon": 12.5}) == "cold"


def test_one_open_alert_per_day_then_close():
    s = {"day": "", "open": False, "last_alert": ""}
    s, a = next_state(s, "d1", True, None)
    assert a == "open"
    s, a = next_state(s, "d1", True, None)        # still good: no repeat
    assert a is None
    s, a = next_state(s, "d1", False, "rain")     # rain: close reminder
    assert a == "close" and not s["open"]
    s, a = next_state(s, "d1", True, None)        # good again same day: still only 1/day
    assert a is None
    s, a = next_state(s, "d2", True, None)        # next day: allowed again
    assert a == "open"


def test_close_only_after_open():
    s = {"day": "d1", "open": False, "last_alert": ""}
    s, a = next_state(s, "d1", False, "cold")
    assert a is None


def test_open_forgotten_on_new_day():
    s = {"day": "d1", "open": True, "last_alert": "d1"}
    s, a = next_state(s, "d2", False, "cold")
    assert a is None and not s["open"]


def test_holidays():
    assert holiday_for(date(2026, 10, 31)) == "halloween"
    assert holiday_for(date(2026, 10, 24)) == "halloween"
    assert holiday_for(date(2026, 10, 22)) is None
    assert holiday_for(date(2026, 10, 12)) == "thanksgiving"
    assert holiday_for(date(2026, 12, 25)) == "christmas"
    assert holiday_for(date(2027, 1, 1)) == "newyear"
    assert holiday_for(date(2026, 6, 24)) == "stjean"


def test_message_builds():
    t, b = build_message(date(2026, 10, 22), GOOD, rng=random.Random(1))
    assert t and "19 C" in b
    t, b = build_message(date(2026, 10, 22), GOOD, spoken=True)
    assert "degrees" in b
    assert build_message(date(2026, 10, 30), GOOD)[0]
    assert build_message(date(2026, 10, 22), GOOD, close="rain") in CLOSE_LINES["rain"]
    assert build_message(date(2026, 10, 22), GOOD, close="cold") in CLOSE_LINES["cold"]


def test_weather_kind():
    assert weather_kind({**GOOD, "temp": 16}) == "cool"
    assert weather_kind({**GOOD, "temp": 18}) == "mild"
    assert weather_kind({**GOOD, "temp": 20}) == "mild"
    assert weather_kind({**GOOD, "temp": 21}) == "warm"
    assert weather_kind({**GOOD, "wind": 20}) == "breezy"


def test_titles_match_weather_and_temp():
    d = date(2026, 10, 22)
    for kind, w in (("cool", {**GOOD, "temp": 16}), ("mild", GOOD),
                    ("warm", {**GOOD, "temp": 21.6}), ("breezy", {**GOOD, "wind": 25})):
        allowed = {t for t, _ in WEATHER_LINES[kind]}
        for seed in range(10):
            t, _ = build_message(d, w, rng=random.Random(seed))
            deg = f"{w['temp']:.0f}°"
            assert deg in t and t.replace(deg, "{deg}") in allowed
    assert "19 degrees" in build_message(d, GOOD, spoken=True)[0]
    assert build_message(date(2026, 10, 30), GOOD)[0].endswith(", 19°")  # holiday title

def test_announce_shows_text_on_screen(monkeypatch):
    sent = {}

    class Resp:
        def raise_for_status(self):
            pass

    def fake_post(url, timeout, json):
        sent.update(json)
        return Resp()

    monkeypatch.setattr(alert.requests, "post", fake_post)
    alert._announce("Open up", "19 degrees outside", "t", "d")
    assert sent["token"] == "t" and sent["device"] == "d"
    assert sent["speech"] == "Open up. 19 degrees outside"
    assert sent["text_display"] == "Open up\n19 degrees outside"
    assert sent["display_seconds"] == alert.CONFIG["display_seconds"]


FRIEND = '{"name": "Mom", "lat": 46.81, "lon": -71.21, "tz": "America/Toronto", "notifyme": "abc"}'


def test_load_homes_main_plus_friends():
    env = {"NOTIFYME_ACCESS_CODE": "mine", "MODE": "announce",
           "ALL_SECRETS": json.dumps({"HOME_MOM": FRIEND, "HOME_BAD": "oops",
                                      "VOICEMONKEY_TOKEN": "x", "GITHUB_TOKEN": "y"})}
    homes = alert.load_homes(env)
    assert [h["id"] for h in homes] == ["main", "mom"]   # broken code skipped
    main, mom = homes
    assert main["notifyme"] == "mine" and main["mode"] == "announce"
    assert mom["name"] == "Mom" and mom["lat"] == 46.81 and mom["notifyme"] == "abc"
    assert mom["mode"] == "auto" and mom["vm_token"] == ""
    assert alert.home_cfg(mom)["lat"] == 46.81 and alert.home_cfg(mom)["temp_min"] == 15.0
    assert [h["id"] for h in alert.load_homes({})] == ["main"]


def test_send_uses_each_homes_codes(monkeypatch):
    calls = []
    monkeypatch.setattr(alert, "_notify_me", lambda t, m, code: calls.append(("nm", code)))
    monkeypatch.setattr(alert, "_announce", lambda t, m, tok, dev, ch: calls.append(("vm", tok)))
    home = {"mode": "auto", "notifyme": "abc", "vm_token": "", "vm_device": "", "chime": ""}
    alert.send(home, "t", "m", speak=True)
    assert calls == [("nm", "abc")]   # no Voice Monkey set up: silent only
    calls.clear()
    alert.send({**home, "vm_token": "tok", "vm_device": "dev"}, "t", "m", speak=True)
    assert calls == [("nm", "abc"), ("vm", "tok")]


def test_old_state_file_becomes_main(tmp_path, monkeypatch):
    f = tmp_path / "state.json"
    f.write_text('{"day": "2026-10-22", "open": true, "last_alert": "2026-10-22", "heartbeat": "2026-10-22"}')
    monkeypatch.setattr(alert, "STATE_FILE", f)
    s = alert.load_state()
    assert s == {"heartbeat": "2026-10-22",
                 "homes": {"main": {"day": "2026-10-22", "open": True, "last_alert": "2026-10-22"}}}
    f.unlink()
    assert alert.load_state()["homes"]["main"] == alert.BLANK


def test_one_broken_home_does_not_stop_others(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(alert, "STATE_FILE", tmp_path / "state.json")
    monkeypatch.setenv("ALL_SECRETS", json.dumps({"HOME_MOM": FRIEND}))
    monkeypatch.delenv("FORCE_TEST", raising=False)
    monkeypatch.delenv("DRY_RUN", raising=False)
    seen = []

    def fake_run(home, state, dry, force):
        seen.append(home["id"])
        if home["id"] == "main":
            raise RuntimeError("https://x/?accessCode=SECRET")
        return {"day": "d", "open": True, "last_alert": "d"}

    monkeypatch.setattr(alert, "run_home", fake_run)
    assert alert.main() == 1
    assert seen == ["main", "mom"]
    assert "SECRET" not in capsys.readouterr().err   # error text is never printed
    saved = json.loads((tmp_path / "state.json").read_text())
    assert saved["homes"]["mom"]["open"] is True     # mom's state still saved
    assert saved["homes"]["main"] == alert.BLANK     # main left as it was


def test_test_alert_only_goes_to_chosen_home(tmp_path, monkeypatch):
    monkeypatch.setattr(alert, "STATE_FILE", tmp_path / "state.json")
    monkeypatch.setenv("ALL_SECRETS", json.dumps({"HOME_MOM": FRIEND}))
    monkeypatch.setenv("FORCE_TEST", "1")
    seen = []
    monkeypatch.setattr(alert, "run_home", lambda h, s, d, f: seen.append(h["id"]) or s)
    monkeypatch.setenv("TEST_HOME", "Mom")
    assert alert.main() == 0 and seen == ["mom"]
    seen.clear()
    monkeypatch.delenv("TEST_HOME")
    assert alert.main() == 0 and seen == ["main"]
    monkeypatch.setenv("TEST_HOME", "nobody")
    assert alert.main() == 1
