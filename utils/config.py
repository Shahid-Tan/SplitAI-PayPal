"""Configuration and credential resolution for SplitAI.

Credentials are read from st.secrets or environment variables / a local .env
file. Secrets are never hard-coded, logged, or written back anywhere.
"""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# A local .env next to the repo root is a convenience for local runs only.
load_dotenv(PROJECT_ROOT / ".env")

DEFAULT_PAYPAL_ME_HANDLE = "syedshahidafridi"

CURRENCIES = {
    "USD": "$",
    "EUR": "\u20ac",
    "GBP": "\u00a3",
    "INR": "\u20b9",
    "CAD": "CA$",
    "AUD": "A$",
    "SGD": "S$",
}


def _secret(*path: str):
    """Look up a value in st.secrets across a few plausible layouts.

    Accepts nested tables (e.g. [paypal] client_id = ...) and flat keys
    (paypal_client_id = ...). Returns None when secrets are not configured at
    all instead of raising, so the app degrades gracefully.
    """
    try:
        node = st.secrets
    except Exception:
        return None
    try:
        value = node
        for key in path:
            value = value[key]
        text = str(value)
        return text if text else None
    except Exception:
        return None


def gemini_api_key() -> str | None:
    """Gemini key: st.secrets first, then environment (and .env)."""
    for key_path in (("gemini", "GEMINI_API_KEY"), ("gemini", "api_key"),
                     ("gemini_api_key",), ("GOOGLE_API_KEY",)):
        value = _secret(*key_path)
        if value:
            return value
    env_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    return env_key if env_key else None


def _paypal_pair() -> tuple[str, str] | None:
    client_id = (_secret("paypal", "client_id") or _secret("paypal_client_id")
                 or os.environ.get("PAYPAL_CLIENT_ID") or "")
    client_secret = (_secret("paypal", "client_secret")
                     or _secret("paypal_client_secret")
                     or os.environ.get("PAYPAL_CLIENT_SECRET") or "")
    client_id = client_id.strip().strip('"').strip("'")
    client_secret = client_secret.strip().strip('"').strip("'")
    if client_id and client_secret:
        return client_id, client_secret
    return None


def paypal_credentials() -> tuple[str, str] | None:
    """PayPal REST (client_id, client_secret) for the sandbox, or None."""
    return _paypal_pair()


def payee_email() -> str | None:
    """Optional payee email attached to created orders (mostly for clarity)."""
    return (_secret("paypal", "payee_email") or _secret("paypal_payee_email")
            or os.environ.get("PAYPAL_PAYEE_EMAIL") or None)


def paypal_me_handle() -> str:
    raw = (_secret("paypal", "me_handle") or _secret("paypal_me_handle")
           or os.environ.get("PAYPAL_ME_HANDLE") or DEFAULT_PAYPAL_ME_HANDLE)
    cleaned = raw.strip().lstrip("@").replace(" ", "")
    return cleaned or DEFAULT_PAYPAL_ME_HANDLE


def app_base_url() -> str:
    """Public base URL used for PayPal return redirects.

    Order: explicit env override, then the URL the user is currently browsing,
    then a localhost default for local sandbox runs.
    """
    explicit = os.environ.get("APP_BASE_URL")
    if explicit:
        return explicit.rstrip("/")
    try:
        url = getattr(st.context, "url", None)
    except Exception:
        url = None
    if url:
        url = str(url).split("?")[0].rstrip("/")
        if "localhost" not in url and "127.0.0.1" not in url:
            return url
    return "http://localhost:8501"


def money(amount: float, symbol: str) -> str:
    """Format 1000 -> $1,000.00 using the display symbol."""
    return f"{symbol}{amount:,.2f}"
