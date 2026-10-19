
from pathlib import Path
import pandas as pd
from pandas.testing import assert_frame_equal

ROOT = Path(__file__).resolve().parent.parent

RUN_1 = ROOT / "datasets" / "orders_run_1.csv"
RUN_2 = ROOT / "datasets" / "orders_run_2.csv"
BASELINE = ROOT / "datasets" / "orders_baseline_cleaned.csv"


def load_csv(path):
    assert path.exists(), f"Missing file: {path}"

    df = pd.read_csv(path)

    assert df["order_id"].is_unique, (
        f"Duplicate order IDs in {path.name}"
    )

    return df.sort_values(
        by="order_id"
    ).reset_index(drop=True)


def test_same_row_count():
    run1 = load_csv(RUN_1)
    run2 = load_csv(RUN_2)

    assert len(run1) == 20
    assert len(run2) == 20

    print("PASS: Both runs contain 20 rows")


def test_same_schema():
    run1 = load_csv(RUN_1)
    run2 = load_csv(RUN_2)

    assert list(run1.columns) == list(run2.columns)

    print("PASS: Both runs have identical schemas")


def test_identical_output():
    run1 = load_csv(RUN_1)
    run2 = load_csv(RUN_2)

    assert_frame_equal(
        run1,
        run2,
        check_dtype=False,
        check_exact=True
    )

    print("PASS: All values identical across both runs")


def test_matches_baseline():
    baseline = load_csv(BASELINE)
    run1 = load_csv(RUN_1)
    run2 = load_csv(RUN_2)

    assert_frame_equal(
        baseline,
        run1,
        check_dtype=False,
        check_exact=True
    )

    assert_frame_equal(
        baseline,
        run2,
        check_dtype=False,
        check_exact=True
    )

    print("PASS: Both runs match the baseline output")
