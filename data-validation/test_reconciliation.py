
from pathlib import Path
import pandas as pd
from pandas.testing import assert_frame_equal

ROOT = Path(__file__).resolve().parent.parent

RAW = ROOT / "datasets" / "orders_original.csv"
CLEAN = ROOT / "datasets" / "orders_baseline_cleaned.csv"


def load_data():
    raw = pd.read_csv(RAW)
    cleaned = pd.read_csv(CLEAN)
    return raw, cleaned


def test_removed_orders():
    raw, cleaned = load_data()

    removed = set(raw["order_id"]) - set(cleaned["order_id"])

    assert removed == {"ORD-1021", "ORD-1022"}
    assert raw["order_id"].duplicated().sum() == 2

    print("PASS: Invalid orders correctly removed")
    print("PASS: Two duplicate rows identified")


def test_row_level_reconciliation():
    raw, actual = load_data()

    # Independently reproduce expected cleaning rules
    expected = raw.drop_duplicates(
        subset=["order_id"], keep="first"
    ).copy()

    expected["quantity"] = pd.to_numeric(
        expected["quantity"], errors="coerce"
    )

    expected["unit_price_usd"] = pd.to_numeric(
        expected["unit_price_usd"], errors="coerce"
    )

    expected = expected[
        (expected["quantity"] > 0)
        & (expected["unit_price_usd"] > 0)
    ].copy()

    expected["region"] = (
        expected["region"]
        .fillna("Unknown")
        .astype(str)
        .str.strip()
        .str.title()
    )

    expected["status"] = (
        expected["status"]
        .astype(str)
        .str.strip()
        .str.lower()
    )

    expected["order_date"] = pd.to_datetime(
        expected["order_date"],
        format="%m/%d/%Y"
    ).dt.strftime("%Y-%m-%d")

    expected = expected.reset_index(drop=True)
    actual = actual.reset_index(drop=True)

    # Compare every row and every column
    assert_frame_equal(
        expected,
        actual,
        check_dtype=False,
        check_exact=False,
        rtol=1e-8,
        atol=1e-8
    )

    print("PASS: All 20 orders match expected results")
    print("PASS: All 7 columns match")
    print("PASS: Dates, regions, status, quantity and price")
