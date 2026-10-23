# HANDOFF

## LATEST (2026-10-22, main @ b029aeb)
Friends-and-family release is live.
- Setup page: https://ghostaiproject.github.io/Ouvrelesfnetre/ (GitHub Pages, main /docs, `docs/index.html`).
  FR first + EN toggle. Steps: name, town search (Open-Meteo geocoding, manual lat/lon fallback),
  Notify Me 7-step drawn tap-by-tap guide, optional Voice Monkey 12-step guide (from voicemonkey.io v3 docs),
  Paste buttons, then "Créer mon code" makes a message: secret name `HOME_<NAME>` + JSON value.
  Voice-Monkey-only homes get mode `announce` (else `auto`). Lat/lon rounded to 2 decimals.
- Multi-home (PR #3, includes #1 weather titles and #2 Echo Show screen text):
  `load_homes()` = "main" (old secrets) + one home per `HOME_*` secret, via `ALL_SECRETS: toJSON(secrets)`.
  Per-home weather/tz/state; one broken home never stops others; Save state step `if: always()`.
  Codes `::add-mask::`ed; errors print only type + HTTP status (URLs carry codes/locations; repo is PUBLIC).
  Run workflow has a `home` input (default main, a name, or all).
- Adding a home: friend sends message -> repo Settings > Secrets > Actions > New secret (name + value)
  -> Actions > Run workflow, home = their name.
- Tests: 22 pass locally (Python 3.12 at %LOCALAPPDATA%\Programs\Python\Python312, needs `pip install tzdata` on Windows).

## Open / NOT verified
- First scheduled multi-home run not seen yet (state.json still old flat format; it migrates to
  `{"heartbeat", "homes": {...}}` on the next run).
- Guide screens are drawings: French Alexa menu names (esp. routine: "Lorsque ceci se produit",
  "Maison intelligente", "À partir de") not checked on a real phone.
- No friend home added yet; no real Notify Me test for a HOME_ secret.
- Alert texts are English only (flair.py).

## Project
Window-open alert for Sainte-Anne-des-Plaines QC (lat 45.76, lon -73.82). GitHub Actions cron every 15 min
(`.github/workflows/window-alert.yml`): pytest, then `python alert.py`, then commit state.json.
Files: alert.py (rules, homes, sending), flair.py (titles/jokes, weather lines, holidays), test_alert.py, docs/index.html.
Echo: Voice Monkey v3 Speaker "Echo", device echo-mpzmw, Echo Show (Amazon.ca); routine made in phone app.
Secrets: NOTIFYME_ACCESS_CODE, VOICEMONKEY_TOKEN, VOICEMONKEY_DEVICE, HOME_*. Vars: MODE, VOICEMONKEY_CHIME.

## How it works
- Open alert max 1/day: weekdays noon/5pm slots (30 min), weekends 8-20; temp 15-22, hum 30-65, dew < 15,
  no rain now/next 2h, not dropping < 13, wind < 30. Optimal (>= 18) = also spoken in `auto`.
- Close reminder after that day's open alert, 7-23: rain likely or temp < 13.
- Modes: auto (silent Notify Me + spoken when optimal/closing), notify_me, announce.
- Titles: weather kind (breezy/cool/mild/warm) + temp ("19°", "19 degrees" spoken); holidays append temp.
- Voice Monkey announce sends speech + text_display + display_seconds (CONFIG, 60).

## History
- PR #1 weather-aware titles with temp. PR #2 Echo Show screen text. PR #3 multi-home + setup page.
- 7c31f21 Notify Me picture guide. b029aeb Voice Monkey picture guide.
- Windows clone needs `git -c core.longpaths=true`. gh CLI not logged in; git credential manager works.
