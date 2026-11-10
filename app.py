"""SplitAI — AI bill splitting with instant PayPal settlement.

Layout follows Streamlit ≥1.57 patterns:
- theme lives in .streamlit/config.toml (PayPal navy/gold palette)
- business logic lives in utils/ (parsing, gemini, paypal, config)
- the deterministic fallback parser keeps results honest without a key
"""

from __future__ import annotations

import datetime as _dt

import pandas as pd
import streamlit as st

import utils.parsing as parsing
from utils.config import (CURRENCIES, gemini_api_key, money,
                          paypal_credentials, paypal_me_handle)
from utils.gemini import split_with_gemini
from utils.paypal import (PayPalError, capture_order, create_order,
                          oauth_token, paypal_me_url)

# ------------------------------------------------------------------ setup
st.set_page_config(
    page_title="SplitAI · AI bill splitting, instant PayPal settlement",
    page_icon=":material/receipt_long:",
    layout="centered",
)

st.html(
    """<style>
    .st-key-hero {background: linear-gradient(135deg,#003087 0%,#0070ba 62%,
                  #009cde 100%); border-radius: 16px;
                  box-shadow: 0 10px 30px rgba(0,48,135,.18);}
    .st-key-hero h1 {color:#ffffff !important; margin-bottom: 0 !important;}
    .st-key-hero [data-testid="stCaptionContainer"] p {color:#cfe3ff !important;}
    [class*="st-key-paybtn"] button {background:
        linear-gradient(180deg,#ffc439,#f0a92f) !important; color:#003087
        !important; border:1px solid #e0a31b; font-weight:700;}
    [class*="st-key-paybtn"] button:hover {background:
        linear-gradient(180deg,#ffd45e,#f6b527) !important;}
    </style>"""
)

output_slot = st.container()  # reserve the results slot before slow work

# --- state (single init place, per Streamlit best practice) --------------
st.session_state.setdefault("bill_text", "")
st.session_state.setdefault("instructions_text", "")
st.session_state.setdefault("result", None)
st.session_state.setdefault("result_meta", None)
st.session_state.setdefault("history", [])
st.session_state.setdefault("ai_probe_done_key", None)
st.session_state.setdefault("ai_probe", None)
st.session_state.setdefault("raw_ai_text", None)
st.session_state.setdefault("orders", {})          # transfer_id -> order dict

# --- credentials / providers ---------------------------------------------
gemini_env_key = gemini_api_key()
if not gemini_env_key:
    manual_key = st.sidebar.text_input(
        "Gemini API key", type="password", key="manual_gemini_key",
        help="Optional. For production keep it in .env or secrets.toml, "
             "never in code.")
else:
    manual_key = None
running_key = gemini_env_key or (manual_key or "").strip() or None

sandbox_creds = paypal_credentials()
handle_base = paypal_me_handle()

with st.sidebar:
    st.subheader("Settings", icon=":material/tune:")
    handle_value = st.text_input(
        "PayPal.Me handle", value=handle_base, key="me_handle",
        help="Fallback link target when sandbox credentials are absent.")
    handle = handle_value.strip().lstrip("@").replace(" ", "") or handle_base
    st.caption("Credentials come from `.env` or `.streamlit/secrets.toml` "
               "— never from code.")

    key_ok = running_key is not None
    st.badge("Gemini connected" if key_ok else "Deterministic parser",
             icon=":material/bolt:" if key_ok else ":material/rule:",
             color="green" if key_ok else "orange")
    if sandbox_creds:
        st.badge("PayPal Orders sandbox on", icon=":material/sync:",
                 color="blue")
    else:
        st.badge("Sandbox off · PayPal.me links", icon=":material/link:",
                 color="gray")

    # ONE validation generation per key; results cached in session state.
    if running_key and st.session_state["ai_probe_done_key"] != \
            (running_key[:8] if running_key else None):
        try:
            from utils.gemini import probe_models
            st.session_state["ai_probe"] = probe_models(running_key)
        except Exception as exc:  # noqa: BLE001 — never break the app here
            st.session_state["ai_probe"] = {"error": str(exc)[:120]}
        st.session_state["ai_probe_done_key"] = running_key[:8]
    probe = st.session_state["ai_probe"] or {}
    if running_key and "error" in probe:
        st.caption(f"Gemini check skipped ({probe['error'][:80]}).")
    elif running_key and probe:
        working = [model for model, ok in probe.items() if ok]
        st.caption(("Responsive model(s): " + ", ".join(working)) if working
                   else "No Gemini model answered — parser covers you.")

    st.divider()
    st.caption("**Ask SplitAI for**")
    st.markdown("- itemized dinner with an equal tip\n"
                "- rent with a private-room surcharge\n"
                "- road trip where one friend fronts everything\n"
                "- weighted splits like 60/40")


