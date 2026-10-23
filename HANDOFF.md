# HANDOFF

## LATEST (2026-10-22, main @ b029aeb)
Multi-home release is live.
- Setup page: https://ghostaiproject.github.io/Ouvrelesfnetre/ (GitHub Pages, main /docs). Root `docs/index.html` = project explanation + the two options grouped (2026-10-23) -> `echo.html` (Echo setup, was index.html) or `phone.html`.
  FR first + EN toggle. Steps: name, town search (Open-Meteo geocoding, manual lat/lon fallback),
  Notify Me 7-step drawn tap-by-tap guide, optional Voice Monkey 12-step guide (from voicemonkey.io v3 docs),
  Paste buttons, then "Créer mon code" makes a message: secret name `HOME_<NAME>` + JSON value.
  Voice-Monkey-only homes get mode `announce` (else `auto`). Lat/lon rounded to 2 decimals.
- Multi-home (PR #3, includes #1 weather titles and #2 Echo Show screen text):
  `load_homes()` = "main" (old secrets) + one home per `HOME_*` secret, via `ALL_SECRETS: toJSON(secrets)`.
  Per-home weather/tz/state; one broken home never stops others; Save state step `if: always()`.
  Codes `::add-mask::`ed; errors print only type + HTTP status (URLs carry codes/locations; repo is PUBLIC).
  Run workflow has a `home` input (default main, a name, or all).
- Adding a home: the person sends their message -> repo Settings > Secrets > Actions > New secret (name + value)
  -> Actions > Run workflow, home = their name.
- Tests: 22 pass locally (Python 3.12 at %LOCALAPPDATA%\Programs\Python\Python312, needs `pip install tzdata` on Windows).

## UPDATE (2026-10-23, later): renamed "Google" -> "phone" (owner: it's the no-Echo crutch, not a Google thing)
- Page `docs/phone.html` (google.html now just redirects there). Secrets `PHONE_<NAME>`, id `p-<name>`; `GHOME_` still read.
- Chooser card: "Pas d'Echo? Ton téléphone". Echo page link: "Pas d'Echo? Ton téléphone peut faire la job".

## UPDATE (2026-10-23): Google Home / Android homes = phone push via ntfy
- Why not the Nest speaker: Assistant SDK "broadcast" only works from the same home network (not GitHub cloud);
  Google has no Voice Monkey equivalent; routines can't read a URL or play an MP3 link. Owner chose simple, no Pi.
- New page `docs/google.html` (FR first, EN toggle), linked from the chooser and echo.html. Name, town, 5-step drawn ntfy guide,
  "Subscribe in ntfy" = `ntfy://ntfy.sh/<topic>` deep link (Android), iPhone: copy topic + App Store link,
  Test button POSTs to ntfy.sh. Topic `fenetres-<16 random>` kept in localStorage so reloads keep it.
- Secret `GHOME_<NAME>` = `{"n","p","l","z"?,"g": topic}`. `alert.py _google_home()`: id `g-<name>`, mode `push`,
  every alert -> `_ntfy()` (JSON publish to https://ntfy.sh/, tags by kind, priority 4 for close reminders).
  TEST_HOME `chalet` also finds `p-chalet`. Topic masked in logs.
- Owner tested: deep link subscribed directly (no dialog), page Test push arrived on S23. Nest stays silent (expected).
- Read aloud: optional MacroDroid section on google.html (9 drawn steps: Notification Received from ntfy ->
  Speak Text "[notification_title]. [notification]"). Push homes now get the spoken wording ("19 degrés") and
  no emoji tags (TTS would read them). MacroDroid menu drawings are from memory (English labels), not checked.
- NOT verified: ntfy.sh is blocked from the cloud workspace, so no real push sent yet; tests 31/31 with the stand-in runner.
  Page drawings of the ntfy app are from memory, not real screenshots.

## UPDATE (2026-10-22 late): "Alexa, should I open the windows?" skill
- `skill/`: Alexa-hosted custom skill (Python). Handler `skill/lambda/lambda_function.py` answers with `alert.answer()`:
  same rules as alerts minus the time slots; Yes + weather joke, or "Not right now:" + top 2 reasons. Locale fr-* = French.
- Invocation: "window check" (en-CA/en-US), "conseil fenêtres" (fr-CA). Phrase "should I open the windows" = Alexa routine
  Voice trigger -> Customized action "open window check". Steps: `skill/SETUP.md`.
- `skill/lambda/alert.py` + `flair.py` are copies: run `python skill/build.py` and redeploy after rule/joke changes.
- NOT done yet: the skill is not created in the developer console; routine not made. Not tested on a real Echo.

## UPDATE (2026-10-22 late): FR/EN alerts, 25 jokes per pool, compact code, sun check
- Each home has a language: `lang` (en|fr). Setup page saves the page's FR/EN choice; your own home uses repo var `ALERT_LANG` (default en).
  Titles, jokes, weather line and spoken text all follow it (flair.py `build_message(..., lang=)`).
- flair.py stores lines as compact "Title | Joke" text blocks. 25 lines per weather pool (breezy/cool/mild/warm) and close pool (rain/cold), per language; holidays 3-5 each.
- Jokes match the weather right now: pool by wind/temp, and lines starting with `*` (sun jokes) only when Open-Meteo says is_day and cloud_cover < 40 (`sunny_cloud_max`).
- Home code is compact: `{"n","p":[lat,lon] 3 decimals,"l","z" if not Toronto,"c","t","d"}`; no `c` = announce. Old long-key codes still load.
- PyPI is blocked in the cloud workspace; tests were run with a stand-in runner (27/27). CI runs real pytest.
- French speech sounds right only if the Echo itself is set to French; Voice Monkey has no per-message voice option documented.

## UPDATE (2026-10-22 night): guides use the app menus only, no Alexa+ chat
Owner's call: do NOT use Alexa+ chat (typing "Enable Notify Me" did not work; chat-navigation version a811bf7 replaced).
Skills: home ≡ menu top left -> More -> Skills & Games tile -> "Search Alexa Skills" bar -> result -> Enable to use.
Notify Me guide = 7 steps (step 6: say "Alexa, open Notify Me" to the Echo, then email). Voice Monkey = 14 steps
(routine = steps 7-12: ≡ -> Routines tile -> ⊕ -> WHEN Add an event -> ALEXA WILL Add an action -> Save).

## Open / NOT verified
- First scheduled multi-home run not seen yet (state.json still old flat format; it migrates to
  `{"heartbeat", "homes": {...}}` on the next run).
- Guide screens redrawn 2026-10-22 for the new dark Alexa+ app from real (English) phone screenshots:
  More = tile grid, Skills & Games = "Discover Alexa" with search bar on top, Routines ⊕ top right,
  New Routine = WHEN "Add an event" / ALEXA WILL "Add an action" + big Save at bottom. Home = ≡ menu top left -> More.
- Guide screens are drawings: French Alexa menu names (esp. routine: "Lorsque ceci se produit",
  "Maison intelligente", "À partir de") not checked on a real phone.
- No other home added yet; no real Notify Me test for a HOME_ secret.
- Alert texts are English only (flair.py).

## Project
Window-open alert for Sainte-Anne-des-Plaines QC (lat 45.76, lon -73.82). GitHub Actions cron every 15 min
(`.github/workflows/window-alert.yml`): pytest, then `python alert.py`, then commit state.json.
Files: alert.py (rules, homes, sending), flair.py (titles/jokes, weather lines, holidays), test_alert.py, docs/ (index chooser, echo.html, phone.html).
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
