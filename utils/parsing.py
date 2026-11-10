"""Honest deterministic bill parser used when no Gemini key is configured.

Rules of engagement:
- Only names that actually appear in the input become participants.
- When no names are present but a head-count is, derived placeholders
  ("Person 1".."Person N") are used and clearly reported as derived.
- When the bill cannot be parsed reliably, the caller is told (ok=False)
  instead of being shown invented results.

Pure logic, no Streamlit dependency, so it can be unit-tested with pytest.
"""

from __future__ import annotations

import re
from collections import defaultdict

# ----------------------------------------------------------------- vocab

SYMBOL_TO_CURRENCY = {"$": "USD", "\u20b9": "INR", "\u20ac": "EUR",
                      "\u00a3": "GBP"}
WORD_TO_CURRENCY = {"usd": "USD", "dollar": "USD", "dollars": "USD",
                    "inr": "INR", "rupee": "INR", "rupees": "INR",
                    "eur": "EUR", "euro": "EUR", "euros": "EUR",
                    "gbp": "GBP", "pound": "GBP", "pounds": "GBP"}
CURRENCY_SYMBOLS = {"USD": "$", "INR": "\u20b9", "EUR": "\u20ac",
                    "GBP": "\u00a3", "CAD": "CA$", "AUD": "A$", "SGD": "S$"}

PRONOUN_MASKS = {"i": "You", "me": "You", "my": "You", "mine": "You",
                 "we": "Us", "our": "Us", "us": "Us"}

NON_NAME_WORDS = {
    "bill", "total", "tip", "tax", "gst", "vat", "split", "add", "added",
    "dinner", "rent", "wifi", "electricity", "fuel", "gas", "snacks", "car",
    "road", "trip", "groceries", "food", "order", "orders", "monthly", "flat",
    "the", "and", "or", "plus", "was", "were", "is", "are", "in", "at",
    "on", "for", "from", "with", "paid", "pay", "paying", "convert",
    "incl", "including", "grand", "net", "each", "friend", "friends",
    "guys", "people", "participants", "note", "notes", "invoice", "receipt",
    "cafe", "restaurant", "lunch", "breakfast", "amount", "amounts", "price",
    "cost", "costs", "hello", "hi", "hey", "please", "everything", "upfront",
    "internet", "diesel", "petrol", "movie", "movies", "shopping", "hobby",
    "training", "trainer", "class", "classes", "course", "sports", "club",
}

PERSON_VERBS = ("had", "has", "have", "ordered", "gets", "got", "spent",
                "paid", "ate", "drank", "bought", "took", "used", "owe",
                "owes", "pays", "pay")
EXTRA_LABELS = ("tip", "gratuity", "tax", "gst", "vat", "service", "delivery",
                "parking", "toll", "fee", "charge", "discount")

AMOUNT_TOKEN = r"\d[\d,]*(?:\.\d{1,2})?"
AMOUNT_RE = re.compile(
    rf"(?P<prefix>[$\u20b9\u20ac\u00a3])\s?(?P<sym_amount>{AMOUNT_TOKEN})"
    rf"|(?P<bare>{AMOUNT_TOKEN})\s?(?P<word>USD|INR|EUR|GBP|Rupees?|Dollars?)",
    re.IGNORECASE)
YEAR_RE = re.compile(r"\b(?:19|20)\d{2}\b")
SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?;:])\s+|\n+")


# ------------------------------------------------------------- primitives

def detect_currency(text: str) -> str:
    for symbol, code in SYMBOL_TO_CURRENCY.items():
        if symbol in text:
            return code
    lowered = text.lower()
    for word, code in WORD_TO_CURRENCY.items():
        if re.search(rf"\b{re.escape(word)}\b", lowered):
            return code
    return "USD"


def _num(raw: str) -> float:
    return round(float(raw.replace(",", "")), 2)


