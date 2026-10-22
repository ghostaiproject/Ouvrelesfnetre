"""Fun titles and jokes for the window alert. Pure functions, no network."""
import random
from datetime import date, timedelta


def _fixed(month, day):
    return lambda year: date(year, month, day)


def _thanksgiving(year):
    """Canadian Thanksgiving: second Monday of October."""
    d = date(year, 10, 1)
    first_monday = d + timedelta(days=(0 - d.weekday()) % 7)
    return first_monday + timedelta(days=7)


# name, date function, days the theme starts BEFORE, days it lasts AFTER
HOLIDAYS = [
    ("newyear", _fixed(1, 1), 2, 1),
    ("valentine", _fixed(2, 14), 2, 0),
    ("stpatrick", _fixed(3, 17), 1, 0),
    ("stjean", _fixed(6, 24), 2, 0),
    ("canadaday", _fixed(7, 1), 2, 0),
    ("thanksgiving", _thanksgiving, 2, 0),
    ("halloween", _fixed(10, 31), 7, 0),
    ("christmas", _fixed(12, 25), 13, 1),
    ("nye", _fixed(12, 31), 1, 0),
]

LINES = {
    "newyear": [
        ("New Year, new breeze", "Fresh year, fresh air. Crack those windows."),
        ("Cheers to cool air", "Resolution number one: open the windows."),
    ],
    "valentine": [
        ("Windows, my valentine", "The night air has a crush on your apartment."),
        ("Love is in the air", "Literally. Let it in."),
    ],
    "stpatrick": [
        ("Luck of the breeze", "Lucky night. The air is perfect, no pot of gold needed."),
    ],
    "stjean": [
        ("Bonne Saint-Jean", "Fete nationale vibes. Open up and let the night in."),
        ("Vive le Quebec, vive le vent", "Good night to open up and enjoy the breeze."),
    ],
    "canadaday": [
        ("Happy Canada Day", "Perfect night to open up. Very polite weather, eh."),
    ],
    "thanksgiving": [
        ("Thankful for cool air", "Be thankful, the weather delivered. Windows open, leftovers cold."),
    ],
    "halloween": [
        ("Spooky season breeze", "The night is whispering. Open a window, if you dare."),
        ("Boo! It's window time", "Ghosts need ventilation too."),
        ("Fresh air, fright night", "Perfect crisp night. Just don't invite anything in."),
    ],
    "christmas": [
        ("Frosty fresh air", "Santa checked the forecast. Windows open, you're good."),
        ("Jingle all the breeze", "Cool air is your free Christmas present."),
    ],
    "nye": [
        ("Last breeze of the year", "End the year with fresh air."),
    ],
}

GENERAL = [
    ("Perfect window weather", "Goldilocks night: not too hot, not too cold."),
    ("Breeze o'clock", "Top floor heat meets its match tonight."),
    ("Window time, champ", "Open them up and let the heat escape."),
    ("Free AC unlocked", "Nature's air conditioning, no bill."),
    ("Heat escape hatch", "The top floor sauna can finally vent."),
    ("Windows: engage", "Fresh air beats a fan. Take the win."),
    ("Your apartment called", "It wants some fresh air. Answer it."),
    ("Open sesame", "The magic word for your windows tonight."),
    ("Air swap time", "Out with the stale, in with the fresh."),
    ("Night shift breeze", "The air is on duty. Let it in."),
]

CLOSE_LINES = [
    ("Close the windows", "The perfect air is over. Shut them to keep the good air in."),
    ("Window curfew", "Conditions changed. Time to close up."),
]


def holiday_for(d: date):
    for name, fn, before, after in HOLIDAYS:
        for year in (d.year - 1, d.year, d.year + 1):
            delta = (fn(year) - d).days
            if -after <= delta <= before:
                return name
    return None


def build_message(d: date, w: dict, spoken: bool = False, rng=random, close=False):
    """Return (title, body). Themed lines near a holiday, otherwise a random pick."""
    if close:
        title, joke = rng.choice(CLOSE_LINES)
        return title, joke
    pool = LINES.get(holiday_for(d)) or GENERAL
    title, joke = rng.choice(pool)
    unit = "degrees" if spoken else "C"
    stats = (f"{w['temp']:.0f} {unit} outside, {w['humidity']:.0f} percent humidity, "
             f"dew point {w['dew_point']:.0f}.")
    return title, f"{joke} {stats}"
