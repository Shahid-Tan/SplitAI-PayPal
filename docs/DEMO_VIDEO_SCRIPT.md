# SplitAI — Demo Video Script (<3:00, YouTube public link)

**Goal:** Best Demo Delivery ($5,000) + strong "presentation" score.
**Target runtime: 2:50** (hard ceiling 2:59 — Devpost requires under 3 min).
**Format:** 1920×1080 min (record 1440p, export 1080p), 30 fps, English narration, English captions burned in.
**Tone:** Relatable, fast, zero fluff. Every claim on screen must match the app's real behavior — sandbox disclosed on screen.

> **Depends on the boss / NOVA:** record ONLY after `app.py` rewrite is frozen — names, preset labels, and the PayPal step shown on screen must match the narration. Audio is recorded LAST, after screen capture.

---

## Second-by-second timeline

| # | Time | On screen (capture this) | Narration (verbatim) | On-screen text / captions | Motion / B-roll |
|---|------|--------------------------|----------------------|---------------------------|-----------------|
| 1 Hook | 0:00–0:12 | Mock group-chat B-roll (fake chat, fake names): pings "bro how much do I owe?", "?", 😤. Then slam-cut to the app. | "Splitting a ₹24,000 flat bill in a college group chat. Three roommates. One AC bedroom. Forty-one unanswered texts." | "₹24,000 · 3 flatmates · 41 unread messages" | Bubbles pop in rapid-fire; cut on beat. 2–3 s of chat is enough. |
| 2 Reveal | 0:12–0:20 | SplitAI lands in browser: navy header card scales in, clean UI settles. | "This is SplitAI. One messy bill in — one fair split out." | "messy bill → fair split" | Slow 110%→100% zoom-in on header; hold steady. |
| 3 Demo: Flat Rent INR | 0:20–0:55 | Click **🏠 Flat Rent (INR)** preset → text area fills. Optional edit: rename a flatmate. Click **🚀 Calculate Split with AI**. Show spinner briefly. Result card appears: per-person INR amounts + itemized logic. Zoom tightly to the three amount lines. | "Here's the exact note from a real flat month: rent, WiFi, electricity — and someone had the AC room. Watch: Gemini reads it, figures who pays extra, and the math adds up to the last rupee." | "Gemini reads the receipts" → highlight: "AC premium applied ✓" | Cursor moves with intent, no wandering. Zoom-punch (110%) on the amounts for ~3 s. No screen skew — keep text crisp. |
| 4 AI flex | 0:55–1:20 | Same bill + instruction box: type "Split 60–40 between the two non-AC rooms" → recalc. Then currency flip: request INR→USD; result renders with $. | "Then just ask. 'Split it sixty–forty.' 'Convert to dollars.' The split re-runs in seconds — no spreadsheet, no group-chat war." | "60–40 ✓" · "USD/Currency ✓" | Quick-cut between the two recalcs; match-cut on the result card position. |
| 5 PayPal settle | 1:20–1:55 | Click the settle/Pay button for the flatmates → **PayPal sandbox checkout** opens → click **Approve** → confirmation screen. Then show the fallback in one cut: a generated **PayPal.me** link/button opening the PayPal page. | "Every split lands on PayPal. In sandbox mode the full checkout runs end to end — approve, confirm, done. No merchant account? A PayPal.me link still settles it instantly." | Disclosure chip, persistent 6 s: "Demo: PayPal Sandbox — no real money" | This is the money shot. Full-screen the approve click. Cut AFTER the success state, not during a redirect. |
| 6 How it's built | 1:55–2:20 | Split screen / picture-in-picture: left = 3-node architecture animation (Gemini → itemized split → PayPal), right = app or repo code drifts by. | "Under the hood: a Streamlit frontend, Google Gemini turning free-text bills into itemized splits, model rotation so free-tier quota never breaks a demo — plus an offline parser fallback. Payments run on PayPal's sandbox Orders API, with PayPal.me as instant fallback." | Chips row (one at a time, 1.5 s each): "Streamlit" · "Google Gemini" · "PayPal Orders API (sandbox)" · "Python" | Keep code scroll slow and readable; never linger on secrets. |
| 7 Montage | 2:20–2:33 | 2× speed cuts: 🍕 Restaurant preset result → 🚗 Road Trip "who owes whom" list → totals ticking up. | "Restaurant dinners. Road trips. Flat rent. If you can type it, SplitAI can split it." | "41 messages → 1 tap" | Time-lapse energy, 2–3 s per cut, hard music beat. |
| 8 Close / CTA | 2:33–2:50 | Full-frame end card: logo, tagline, Devpost + GitHub placeholder links. Static hold last ~4 s. | "SplitAI — built for the PayPal & AI Hackathon. Try the repo, split your next bill, then thank me at dinner." | "Stop arguing. It's already split." + "Devpost · GitHub · Live demo" | Logo eases onto the frame; hold the end card ≥3 s for link readability and the YouTube end-screen slot. |