def _restore_history(bill: str, instructions: str) -> None:
    # callbacks run before widgets exist on the next rerun — safe to assign
    st.session_state["bill_text"] = bill
    st.session_state["instructions_text"] = instructions


# ---------------------------------------------------------------- hero
with st.container(key="hero"):
    st.title("SplitAI", icon=":material/receipt_long:")
    st.caption("Paste any bill in plain words. Get exact shares. Settle "
               "with PayPal — AI when you have it, honest math when you don't.")

# ---------------------------------------------------------------- presets
st.caption("Load a sample to see the full pipeline:")
presets = st.container(horizontal=True)
with presets:
    if st.button("Pizza dinner", icon=":material/local_pizza:",
                 key="preset_pizza"):
        st.session_state["bill_text"] = (
            "Dinner bill: $54. Rahul ordered pasta for $22, Sneha ordered "
            "pizza for $18, and I had salad for $14. Add $6 service tax "
            "split equally.")
        st.session_state["instructions_text"] = ""
    if st.button("Flat rent \u00b7 INR", icon=":material/apartment:",
                 key="preset_rent"):
        st.session_state["bill_text"] = (
            "Monthly 3BHK flat expenses in Bangalore: Total rent \u20b924,000, "
            "WiFi \u20b91,000, Electricity \u20b92,000. Shahid has master "
            "bedroom with AC so he pays \u20b92,000 extra on rent. Split "
            "rest equally among Shahid, Kabir, and Zaid.")
        st.session_state["instructions_text"] = ""
    if st.button("Road trip", icon=":material/directions_car:",
                 key="preset_trip"):
        st.session_state["bill_text"] = (
            "Road trip fuel was $90. Car snacks were $30. 4 friends: Shahid, "
            "Alex, John, David. Shahid paid upfront for everything.")
        st.session_state["instructions_text"] = "Show who owes Shahid."
    if st.button("Weighted split", icon=":material/percent:",
                 key="preset_weight"):
        st.session_state["bill_text"] = (
            "Our streaming subscriptions and shared utilities for October "
            "came to $240 all in. Ramon and Izzie are splitting as "
            "housemates.")
        st.session_state["instructions_text"] = "Split 60/40, Ramon pays 60."

# ---------------------------------------------------------------- inputs
with st.form("split_form"):
    st.text_area(
        "The bill \u2014 paste a receipt, chat message, or notes",
        key="bill_text",
        height=140,
        placeholder='Dinner total $70 - Alice had steak ($35), Bob had '
                    'burger ($20). Split a $10 tip equally',
    )
    st.text_input(
        "Special instructions (optional)", key="instructions_text",
        placeholder="e.g. split 60/40, add 10% tip, show who owes whom",
    )
    submitted = st.form_submit_button(
        "Calculate split", type="primary", icon=":material/calculate:",
        width="stretch")


# --- calculation ---------------------------------------------------------
def _push_history() -> None:
    meta = st.session_state.get("result_meta")
    result = st.session_state.get("result")
    if not meta or not result or not result.get("ok"):
        return
    st.session_state["history"].insert(0, {
        "ts": meta["ts"], "engine": meta["engine"], "model": meta.get("model"),
        "currency": result.get("currency"), "symbol": result.get("symbol"),
        "total": result.get("bill_total"),
        "people": len(result.get("entries", [])),
        "bill": meta["bill"][:240],
    })
    del st.session_state["history"][6:]


