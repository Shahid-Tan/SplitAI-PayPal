"""PayPal Orders v2 integration (sandbox) using plain `requests`.

Flow used by the app:
1. client-credentials OAuth token (cached ~50 minutes)
2. POST /v2/checkout/orders  -> approve link for the payer
3. payer approves in the browser; PayPal redirects back with ?token=
4. POST /v2/checkout/orders/{id}/capture -> COMPLETED

Everything degrades gracefully: without credentials the UI switches to
PayPal.me deep links instead (see paypal_me_url).
Secrets are never logged, printed, or embedded in URLs shown to users.
"""

from __future__ import annotations

import re
import uuid

import requests
import streamlit as st

from utils.config import app_base_url, payee_email

API_BASE = "http://api-m.sandbox.paypal.com"  # overridden by env below
OAUTH_PATH = "/v1/oauth2/token"
ORDERS_PATH = "/v2/checkout/orders"


class PayPalError(RuntimeError):
    """Human-safe PayPal failure (never includes credentials/tokens)."""


def api_base() -> str:
    import os

    return os.environ.get("PAYPAL_API_BASE", "https://api-m.sandbox.paypal.com").rstrip("/")


@st.cache_data(ttl=3300, max_entries=8, show_spinner=False)
def oauth_token(client_id: str, client_secret: str) -> str:
    """Fetch (and cache) a client-credentials access token."""
    try:
        response = requests.post(
            api_base() + OAUTH_PATH,
            auth=(client_id, client_secret),
            data={"grant_type": "client_credentials"},
            timeout=20,
        )
    except requests.RequestException as exc:
        raise PayPalError("Could not reach PayPal (network error). "
                          "Check your connection and try again.") from exc
    if response.status_code != 200:
        raise PayPalError("PayPal rejected the API credentials. Check the "
                          "client id / secret in your environment setup.")
    token = response.json().get("access_token")
    if not token:
        raise PayPalError("PayPal did not return an access token.")
    return token


def _headers(token: str) -> dict:
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "PayPal-Partner-Attribution-Id": "SplitAI_Hackathon_PCP",
    }


def create_order(token: str, amount: float, currency: str,
                 description: str, reference_id: str) -> dict:
    """Create an Orders v2 order and return {id, approve_url, request_id}."""
    base = app_base_url()
    request_id = str(uuid.uuid4())
    unit: dict = {
        "reference_id": reference_id[:127],
        "description": description[:127],
        "amount": {"currency_code": currency,
                   "value": f"{amount:.2f}"},
    }
    payee = payee_email()
    if payee:
        unit["payee"] = {"email_address": payee}
    payload = {
        "intent": "CAPTURE",
        "purchase_units": [unit],
        "application_context": {
            "brand_name": "SplitAI",
            "locale": "en-US",
            "shipping_preference": "NO_SHIPPING",
            "user_action": "PAY_NOW",
            "return_url": base + "/",
            "cancel_url": base + "/?cancel=1",
        },
    }
    try:
        response = requests.post(
            api_base() + ORDERS_PATH,
            headers=_headers(token),
            json=payload,
            timeout=20,
        )
    except requests.RequestException as exc:
        raise PayPalError("Could not reach PayPal while creating the order.") from exc
    body = response.json() if response.content else {}
    if response.status_code not in (200, 201):
        detail = _sanitized_issue(body)
        raise PayPalError(detail or "PayPal rejected the order request.")
    approve_url = next((link["href"] for link in body.get("links", [])
                        if link.get("rel") == "approve"), None)
    if not approve_url:
        raise PayPalError("PayPal returned an order without an approve link.")
    return {"id": body.get("id"), "approve_url": approve_url,
            "request_id": request_id}


def capture_order(token: str, order_id: str) -> dict:
    """Capture an approved order. Returns {status, capture_id, payer}."""
    headers = _headers(token)
    headers["PayPal-Request-Id"] = str(uuid.uuid4())
    headers["Prefer"] = "return=minimal"
    try:
        response = requests.post(
            f"{api_base()}{ORDERS_PATH}/{order_id}/capture",
            headers=headers,
            timeout=25,
        )
    except requests.RequestException as exc:
        raise PayPalError("Could not reach PayPal while capturing the order.") from exc

    body = response.json() if response.content else {}
    status = body.get("status")
    if status == "COMPLETED":
        capture = _first_capture(body)
        return {"status": "COMPLETED",
                "capture_id": (capture or {}).get("id"),
                "payer": body.get("payer", {}).get("email_address")}
    issue = _sanitized_issue(body)
    if issue and "ALREADY_CAPTURED" in issue.upper():
        # Idempotent path: someone already captured; fetch final state.
        return _order_state(token, order_id)
    raise PayPalError(issue or f"Capture failed (HTTP {response.status_code}).")


def _order_state(token: str, order_id: str) -> dict:
    try:
        response = requests.get(
            f"{api_base()}{ORDERS_PATH}/{order_id}",
            headers=_headers(token), timeout=20)
    except requests.RequestException as exc:
        raise PayPalError("Could not reach PayPal to verify the order.") from exc
    body = response.json() if response.content else {}
    capture = _first_capture(body)
    return {"status": body.get("status") or "UNKNOWN",
            "capture_id": (capture or {}).get("id"),
            "payer": body.get("payer", {}).get("email_address")}


def _first_capture(body: dict) -> dict | None:
    for unit in body.get("purchase_units") or []:
        for capture in (unit.get("payments") or {}).get("captures") or []:
            return capture
    return None


def _sanitized_issue(body: dict) -> str | None:
    """Extract a user-safe issue message; never echoes tokens/ids/secrets."""
    details = body.get("details") or []
    for detail in details:
        issue = detail.get("issue")
        if issue:
            return "PayPal: " + issue.replace("_", " ").title()
    message = body.get("message")
    if message:
        cleaned = re.sub(r"(?i)(token|secret|access)[^\s]*", "…", str(message))
        return cleaned[:200]
    return None


def paypal_me_url(handle: str, amount: float, currency: str) -> str:
    """Per-person PayPal.me deep link with the amount pre-filled."""
    return f"https://www.paypal.com/paypalme/{handle}/{amount:.2f}{currency}"
