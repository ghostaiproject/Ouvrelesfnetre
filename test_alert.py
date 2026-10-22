import random
from datetime import date, datetime
from zoneinfo import ZoneInfo

from alert import close_reason, evaluate, in_alert_window, is_optimal, next_state
from flair import CLOSE_LINES, build_message, holiday_for

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