def sentences_with_spans(text: str) -> list[tuple[str, int, int]]:
    out, cursor = [], 0
    for sentence in SENTENCE_SPLIT_RE.split(text):
        start = text.find(sentence, cursor)
        if start == -1:
            start = cursor
        end = start + len(sentence)
        out.append((sentence, start, end))
        cursor = end
    return out or [(text, 0, len(text))]


def stated_totals(text: str) -> list[tuple[float, int]]:
    """Explicit grand totals: "total was $70", "…in total", "overall $70".
    A noun wedged between "total" and the amount (e.g. "total rent ₹24,000")
    is deliberately NOT treated as the bill grand total.
    """
    patterns = [
        rf"(?i)(?:grand\s+total|total(?:\s+bill|\s+amount)?|overall)\s*"
        rf"(?:was|is|:|came\s+to|comes\s+to)?\s*[$\u20b9\u20ac\u00a3]\s*({AMOUNT_TOKEN})",
        rf"(?i)[$\u20b9\u20ac\u00a3]\s*({AMOUNT_TOKEN})\s*(?:in\s+)?total\b",
        rf"(?i)total[^\n]{{0,50}}(?:was|is|:|of)\s*[$\u20b9\u20ac\u00a3]\s*({AMOUNT_TOKEN})",
        rf"(?i)(?:overall|grand\s+total)\s*($|[^.]+)",
    ]
    totals: list[tuple[float, int]] = []
    for pattern in patterns[:3]:
        for m in re.finditer(pattern, text):
            value = _num(m.group(1))
            if value > 0:
                totals.append((value, m.start(1)))
    return totals


def extra_charges(text: str) -> list[dict]:
    """Flat (absolute) and percentage surcharges for the whole bill."""
    flats: list[dict] = []
    seen_positions: set[int] = set()

    def flat_from(match: re.Match, group: int) -> dict | None:
        value = _num(match.group(group))
        position = match.start(group)
        if value <= 0 or position in seen_positions:
            return None
        seen_positions.add(position)
        window = match.group(0).lower()
        label = next((word for word in EXTRA_LABELS if word in window),
                     "extra")
        return {"amount": value, "label": label, "position": position}

    patterns = [
        rf"(?i)\b(?:add(?:s|ed|ing)?|plus|incl\w*|with)\s+(?:an?\s+)?"
        rf"[$\u20b9\u20ac\u00a3]?\s?({AMOUNT_TOKEN})[^%;.\n]{{0,20}}?"
        rf"\b(?:tip|gratuity|service|tax|gst|vat|toll|parking|delivery|fee|charge)\b",
        rf"(?i)\b(tip|gratuity|tax|gst|vat|service\s+(?:tax|charge|fee)|"
        rf"delivery\s*fee|parking|toll)\s*(?:of|was|is|:|=)?\s*"
        rf"[$\u20b9\u20ac\u00a3]\s?({AMOUNT_TOKEN})",
        rf"(?i)[$\u20b9\u20ac\u00a3]\s?({AMOUNT_TOKEN})\s?"
        rf"(?:tip|gratuity|tax|gst|vat|service\s+(?:tax|charge|fee))",
    ]
    for pattern in patterns:
        for match in re.finditer(pattern, text):
            group = 1 if match.lastindex == 1 else 2 if match.group(2) else 1
            extra = flat_from(match, group)
            if extra:
                flats.append({"amount": extra["amount"], "label": extra["label"],
                              "position": extra["position"]})

    percents = [{"percent": float(m.group(1)), "label": m.group(2).lower()}
                for m in re.finditer(
                    r"(?i)(\d{1,2}(?:\.\d+)?)\s?(?:%|percent)\s*"
                    r"(tip|gratuity|tax|gst|vat|service)", text)]
    return flats + [{"percent": extra["percent"], "label": extra["label"]}
                    for extra in percents]