def _run_split() -> None:
    bill = (st.session_state.get("bill_text") or "").strip()
    instructions = (st.session_state.get("instructions_text") or "").strip()
    st.session_state["raw_ai_text"] = None
    if not bill:
        st.warning("Add some bill details first.",
                   icon=":material/edit_note:")
        return
    result, engine, model_name = None, "det", None
    if running_key:
        with st.spinner("Gemini is reading the bill\u2026"):
            try:
                response = split_with_gemini(running_key, bill, instructions)
            except Exception as exc:  # noqa: BLE001
                response = {"kind": "failed",
                            "errors": {"gemini": str(exc)[:160]}}
        if response["kind"] == "json":
            result, engine, model_name = (response["result"], "ai",
                                          response["model"])
        elif response["kind"] == "raw":
            engine, model_name = "ai-raw", response["model"]
            st.session_state["raw_ai_text"] = response["text"]
        else:
            engine = "ai-failed"
    if result is None:
        result = parsing.parse_bill(bill, instructions)
    st.session_state["result"] = result
    st.session_state["result_meta"] = {
        "engine": engine, "model": model_name, "bill": bill,
        "instructions": instructions,
        "ts": _dt.datetime.now().strftime("%H:%M:%S"),
    }
    _push_history()


if submitted:
    _run_split()


# --- PayPal redirect handling -------------------------------------------
query = st.query_params
try:
    if "cancel" in query:
        st.warning("PayPal checkout was cancelled \u2014 nothing charged.",
                   icon=":material/money_off:")
        st.query_params.clear()
    elif "token" in query:
        order_id = str(query["token"])
        payer_id = query.get("PayerID")
        if payer_id and sandbox_creds:
            token_str = oauth_token(sandbox_creds[0], sandbox_creds[1])
            capture = capture_order(token_str, order_id)
            if capture["status"] == "COMPLETED":
                st.success(
                    "Payment captured. Order approved"
                    + (f" \u00b7 capture id {capture['capture_id']}"
                       if capture.get("capture_id") else ""),)
            else:
                st.info(f"Order status: {capture['status']} \u2014 finish "
                        "the payment to settle.", icon=":material/pending:")
        elif payer_id:
            st.info("PayPal approval received, but sandbox credentials are "
                    "not configured on this deployment \u2014 capture skipped.",
                    icon=":material/info:")
        else:
            st.info("PayPal sent you back before approving. Nothing charged.",
                    icon=":material/info:")
        st.query_params.clear()
except PayPalError as exc:
    st.error(str(exc), icon=":material/error:")
except Exception as exc:  # noqa: BLE001 — capture must never crash the app
    st.error(f"Unexpected capture failure: {str(exc)[:150]}",
             icon=":material/error:")


# --- rendering helpers ----------------------------------------------------
def _engine_badge() -> None:
    meta = st.session_state.get("result_meta") or {}
    engine = meta.get("engine")
    if engine == "ai":
        st.badge(f"Gemini \u00b7 {meta.get('model')}", color="green",
                 icon=":material/auto_awesome:")
    elif engine == "ai-raw":
        st.badge("Gemini \u00b7 raw text (JSON unavailable)", color="orange",
                 icon=":material/auto_awesome:")
    elif engine == "ai-failed":
        st.badge("Gemini unreachable \u00b7 parser used", color="orange",
                 icon=":material/cloud_off:")
    else:
        st.badge("Deterministic parser mode (no AI key)", color="gray",
                 icon=":material/calculate:")


def _currency_of(result: dict) -> tuple[str, str]:
    currency = (result.get("currency") or "USD").upper()
    symbol = result.get("symbol") or CURRENCIES.get(currency, currency)
    return currency, str(symbol or currency)


