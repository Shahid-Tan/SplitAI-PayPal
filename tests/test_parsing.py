"""Unit tests for the deterministic bill parser (pure logic, no UI)."""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.parsing import (compute_transfers, equal_split, parse_bill,  # noqa: E402
                           payer_names)


def _shares(result):
    return {entry["name"]: entry["share"] for entry in result["entries"]}


def _pay_map(result):
    return {(t["from"], t["to"]): t["amount"] for t in result["transfers"]}


# ------------------------------------------------------------------ cases

def test_itemized_dinner_with_equal_tip():
    bill = ("Dinner bill: $54. Rahul ordered pasta for $22, Sneha ordered "
            "pizza for $18, and I had salad for $14. Add $6 service tax "
            "split equally.")
    result = parse_bill(bill)
    assert result["ok"] is True
    assert result["currency"] == "USD"
    shares = _shares(result)
    assert shares["Rahul"] == 24.00
    assert shares["Sneha"] == 20.00
    assert shares["You"] == 16.00
    assert round(sum(shares.values()), 2) == result["bill_total"] == 60.00


def test_shared_household_inr_with_surcharge():
    bill = ("Monthly 3BHK flat expenses in Bangalore: Total rent \u20b924,000, "
            "WiFi \u20b91,000, Electricity \u20b92,000. Shahid has master "
            "bedroom with AC so he pays \u20b92,000 extra on rent. Split rest "
            "equally among Shahid, Kabir, and Zaid.")
    result = parse_bill(bill)
    assert result["ok"] is True
    assert result["currency"] == "INR"
    shares = _shares(result)
    assert set(shares) == {"Shahid", "Kabir", "Zaid"}
    assert shares["Kabir"] == shares["Zaid"] == 8333.33
    assert shares["Shahid"] == 10333.34
    assert round(sum(shares.values()), 2) == result["bill_total"] == 27000.00


def test_payer_covers_everything_transfers():
    bill = ("Road trip fuel was $90. Car snacks were $30. 4 friends: Shahid, "
            "Alex, John, David. Shahid paid upfront for everything.")
    result = parse_bill(bill)
    assert result["ok"] is True
    shares = _shares(result)
    assert shares == {"Alex": 30.00, "David": 30.00, "John": 30.00,
                      "Shahid": 30.00}
    assert result["payers"] == ["Shahid"]
    transfers = result["transfers"]
    total_settled = sum(t["amount"] for t in transfers)
    assert round(total_settled, 2) == 90.00
    for t in transfers:
        assert t["to"] == "Shahid"
        assert t["amount"] == 30.00


def test_equal_tip_applies_to_per_person_items():
    bill = ("A $70 dinner. Alice had steak ($35), Bob had burger ($20), "
            "Charlie had soup ($15). Split $10 tip equally.")
    result = parse_bill(bill)
    assert result["ok"] is True
    shares = _shares(result)
    assert shares["Alice"] == 38.34
    assert shares["Bob"] == 23.33
    assert shares["Charlie"] == 18.33
    assert round(sum(shares.values()), 2) == 80.00


def test_weighted_percentage_split():
    bill = "Split 60/40 between Alice and Bob. Total $100."
    result = parse_bill(bill)
    assert result["ok"] is True
    shares = _shares(result)
    assert shares["Alice"] == 60.00
    assert shares["Bob"] == 40.00
    assert (any("60/40" in notice for notice in result["notices"]))


def test_head_count_placeholders_are_honest():
    bill = "Split $90 equally among 4 friends. Shahid paid everything."
    result = parse_bill(bill)
    assert result["ok"] is True
    shares = _shares(result)
    assert len(shares) == 4
    placeholders = [name for name in shares if name.startswith("Person")]
    assert placeholders, "count-based placeholders should appear"
    assert any("placeholder" in notice.lower()
               for notice in result["notices"])
    transfers = result["transfers"]
    assert round(sum(t["amount"] for t in transfers), 2) == 67.50
    for t in transfers:
        assert t["to"] == "Shahid"


def test_junk_text_is_rejected_not_invented():
    result = parse_bill("zzz no amounts here at all")
    assert result["ok"] is False
    assert result["fail_reason"]
    assert result["entries"] == []


def test_no_invented_names():
    bill = "We had a $60 dinner, split it equally among the four of us."
    result = parse_bill(bill)
    shares = _shares(result)
    for name in shares:
        assert name in {"Us", "You", "Person 2", "Person 3", "Person 4"}
    assert round(sum(shares.values()), 2) == result["bill_total"] == 60.00


def test_splits_sum_back_to_amount():
    assert round(sum(equal_split(10.00, 3)), 2) == 10.00
    assert round(sum(equal_split(0.02, 3)), 2) == 0.02
    assert round(sum(equal_split(100.00, 7)), 2) == 100.00


def test_transfer_algorithm_conserves():
    entries = [
        {"name": "Ann", "share": 30.0, "payer": True, "paid_amount": 90.0},
        {"name": "Ben", "share": 30.0, "payer": False, "paid_amount": None},
        {"name": "Cy", "share": 30.0, "payer": False, "paid_amount": None},
    ]
    transfers = compute_transfers(entries)
    assert round(sum(t["amount"] for t in transfers), 2) == 60.00
    assert all(t["to"] == "Ann" for t in transfers)


def test_percentage_tip_on_total():
    bill = "Lunch total was $80. Add 10% service charge. Alice ordered pasta $40, Bob ordered rice $40."
    result = parse_bill(bill)
    shares = _shares(result)
    assert shares["Alice"] == 44.00
    assert shares["Bob"] == 44.00


def test_paid_by_detection():
    bill = "Tickets were $120, paid by Priya. Share equally among Priya, Sam, and Rhea."
    result = parse_bill(bill)
    assert payer_names(bill) == ["Priya"]
    assert result["ok"] is True
    transfers = {(t["from"], t["to"]) for t in result["transfers"]}
    assert (("Sam", "Priya") in transfers or ("Rhea", "Priya") in transfers)
