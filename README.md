# Ouvrelesfnetre

Pings an Amazon Echo when it's a good night to open the windows
(Sainte-Anne-des-Plaines, QC). Runs free on GitHub Actions every 15 min.

## Rule
Opens (max ONE alert per day), when all true:
- Weekdays: only at noon or 5pm (a 30 min slot each). Weekends: 8:00 to 20:00
- Temp 15 to 22 C, humidity 30 to 65 %
- Dew point under 15 C, no rain now or in the next ~2h, not dropping below 13 C, wind under 30 km/h
- Optimal (18 C or warmer): the alert is also spoken, if Voice Monkey is set up

Close reminder (only after that day's open alert, 7:00 to 23:00): rain now or likely
in the next ~2h (50 %+), or temp now / next ~2h below 13 C.

Numbers live in `CONFIG` at the top of `alert.py`.
MODE (repo variable): `auto` (default: silent ping, plus spoken when optimal or closing),
`notify_me` (silent only), `announce` (spoken only).

## Setup (phone friendly)
1. Repo > Settings > Secrets and variables > Actions > New secret:
   - Silent mode: `NOTIFYME_ACCESS_CODE` (Alexa app: enable the "Notify Me" skill, code arrives by email)
   - Spoken mode: `VOICEMONKEY_TOKEN` and `VOICEMONKEY_DEVICE` (voicemonkey.io: account, add a Speaker device, copy token and device ID)
2. Optional: Variables tab > `MODE` = `announce` to make it spoken. Default is `notify_me`.
3. Actions tab > window-alert > Run workflow > Run workflow. That sends one test alert right now (to your home only).
4. Green check = it worked. The Echo should glow yellow.

## Friends and family (other homes)
This repo checks every home with its own local weather; friends never touch GitHub.
1. Send them the setup page: `https://ghostaiproject.github.io/Ouvrelesfnetre/` (from `docs/index.html`;
   turn on once at Settings > Pages > Deploy from branch `main`, folder `/docs`).
   French first, English button. They type a name, pick their town, enable the "Notify Me" Alexa skill
   and paste its code. The page gives them a message to send back to you.
2. Their message has a secret name (like `HOME_MAMAN`) and a value. Repo > Settings > Secrets and
   variables > Actions > New repository secret: paste the name, paste the value.
3. Test it: Actions > window-alert > Run workflow, type their name (`maman`) in the home box. `all` tests every home.
- To remove a home, delete its secret. A broken code is skipped (see the run log), the other homes keep working.
- Each home gets the same rules and times as yours, in its own time zone. Codes never show in the logs.

## Google Home / Android homes (separate setup)
Google speakers can't say custom text from the cloud, so Google homes get every alert
(open and close) as a phone push through the free ntfy app, joke included. No Pi, nothing at home.
1. Send them: `https://ghostaiproject.github.io/Ouvrelesfnetre/google.html` (the Echo page links to it too).
   They type a name, pick their town, install ntfy, tap "Subscribe in ntfy", tap Test, then send you the message.
2. Their message has a secret name like `GHOME_MAMAN` (G for Google, so it never mixes with Echo `HOME_` secrets).
   Add it the same way: Settings > Secrets and variables > Actions > New repository secret.
3. Test: Actions > window-alert > Run workflow, home = `maman` (or `g-maman`).
- Same rules, times and jokes as Echo homes, in their own language and time zone.
- The ntfy topic in their code is the only key to their alerts: keep it private (it's masked in logs).

## Notes
- Cron can run a few minutes late. Normal.
- `state.json` is committed back about once a day, which also keeps the schedule from auto-disabling after 60 days idle.
- Silent mode: Echo ring glows yellow; ask "Alexa, what are my notifications?"

## Flair
`flair.py` picks a themed title and joke (Halloween, Christmas, Saint-Jean, Canada Day, etc.), otherwise one matching the weather: breezy (wind 20 km/h+), cool (under 18 C), mild (18 to 20 C) or warm (over 20 C). Every open title includes the current temp, e.g. "Goldilocks 19°". Edit the lists in `flair.py` to add your own.
- Silent mode: only the title shows on the Echo itself; the full joke and numbers are read out when you ask for notifications.
- Custom sound: Notify Me always uses Amazon's default sound. In spoken mode (`announce`), set repo variable `VOICEMONKEY_CHIME` to a sound from Voice Monkey's sound picker.