def _render_table(result: dict, symbol: str) -> None:
    frame = pd.DataFrame([{
        "Person": entry["name"],
        "Share": round(float(entry["share"]), 2),
        "Paid up front": "Yes" if entry.get("payer") else "",
        "Breakdown": " \u00b7 ".join(entry.get("breakdown", []))[:180],
    } for entry in result["entries"]])
    st.dataframe(
        frame,
        column_config={
            "Person": st.column_config.TextColumn("Person"),
            "Share": st.column_config.NumberColumn(format=f"{symbol}%.2f"),
            "Paid up front": st.column_config.TextColumn("Paid up front"),
            "Breakdown": st.column_config.TextColumn("Breakdown",
                                                     width="large"),
        },
        hide_index=True,
        alt="Per-person share table",
        key="share_table",
    )


def _render_person_cards(result: dict, symbol: str) -> None:
    st.subheader("Per person", icon=":material/account_balance_wallet:")
    entries = result["entries"]
    currency = (result.get("currency") or "USD").upper()
    for index, entry in enumerate(entries):
        with st.container(border=True, key=f"person_{index}"):
            head = st.columns([2.4, 1.6])
            with head[0]:
                st.markdown(f"**{entry['name']}**")
                st.caption(" \u00b7 ".join(entry.get("breakdown", [])
                                           or ["Share of the bill"]))
            with head[1]:
                if entry.get("payer"):
                    st.badge("Paid up front", color="green",
                             icon=":material/verified:")
                else:
                    st.badge("Owes", color="gray", icon=":material/schedule:")
                st.markdown(f"### {symbol}{entry['share']:,.2f}")
            st.code(paypal_me_url(handle, float(entry["share"]), currency),
                    language=None)


def _transfer_order(index: int, transfer: dict, result: dict) -> dict | None:
    """Create the PayPal order once per result (session-cached)."""
    cache_key = (id(st.session_state["result"]), index,
                 round(float(transfer["amount"]), 2),
                 (result.get("currency") or "USD").upper())
    orders = st.session_state["orders"]
    cached = orders.get(cache_key)
    if cached:
        return cached
    try:
        token_str = oauth_token(sandbox_creds[0], sandbox_creds[1])
        order = create_order(
            token_str, float(transfer["amount"]),
            (result.get("currency") or "USD").upper(),
            f"SplitAI settlement from {transfer['from']} to {transfer['to']}",
            f"splitai-{transfer['from']}-{transfer['to']}")
    except PayPalError as exc:
        st.error(str(exc), icon=":material/error:")
        return None
    if len(orders) > 8:
        orders.clear()
    orders[cache_key] = order
    return order


def _render_transfers(result: dict, symbol: str) -> None:
    transfers = result.get("transfers") or []
    if not transfers:
        if result.get("payers"):
            st.caption("A payment plan could not be derived \u2014 see notices.")
        return
    st.subheader("Who pays whom", icon=":material/swap_horizontal_circle:")
    for index, transfer in enumerate(transfers):
        with st.container(border=True, key=f"transfer_{index}"):
            columns = st.columns([1.5, 2.6, 2.4])
            with columns[0]:
                st.markdown(f"**{transfer['from']}** \u2192 **{transfer['to']}**")
                st.caption(f"amount owed: {symbol}"
                           f"{transfer['amount']:,.2f}")
            with columns[1]:
                if sandbox_creds:
                    order = _transfer_order(index, transfer, result)
                    if order:
                        st.link_button(
                            f"Pay {transfer['to']} via PayPal",
                            url=order["approve_url"],
                            key=f"paybtn_{index}",
                            icon=":material/shopping_cart_checkout:")
                        st.caption("Sandbox order \u2014 approve in PayPal; "
                                   "capture happens when you return.")
                else:
                    st.markdown(f"### {symbol}{transfer['amount']:,.2f}")
            with columns[2]:
                currency = (result.get("currency") or "USD").upper()
                st.code(paypal_me_url(handle, float(transfer["amount"]),
                                      currency), language=None)


