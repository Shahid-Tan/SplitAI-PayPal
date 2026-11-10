# 📋 SplitAI — Devpost Submission Checklist

> **⏰ DEADLINE: Wed, Nov 12, 2026 · 12:00 PM Pacific** (PST, UTC-8 in Nov)
> = **20:00 UTC** = **Thu, Nov 13 · 1:30 AM IST**
> ⚠️ Verify the exact countdown on the Devpost project page — Devpost enforces its own timer.
> **Internal freeze target: Tue, Nov 11 · 9:00 PM Pacific** (15-hour buffer for Devpost form completion + video upload latency).

**Legend:** ✅ done · 🔶 in progress · ❌ to do · ␣ n/a — and an owner tag: **Boss**, **Nova** (code), **Pixel** (copy), **Filer** (files/docs). *Last updated: Nov 10, 2026.*

---

## 1️⃣ Devpost hard requirements (submission cannot go public without these)

| # | Requirement | Status | Owner | Notes |
|---|---|---|---|---|
| 1.1 | **Working working demo** — app runs live for judges | ❌ | Boss | Hosted URL = dev target; fallback: judge runs locally via README Quick start (verified steps) |
| 1.2 | **Hosted demo URL** on Devpost form | ❌ | Boss | Placeholder in README `Demo & Links` waiting for it |
| 1.3 | **Public GitHub repo** | ✅* | Boss | Remote = `github.com/Shahid-Tan/SplitAI-PayPal` verified locally; *confirm visibility = Public on github.com (Settings) before submission |
| 1.4 | **Open-source LICENSE in repo** | ✅ | Filer | MIT, `Copyright (c) 2026 Shahid-Tan` — committed as `LICENSE` |
| 1.5 | **YouTube video < 3 min** | ❌ | Boss | Must be public or unlisted; Devpost rejects private videos |
| 1.6 | **Video link on Devpost form** | ❌ | Boss | Also back-fill README `Demo & Links` |
| 1.7 | **Complete Devpost entry form** (all required fields) | ❌ | Boss | See §3 |
| 1.8 | **Project description with setup instructions** | 🔶 | Pixel | Draft stub at `docs/DEVPOST_DESCRIPTION.md`; final copy = Pixel's |
| 1.9 | **Press "Submit" / enter the hackathon** | ❌ | Boss | Submit ≥ 1 hour before deadline; don't trust the last 5 minutes |

## 2️⃣ Repo hygiene (judges open the repo)

| # | Item | Status | Owner |
|---|---|---|---|
| 2.1 | README: accurate, judge-friendly, setup steps | ✅ | Filer |
| 2.2 | README: "How PayPal is used" + "How AI is used" tables | ✅ | Filer |
| 2.3 | README: demo/video/Devpost placeholders back-filled with real URLs | ❌ | Boss |
| 2.4 | `.gitignore` covers secrets (`.env`, `.streamlit/secrets.toml`) | ✅ | Filer |
| 2.5 | **No secrets ever committed** (scan history before push) | ␣ | Boss |
| 2.6 | Repo publicly buildable: fresh clone → `pip install -r requirements.txt` → `streamlit run app.py` passes | ❌ | Nova |
| 2.7 | `requirements.txt` (streamlit, google-generativeai) final — owned by Nova | 🔶 | Nova |
| 2.8 | Final push: LICENSE/README/docs/.gitignore to GitHub | ❌ | Boss (approval) / Filer ready |

## 3️⃣ Devpost form fields (collect these into one doc before filling in)

