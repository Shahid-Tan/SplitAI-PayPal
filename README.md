# 💰 SplitAI

> **AI-powered conversational bill splitting with instant PayPal settlement.**

![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
![Python](https://img.shields.io/badge/Python-3-blue.svg)
![Streamlit](https://img.shields.io/badge/UI-Streamlit-FF4B4B?logo=streamlit&logoColor=white)
![AI](https://img.shields.io/badge/AI-Google%20Gemini-4E8CF5)
![Payments](https://img.shields.io/badge/Payments-PayPal-003087?logo=paypal&logoColor=ffc439)

[![Built for the PayPal AI Hackathon](https://img.shields.io/badge/Built%20for%20the-PayPal%20AI%20Hackathon-ffc439?logo=paypal&logoColor=003087)](https://devpost.com)

---

**SplitAI** turns a messy group bill — a restaurant receipt, a flat-rent note, a road-trip fuel tally — written in plain English into an exact, itemized per-person split using **Google Gemini**, then hands every debtor a one-tap **Pay with PayPal** button built on a **PayPal.Me** settlement link.

## 🎬 Demo & Links

| Asset | Link |
|---|---|
| 🌐 Live demo (hosted app) | **[TO ADD — hosted URL]** |
| ▶️ Video walkthrough (< 3 min) | **[TO ADD — YouTube URL]** |
| 🏆 Devpost project page | **[TO ADD — Devpost URL]** |

## 🧭 Why it matters

Splitting a shared expense is all friction: someone does mental math, forgets the tax, misreads the receipt, and chases three people on chat. SplitAI removes every step — you paste the bill the way it was written (or read out at the table), the AI itemizes and allocates it fairly — including taxes, tips, and special cases — and the money settles instantly through PayPal instead of an IOU spreadsheet.

## ✨ Features

Everything below is verified against the code in `app.py` today.

- 💬 **Conversational bill parsing** — type or paste ANY bill, receipt, or "who paid what" note in natural language.
- 🧮 **Automatic itemized allocation** — per-person amounts with a brief breakdown and a total-and-taxes summary, per the AI prompt's clean output format.
- 🎛️ **Custom special instructions** — a second input box for things like *"Convert results to INR (₹)"*, *"Split 60–40 between two people"*, *"Add 18% GST / 10% tip"*.
- ⚡ **One-tap demo presets** — 🍕 Restaurant ($70 dinner + shared $10 tip), 🏠 Flat Rent (INR: ₹24,000 rent + WiFi + electricity, with a ₹2,000 surcharge for the bedroom with AC), 🚗 Road Trip ($90 fuel + $30 snacks, four friends, one payer).
- 💳 **Instant PayPal settlement** — enter any PayPal.Me handle in the sidebar (spaces and `@` are stripped automatically) and the app generates a `paypal.com/paypalme/<handle>` settlement link with a bold PayPal-styled **"👉 Pay with PayPal"** button.
- 🌍 **Multi-currency by request** — USD ($) and Indian Rupees (₹) demos built in; the AI honors currency instructions in the prompt.
- 💙 **PayPal-branded UI** — PayPal blue-gradient header card and gold payoff button for an on-brand experience.
- 🔐 **Key-light by design** — the only credential needed for the app to function is a free Gemini API key (optional — see the fallback below); the app never stores or transmits it anywhere but the Gemini API.

### ⚠️ Honest status

- 🔜 **PayPal Sandbox (REST) integration** — documented below and planned for the sprint, but **not yet wired into `app.py`**: the shipping settlement path today is PayPal.Me links.
- 🔜 **`secrets.toml` support** — the Gemini key is currently entered in the sidebar per session; `.streamlit/secrets.toml` is described below as the recommended convention (already covered by `.gitignore`).
- ✅ **Deterministic fallback disclosed** — if no API key is set or all model quotas are exhausted, the app prints a **canned demo breakdown** of the built-in $54 sample bill (Rahul $24 / Sneha $20 / you $16, total $60) under an "Instant Smart Parser Active" badge, so the full UI journey stays demonstrable without credentials. It shows the exact sample bill — it does not parse your custom bill.

## 🏗️ How it works

```
┌─────────────────────────────────────────────────────────────┐
│                       Streamlit UI (app.py)                 │
│                                                             │
│  Bill text ──────┐   ┌────────────────────────────────────┐  │
│  Instructions ───┼──►│ Gemini API (free-tier rotation:    │  │
│  Presets ────────┘   │ try Flash variants until one       │  │
│                      │ answers; skip quota errors)        │  │
│                      └──────────────┬─────────────────────┘  │
│                                     │  reply (or NO KEY /    │
│                                     │  all quotas hit        │
│                                     ▼                        │
│                      ┌────────────────────────────────────┐  │
│                      │ deterministic demo fallback        │  │
│                      │ (canned $54 sample split)          │  │
│                      └──────────────┬─────────────────────┘  │
│                                     ▼                        │
│                      Result card + PayPal.Me deep link      │
│                      ──►  👉 Pay with PayPal                │
└─────────────────────────────────────────────────────────────┘
```

One request, one page: parse → split → settle. No accounts, no database, no server state beyond Streamlit session state.

## 💳 How PayPal is used

| # | Touchpoint | What happens | Status |
|---|---|---|---|
| 1 | **PayPal.Me handle** (sidebar) | User sets the destination handle; the app normalizes it — strips spaces and `@` — before building any link. | ✅ Live |
| 2 | **Settlement deep link** | After each split, the app builds `https://www.paypal.com/paypalme/<handle>` and renders a gold **"👉 Pay with PayPal"** button opening PayPal in a new tab. | ✅ Live |
| 3 | **On-brand checkout UX** | PayPal-blue header, PayPal-gold payoff button, PayPal-badged UI styling. | ✅ Live |
| 4 | **PayPal Sandbox** | REST order create/capture flow against a developer.paypal.com sandbox app (credentials via `secrets.toml` / env vars). | 🔜 In progress |
| 5 | **Security posture** | The app never requests, stores, or transmits PayPal credentials, and never moves money itself — a PayPal click hands the session to PayPal's own platform. | ✅ Live |

> **Scope note:** money settlement is **sandbox / PayPal.Me only** in this build; no production PayPal rails are touched.

## 🤖 How AI is used

| # | Capability | How it works | Model |
|---|---|---|---|
| 1 | **Natural-language bill understanding** | Messy bill text and receipts are sent to Gemini with the correct role framing so any phrasing works — not just structured fields. | Gemini Flash |
| 2 | **Fair itemized math** | The prompt asks for the exact itemized split per person with currency symbols, brief per-person breakdown logic, and a total + taxes summary. | Gemini Flash |
| 3 | **Instruction following** | The user's custom questions are spliced into the same prompt: currency conversion (₹), percentage splits (60–40), taxes (18% GST), tips, discounts. | Gemini Flash |
| 4 | **Free-tier resilience** | Before answering, the app tries a rotation of free Gemini Flash model variants; if one hits a quota error, it silently falls through to the next. | Rotation |
| 5 | **Deterministic fallback** | With no key or after all models are exhausted, a canned, fully-accurate sample split keeps the demo experience complete (disclosed above). | None (deterministic) |

## 🧱 Tech stack

| Layer | Technology | Where you'll see it |
|---|---|---|
| Frontend & UI | **Streamlit** (Python) | `app.py` — page config, custom CSS, presets |
| AI engine | **Google Gemini** via the `google-generativeai` SDK | Split calculation, model-rotation fallback |
| Payments | **PayPal** — PayPal.Me settlement links (Sandbox REST in progress) | Settlement button after every split |
| Language | **Python 3** | Entire app — a single ~200-line file |
| Secrets | Sidebar input now · `.streamlit/secrets.toml` / env vars (recommended, gitignored) | API keys for Gemini / sandbox |
| Hosting | Free Streamlit hosting — **[TO ADD — hosted URL]** | Live demo for judges |

## 🚀 Quick start (5 minutes)

```bash
# 1. Clone
git clone https://github.com/Shahid-Tan/SplitAI-PayPal.git
cd SplitAI-PayPal

# 2. (Optional but recommended) virtual environment
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS / Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run
streamlit run app.py
```

Then:

1. **Get a free Gemini API key** at [aistudio.google.com](https://aistudio.google.com) (Google AI Studio — free tier, no credit card) and paste it into the sidebar's *Gemini API Key* box (password-masked).
2. **Enter your PayPal.Me handle** in the sidebar — the default handle ships as the author's (`syedshahidafridi`); replace it with your own when testing.
3. Click **🚀 Calculate Split with AI** — or try a preset button first.

**No API key? The app still runs** — it will show the disclosed deterministic demo split so you can see the complete flow end-to-end.

## 🔐 Optional: PayPal developer / sandbox credentials

The current build needs **no** PayPal credentials (PayPal.Me links are static and public). If you want the in-progress Sandbox REST experience when it lands, prepare credentials now — they're free:

1. Create (or sign in to) a developer account at [developer.paypal.com](https://developer.paypal.com).
2. Under *Apps & Credentials*, create a **Sandbox** app and copy the **Client ID** and **Client Secret**.
3. Store them **out of Git** (both places are already covered by `.gitignore`):

   **Option A — Streamlit secrets:** create `.streamlit/secrets.toml` next to `app.py`:
   ```toml
   PAYPAL_CLIENT_ID = "AZ…"
   PAYPAL_CLIENT_SECRET = "EF…"
   GEMINI_API_KEY = "AIza…"        # optional alternative to the sidebar field
   ```

   **Option B — environment variables:**
   ```bash
   PAYPAL_CLIENT_ID=AZ… PAYPAL_CLIENT_SECRET=EF… streamlit run app.py
   ```

> The Gemini key today is read from the sidebar; `secrets.toml` wiring for it (and for sandbox PayPal) is part of the current sprint — neither file is required to run the app as shipped.

## 📁 Project structure

```
SplitAI-PayPal/
├─ app.py                        # The whole app: UI, AI calls, PayPal settlement link
├─ requirements.txt              # streamlit, google-generativeai
├─ README.md                     # You are here
├─ LICENSE                       # MIT
├─ .gitignore                    # Keeps secrets & junk out of the repo
└─ docs/
   ├─ SUBMISSION_CHECKLIST.md    # Every Devpost requirement as checkboxes + key dates
   └─ DEVPOST_DESCRIPTION.md     # Devpost copy stub (final text in progress)
```

## ❓ FAQ

**Does the app move real money?**
No. It builds a PayPal.Me link that opens PayPal's own site; the payment happens entirely on PayPal. That's sandbox/links scope, disclosed above.

**Do I need API keys to run it?**
A Gemini key is optional — leave it blank and the disclosed deterministic demo split appears. PayPal keys are never needed in the current build.

**Is my Gemini key safe?**
It's entered in a password-masked sidebar field, sent only to the Gemini API, and never logged, persisted, or committed — and `.streamlit/secrets.toml` / `.env` are gitignored as a safety net.

**Which Gemini models does it use?**
A rotation of free Gemini Flash variants (see `models_to_try` in `app.py`); the exact list may be tuned during the sprint. Quota errors trigger automatic failover to the next model.

**What happens when the AI is unavailable?**
You get the deterministic fallback: an exact, correct sample split for the built-in demo bill — so judges can always see the full experience. It's honestly labeled and it isn't a parser for your custom bill.

**What currencies work?**
USD and INR are the demoed cases; since currency handling is prompt-driven, Gemini follows instructions like "convert to INR (₹)" as requested.

**Why PayPal.Me links instead of a full checkout?**
Speed and zero-credential simplicity for the hackathon build; the Sandbox REST flow is the next step (status section above).

## 📦 Submission materials

- 📋 **Submission checklist:** [`docs/SUBMISSION_CHECKLIST.md`](docs/SUBMISSION_CHECKLIST.md) — every Devpost requirement with key dates.
- ✍️ **Devpost description draft:** [`docs/DEVPOST_DESCRIPTION.md`](docs/DEVPOST_DESCRIPTION.md) — final copy in progress.
- 📜 **License:** MIT — see [`LICENSE`](LICENSE).

## 🏆 Built for the PayPal AI Hackathon

![Built for the PayPal AI Hackathon](https://img.shields.io/badge/Built%20for%20the-PayPal%20AI%20Hackathon-ffc439?logo=paypal&logoColor=003087)

SplitAI was built for the **"Build What's Next with PayPal and AI"** hackathon on Devpost — combining Google Gemini's natural-language intelligence with PayPal's payment rails to make group money awkwardness a thing of the past.

## 👤 Author

Built by **Shahid-Tan** · [github.com/Shahid-Tan](https://github.com/Shahid-Tan)

## 📄 License

Released under the [MIT License](LICENSE) — free to use, remix, and build upon with attribution.
