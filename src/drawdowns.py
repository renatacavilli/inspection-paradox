"""Find the drawdowns of a price series.

A drawdown starts at a record close and ends at the first close that is at least as high.
Its length is the number of calendar days between those two dates.
"""
from __future__ import annotations

import numpy as np
import pandas as pd


def find_drawdowns(closes: pd.Series) -> pd.DataFrame:
    """One row per completed drawdown: peak date, trough date, recovery date, days and depth.

    A drawdown that has not recovered by the end of the series is left out.
    """
    dates = closes.index
    values = closes.to_numpy()
    below = values < np.maximum.accumulate(values)
    rows = []
    first = None                      # position of the first close below the record
    for i, is_below in enumerate(below):
        if is_below and first is None:
            first = i
        elif not is_below and first is not None:
            trough = first + int(np.argmin(values[first:i]))
            rows.append({
                "peak_date": dates[first - 1],
                "trough_date": dates[trough],
                "recovery_date": dates[i],
                "days": (dates[i] - dates[first - 1]).days,
                "depth_pct": round((values[trough] / values[first - 1] - 1) * 100, 2),
            })
            first = None
    return pd.DataFrame(rows, columns=["peak_date", "trough_date", "recovery_date", "days", "depth_pct"])


def share_of_days_below_record(closes: pd.Series) -> float:
    """Fraction of trading days that closed below the highest close so far."""
    return float((closes < closes.cummax()).mean())


def days_left(lengths) -> np.ndarray:
    """Days left until the recovery, for every calendar day spent inside a drawdown.

    A drawdown of L days contributes L values: L days left on the day of the peak, then L - 1,
    and so on down to 1 on the day before the recovery. Picking one of these values at random
    is what someone who looks at the index on a random day of a drawdown experiences.
    """
    return np.concatenate([np.arange(length, 0, -1) for length in np.asarray(lengths, dtype=int)])


def wait_after(lengths, elapsed: int) -> dict[str, float]:
    """What is left of the drawdowns that have already lasted more than `elapsed` days."""
    lengths = np.asarray(lengths, dtype=float)
    left = lengths[lengths > elapsed] - elapsed
    return {
        "drawdowns_still_open": len(left),
        "share_recovering_within_30_days": float((left <= 30).mean()),
        "median_days_left": float(np.median(left)),
        "mean_days_left": float(left.mean()),
    }