- ❌ Hackathon: **"Build What's Next with PayPal and AI"** → project published to it
- ❌ Project name / title
- ❌ Short tagline (matches README one-liner: *"AI-powered conversational bill splitting with instant PayPal settlement"*)
- ❌ Project description → **source: `docs/DEVPOST_DESCRIPTION.md` (Pixel)**; must include setup instructions
- ❌ GitHub repo URL: `https://github.com/Shahid-Tan/SplitAI-PayPal`
- ❌ Demo URL (hosted) — from §1.2
- ❌ Video URL (YouTube, < 3 min) — from §1.5
- ❌ Images/screenshots (≥ 1): PayPal-blue header, split result card, Pay-with-PayPal button
- ❌ "Built with" tags: Streamlit, Python, Google Gemini, PayPal
- ❌ Team members listed
- ❌ Categories/prizes selection as applicable

## 4️⃣ Video production checklist (< 3 min hard cap)

- ❌ Hook in the first 5 seconds (problem → one sentence)
- ❌ Show: pasting a messy bill → custom instruction (e.g., "convert to INR") → 🚀 Calculate Split with AI → result card
- ❌ Show the 👉 Pay with PayPal deep link to `paypal.com/paypalme/…`
- ❌ Show a preset button (🏠 Flat Rent INR is the most impressive/multi-currency)
- ❌ State sandbox/PayPal.Me scope + disclosed deterministic fallback on screen (one caption line)
- ❌ Screen-record 1080p ≤ 3:00 — no dead air — then upload

## 5️⃣ Judging-criteria self-audit

> ⚠️ Cross-check the **actual criteria list** on the Devpost page the day of submission; map rows below to it.

| Criterion (typical for PayPal × AI hackathons) | Evidence in our submission | Status | Tip |
|---|---|---|---|
| **Use of PayPal** | PayPal.Me settlement links + on-brand UI in every result card; Sandbox integration documented & in flight | 🔶 | Lead with the settlement button in the video — it's the money moment. Don't imply production PayPal rails; "sandbox/PayPal.Me" is the honest pitch |
| **Use of AI** | Gemini natural-language parsing, itemized math, instruction following, multi-model quota-rotation fallback | ✅ | Name Gemini + show a non-trivial bill (room surcharge + tax) so AI value is undeniable |
| **Innovation / creativity** | Bills → `paypal.com/paypalme/…` in one conversational step; presets for real-world Indian rent & trip scenarios | 🔶 | Pitch the "paste what a waiter wrote" angle — zero-structure input |
| **Design & UX** | PayPal-branded Streamlit UI, presets, masked key field, gated clean input card | ✅ | Screenshot the result card; one polished screen beats a feature haul |
| **Technical execution / accuracy** | Clean ~200-line Python, graceful multi-model fallback, deterministic demo path, secrets hygiene | ✅ | Disclose the fallback confidently — judges reward honesty over overclaiming |
| **Practicality / impact** | Instant settlements for rent/taxi/dinner groups, no accounts, 100% free-tier tech | 🔶 | Quantify the friction removed in the description |
| **Presentation (description + video)** | Devpost copy = Pixel; video = §4 checklist; README carries judge tables | ❌ | First 200 words of Devpost description are skimmed most — strongest line goes first |

## 6️⃣ Key dates

| Milestone | Date (Pacific) | Date (IST) |
|---|---|---|
| Today | Tue, Nov 10, 2026 | Wed, Nov 11, 2026 (checkpoints) |
| Internal freeze (all assets ready) | Tue, Nov 11 · 9:00 PM | Wed, Nov 12 · 10:30 AM |
| **Submissions close (hard)** | **Wed, Nov 12 · 12:00 PM** | **Thu, Nov 13 · 1:30 AM** |
| After close: verify submission shows "COMPLETE" in the Devpost dashboard | Wed, Nov 12 · by 2:00 PM | Thu, Nov 13 · 3:30 AM |

## 7️⃣ Final 60 minutes before submit

1. Fresh-clone smoke test from GitHub (§2.6) on a second machine/user.
2. Click every link in README + Devpost (no placeholders left `[TO ADD]`).
3. Video duration < 3:00 and audio legibility spot-check.
4. Judging self-audit above is green; status text says "demo/links updated".
5. Submit; then confirm the entry appears on the hackathon's *Gallery/Submissions*.
