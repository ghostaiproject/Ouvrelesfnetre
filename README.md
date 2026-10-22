# Ouvrelesfnetre

Pings an Amazon Echo when it's a good night to open the windows
(Sainte-Anne-des-Plaines, QC). Runs free on GitHub Actions every 15 min.

## Rule (all must be true)
- 22:00 to 06:00 Toronto time
- Temp 12 to 22 C, humidity 30 to 65 %
- Dew point under 15 C, no precipitation, wind under 30 km/h

Numbers live in `CONFIG` at the top of `alert.py`.
Alerts once on entry; re-arms after 2 bad checks in a row.

## Setup (phone friendly)
1. Repo > Settings > Secrets and variables > Actions > New secret:
   - Silent mode: `NOTIFYME_ACCESS_CODE` (Alexa app: enable the "Notify Me" skill, code arrives by email)
   - Spoken mode: `VOICEMONKEY_TOKEN` and `VOICEMONKEY_DEVICE` (voicemonkey.io: account, add a Speaker device, copy token and device ID)
2. Optional: Variables tab > `MODE` = `announce` to make it spoken. Default is `notify_me`.
3. Actions tab > window-alert > Run workflow with dry_run on, check the log.
4. Run again with dry_run off + force_test on to hear/see a real alert.

## Notes
- Cron can run a few minutes late. Normal.
- `state.json` is committed back about once a day, which also keeps the schedule from auto-disabling after 60 days idle.
- Silent mode: Echo ring glows yellow; ask "Alexa, what are my notifications?"

## Flair
`flair.py` picks a themed title and joke (Halloween, Christmas, Saint-Jean, Canada Day, etc.), otherwise one matched to how cool the night is. Edit the lists in `flair.py` to add your own.
- Silent mode: only the title shows on the Echo itself; the full joke and numbers are read out when you ask for notifications.
- Custom sound: Notify Me always uses Amazon's default sound. In spoken mode (`announce`), set repo variable `VOICEMONKEY_CHIME` to a sound from Voice Monkey's sound picker.
