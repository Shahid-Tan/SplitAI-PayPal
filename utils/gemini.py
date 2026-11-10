"""Gemini (google-genai SDK, the maintained successor of google-generativeai).

Strategy:
- rotate through plausible, free-tier flash models (3 tries total);
- ask for strict JSON and parse it into the same schema the deterministic
  parser produces, so downstream UI code is identical for both engines;
- if Gemini answers but returns unparseable text, surface the raw text
  honestly instead of inventing structured data.

Pure logic (no st.* calls) so it stays testable and importable anywhere.
"""

from __future__ import annotations

import json
import re

MODELS = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash"]

PROMPT = """You are a rigorous expense-splitting engine. Read the bill and
produce EXACTLY this JSON shape (no markdown, no commentary):

{{
  "people": [{{"name": "...", "share": 0.00, "breakdown": "...", "payer": false}}],
  "transfers": [{{"from": "...", "to": "...", "amount": 0.00}}],
  "currency": "USD",
  "notes": ["..."]
}}

Rules:
- "people" = how much each person OWES for this bill (their share).
- "payer" true only for people who ALREADY paid the bill upfront.
- "transfers" = minimum payments from debtors to payers that settle all debts.
- Only use names that appear in the bill text; use "You" for the writer
  speaking in first person; never invent people.
- Keep the arithmetic exact to the cent. Taxes/tips/discounts applied as the
  bill text implies, and mention the logic in "notes".
- Currency is whatever the bill uses (e.g. USD, INR).

Bill:
\"\"\"{bill}\"\"\"

User instructions (may be empty):
\"\"\"{instructions}\"\"\"
"""


def _client(api_key: str):
    from google import genai
    return genai.Client(api_key=api_key)


def _extract_json(text: str) -> dict | None:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?|```$", "", text, flags=re.MULTILINE).strip()
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end <= start:
        return None
    try:
        return json.loads(text[start:end + 1])
    except json.JSONDecodeError:
        return None


def _normalize(payload: dict, bill_text: str) -> dict | None:
    """Validate/clean Gemini JSON into the internal schema."""
    people = payload.get("people")
    if not isinstance(people, list) or not people:
        return None
    entries = []
    for person in people[:30]:
        name = str(person.get("name", "")).strip()
        try:
            share = round(float(person.get("share", 0.0)), 2)
        except (TypeError, ValueError):
            share = 0.0
        if not name:
            continue
        entries.append({
            "name": name,
            "share": max(share, 0.0),
            "breakdown": [str(person.get("breakdown", "Share of the bill"))],
            "payer": bool(person.get("payer")),
        })
    if not entries:
        return None

    from utils.parsing import compute_transfers
    for entry in entries:
        entry["paid_amount"] = None
    transfers = payload.get("transfers")
    if not isinstance(transfers, list) or not transfers:
        transfers = compute_transfers(entries)
    cleaned_transfers = []
    for transfer in transfers[:30]:
        try:
            amount = round(float(transfer.get("amount", 0.0)), 2)
        except (TypeError, ValueError):
            continue
        sender = str(transfer.get("from", "")).strip()
        receiver = str(transfer.get("to", "")).strip()
        if sender and receiver and amount > 0:
            cleaned_transfers.append({"from": sender, "to": receiver,
                                      "amount": amount})

    currency_raw = str(payload.get("currency", "USD")).strip().upper()
    notes = [str(note) for note in payload.get("notes", [])[:8]
             if str(note).strip()]
    return {
        "ok": True,
        "mode": "ai",
        "entries": entries,
        "transfers": cleaned_transfers,
        "currency": currency_raw,
        "bill_total": round(sum(entry["share"] for entry in entries), 2),
        "shares_total": round(sum(entry["share"] for entry in entries), 2),
        "notices": notes,
        "covered": {},
        "payer_names_used": [entry["name"] for entry in entries if entry["payer"]],
    }


def split_with_gemini(api_key: str, bill: str, instructions: str = ""
                      ) -> dict:
    """Try each model; returns {kind:"json", result, model:{ok,failed}} or
    {kind:"raw", text, model} or {kind:"failed", errors}."""
    client = _client(api_key)
    prompt = PROMPT.format(bill=bill[:4000],
                           instructions=(instructions or "none")[:1000])
    errors, tried, raw_text, raw_model = {}, [], None, None

    for model in MODELS:
        try:
            response = client.models.generate_content(
                model=model,
                contents=prompt,
                config={"response_mime_type": "application/json",
                        "temperature": 0.1},
            )
            text = (response.text or "").strip()
            if not text:
                errors[model] = "empty response"
                tried.append(model)
                continue
            payload = _extract_json(text)
            result = _normalize(payload, bill) if payload else None
            if result:
                result["ai_model"] = model
                return {"kind": "json", "result": result, "model": model,
                        "tried": tried + [model]}
            if raw_text is None:
                raw_text, raw_model = text, model
            errors[model] = "response was not valid JSON"
        except Exception as exc:  # noqa: BLE001 — model/ quota errors vary
            message = str(exc)
            errors[model] = message[:160]
        finally:
            tried.append(model)

    if raw_text:
        return {"kind": "raw", "text": raw_text, "model": raw_model,
                "tried": tried}
    return {"kind": "failed", "errors": errors, "tried": tried}


def probe_models(api_key: str) -> dict[str, bool]:
    """ONE quick validation generation per configured model on first use."""
    client = _client(api_key)
    status: dict[str, bool] = {}
    for model in MODELS:
        try:
            response = client.models.generate_content(
                model=model,
                contents="Say OK",
                config={"max_output_tokens": 8},
            )
            status[model] = bool(response.text)
        except Exception:  # noqa: BLE001
            status[model] = False
    return status
