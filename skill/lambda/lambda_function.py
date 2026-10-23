"""Alexa skill: "Alexa, should I open the windows?" -> checks the weather now
with the same rules as the alerts (alert.py) and answers in the request's
language (fr-* = French, else English). Alexa-hosted, handler
lambda_function.lambda_handler. alert.py and flair.py are copies made by
skill/build.py: run it after changing the rules or jokes, then redeploy."""
import sys
from datetime import datetime

try:
    import zoneinfo  # noqa: F401  (Python 3.9+)
except ImportError:  # older Alexa-hosted runtimes
    from backports import zoneinfo
    sys.modules["zoneinfo"] = zoneinfo

import alert  # noqa: E402
from flair import REASONS, norm_lang  # noqa: E402

CARD = {"en": "Open the windows?", "fr": "J'ouvre les fenêtres?"}


def _say(text, lang, end=True):
    return {"version": "1.0", "response": {
        "outputSpeech": {"type": "PlainText", "text": text},
        "card": {"type": "Simple", "title": CARD[lang], "content": text},
        "shouldEndSession": end}}


def reply(lang, now=None, weather=None):
    cfg = alert.CONFIG
    now = now or datetime.now(alert.ZoneInfo(cfg["tz"]))
    try:
        w = weather or alert.fetch_weather(cfg, tries=2, timeout=3)  # Alexa waits 8 s max
    except Exception:  # noqa: BLE001
        return REASONS[lang]["error"]
    return alert.answer(w, now, lang, cfg)


def lambda_handler(event, context=None):
    req = event.get("request", {})
    lang = norm_lang((req.get("locale") or "en")[:2])
    kind, intent = req.get("type"), req.get("intent", {}).get("name", "")
    if kind == "SessionEndedRequest":
        return {"version": "1.0", "response": {}}
    if intent in ("AMAZON.StopIntent", "AMAZON.CancelIntent", "AMAZON.NavigateHomeIntent"):
        return _say(REASONS[lang]["bye"], lang)
    if intent == "AMAZON.HelpIntent":
        return _say(REASONS[lang]["help"], lang, end=False)
    # LaunchRequest, ShouldOpenIntent, FallbackIntent: just answer.
    return _say(reply(lang), lang)