def equal_split(amount: float, parts: int) -> list[float]:
    """Split into exactly `parts` shares that sum back to `amount` to the cent."""
    if parts <= 0:
        return []
    base = round(amount / parts, 2)
    shares = [base] * parts
    remainder = round(amount - base * parts, 2)
    steps = int(abs(remainder) * 100)
    step = 0.01 if remainder > 0 else -0.01
    order = sorted(range(parts), key=lambda i: (-shares[i], i))
    for i in range(min(steps, parts * 100)):
        shares[order[i % parts]] = round(shares[order[i % parts]] + step, 2)
    return shares


def pct_weights(text: str) -> tuple[int, int] | None:
    """Percent split like "split 60-40", "60/40", "60 40" (near "split")."""
    match = re.search(
        r"(?i)\bsplit\b[^\n]{0,40}?\b(\d{1,3})\s?(?:-|/|,)\s?(\d{1,3})\b"
        r"|\b(\d{1,3})\s?(?:-|/|,)\s?(\d{1,3})\b[^\n]{0,40}?\bsplit\b", text)
    if not match:
        return None
    w1 = int(match.group(1) or match.group(3))
    w2 = int(match.group(2) or match.group(4))
    if 0 < w1 < 101 and 0 < w2 < 101 and w1 + w2 > 0:
        return w1, w2
    return None


def head_count(text: str) -> int | None:
    lowered = text.lower()
    words = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6,
             "seven": 7, "eight": 8, "nine": 9, "ten": 10}
    m = re.search(r"\b(\d+)\s*(?:people|persons|members|friends|roommates|"
                  r"guys|participants|of\s+us)\b", lowered)
    if m and m.group(1):
        return int(m.group(1))
    for word, count in words.items():
        if re.search(rf"\b{word}\s+(?:people|persons|members|friends|"
                     rf"roommates|guys|of\s+us)\b", lowered):
            return count
    m = re.search(r"\b(\d+)\s*(?:friends|people|members)\b[^\n.:]{0,40}?", text)
    if m and m.group(1):
        return int(m.group(1))
    return None


def roster_names(text: str) -> list[str]:
    roster: list[str] = []

    def add(label: str | None):
        if label and label.lower() not in {name.lower() for name in roster}:
            roster.append(label)

    for verb in PERSON_VERBS:
        for m in re.finditer(
            rf"\b([A-Z][a-z'`\u2019]+(?:\s+[A-Z][a-z'`\u2019]+)?)\s+{verb}\b", text):
            raw = m.group(1)
            add(PRONOUN_MASKS.get(raw.lower()) or clean_name(raw))
        for m in re.finditer(rf"\b(?:(I|We))\s+{verb}\b", text):
            add(PRONOUN_MASKS[m.group(1).lower()])
    for m in re.finditer(r"\b([A-Z][a-z'`\u2019]+)\s*:", text):
        # skip place-of-transaction colons like "in Bangalore:" / "at Cafe:"
        before = text[max(0, m.start() - 6):m.start()].lower()
        if re.search(r"\b(?:in|at|from|near)\s+$", before):
            continue
        raw = m.group(1)
        add(PRONOUN_MASKS.get(raw.lower()) or clean_name(raw))
    list_patterns = [
        r"(?i)\b(?:among(?:st)?|between)\s+([A-Za-z0-9' ,/&+]+?)(?=[.;]|$|and\s+the)",
        r"(?i)(?:\bfriends\b|people|participants|roommates|flatmates|mates|"
        r"colleagues|team)\s*[:\-]?\s*([A-Z][A-Za-z0-9' ,/&+]+)",
        r"\b([A-Z][a-z'`\u2019]+(?:\s*,\s*[A-Z][a-z'`\u2019]+){1,5}"
        r"(?:\s+and\s+[A-Z][a-z'`\u2019]+)?)\b",
    ]
    stripped_patterns = []
    for pattern in list_patterns:
        for group in re.findall(pattern, text):
            for token in re.split(r",|\band\b|/|&|\+", group):
                token = token.strip(" .:%'\u201c\u201d\"")
                add(clean_name(token) or PRONOUN_MASKS.get(token.lower()))
    del stripped_patterns
    for pronoun_match in re.findall(r"\b(?:I|We)\b", text):
        add("You" if pronoun_match == "I" else "Us")
    return roster


