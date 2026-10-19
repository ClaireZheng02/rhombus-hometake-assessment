
from pathlib import Path
import pandas as pd

# File paths
ROOT = Path(__file__).resolve().parent.parent

RAW_PATH = ROOT / "datasets" / "orders_original.csv"
CLEAN_PATH = ROOT / "datasets" / "orders_baseline_cleaned.csv"

EXPECTED_COLUMNS = [
    "order_id",
    "order_date",
    "customer_email",
    "region",
    "status",
    "quantity",
    "unit_price_usd"
]


def load_data():
    raw = pd.read_csv(RAW_PATH)
    cleaned = pd.read_csv(CLEAN_PATH)
    return raw, cleaned


def test_row_counts():
    raw, cleaned = load_data()

    assert len(raw) == 24, "Original data should have 24 rows"
    assert len(cleaned) == 20, "Cleaned data should have 20 rows"

    print("PASS: Input 24 rows, Output 20 rows")


def test_output_schema():
    _, cleaned = load_data()

    assert list(cleaned.columns) == EXPECTED_COLUMNS, (
        f"Unexpected columns: {list(cleaned.columns)}"
    )

    print("PASS: All 7 expected columns are present in order")


def test_no_duplicate_orders():
    _, cleaned = load_data()

    assert cleaned["order_id"].is_unique, (
        "Duplicate order IDs found"
    )

    print("PASS: No duplicate orders")


def test_no_missing_values():
    _, cleaned = load_data()

    assert not cleaned.isna().any().any(), (
        "Missing values found in cleaned data"
    )

    print("PASS: No missing values")


def test_valid_numeric_values():
    _, cleaned = load_data()

    quantity = pd.to_numeric(
        cleaned["quantity"], errors="coerce"
    )

    price = pd.to_numeric(
        cleaned["unit_price_usd"], errors="coerce"
    )

    assert quantity.notna().all()
    assert price.notna().all()
    assert (quantity > 0).all()
    assert (price > 0).all()

    print("PASS: Quantity and price are valid positive numbers")
