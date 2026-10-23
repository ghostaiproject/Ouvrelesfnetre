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

# Picked by the weather outside. {deg} becomes the current temp ("19°" or "19 degrees").
WEATHER_LINES = {
    "breezy": [  # wind 20 km/h or more
        ("Breezy {deg}, wind-ow time", "A wind-ow of fresh air awaits. Hold on to your papers."),
        ("{deg} and gust-o", "Good gusts out there. Breeze through it and open up."),
        ("Hinge-credible {deg} breeze", "Hinge-credible air is blowing outside."),
    ],
    "cool": [  # under 18
        ("Crisp {deg}, crack a pane", "Crack it open. Crack a smile. Crack a pane joke."),
        ("Cool {deg}, sill waiting", "Why sit around being sill-y? Let the cool air in."),
        ("{deg} of chill-ax air", "Not cold, just chill. Unlatch it and let it in."),
    ],
    "mild": [  # 18 to 20
        ("{deg} of pane relief", "Open up and feel the glass-ful of fresh air."),
        ("Window of opportunity at {deg}", "Don't let this one slide. Windows slide, get it?"),
        ("Goldilocks {deg}", "Not too hot, not too cold. Frame-worthy air."),
        ("{deg}, open and shut case", "The case for fresh air is wide open."),
    ],
    "warm": [  # over 20
        ("Warm {deg}, glass half open", "The optimist's way to cool the place."),
        ("Ledge-endary {deg}", "Today's warm breeze is ledge-endary. Open up."),
        ("{deg}, don't pane", "It's easy. Just sash-ay on over to the window."),
    ],
}

CLOSE_LINES = {
    "rain": [
        ("Pane in the forecast", "Rain is on the way. Close the windows!"),
        ("Rain check on that breeze", "Rain incoming. Shut the windows."),
        ("Don't rain on your own parade", "Close the windows before it pours."),
    ],
    "cold": [
        ("Pane-ful chill", "It's getting cold out. Close the windows."),
        ("Chill out, close up", "The temperature is dropping. Time to shut the windows."),
        ("Cold front, hold the pane", "Close the windows to keep the warmth in."),
    ],
}


def holiday_for(d: date):
    for name, fn, before, after in HOLIDAYS:
        for year in (d.year - 1, d.year, d.year + 1):
            delta = (fn(year) - d).days
            if -after <= delta <= before:
                return name
    return None


def weather_kind(w: dict) -> str:
    """breezy, cool, mild or warm: picks which WEATHER_LINES pool to use."""
    if w["wind"] >= 20:
        return "breezy"
    if w["temp"] < 18:
        return "cool"
    if w["temp"] <= 20:
        return "mild"
    return "warm"


def build_message(d: date, w: dict, spoken: bool = False, rng=random, close=None):
    """Return (title, body). Themed lines near a holiday, otherwise one matching
    the weather. Open titles always carry the current temp."""
    if close:
        title, joke = rng.choice(CLOSE_LINES.get(close) or CLOSE_LINES["cold"])
        return title, joke
    deg = f"{w['temp']:.0f} degrees" if spoken else f"{w['temp']:.0f}°"
    holiday = LINES.get(holiday_for(d))
    if holiday:
        title, joke = rng.choice(holiday)
        title = f"{title}, {deg}"
    else:
        title, joke = rng.choice(WEATHER_LINES[weather_kind(w)])
        title = title.format(deg=deg)
    unit = "degrees" if spoken else "C"
    stats = (f"{w['temp']:.0f} {unit} outside, {w['humidity']:.0f} percent humidity, "
             f"dew point {w['dew_point']:.0f}.")
    return title, f"{joke} {stats}"