def clean_name(raw: str) -> str | None:
    words = raw.strip().split()
    if not words:
        return None
    for word in words:
        if word.lower().strip("',`\u2019") in NON_NAME_WORDS:
            return None
        if not re.fullmatch(r"[A-Z][a-z'`\u2019]+", word):
            return None
    return " ".join(words)


def payer_names(text: str) -> list[str]:
    """Names explicitly recorded as having paid. Never invented."""
    payers: list[str] = []

    def add(label: str | None):
        if label and label.lower() not in {name.lower() for name in payers}:
            payers.append(label)

    for m in re.finditer(
        rf"\b([A-Z][a-z'`\u2019]+(?:\s+[A-Z][a-z'`\u2019]+)?)\s+(?:has\s+|have\s+)?paid\b",
        text, flags=re.I):
        add(clean_name(m.group(1)))
    for m in re.finditer(r"\b(?:paid|paying|paid\s+for|settled|covered|fronted)"
                         rf"\s+(?:by|to)?\s+([A-Z][a-z'`\u2019]+)", text):
        add(clean_name(m.group(1)))
    for m in re.finditer(rf"\b([A-Z][a-z'`\u2019]+)\s+(?:covered|settled|"
                         rf"fronted)\b", text):
        add(clean_name(m.group(1)))
    for m in re.finditer(r"\b(I|We)\s+(?:have|has)?\s*paid\b", text):
        add("You" if m.group(1) == "I" else "Us")
    for m in re.finditer(r"\bpaid\s+(?:by|to)\s+(?:me|us)\b", text, flags=re.I):
        add("You" if "me" in m.group(0).lower() else "Us")
    return payers


# ------------------------------------------------------------ item spans

def person_spans(text: str) -> list[dict]:
    """Each person mention with a capture window for their paid items.

    Window ends either at the next person mention or the sentence end,
    whichever comes first — so "$22, Sneha ordered ..." hands items to
    Rahul only until Sneha's mention starts.
    """
    spans: list[dict] = []
    for verb in PERSON_VERBS:
        for m in re.finditer(
            rf"\b(?P<who>[A-Z][a-z'`\u2019]+(?:\s+[A-Z][a-z'`\u2019]+)?)\s+{verb}\b",
            text):
            raw = m.group("who")
            mask = PRONOUN_MASKS.get(raw.lower())
            if mask:                       # "We had" is handled by the scan below
                label = mask
            else:
                label = clean_name(raw)
            if not label:
                continue
            spans.append({"label": label, "start": m.start(),
                          "detail": m.group(0)})
        for m in re.finditer(rf"\b(?P<who>I|We)\s+{verb}\b", text):
            spans.append({"label": PRONOUN_MASKS[m.group("who").lower()],
                          "start": m.start(), "detail": m.group(0)})
    for m in re.finditer(r"\b(?P<who>[A-Z][a-z'`\u2019]+)\s*:", text):
        # skip place-of-transaction colons like "in Bangalore:" / "at Cafe:"
        before = text[max(0, m.start() - 6):m.start()].lower()
        if re.search(r"\b(?:in|at|from|near)\s+$", before):
            continue
        label = clean_name(m.group("who"))
        if label:
            spans.append({"label": label, "start": m.start(),
                          "detail": m.group(0)})
    spans.sort(key=lambda s: s["start"])
    deduped: list[dict] = []
    for span in spans:
        key = (span["label"].lower(), span["start"])
        if not deduped or (deduped[-1]["label"].lower(),
                           deduped[-1]["start"]) != key:
            deduped.append(span)
    spans = deduped
    sentences = sentences_with_spans(text)
    for i, span in enumerate(spans):
        sentence_end = next((end for _, start, end in sentences
                             if start <= span["start"] < end), len(text))
        boundary = sentence_end
        if i + 1 < len(spans) and spans[i + 1]["start"] > span["start"]:
            boundary = min(boundary, spans[i + 1]["start"])
        span["end"] = boundary
    return spans


