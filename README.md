# 💰 SplitAI

> **Paste any bill in plain words. Get exact shares. Settle with PayPal.**

![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
![Python](https://img.shields.io/badge/Python-3.12-blue.svg)
![Streamlit](https://img.shields.io/badge/UI-Streamlit-FF4B4B?logo=streamlit&logoColor=white)
![AI](https://img.shields.io/badge/AI-Google%20Gemini-4E8CF5)
![Payments](https://img.shields.io/badge/Payments-PayPal%20Orders%20v2-003087?logo=paypal&logoColor=ffc439)

[![Built for the PayPal AI Hackathon](https://img.shields.io/badge/Built%20for%20the-PayPal%20AI%20Hackathon-ffc439?logo=paypal&logoColor=003087)](https://devpost.com)

---

**SplitAI** turns a messy group bill — a restaurant receipt, a flat-rent note, a road-trip fuel tally — written in plain English into an exact, itemized per-person split using **Google Gemini**, and every debtor gets a one-tap **Pay** button on a real **PayPal Orders v2 (sandbox)** approval flow. No sandbox credentials? The flow degrades gracefully to prefilled **PayPal.me** links. And when no Gemini key is present at all, an honest **deterministic parser** does the math — it never invents people or amounts.

## 🎬 Demo & Links

| Asset | Link |
|---|---|
| 🌐 Live demo (hosted app) | **https://splitai-paypal.streamlit.app/** |
| ▶️ Video walkthrough (< 3 min) | **[TO ADD — YouTube URL]** |
| 🏆 Devpost project page | **[TO ADD — Devpost URL]** |

## 🧭 Why it matters

Splitting a shared expense is all friction: someone does mental math, forgets the tax, misreads the receipt, and chases three people on chat. SplitAI removes every step — paste the bill the way it was written, get exact shares with the arithmetic shown, and settle through PayPal instead of an IOU spreadsheet.

## ✨ Features

- 💬 **Conversational bill parsing** — paste any receipt or "who paid what" note in natural language.
- 🧠 **Gemini engine** — strict-JSON structured output, 3-model rotation for quota resilience (`gemini-2.5-flash` → `2.0-flash` → `1.5-flash`), raw-text fallback that is *shown*, never silently re-guessed. The sidebar reports which models actually responded — one quick validation probe per key.
- 🧮 **Honest deterministic parser (no key needed)** — a real regex/heuristics parser: totals and currencies (USD/INR/EUR/GBP/CAD/AUD/SGD), per-item detection, equal-splits with largest-remainder rounding, percentage weights and 60/40-style instructions, private-room surcharges, service taxes, payer-coverage lines like *"Shahid paid upfront"*, then a greedy min-cash-flow planner for the minimum set of transfers. Clearly badged **"Deterministic parser mode (no AI key)"** — it never fabricates names or amounts and says so plainly when a bill is unparseable. Covered by 12 unit tests in `tests/test_parsing.py`.
- 🎛️ **Custom instructions** — *"split 60/40"*, *"add 10% tip"*, *"show who owes whom"* feed both engines.
- ⚡ **One-tap presets** — pizza dinner with shared `$6` service tax, flat rent in **₹** with a ₹2,000 master-bedroom surcharge, road trip where one friend fronts everything, weighted 60/40 housemate split.
- 💳 **Real PayPal storefront (sandbox)** — PayPal **Orders v2**: client-credentials OAuth (cached ~50 min), `POST /v2/checkout/orders` per transfer → approve link → **capture on return** via `?token=` detection, with order creation session-cached and idempotent capture. Falls back to prefilled **PayPal.me deep links** when credentials are absent.
- 📊 **Judge-friendly results** — engine badge + notice trail, three headline metrics, split table with per-person breakdown math, horizontal share chart, per-person cards with copyable links, "who pays whom" settlement plan, CSV export, and a sidebar history of past splits you can reload.
- 💙 **PayPal-branded UI** — locked theme in `.streamlit/config.toml`: PayPal navy sidebar (`#003087`), PayPal blue (`#0070ba`) accents, gold (`#ffc439`) pill pay buttons. Theme-first styling; only two small **keyed** CSS rules (hero gradient + gold pay button).
- 🔐 **Credentials stay out of code** — `.env` / `.streamlit/secrets.toml` only (both git-ignored); secrets are never logged, and PayPal API errors are sanitized before display.

## 🏗️ How it works

```
┌────────────────────────────────────────────────────────────────────┐
│                            Streamlit UI                            │
│                                                                    │
│  bill text ──┐    ┌───────────────────────────────────────────┐    │
│  instructions┼───►│ utils/gemini.py — strict-JSON prompt,     │    │
│  presets     ─┘    │ 3-model rotation; bad JSON → raw text     │    │
│                    │ (shown honestly) → deterministic result    │    │
│                    └────────────────┬────────────────────────────┘    │
│              no key / failures      ▼                                 │
│                    ┌───────────────────────────────────────────┐    │
│                    │ utils/parsing.py — deterministic parser   │    │
│                    │ totals · items · weights · surcharges     │    │
│                    │ equal-split remainder · min-cash-flow     │    │
│                    └────────────────┬────────────────────────────┘    │
│                                     ▼                                │
│     metrics · split table · chart · per-person cards                │
│                                     ▼                                │
│                    ┌───────────────────────────────────────────┐    │
│                    │ utils/paypal.py — Orders v2 sandbox       │    │
│                    │ oauth → create order → approve link       │    │
│                    │ return ?token= → capture (idempotent)     │    │
│                    │ no creds → paypal.me deep links instead   │    │
│                    └───────────────────────────────────────────┘    │
└────────────────────────────────────────────────────────────────────┘
```

One fast-rendering page: UI first, slow work last, output reserved in a slot. No accounts, no database — state lives in Streamlit session state.

## 💳 How PayPal is used

| # | Touchpoint | What happens | Status |
|---|---|---|---|
| 1 | **OAuth (sandbox)** | Client-credentials token from `api-m.sandbox.paypal.com`, cached ~50 min. | ✅ Live |
| 2 | **Order create** | One Orders v2 order per transfer (`reference_id`, description, amount, optional payee email); session-cached so reruns don't re-order. | ✅ Live |
| 3 | **Approve → capture** | Gold **Pay via PayPal** pill opens the approval page; on return, `?token=` (== order id) triggers a capture, idempotent when PayPal already did it. | ✅ Live |
| 4 | **Fallback links** | Without credentials, every transfer still ships as a prefilled `paypal.com/paypalme/<handle>/<amount><currency>` deep link. | ✅ Live |
| 5 | **Brand UX** | PayPal navy/gold theme everywhere; approval/cancel notice states on return. | ✅ Live |

> **Scope note:** settlement is **sandbox Orders v2** (or PayPal.Me fallback) in this build — no production PayPal rails. Sandbox apps use the `api-m.sandbox.paypal.com` endpoint and stay testable with fake money.

## 🤖 How AI is used

| # | Capability | How it works | Model |
|---|---|---|---|
| 1 | **Natural-language bill understanding** | Messy text → structured people/shares with exact-to-the-cent arithmetic. | Gemini Flash |
| 2 | **Structured output** | JSON-mode request, normalized and validated into the same schema the deterministic parser emits — downstream UI is identical for both engines. | Gemini Flash |
| 3 | **Instruction following** | Weighted splits, tips, surcharges, currency hints in the instructions box. | Gemini Flash |
| 4 | **Free-tier resilience** | 3-model rotation; first clean JSON wins. Bad-but-real answers are surfaced as **raw text**, with the deterministic result shown next to them for verification — never silently re-guessed. | Rotation |
| 5 | **Deterministic fallback** | No key or all models down → the genuine regex/heuristics parser (tested), labeled exactly as such. | None (deterministic) |

## 🧱 Tech stack

| Layer | Technology | Where |
|---|---|---|
| Frontend & UI | **Streamlit 1.67** (locked PayPal theme in `.streamlit/config.toml`) | `app.py` |
| AI engine | **Google Gemini** via the maintained `google-genai` SDK (3.0) | `utils/gemini.py` |
| Parsing (fallback) | Regex/heuristics parser + min-cash-flow planner | `utils/parsing.py` |
| Payments | **PayPal Orders v2** sandbox over plain `requests` (no checkout SDK) | `utils/paypal.py` |
| Config & secrets | `st.secrets` / env vars / `.env` via `python-dotenv` | `utils/config.py` |
| Tests | `pytest` — 12 parser cases | `tests/test_parsing.py` |
| Language | **Python 3.12** | fully typed helper modules |

## 🚀 Quick start (5 minutes)

```bash
# 1. Clone
git clone https://github.com/Shahid-Tan/SplitAI-PayPal.git
cd SplitAI-PayPal

# 2. (Recommended) virtual environment
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS / Linux

# 3. Install pinned dependencies
pip install -r requirements.txt

# 4. (Optional) add credentials — see the two example files:
#    .env.example                     → copy to .env
#    .streamlit/secrets.toml.example  → copy to .streamlit/secrets.toml

# 5. Run
streamlit run app.py
```

**Zero credentials? It still runs** — you'll see the **Deterministic parser mode (no AI key)** badge, real splits from the tested parser, and PayPal.me settlement links. That's the honest fallback, not a demo stall.

To unlock the full experience:

1. **Gemini (optional):** free key at [aistudio.google.com](https://aistudio.google.com) → put it in `.env` as `GEMINI_API_KEY` or paste it into the sidebar field (password-masked, per-session only).
2. **PayPal sandbox (optional):** [developer.paypal.com](https://developer.paypal.com) → *Apps & Credentials* → create a **Sandbox** REST app → copy the client id/secret into `.env` or `.streamlit/secrets.toml` (shapes in the example files).
3. **Your own PayPal.me handle (fallback links):** sidebar box or `PAYPAL_ME_HANDLE`; the default ships as the author's handle (`syedshahidafridi`).

## 🔐 Credential shapes

Config resolution order per value: `.streamlit/secrets.toml` → environment / `.env` → safe default.

```toml
# .streamlit/secrets.toml  (git-ignored; see .streamlit/secrets.toml.example)
[gemini]
api_key = "your-gemini-api-key"

[paypal]
client_id     = "AYSq3RDGsmBLJE-…"
client_secret = "EGnHDxD_qRPd-…"
payee_email   = "your-sandbox-business@example.com"
me_handle     = "syedshahidafridi"
```

```bash
# .env  (git-ignored; see .env.example)
GEMINI_API_KEY=your-gemini-api-key
PAYPAL_CLIENT_ID=your-paypal-sandbox-client-id
PAYPAL_CLIENT_SECRET=your-paypal-sandbox-client-secret
APP_BASE_URL=https://your-public-host   # needed for PayPal redirects behind a tunnel
```

Never hard-code keys, and never commit `.env` / `.streamlit/secrets.toml` — the `.gitignore` covers both.

## 🧪 Tests

```bash
.venv\Scripts\python -m pytest tests/ -q     # 12 passed
```

## 📁 Project structure

```
SplitAI-PayPal/
├─ app.py                              # UI only: hero, presets, form, results, history
├─ utils/
│  ├─ config.py                        # credentials (secrets/env), currencies, money fmt
│  ├─ gemini.py                        # 3-model rotation, JSON normalization, probe
│  ├─ parsing.py                       # deterministic parser + transfer planner
│  └─ paypal.py                        # Orders v2 sandbox client (token/order/capture)
├─ tests/
│  └─ test_parsing.py                  # 12 parser unit tests
├─ .streamlit/
│  ├─ config.toml                      # locked PayPal-branded theme
│  └─ secrets.toml.example             # credentials shape (copy → secrets.toml)
├─ .env.example                        # env credential shape (copy → .env)
├─ requirements.txt                    # pinned deps (streamlit, google-genai, requests, dotenv, pandas)
├─ .gitignore                          # excludes .env, secrets.toml, .venv, caches
├─ LICENSE                             # MIT
├─ README.md                           # you are here
└─ docs/
   ├─ SUBMISSION_CHECKLIST.md          # every Devpost requirement + key dates
   ├─ DEVPOST_DESCRIPTION.md           # Devpost copy stub
   ├─ DEMO_VIDEO_SCRIPT.md             # <3 min video script
   └─ THUMBNAIL_IDEAS.md               # thumbnails for Devpost/YouTube
```

## ❓ FAQ

**Does the app move real money?**
No. Orders are created on the **sandbox** API, and the fallback PayPal.Me links hand off to PayPal's own platform. Scope is disclosed in the UI and here.

**Do I need API keys to run it?**
No. Without a Gemini key the tested deterministic parser does the splits; without PayPal credentials the settlement is PayPal.me links. With keys, you get the Gemini engine and real sandbox order approve/capture.

**How does the sandbox capture work?**
Approve opens PayPal; PayPal returns to the app with `?token=<order id>`, the app captures the order server-side (idempotent, safe if PayPal captured first), and clears the URL so reruns don't re-capture.

**Is my Gemini key safe?**
Keys live only in git-ignored files (or a masked sidebar field for the session), go only to the Gemini API, and are never logged. PayPal credentials are never sent to the browser and API errors are sanitized.

**Which Gemini models does it use?**
`gemini-2.5-flash` → `gemini-2.0-flash` → `gemini-1.5-flash`, tried in order. On first use the sidebar runs **one** quick probe and reports exactly which models responded — so you always know the app's live AI status.

**What happens when the AI is unavailable?**
Bad structured output is shown as raw text with the deterministic result alongside for verification; complete failures fall back to the parser. The parser itself refuses to invent people or amounts and tells you honestly when a bill is unparseable.

**What currencies work?**
USD ($), INR (₹), EUR (€), GBP (£), CAD (CA$), AUD (A$), SGD (S$) are auto-detected from the bill text and drive both table formatting and PayPal amounts.

**Why sandbox instead of live PayPal?**
Judge-safe: the sandbox app is free, cannot move real money, and still exercises the full OAuth → order → approve → capture integration end-to-end.

## 📦 Submission materials

- 📋 **Submission checklist:** [`docs/SUBMISSION_CHECKLIST.md`](docs/SUBMISSION_CHECKLIST.md) — every Devpost requirement with key dates.
- ✍️ **Devpost description draft:** [`docs/DEVPOST_DESCRIPTION.md`](docs/DEVPOST_DESCRIPTION.md).
- 🎬 **Video script:** [`docs/DEMO_VIDEO_SCRIPT.md`](docs/DEMO_VIDEO_SCRIPT.md) · **Thumbnail ideas:** [`docs/THUMBNAIL_IDEAS.md`](docs/THUMBNAIL_IDEAS.md).
- 📜 **License:** MIT — see [`LICENSE`](LICENSE).

## 🏆 Built for the PayPal AI Hackathon

![Built for the PayPal AI Hackathon](https://img.shields.io/badge/Built%20for%20the-PayPal%20AI%20Hackathon-ffc439?logo=paypal&logoColor=003087)

SplitAI was built for the **"Build What's Next with PayPal and AI"** hackathon on Devpost — combining Google Gemini's natural-language intelligence with PayPal's payment rails to make group money awkwardness a thing of the past.

## 👤 Author

Built by **Shahid-Tan** · [github.com/Shahid-Tan](https://github.com/Shahid-Tan)

## 📄 License

Released under the [MIT License](LICENSE) — free to use, remix, and build upon with attribution.