**Running math:** 0:12 + 0:08 + 0:35 + 0:25 + 0:35 + 0:25 + 0:13 + 0:17 = **2:50** ✓

---

## Run-of-show (recording order)

1. **Prep browser** (see tips below). Open app logged in with sandbox/demo settings. Hide the Gemini API key input (or blur in post).
2. **Dry run once, completely, unrecorded.** Time the spinner; if Gemini wants >6–8 s, pre-run each request once before recording so results return fast (cache it in the session) — or trim dead spinner frames in post rather than speeding up audio-synced UI.
3. **Screen capture pass** — all 8 scenes, mouse only, take each scene twice.
4. **Interface polish pass:** inserts (zoom-punches, chip overlays), group-chat B-roll, architecture animation. Build B-roll from *fictional* data only.
5. **Voiceover last**, after NOVA's rewrite is frozen — so narration names match the app exactly (flatmate names, preset labels, what the PayPal step actually shows).
6. **Edit order:** cut picture → VO → captions → music ducked under VO → level loudness → final export.

### Typed-bill examples to have on the clipboard (demo data, fictional names)

- Flat rent (preset): Monthly 3BHK flat expenses: total rent ₹24,000, WiFi ₹1,000, electricity ₹2,000; one flatmate's AC room costs extra.
- Follow-up instruction: `Split 60–40 between the two non-AC rooms`
- Currency flip: `Convert results to USD`
- Road-trip montage sample: fuel + snacks shared by 4 friends, one friend paid everything upfront, "show who owes whom".
- Restaurant montage sample: dinner for 4, individual mains, tip split equally.

---

## Recording tips

- **Resolution:** record at 2560×1440, export 1920×1080, bitrate ≥10 Mbps — Streamlit text must stay razor sharp; no JPEG-looking artifacts.
- **Clean browser profile:** separate Chrome profile, hide bookmarks bar (Ctrl+Shift+B), no extensions visible, zoom 125%, fullscreen (F11) so no browser chrome shows.
- **No personal info leaks — hard rules:** no real Gemini API key on screen (blur or pre-hide the sidebar key field), no real PayPal.me handle, email, or phone, fictional flatmate names only, no real chat screenshots, clean desktop (no personal wallpaper, bookmarks, or file names visible). Demo handle like `@demo-friend`; all payment flows shown in sandbox mode.
- **OS hygiene:** Focus Assist / Do-Not-Disturb ON (no notification toasts), hide Windows taskbar, hide desktop icons, disable the mouse-highlight cursor animation, clean single pointer movement.
- **Demo data:** sandbox only, amounts modest and plausible, all names fictional.
- **Audio:** quiet room, mic ≤15 cm from mouth, record noise floor first: 10 s of silence for noise reduction. Target VO ~-14 LUFS; gentle compression, no clipped peaks.
- **Music:** license-cleared tracks only (e.g., YouTube Audio Library), ducked 10–14 dB below VO; cut on the beat so clicks and scene changes land.
- **Frame pacing:** each scene ends with a static hold of ≥1.5s (easy cut points).
- **Captions:** burned-in English captions, capped at ~10% of frame height inside the safe area; never cover the numbers.
- **Cut discipline:** no single static shot over ~20 s in a 3-min demo; use hard cuts (cross-fades only allowed on the open and close).

---

## Failure contingency — the cut list (if we run long)

Cuts are ordered; apply top-down, then re-time. Each line shows runtime after cut.

| Priority | Cut | Runtime |
|---|---|---|
| Keep everything | — | 2:50 |
| 1 (if >2:55) | Trim Scene 6 → only chips + one line of narration | 2:38 |
| 2 (if next test is longer) | Scene 7 montage → 2 shots, shorter VO | 2:30 |
| 3 | Scene 4: keep 60–40 split, drop currency flip | 2:22 |
| 4 (last resort) | Scene 1 B-roll to 6 s flat; VO to: "College flat, ₹24,000, three roommates, zero agreement." | 2:15 |

**Untouchable:** hook (scene 1), one full end-to-end split (scene 3), the PayPal approve step (scene 5), close card (scene 8). Scene 4 and 6 are nice-to-have and thus first to go.

**If something breaks mid-recording** (spinner hangs, sandbox popup misbehaves, a number looks wrong):
- Every scene is a standalone take — re-record only the broken scene; the plan stays modular.
- The PayPal approve step (scene 5) is the one sacred take: record it twice for safety.
- If the Orders-API approve flow isn't wired yet when we record: ship the PayPal.me fallback take — it's honest and judge-legit — and schedule a pickup take later for the sandbox approve step to swap in if it lands.
- If a preset label or flatmate name changed overnight: shoot the button unclicked and insert the click in post; never re-roll a whole scene for a label.
- If a retake is impossible at export time: fix small text with an overlay, nothing more invasive.

---
*Devpost requires the video link public and under 3:00. Final QA: scrub with captions ON, check the first 10 s and the PayPal step at 1× and 2× speed, confirm no low-contrast or clipped text, verify every on-screen total equals the bill inputs.*