def amounts_in(text: str, blocked_positions: set[int]) -> list[dict]:
    """Currency amounts [(value, position, symbol_flag)], in reading order."""
    stripped = YEAR_RE.sub(lambda m: " " * len(m.group(0)), text)
    found: list[dict] = []
    for m in AMOUNT_RE.finditer(stripped):
        raw = m.group("sym_amount") or m.group("bare")
        if not raw:
            continue
        value = _num(raw)
        position = m.start("sym_amount") if m.group("sym_amount") else m.start("bare")
        if value <= 0 or position in blocked_positions:
            continue
        if m.group("bare"):                      # bare numbers need a unit
            unit = m.group("word") or ""
            if not unit:
                continue
        found.append({"value": value, "position": position,
                      "symbol": bool(m.group("sym_amount"))})
    return found


EXTRA_WORD = (r"(?:service\s+(?:tax|charge|fee)|delivery\s*fee|tip|gratuity|"
              r"tax|gst|vat|parking|toll)")
_SUFFIX_EXTRA_RE = re.compile(
    rf"(?i)^{AMOUNT_TOKEN}\s?(?:is|:|=|of)?\s?(?:{EXTRA_WORD}|extra)\b")
_PREFIX_EXTRA_RE = re.compile(
    rf"(?i)(?:(?:{EXTRA_WORD})|extra)\s?(?:of|was|is|:|=|\u2014|-)?\s*$")


def _window_includes_extra(text: str, position: int,
                           extra_positions: set[int]) -> bool:
    """True only when a charge label sits immediately around the amount.

    The label must hug the amount (so "$10 tip" and "tip of $10" are
    extras, while "$18, and I had salad for $14. Add $6 service tax" is
    not) — a loose neighbourhood window mis-blocked neighbouring items.
    """
    if position in extra_positions:
        return True
    after = text[position:position + 30]
    if _SUFFIX_EXTRA_RE.match(after):
        return True
    before = text[max(0, position - 26):position]
    return bool(_PREFIX_EXTRA_RE.search(before))


# ----------------------------------------------------------------- main