# ---------------------------------------------------------------- render
with output_slot:
    result = st.session_state.get("result")
    meta = st.session_state.get("result_meta") or {}
    if result and not result.get("ok"):
        _engine_badge()
        st.error(result.get("fail_reason") or "The bill could not be parsed.",
                 icon=":material/block:")
        st.caption("Tip: include a total (\"total was $70\") and the people "
                   "sharing it. The deterministic parser never invents results.")
        if st.session_state.get("raw_ai_text"):
            with st.expander("Raw Gemini output", icon=":material/article:"):
                st.markdown(st.session_state["raw_ai_text"])
    elif result and result.get("ok"):
        currency, symbol = _currency_of(result)
        _engine_badge()
        if meta.get("engine") == "ai-raw":
            with st.expander("Raw Gemini output (structured parse was "
                             "unavailable)", icon=":material/article:"):
                st.markdown(st.session_state.get("raw_ai_text") or "")
            det = parsing.parse_bill(meta.get("bill", ""),
                                     meta.get("instructions", ""))
            if det.get("ok"):
                st.info("Deterministic fallback shown below; verify the "
                        "Gemini text against it.", icon=":material/fallback:")
                result = det
                currency, symbol = _currency_of(result)

        totals = st.columns(3)
        with totals[0]:
            st.metric("Bill total", money(float(result["bill_total"]), symbol),
                      border=True)
        with totals[1]:
            st.metric("People sharing",
                      str(len(result["entries"])), border=True)
        with totals[2]:
            pending = round(sum(t["amount"] for t in
                                result.get("transfers", [])), 2)
            st.metric("Left to settle", money(pending, symbol),
                      delta=f"{len(result.get('transfers', []))} transfer(s)",
                      border=True)

        st.subheader("Split table", icon=":material/table_chart:")
        _render_table(result, symbol)

        chart_frame = pd.DataFrame({
            "Person": [entry["name"] for entry in result["entries"]],
            "Share": [float(entry["share"]) for entry in result["entries"]],
        }).set_index("Person")
        st.bar_chart(chart_frame, horizontal=True, color="#0070ba",
                     alt="Share by person",
                     height=min(40 * max(len(chart_frame), 2) + 60, 300))
        st.caption("Every share is derived from your bill text and shown "
                   "with its math.")

        _render_person_cards(result, symbol)
        _render_transfers(result, symbol)

        if result.get("notices"):
            with st.expander(f"Notices ({len(result['notices'])})",
                             icon=":material/info:"):
                for notice in result["notices"]:
                    st.markdown(f"- {notice}")
        st.download_button(
            "Download splits (CSV)",
            data="\n".join(["Name,Share,Currency"] + [
                f"{entry['name']},{entry['share']:.2f},{currency}"
                for entry in result["entries"]]),
            file_name="splitai-splits.csv",
            mime="text/csv",
            icon=":material/download:",
            key="csv_download",
        )
    else:
        st.info("Paste a bill above and hit **Calculate split**.",
                icon=":material/waving_hand:")
        with st.expander("How it works", icon=":material/school:"):
            st.markdown(
                "1. **Parse** \u2014 Gemini converts messy bill text into "
                "structured shares; without a key the honest deterministic "
                "parser does it.\n"
                "2. **Settle** \u2014 net balances (who advanced money vs "
                "who owes) produce the minimum set of transfers.\n"
                "3. **Pay** \u2014 with PayPal sandbox credentials every "
                "transfer gets a real Orders v2 approval link and is "
                "captured on return; without them, prefilled PayPal.me "
                "links keep the flow alive.")
        st.caption("No data leaves this app except the bill text you submit "
                   "to Gemini when a key is set.")

# ---------------------------------------------------------------- history
with st.sidebar:
    history = st.session_state.get("history") or []
    if history:
        st.divider()
        st.subheader("History", icon=":material/history:")
        for index, entry in enumerate(history):
            with st.expander(
                    f"{entry['people']}-way split \u00b7 {entry['symbol']}"
                    f"{entry['total']:,.2f} \u00b7 {entry['ts']}"):
                st.caption(f"engine: {entry['engine']}"
                           + (f" ({entry['model']})" if entry.get("model")
                              else ""))
                st.caption(entry["bill"][:200])
                st.button(
                    "Load this bill", key=f"history_load_{index}",
                    icon=":material/undo:", on_click=_restore_history,
                    args=(entry["bill"], ""),
                )
