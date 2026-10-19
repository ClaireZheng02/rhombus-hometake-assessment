
from pathlib import Path
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parent.parent

BASELINE = ROOT / "datasets" / "orders_baseline_cleaned.csv"
DRIFT = ROOT / "datasets" / "orders_dates_output.csv"


@pytest.fixture(scope="module")
def compared_data():
    baseline = pd.read_csv(BASELINE)
    drift = pd.read_csv(DRIFT)

    assert len(baseline) == len(drift) == 20
    assert list(baseline.columns) == list(drift.columns)
    assert baseline["order_id"].is_unique
    assert drift["order_id"].is_unique

    merged = baseline.merge(
        drift,
        on="order_id",
        how="outer",
        suffixes=("_baseline", "_drift"),
        indicator=True,
        validate="one_to_one"
    )

    assert merged["_merge"].eq("both").all(), (
        "Order IDs do not match"
    )

    return merged


def test_date_drift_detected(compared_data):
    df = compared_data

    changed = (
        df["order_date_baseline"]
        != df["order_date_drift"]
    )

    assert changed.sum() == 18, (
        f"Expected 18 changed dates, got {changed.sum()}"
    )

    print(f"PASS: Detected {changed.sum()}/20 changed dates")


def test_day_month_swapped(compared_data):
    df = compared_data

    baseline_dates = pd.to_datetime(
        df["order_date_baseline"],
        format="%Y-%m-%d"
    )

    expected_wrong_dates = baseline_dates.dt.strftime(
        "%Y-%d-%m"
    )

    actual_dates = df["order_date_drift"]

    assert (actual_dates == expected_wrong_dates).all(), (
        "Dates do not match the expected day/month swap pattern"
    )

    print("PASS: Day/month swap pattern confirmed")


def test_non_date_fields_unchanged(compared_data):
    df = compared_data

    fields = [
        "customer_email",
        "region",
        "status",
        "quantity",
        "unit_price_usd"
    ]

    for field in fields:
        baseline = df[f"{field}_baseline"]
        drift = df[f"{field}_drift"]

        assert baseline.equals(drift), (
            f"Unexpected difference in {field}"
        )

    print("PASS: All non-date fields match baseline")