def parse_bill(text: str, instructions: str = "") -> dict:
    """Deterministic parse of bill text (+ optional instruction text)."""
    combined = f"{text}\n{instructions}" if instructions else text
    result: dict = {
        "ok": False,
        "mode": "det",
        "currency": detect_currency(combined),
        "entries": [], "payers": [], "transfers": [],
        "bill_total": None, "shares_total": 0.0, "notices": [],
        "fail_reason": None,
    }
    result["symbol"] = CURRENCY_SYMBOLS.get(result["currency"], result["currency"])
    notices: list[str] = result["notices"]

    if not text.strip():
        result["fail_reason"] = "No bill details to parse."
        return result

    totals = stated_totals(combined)
    total_positions = {pos for _, pos in totals}
    extras = extra_charges(combined)
    extra_positions = {e["position"] for e in extras if "position" in e}
    roster = roster_names(combined)
    payers = payer_names(combined)
    individual_surcharge, surcharge_positions = surcharges(combined, roster)
    surcharge_total = round(sum(individual_surcharge.values()), 2)

    all_amounts = amounts_in(combined, total_positions | extra_positions)
    spans = person_spans(combined)

    shares: dict[str, float] = {}
    breakdown: dict[str, list[str]] = defaultdict(list)
    for span in spans:
        label = span["label"]
        if label.lower() in shares:
            # repeated mentions by the same person: extend the window
            continue
        window_amounts = [a for a in all_amounts
                          if span["start"] < a["position"] < span["end"]
                          and not _window_includes_extra(combined, a["position"],
                                                         extra_positions)]
        if not window_amounts:
            continue
        numbered = round(sum(a["value"] for a in window_amounts), 2)
        if numbered <= 0:
            continue
        shares[label.lower()] = numbered
        detail = ", ".join(f"{a['value']:,.2f}" for a in window_amounts)
        breakdown[label.lower()].append(f"Items: {detail}")

    # ---- bill base -------------------------------------------------------
    item_total = round(sum(shares.values()), 2)
    flat_extras = [e for e in extras if "amount" in e]
    pct_extras = [e for e in extras if "percent" in e]
    flat_total = round(sum(e["amount"] for e in flat_extras), 2)

    itemized = item_total > 0
    open_amounts = [a for a in all_amounts
                    if a["position"] not in extra_positions
                    and a["position"] not in total_positions
                    and a["position"] not in surcharge_positions]

    if itemized:
        stated = max((v for v, _ in totals), default=None)
        if stated is not None and abs((stated - item_total)) > 0.5:
            notices.append(f"Stated total {result['symbol']}{stated:,.2f} "
                           f"differs from the itemized sum "
                           f"{result['symbol']}{item_total + flat_total:,.2f}; "
                           "itemized values were used.")
        unassigned = [a for a in open_amounts
                      if not any(span["start"] < a["position"] < span["end"]
                                 for span in spans)]
        if unassigned:
            detail = ", ".join(f"{a['value']:,.2f}" for a in unassigned)
            notices.append(f"Amount {detail} was mentioned outside the "
                           "itemized entries and was not double-counted.")
        base = round(item_total + flat_total, 2)
    elif open_amounts:
        base = round(sum(a["value"] for a in open_amounts) + flat_total, 2)
    elif totals:
        base = round(max(v for v, _ in totals) + flat_total, 2)
    else:
        result["fail_reason"] = (
            "No bill total or per-person share could be read. Phrase an "
            "amount, for example \u201ctotal was $70\u201d, or add item amounts.")
        return result

    # ---- percent extras applied to base -----------------------------------
    pct_amount = 0.0
    for extra in pct_extras:
        if extra["label"] == "discount":
            pct_amount = round(pct_amount - base * extra["percent"] / 100, 2)
        else:
            pct_amount = round(pct_amount + base * extra["percent"] / 100, 2)
        notices.append(f"{extra['label'].capitalize()} of "
                       f"{extra['percent']:.4g}% applied.")
    if pct_amount:
        base = round(base + pct_amount, 2)
        notices.append(f"Percentage extras total {result['symbol']}{pct_amount:,.2f}.")
    flat_total = round(flat_total + pct_amount, 2)
    result["bill_total"] = base

    # ---- participants -----------------------------------------------------
    weights = pct_weights(combined)
    placeholder_names = False

    # Union: people with itemized shares plus everyone named in the text.
    names = list(shares.keys())
    known_lower = {name.lower() for name in names}
    for name in roster:
        if name.lower() not in known_lower:
            names.append(name)
            known_lower.add(name.lower())

    count = head_count(combined)
    if not names:
        if not count or count <= 0:
            result["fail_reason"] = (
                "Couldn't tell who is sharing this bill. Write names "
                "(e.g. \u201camong Alice, Bob and Carol\u201d) or a head-count.")
            return result
        names = [f"Person {i + 1}" for i in range(count)]
        placeholder_names = True
    elif count and count > len(names):
        for i in range(len(names), count):
            names.append(f"Person {i + 1}")
        placeholder_names = True

    entries = []
    if weights and len(names) == 2 and not itemized:
        w1, w2 = weights
        total_w = w1 + w2
        split_base = round(base - surcharge_total, 2)
        first = round(split_base * w1 / total_w, 2)
        second = round(split_base - first, 2)
        shares = {names[0].lower(): first, names[1].lower(): second}
        breakdown[names[0].lower()] = [f"Weighted split \u2014 {w1}% of the bill"]
        breakdown[names[1].lower()] = [f"Weighted split \u2014 {w2}% of the bill"]
        notices.append(f"Weighted split {w1}/{w2} applied.")
    elif itemized or pct_amount or flat_total or not weights:
        equal_total = base if not shares else round(
            base - round(sum(shares.values()), 2) - surcharge_total, 2)
        if not shares:
            equal_total = round(equal_total - surcharge_total, 2)
        if names and (not shares or equal_total > 0.004):
            parts = equal_split(equal_total, len(names))
            for name, share in zip(names, parts):
                shares[name.lower()] = round(shares.get(name.lower(), 0.0) + share, 2)
                breakdown.setdefault(name.lower(), []).append(
                    "Equal share of the shared bill" if not itemized
                    else f"Equal share of unassigned amount: {share:,.2f}")
            if not itemized and len(names) > 1:
                # clear the duplicate "equal share" wording for equal-only splits
                for name in names:
                    breakdown[name.lower()] = ["Equal split of the shared bill"]
    for name in names:
        display = name.title() if not name.isupper() else name
        entries.append({
            "name": display,
            "share": round(shares.get(name.lower(), 0.0), 2),
            "breakdown": breakdown.get(name.lower())
                         or ["Share of the bill"],
            "payer": False,
        })
    if placeholder_names:
        notices.append(
            "Head-count based placeholders (Person 1..N) were used for "
            "participants without stated names.")

    # ---- per-person surcharges -------------------------------------------
    for name, surcharge in individual_surcharge.items():
        label_key = name.lower()
        entry = next((e for e in entries if e["name"].lower() == label_key), None)
        if entry and surcharge > 0:
            entry["share"] = round(entry["share"] + surcharge, 2)
            entry["breakdown"].append(f"Surcharge applied: {surcharge:,.2f}")

    result["entries"] = entries
    result["payers"] = payers
    payers_lower = {payer.lower() for payer in payers}
    for entry in entries:
        entry["payer"] = entry["name"].lower() in payers_lower

    shares_total = round(sum(e["share"] for e in entries), 2)
    result["shares_total"] = shares_total
    if abs(shares_total - result["bill_total"]) > 0.01:
        notices.append(
            f"Allocated {result['symbol']}{shares_total:,.2f} against a bill "
            f"of {result['symbol']}{result['bill_total']:,.2f}.")

    if not shares and not entries:
        result["fail_reason"] = "Nothing could be parsed from the bill."
        return result

    result["covered"] = payer_coverage(combined, payers, result["bill_total"])
    for entry in entries:
        entry["paid_amount"] = result["covered"].get(entry["name"].lower())
    result["transfers"] = compute_transfers(entries)

    if not payers:
        notices.append("No payer was named, so no transfer plan was produced "
                       "\u2014 shares only.")
    result["ok"] = True
    return result


