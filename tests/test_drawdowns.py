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


def test_days_left_counts_every_day_once():
    # a drawdown of 3 days and one of 1 day: 3, 2, 1 days left, then 1
    assert dd.days_left([3, 1]).tolist() == [3, 2, 1, 1]


def test_mean_days_left_is_half_the_size_weighted_length():
    lengths = [5, 15]
    weighted = sum(x * x for x in lengths) / sum(lengths)
    assert dd.days_left(lengths).mean() == (weighted + 1) / 2


def test_wait_after():
    #  lengths 2, 10 and 40; after 5 days only 10 and 40 are still open, with 5 and 35 days left
    wait = dd.wait_after([2, 10, 40], 5)
    assert wait["drawdowns_still_open"] == 2
    assert wait["share_recovering_within_30_days"] == 0.5
    assert wait["median_days_left"] == 20
    assert wait["mean_days_left"] == 20
