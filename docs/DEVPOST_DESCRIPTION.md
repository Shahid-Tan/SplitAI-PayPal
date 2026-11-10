# Devpost Project Description — SplitAI

> Paste into the Devpost "About the project" field. Word count ≈ 320. Keep the sandbox disclosure — do not delete it.

---

## 💸 SplitAI — Paste the bill. AI splits it. PayPal settles it.

### Tagline
**Stop arguing over the bill. SplitAI turns a messy group-chat note into an itemized split — and settles it with PayPal.**

---

### The story

Every group has the same 11 p.m. problem: a bill note full of half-sentences. *One flatmate had the AC room. Someone paid the fuel upfront. There's a service tax… and a tip.* Expense apps handle the easy case and the group chat does the math anyway.

SplitAI started with one insight: you shouldn't have to format your life into a spreadsheet. If you can *describe* the bill in plain language, a modern LLM can parse the structure, apply the exceptions, and get the math right — every rupee and dollar accounted for.

### What it does

- **Conversational bill parsing** — paste receipts, rent notes, dinner messages; Gemini turns them into an itemized, per-person split.
- **Smart instructions** — "Split 60–40," "the AC room pays extra," "add 18% tax and a 10% tip": the AI applies them and shows its logic per person.
- **Multi-currency** — USD ($) and INR (₹), because the teams we built this for live in both billing worlds.
- **Instant settlement** — every split lands on a PayPal step, so "who owes what" becomes "paid, done."

### How we use Google AI

Google Gemini reads free-text bills and produces a structured breakdown — per-person amounts, tax/tip logic, one-off exceptions like room premiums or discounts. If a model hits its free-tier quota, SplitAI rotates through fallback Gemini models, and a built-in offline parser keeps the demo alive end to end.

### How we use PayPal

SplitAI integrates the **PayPal Orders API in sandbox mode**: creating the order, the full buyer approval step, and confirmation run end to end with mock credentials — no live money moves in this demo version. For anyone without a merchant setup, SplitAI also generates a **PayPal.me** link for instant per-person settlement.

### What's next

Live payments via approved PayPal merchant onboarding, bill upload from phone camera, recurring flat bills with per-roommate history, WhatsApp-bot parsing, and shared group balances.

### Built With (that we're proud of)

`python` · `streamlit` · `google-gemini` · `paypal-orders-api (sandbox)` · `paypal.me API` · `multi-currency` · `llm-parsing`

---

**Links**
- 🎬 Demo video: `[YOUTUBE LINK HERE]`
- 🌐 Live app: `[STREAMLIT/REPL URL HERE]`
- 📦 Repo: https://github.com/Shahid-Tan/SplitAI-PayPal

> **Honesty note (keep):** payments are demonstrated in PayPal's sandbox with mock data; the PayPal.me flow is the live-usable path today. No user, revenue, or "production" claims are made.
