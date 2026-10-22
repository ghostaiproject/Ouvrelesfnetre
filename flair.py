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
        ("New year, new pane", "Fresh year, fresh air. Crack those windows."),
        ("Resolution, open up", "Resolution number one: open the windows."),
    ],
    "valentine": [
        ("Windows, my valentine", "The fresh air has a crush on your apartment."),
        ("Pane-ing for you", "Love is in the air. Literally. Let it in."),
    ],
    "stpatrick": [
        ("Luck of the pane", "Lucky break. The air is perfect, no pot of gold needed."),
    ],
    "stjean": [
        ("Saint-Jean pane party", "Fete nationale vibes. Open up and let the fresh air in."),
        ("Pane-triotic breeze", "Vive le Quebec. Good time to open up and enjoy the air."),
    ],
    "canadaday": [
        ("Open up, eh", "Perfect day for it. Very polite weather."),
        ("Pane-adian eh-ir", "Happy Canada Day. Let the breeze in, sorry about the bugs."),
    ],
    "thanksgiving": [
        ("Thankful for panes", "Be thankful, the weather delivered. Windows open, leftovers cold."),
        ("Gobble up the breeze", "Fresh air is the best side dish."),
    ],
    "halloween": [
        ("Window of fright", "The wind is whispering. Open a window, if you dare."),
        ("Pane-ic! Open up", "Ghosts need ventilation too."),
        ("Boo-tiful breeze", "Perfect weather for it. Just don't invite anything in."),
    ],
    "christmas": [
        ("Frosted panes", "Santa checked the forecast. Windows open, you're good."),
        ("Sleigh the heat", "Cool air is your free Christmas present."),
        ("Santa's window of opportunity", "Open up before the elves get cold."),
    ],
    "nye": [
        ("Last pane of the year", "End the year with fresh air."),
    ],
}

GENERAL = [
    ("Pane relief", "Open up and feel the glass-ful of fresh air."),
    ("Window of opportunity", "Don't let this one slide. Windows slide, get it?"),
    ("Open and shut case", "The case for fresh air is wide open."),
    ("Wind-ow time", "A wind-ow of fresh air awaits."),
    ("Sill waiting", "Why sit around being sill-y? Open up."),
    ("Don't pane, open up", "It's easy. Just sash-ay on over to the window."),
    ("Frame the breeze", "A frame-worthy day to let the air in."),
    ("Ledge-endary air", "Today's breeze is ledge-endary. Open up."),
    ("Glass half open", "The optimist's way to cool the place."),
    ("Crack a window", "Crack it open. Crack a smile. Crack a pane joke."),
    ("Latch on to this", "Unlatch it and let the fresh air in."),
    ("Hinge-credible weather", "Hinge-credible air is waiting outside."),
    ("Breeze through it", "Opening the window is a breeze."),
    ("Pane-less cooling", "Pane-free, pain-free, and totally free."),
]

CLOSE_LINES = [
    ("Pane-ful goodbye", "The perfect air is over. Close up to keep it in."),
    ("Closing time", "Conditions changed. Time to close the windows."),
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
