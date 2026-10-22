from datetime import datetime
from zoneinfo import ZoneInfo

from datetime import date

from alert import CONFIG, evaluate, in_night_window, next_state
from flair import build_message, holiday_for

TZ = ZoneInfo("America/Toronto")
GOOD = {"temp": 17, "humidity": 50, "dew_point": 8, "precip": 0, "wind": 10}


def at(h, m=0):
    return datetime(2026, 10, 22, h, m, tzinfo=TZ)


def test_good_night_passes():
    assert evaluate(at(23), GOOD)[0]


def test_time_edges():
    assert in_night_window(at(22, 0))
    assert not in_night_window(at(21, 59))
    assert in_night_window(at(5, 59))
    assert not in_night_window(at(6, 0))


def test_temp_edges():
    assert evaluate(at(23), {**GOOD, "temp": 15})[0]
    assert evaluate(at(23), {**GOOD, "temp": 22})[0]
    assert not evaluate(at(23), {**GOOD, "temp": 14.9})[0]
    assert not evaluate(at(23), {**GOOD, "temp": 22.1})[0]


def test_humidity_edges():
    assert evaluate(at(23), {**GOOD, "humidity": 65})[0]
    assert evaluate(at(23), {**GOOD, "humidity": 30})[0]
    assert not evaluate(at(23), {**GOOD, "humidity": 65.1})[0]
    assert not evaluate(at(23), {**GOOD, "humidity": 29.9})[0]


def test_dew_precip_wind():
    assert not evaluate(at(23), {**GOOD, "dew_point": 15})[0]
    assert not evaluate(at(23), {**GOOD, "precip": 0.1})[0]
    assert not evaluate(at(23), {**GOOD, "wind": 30})[0]


def test_indoor_hook():
    assert evaluate(at(23), GOOD, indoor_temp=20)[0]
    assert not evaluate(at(23), GOOD, indoor_temp=18)[0]


def test_alert_once_then_rearm():
    s = {"armed": True, "open": False, "misses": 0}
    s, a = next_state(s, True)
    assert a == "open"
    s, a = next_state(s, True)
    assert a is None
    s, a = next_state(s, False)          # 1 miss: closes, not re-armed yet
    assert a == "close" and not s["armed"]
    s, a = next_state(s, True)           # flap back in: no alert
    assert a is None
    s, _ = next_state(s, False)
    s, _ = next_state(s, False)          # 2 misses: re-armed
    assert s["armed"]
    s, a = next_state(s, True)
    assert a == "open"


def test_holidays():
    assert holiday_for(date(2026, 10, 31)) == "halloween"
    assert holiday_for(date(2026, 10, 24)) == "halloween"
    assert holiday_for(date(2026, 10, 22)) is None
    assert holiday_for(date(2026, 10, 12)) == "thanksgiving"
    assert holiday_for(date(2026, 12, 25)) == "christmas"
    assert holiday_for(date(2027, 1, 1)) == "newyear"
    assert holiday_for(date(2026, 6, 24)) == "stjean"


def test_message_builds():
    import random
    t, b = build_message(date(2026, 10, 22), GOOD, rng=random.Random(1))
    assert t and "17 C" in b
    t, b = build_message(date(2026, 10, 22), GOOD, spoken=True)
    assert "degrees" in b
    t, b = build_message(date(2026, 10, 30), GOOD)
    assert t
    assert build_message(date(2026, 10, 22), GOOD, close=True)[0]
