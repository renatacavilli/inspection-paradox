import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import drawdowns as dd  # noqa: E402


def series(values, start="2024-01-01"):
    return pd.Series(values, index=pd.date_range(start, periods=len(values), freq="D"), dtype=float)


def test_find_drawdowns_on_a_hand_made_series():
    #                 peak  dip  rec  peak  dip  dip  dip  rec
    closes = series([100,  90, 100, 110, 105,  88,  99, 111])
    table = dd.find_drawdowns(closes)
    assert table["days"].tolist() == [2, 4]
    assert table["depth_pct"].tolist() == [-10.0, -20.0]
    assert table["peak_date"].tolist() == [pd.Timestamp("2024-01-01"), pd.Timestamp("2024-01-04")]
    assert table["trough_date"].tolist() == [pd.Timestamp("2024-01-02"), pd.Timestamp("2024-01-06")]
    assert table["recovery_date"].tolist() == [pd.Timestamp("2024-01-03"), pd.Timestamp("2024-01-08")]


def test_unfinished_drawdown_is_left_out():
    table = dd.find_drawdowns(series([100, 90, 100, 95, 94]))
    assert len(table) == 1


def test_share_of_days_below_record():
    assert dd.share_of_days_below_record(series([100, 90, 100, 95])) == 0.5
