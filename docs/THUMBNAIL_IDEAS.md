# SplitAI — Thumbnail Concepts

Platform: YouTube (DVR 1280×720 crisp, final render 1280×720). Goal: readable **at 320×180** (mobile ~21% of screen) and legible next to 20 other thumbnails.
Palette: **PayPal navy #003087**, sky **#0079c1**, **gold #ffc439**, white, ink #0f172a.
Typography: one ultra-bold sans only — **Montserrat ExtraBold / Archivo Black / Poppins 800**; max **4–5 words** of text; contrast rule: text can be white, ink, or navy **only** (never mid-tone gray on navy).
Emoji: YouTube font emoji render inconsistently across devices → use ≤1 emoji as an *accent*, baked in as a drawn graphic, never as copy-paste font text.
Small-size rules: one focal subject ≥35% of canvas; text block on the opposite side; 6% outer margin stays empty; no thin strokes, no gradients blocking text, nothing taller than 2 lines.

---

## Concept 1 — "Before / After"  ⭐ recommended

```
+--------------------------------------------------+
| navy #003087 full bleed                          |
|  LEFT 40% : mirrored crumpled receipt doodle,    |
|             ink-white scribbles + red ❌ marks,  |
|             tilted -6°, slight blur              |
|             (hand-drawn bill: "total?? tip?? AC")|
|                                                  |
|  CENTER   : bold gold → divider, gold arrow (25px)|
|             "▶" pointing right, hard edge        |
|                                                  |
|  RIGHT 45%: crisp white "result card"             |
|             3 rows: "Aisha  ₹9,000"              |
|             "Sam   ₹9,000"  "Ali   ₹9,000"        |
|             gold "PayPal" pill button bottom      |
|                                                  |
| HEADLINE (top-left, 2 lines, ink-white):          |
|   MESSY BILL                                     |
|   FAIR SPLIT                                     |
| (bottom-right small navy-on-gold chip: "AI →" )  |
+--------------------------------------------------+
```
- **Headline:** *MESSY BILL → FAIR SPLIT*
- **Colors:** navy field, one gold accent (arrow + button), white card, red ❌ accents only.
- **Why it wins:** tells the whole product story in one glance — chaos in, solution out; the three-amount card is big enough to read even at 200 px wide.
- **Emoji:** none needed — replaces them with ❌ ×, drawn.

## Concept 2 — "The Number" (lands as pure curiosity)

```
+--------------------------------------------------+
| navy #003087 top 55% / #0079c1 bottom 45% split,  |
|  diagonal seam                                   |
|                                                  |
|  LEFT: giant white figures dominating the frame: |
|      "₹24,000"  (Archivo Black, 220 px)          |
|      underneath, ink-white sub-line 44 px:       |
|      "who pays what?"                            |
|                                                  |
|  RIGHT: white phone / receipt mock, tilted 8°,   |
|      screen shows 3 equal rows + gold pill =     |
|      tiny readable "₹8,000 each"                 |
|      gold Gemini ✨ sparkle + PayPal "P"          |
|      badges overlap its corner                   |
|                                                  |
| HEADLINE (bottom-left, gold #ffc439, 1 line):    |
|   ONE TAP PAYS IT                                |
+--------------------------------------------------+
```
- **Headline:** *₹24,000 → WHO PAYS WHAT?* (then gold kicker "ONE TAP PAYS IT")
- **Colors:** two-tone blue background for depth, headline in gold, amounts in white.
- **Why it works:** a number with a "?" is a story hook in itself; the split-screen diagonal mimics the "before → after" motion so it reads as motion even static.
- **Emoji:** ✨ sparkle only, drawn on the receipt corner.

## Concept 3 — "Group-chat panic" (most emotional pick)

```
+--------------------------------------------------+
| ink #0f172a background (dark theme for pop)      |
|                                                  |
|  CENTER-LEFT: 3 mock chat bubbles, stacked,      |
|    each tilted ±4°:                              |
|    "bro who has the wifi bill?"   (blue #0079c1) |
|    "I DIDN'T order the paneer??"  (red #ef4444)  |
|    "...still nothing? 😤"          (white 10%)   |
|                                                  |
|  RIGHT 40%: white chat bubble, bold:             |
|    "SplitAI: 3 × ₹9,000 ✓" + small gold P        |
|    wrapped in a gold outline glow (8px)          |
|                                                  |
| HEADLINE (top strip, navy-on-gold pill, 26 px):  |
|   THE DEBT SETTLER                               |
+--------------------------------------------------+
```
- **Headline:** *THE DEBT SETTLER* (gold pill), bubble copy carries the story.
- **Colors:** dark ink field makes the single gold/white solution bubble the brightest pixel region — instant focal point.
- **Why it works:** every judge has lived this group chat; comedy + solution in one frame, and the tilted bubbles add human energy.
- **Emoji:** 😤 allowed as a *drawn accent* on one white bubble only, none in copy.

---

## Shared spec (use for any final pick)

- Canvas 1280×720, PNG/sRGB; check the 320×180 and 210×118 (sidebar) previews before export.
- Only one gold element per concept (arrow *or* button *or* pill) so yellow stays scarce and premium.
- Always keep a face-shaped or object-shaped focal area clear of any text if stock imagery is added later.
- Safe margins 76 px on all sides; nothing key within 8% of edges (YouTube round-corner shadow crop).
- Test at arm's-length squint: if the headline isn't readable at a glance, drop 2 words.