def surcharges(text: str, roster: list[str]) -> tuple[dict[str, float], set[int]]:
    """"X pays 2,000 extra" style per-person surcharges.

    Returns ({name_lower: total}, positions) — positions are needed so the
    surcharge money is not double-counted inside the bill base.
    """
    out: dict[str, float] = {}
    positions: set[int] = set()
    lowered_roster = [(name, name.lower()) for name in roster]
    seen_positions: set[int] = set()
    # "$2,000 extra" (with symbol) and "2000 extra" (bare) forms
    patterns = [
        rf"[$\u20b9\u20ac\u00a3]\s?({AMOUNT_TOKEN})\s+extra\b",
        rf"\b({AMOUNT_TOKEN})\s+extra\b",
    ]
    for pattern in patterns:
        for m in re.finditer(pattern, text, flags=re.IGNORECASE):
            value = _num(m.group(1))
            position = m.start(1)
            if value <= 0 or position in seen_positions:
                continue
            seen_positions.add(position)
            window = text[max(0, m.start() - 90):m.start()].lower()
            nearest, distance = None, 10**9
            for name, lowered in lowered_roster:
                idx = window.rfind(lowered)
                if idx >= 0 and idx < distance:
                    distance, nearest = idx, name
            if nearest is None:
                continue
            out[nearest.lower()] = round(out.get(nearest.lower(), 0.0) + value, 2)
            positions.add(position)
    return {key: value for key, value in out.items() if value > 0}, positions


