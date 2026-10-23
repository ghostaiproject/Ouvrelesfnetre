import json
import random
from datetime import date, datetime
from zoneinfo import ZoneInfo

import alert
from alert import close_reason, evaluate, in_alert_window, is_optimal, next_state
from flair import CLOSE_LINES, LINES, WEATHER_LINES, build_message, holiday_for, weather_kind

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
    assert build_message(date(2026, 10, 22), GOOD, close="rain") in [x[:2] for x in CLOSE_LINES["en"]["rain"]]
    assert build_message(date(2026, 10, 22), GOOD, close="cold") in [x[:2] for x in CLOSE_LINES["en"]["cold"]]


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
        allowed = {t for t, *_ in WEATHER_LINES["en"][kind]}
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


def test_25_unique_lines_per_pool_in_both_languages():
    for pools in (WEATHER_LINES, CLOSE_LINES):
        assert set(pools) == {"en", "fr"}
        assert set(pools["en"]) == set(pools["fr"])
        for lang in pools:
            for kind, lines in pools[lang].items():
                assert len(lines) == 25, (lang, kind)
                assert len({t for t, *_ in lines}) == 25, (lang, kind)   # no repeated titles
                assert any(not sun for *_, sun in lines)                 # always a cloudy-day option
    for kind, lines in WEATHER_LINES["fr"].items():
        assert all("{deg}" in t for t, *_ in lines), kind
    assert set(LINES["en"]) == set(LINES["fr"])


def test_french_messages():
    d = date(2026, 10, 22)
    for seed in range(20):
        t, b = build_message(d, GOOD, rng=random.Random(seed), lang="fr")
        assert "19°" in t and t.replace("19°", "{deg}") in {x for x, *_ in WEATHER_LINES["fr"]["mild"]}
        assert "19 C dehors, 50 pour cent d'humidité, point de rosée 8." in b
    t, b = build_message(d, GOOD, spoken=True, lang="fr")
    assert "19 degrés" in t and "19 degrés dehors" in b
    assert build_message(d, GOOD, close="rain", lang="fr") in [x[:2] for x in CLOSE_LINES["fr"]["rain"]]
    assert build_message(date(2026, 10, 30), GOOD, lang="fr") [0].endswith(", 19°")
    assert build_message(date(2026, 10, 30), GOOD, lang="fr")[0].replace(", 19°", "") in \
        {x for x, *_ in LINES["fr"]["halloween"]}
    assert build_message(d, GOOD, lang="xx")[1].endswith("dew point 8.")  # unknown -> English


def test_homes_carry_their_language():
    fr = json.dumps({**json.loads(FRIEND), "lang": "fr"})
    homes = alert.load_homes({"ALERT_LANG": "FR", "ALL_SECRETS": json.dumps(
        {"HOME_MOM": FRIEND, "HOME_JULIE": fr})})
    assert {h["id"]: h["lang"] for h in homes} == {"main": "fr", "julie": "fr", "mom": "en"}
    assert alert.load_homes({})[0]["lang"] == "en"


def test_sun_jokes_only_when_sunny():
    d, hot = date(2026, 10, 22), {**GOOD, "temp": 21}
    sun_titles = {t for lang in ("en", "fr") for t, _, s in WEATHER_LINES[lang]["warm"] if s}
    for lang in ("en", "fr"):
        for seed in range(200):
            t, _ = build_message(d, {**hot, "sunny": False}, rng=random.Random(seed), lang=lang)
            assert t.replace("21°", "{deg}") not in sun_titles
    seen = {build_message(d, {**hot, "sunny": True}, rng=random.Random(s))[0].replace("21°", "{deg}")
            for s in range(300)}
    assert seen & sun_titles   # sunny days can get them


def test_compact_home_code():
    code = json.dumps({"n": "Julie", "p": [46.813, -71.208], "l": "fr", "c": "abc"})
    vm_only = json.dumps({"n": "Chalet", "p": [45.5, -73.6], "l": "en", "z": "America/Halifax",
                          "t": "tok", "d": "echo-1"})
    homes = {h["id"]: h for h in alert.load_homes({"ALL_SECRETS": json.dumps(
        {"HOME_JULIE": code, "HOME_CHALET": vm_only})})}
    j, c = homes["julie"], homes["chalet"]
    assert (j["name"], j["lat"], j["lon"], j["lang"], j["notifyme"], j["mode"], j["tz"]) == \
        ("Julie", 46.813, -71.208, "fr", "abc", "auto", "America/Toronto")
    assert (c["mode"], c["tz"], c["vm_token"], c["vm_device"], c["notifyme"]) == \
        ("announce", "America/Halifax", "tok", "echo-1", "")


