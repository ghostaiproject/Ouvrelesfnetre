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
3. Actions tab > window-alert > Run workflow > Run workflow. That sends one test alert right now (no options to set).
4. Green check = it worked. The Echo should glow yellow.

## Notes
- Cron can run a few minutes late. Normal.
- `state.json` is committed back about once a day, which also keeps the schedule from auto-disabling after 60 days idle.
- Silent mode: Echo ring glows yellow; ask "Alexa, what are my notifications?"

## Flair
`flair.py` picks a themed title and joke (Halloween, Christmas, Saint-Jean, Canada Day, etc.), otherwise a random one from a general pool. Edit the lists in `flair.py` to add your own.
- Silent mode: only the title shows on the Echo itself; the full joke and numbers are read out when you ask for notifications.
- Custom sound: Notify Me always uses Amazon's default sound. In spoken mode (`announce`), set repo variable `VOICEMONKEY_CHIME` to a sound from Voice Monkey's sound picker.