def payer_coverage(text: str, payers: list[str], bill_total: float | None) -> dict[str, float]:
    """How much each recorded payer has already covered, when stated."""
    if not payers or bill_total is None or bill_total <= 0:
        return {}
    covered: dict[str, float] = {}
    sentences = sentences_with_spans(text)
    positional = amounts_in(text, {pos for _, pos in stated_totals(text)})

    def sentence_end_for(start: int) -> int:
        return next((end for (_, s, end) in sentences if s <= start < end),
                    len(text))

    for payer in payers:
        pattern = rf"\b{re.escape(payer)}\b[^.;]{{0,40}}?"
        for m in re.finditer(rf"{pattern}(?:has\s+|have\s+)?paid\b", text, re.I):
            end = sentence_end_for(m.start())
            within = [a for a in positional if m.end() < a["position"] < end]
            if within:
                covered[payer.lower()] = round(
                    covered.get(payer.lower(), 0.0)
                    + sum(a["value"] for a in within), 2)

    for payer in payers:
        # "Tickets were $120, paid by Priya" — amount surfaces before the verb.
        lowered = payer.lower()
        pattern = rf"(?i)[$\u20b9\u20ac\u00a3]\s?({AMOUNT_TOKEN})[^\n]{{0,40}}?"
        pattern += rf"\bpaid\s+by\s+{re.escape(payer)}\b"
        for m in re.finditer(pattern, text, flags=re.I):
            value = _num(m.group(1))
            if value <= 0:
                continue
            covered[lowered] = round(covered.get(lowered, 0.0) + value, 2)

    if len(payers) == 1 and payers[0].lower() not in covered:
        # Single named payer with no explicit amount: the natural reading is
        # that this person fronted the whole bill ("paid everything/ upfront").
        payer_match = re.search(
            rf"(?i)\b{re.escape(payers[0])}\b[^.;]{{0,60}}?"
            r"\b(?:everything|upfront|full|whole|entire|all)\b", text)
        generic_match = re.search(
            r"(?i)\b(?:everything|upfront|entire|whole bill|full bill)\b", text)
        if payer_match or generic_match:
            covered[payers[0].lower()] = round(bill_total, 2)
    return covered


def compute_transfers(entries: list[dict]) -> list[dict]:
    """Greedy min-cash-flow: debtor pays creditor, smallest number of steps."""
    balance: dict[str, float] = defaultdict(float)
    for entry in entries:
        covered = entry.get("paid_amount") or 0.0
        balance[entry["name"]] = round(covered - entry["share"], 2)
    debtors = sorted([(n, b) for n, b in balance.items() if b < -0.004],
                     key=lambda x: x[1])
    creditors = sorted([(n, b) for n, b in balance.items() if b > 0.004],
                       key=lambda x: -x[1])
    transfers: list[dict] = []
    di = ci = 0
    while di < len(debtors) and ci < len(creditors):
        debtor, debit = debtors[di]
        creditor, credit = creditors[ci]
        amount = round(min(-debit, credit), 2)
        if amount > 0.004:
            transfers.append({"from": debtor.title(), "to": creditor.title(),
                              "amount": amount})
        debit = round(debit + amount, 2)
        credit = round(credit - amount, 2)
        if abs(debit) < 0.005:
            di += 1
        else:
            debtors[di] = (debtor, debit)
        if credit < 0.005:
            ci += 1
        else:
            creditors[ci] = (creditor, credit)
    return transfers