def test_answer_should_i_open():
    late = at(23, 30)   # asking outside the alert slots still gets a real answer
    assert alert.answer(GOOD, late, "en", rng=random.Random(1)).startswith("Yes! 19 degrees")
    assert alert.answer(GOOD, late, "fr").startswith("Oui! 19 degrés")
    assert alert.answer({**GOOD, "precip": 1, "rain_soon": True}, late, "en") == \
        "Not right now: it's raining right now."
    assert alert.answer({**GOOD, "temp": 9, "min_temp_soon": 6}, late, "fr") == \
        "Pas maintenant : il fait juste 9 degrés, trop frais et ça descend à 6 degrés bientôt."
    assert "too warm" in alert.answer({**GOOD, "temp": 25}, late, "en")
    assert "too dry" in alert.answer({**GOOD, "humidity": 20}, late, "en")
    assert "kilomètres à l'heure" in alert.answer({**GOOD, "wind": 40}, late, "fr")


GFRIEND = '{"n": "Maman", "p": [46.81, -71.21], "l": "fr", "g": "fenetres-abc123"}'


def test_phone_homes_get_pushes(monkeypatch):
    env = {"ALL_SECRETS": json.dumps({"PHONE_MAMAN": GFRIEND, "HOME_MOM": FRIEND, "GHOME_OLD": GFRIEND,
                                      "GHOME_BAD": '{"n": "x"}', "GHOME_SLASH": '{"p": [1, 2], "g": "a/b"}'})}
    homes = alert.load_homes(env)
    assert [h["id"] for h in homes] == ["main", "p-old", "mom", "p-maman"]   # broken codes skipped, old GHOME_ read
    g = homes[3]
    assert g["mode"] == "push" and g["ntfy"] == "fenetres-abc123" and g["lang"] == "fr"
    assert g["lat"] == 46.81 and g["tz"] == "America/Toronto" and g["notifyme"] == ""
    calls = []
    monkeypatch.setattr(alert, "_ntfy", lambda t, m, topic, kind: calls.append((topic, kind)))
    monkeypatch.setattr(alert, "_notify_me", lambda *a: calls.append("nm"))
    monkeypatch.setattr(alert, "_announce", lambda *a: calls.append("vm"))
    alert.send(g, "t", "m", speak=False)
    alert.send(g, "t", "m", speak=True, kind="rain")
    assert calls == [("fenetres-abc123", "open"), ("fenetres-abc123", "rain")]


def test_ntfy_payload(monkeypatch):
    sent = {}

    class Resp:
        def raise_for_status(self):
            pass

    def fake_post(url, timeout, json):
        sent.update(json, url=url)
        return Resp()

    monkeypatch.setattr(alert.requests, "post", fake_post)
    alert._ntfy("Fenêtre ouverte 19°", "Il fait doux", "fenetres-abc123", "cold")
    assert sent["url"] == "https://ntfy.sh/" and sent["topic"] == "fenetres-abc123"
    assert sent["title"] == "Fenêtre ouverte 19°" and sent["message"] == "Il fait doux"
    assert "tags" not in sent and sent["priority"] == 4   # no emoji: phones may read it aloud


def test_test_alert_finds_phone_home_by_name(tmp_path, monkeypatch):
    monkeypatch.setattr(alert, "STATE_FILE", tmp_path / "state.json")
    monkeypatch.setenv("ALL_SECRETS", json.dumps({"PHONE_MAMAN": GFRIEND}))
    monkeypatch.setenv("FORCE_TEST", "1")
    seen = []
    monkeypatch.setattr(alert, "run_home", lambda h, s, d, f: seen.append(h["id"]) or s)
    monkeypatch.setenv("TEST_HOME", "maman")
    assert alert.main() == 0 and seen == ["p-maman"]
