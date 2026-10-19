
from pathlib import Path
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parent.parent

BASELINE = ROOT / "datasets" / "orders_baseline_cleaned.csv"
DRIFT = ROOT / "datasets" / "orders_cents_output.csv"


@pytest.fixture
def compared_data():
    baseline = pd.read_csv(BASELINE)
    drift = pd.read_csv(DRIFT)

    assert len(baseline) == 20
    assert len(drift) == 20

    merged = baseline.merge(
        drift,
        on="order_id",
        suffixes=("_baseline", "_drift"),
        how="outer",
        indicator=True,
        validate="one_to_one"
    )

    assert merged["_merge"].eq("both").all()

    return merged


def test_detect_price_multiplier(compared_data):
    df = compared_data

    original_price = pd.to_numeric(
        df["unit_price_usd_baseline"]
    )

    drift_price = pd.to_numeric(
        df["unit_price_usd_drift"]
    )

    ratio = drift_price / original_price

    assert (abs(ratio - 100) < 0.001).all(), (
        "Unexpected price drift pattern"
    )

    print("PASS: Detected 100x price increase")


def test_other_fields_unchanged(compared_data):
    df = compared_data

    fields = [
        "order_date",
        "customer_email",
        "region",
        "status",
        "quantity"
    ]

    for field in fields:
        original = df[f"{field}_baseline"]
        changed = df[f"{field}_drift"]

        if field == "quantity":
            assert pd.to_numeric(original).equals(
                pd.to_numeric(changed)
            )
        else:
            assert original.equals(changed), (
                f"Unexpected change in {field}"
            )

    print("PASS: Non-price fields remain unchanged")
