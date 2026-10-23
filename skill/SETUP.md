# "Alexa, should I open the windows?"

You ask, the skill checks the weather **right now** with the same rules as the
alerts (temp 15-22, humidity 30-65, dew point < 15, no rain now or in 2 h, not
dropping < 13, wind < 30) and answers:

- **Yes!** + a joke that fits the weather + temp, humidity, dew point
- **Not right now:** + the top 2 real reasons (raining, too cool, too windy…)

Language follows the Echo: French Echo = French answer.
Rules and jokes come from `alert.py` / `flair.py` (copied by `build.py`).

One-time setup, about 15 minutes, free. Use the **same Amazon account** as the Echo.

---

## A. Make the skill (computer browser)

1. Open https://developer.amazon.com/alexa/console/ask and sign in.
2. Tap **Create Skill**.

```
┌────────────────────────┐
│ Alexa Skills    [Create│
│                  Skill]│ ← tap
└────────────────────────┘
```

3. Name: `Window Check` · Primary locale: **English (CA)** → Next.
4. Type: **Other** → **Custom** → hosting: **Alexa-hosted (Python)** → Next.
5. Template: **Start from Scratch** → **Create Skill**. Wait ~1 min.

## B. Paste the words it understands

6. Left menu **Interaction Model** → **JSON Editor**.
7. Select all, paste `skill-package/interactionModels/custom/en-CA.json`
   → **Save** → **Build skill** (top).

```
┌────────────────────────┐
│ ▸ Interaction Model    │
│   ▸ JSON Editor   ← tap│
│ ┌────────────────────┐ │
│ │ { paste here }     │ │
│ └────────────────────┘ │
│ [Save]   [Build skill] │
└────────────────────────┘
```

8. French too: language menu top left (**English (CA) ▾**) →
   **Language settings** → **Add new language** → **French (CA)** and
   **English (US)** → Save. For each one, repeat step 7 with `fr-CA.json` /
   `en-US.json`.

## C. Paste the code

9. Top tab **Code**. Open `lambda_function.py`, select all, paste
   `skill/lambda/lambda_function.py`.
10. Same for `requirements.txt`.
11. **New File** (top left icon) → `lambda/alert.py` → paste. Again for
    `lambda/flair.py`.
12. **Save** → **Deploy**. Wait for "Deployed".

```
┌────────────────────────┐
│ Code    [Save][Deploy] │ ← both
│ 📁 lambda              │
│   lambda_function.py   │
│   alert.py             │
│   flair.py             │
│   requirements.txt     │
└────────────────────────┘
```

## D. Test

13. Top tab **Test** → switch **Off ▾** to **Development**.
14. Type `open window check`. It answers yes or not now.
    French: change language top left, type `ouvre conseil fenêtres`.

You can already say: **"Alexa, open window check"** /
**"Alexa, ouvre conseil fenêtres"**.

## E. Make "should I open the windows?" work (phone, Alexa app)

15. ≡ menu top left → **Routines** tile → **⊕** top right.
16. **WHEN** → **Add an event** → **Voice** → type
    `should I open the windows` → Next.
17. **ALEXA WILL** → **Add an action** → **Customized** → type
    `open window check` → Next.
18. **From**: your Echo → **Save**.

```
┌────────────────────────┐
│ ‹   New Routine        │
│ WHEN                   │
│  should I open the     │
│  windows               │
│ ALEXA WILL             │
│  Customized:           │
│  open window check     │
│ ┌────────────────────┐ │
│ │       Save         │ │ ← tap
│ └────────────────────┘ │
└────────────────────────┘
```

French Echo: same routine with
`est-ce que j'ouvre les fenêtres` → Customized `ouvre conseil fenêtres`.

## Changed rules or jokes later?

Run `python skill/build.py`, then paste the new `alert.py` / `flair.py` in the
Code tab and **Deploy** again. The skill doesn't update by itself.

## Limits

- The skill stays in Development mode: it works on this Amazon account's
  Echos only. Friends would need beta-test invites (Distribution → Beta Test).
- It uses your home (CONFIG lat/lon in `alert.py`).
