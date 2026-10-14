"""Download and load four public friendship networks and the daily S&P 500, with and without dividends."""
from __future__ import annotations

import gzip
import io
import json
import urllib.request
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"

# name: (file kept in data/raw, download address, edge file inside the zip or None, description)
NETWORKS = {
    "Facebook": ("facebook_combined.txt.gz",
                 "https://snap.stanford.edu/data/facebook_combined.txt.gz", None, "friends"),
    "Deezer": ("deezer_europe_edges.csv.gz",
               "https://snap.stanford.edu/data/deezer_europe.zip",
               "deezer_europe/deezer_europe_edges.csv", "mutual followers"),
    "Last.fm": ("lastfm_asia_edges.csv.gz",
                "https://snap.stanford.edu/data/lastfm_asia.zip",
                "lasftm_asia/lastfm_asia_edges.csv", "mutual followers"),
    "GitHub": ("musae_git_edges.csv.gz",
               "https://snap.stanford.edu/data/git_web_ml.zip",
               "git_web_ml/musae_git_edges.csv", "mutual followers"),
}

SP500 = RAW / "sp500_yahoo_daily.csv"                         # price index, from 1927
SP500_TOTAL_RETURN = RAW / "sp500_total_return_yahoo_daily.csv"  # dividends reinvested, from 1988
LAST_DAY = "2026-10-07"   # fixed, so that a fresh download gives the same sample
YAHOO_URL = (
    "https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"
    "?period1=-1500000000&period2={end}&interval=1d"
)


def download(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    return urllib.request.urlopen(request).read()


def fetch(name: str) -> Path:
    """Return the path of a network's edge file, downloading it first if it is not there."""
    filename, url, member, _ = NETWORKS[name]
    path = RAW / filename
    if not path.exists():
        RAW.mkdir(parents=True, exist_ok=True)
        content = download(url)
        if member is not None:                      # keep only the list of links, compressed
            content = gzip.compress(zipfile.ZipFile(io.BytesIO(content)).read(member))
        path.write_bytes(content)
    return path


def load_links(name: str) -> np.ndarray:
    """The links of a network as an array with one row per pair of connected people."""
    links = set()
    with gzip.open(fetch(name), "rt") as lines:
        for line in lines:
            pair = line.replace(",", " ").split()
            if len(pair) == 2 and pair[0].isdigit():            # skips the header of the csv files
                a, b = int(pair[0]), int(pair[1])
                if a != b:
                    links.add((min(a, b), max(a, b)))
    return np.array(sorted(links))


def fetch_index(path: Path, ticker: str) -> Path:
    """Return the path of a daily index file, downloading it from Yahoo first if it is not there."""
    if not path.exists():
        RAW.mkdir(parents=True, exist_ok=True)
        end = int((pd.Timestamp(LAST_DAY) + pd.Timedelta(days=1)).timestamp())
        chart = json.loads(download(YAHOO_URL.format(ticker=ticker, end=end)))["chart"]["result"][0]
        closes = pd.Series(
            chart["indicators"]["quote"][0]["close"],
            index=pd.to_datetime(chart["timestamp"], unit="s").normalize(),
            name="close",
        ).dropna().round(2)
        closes.index.name = "date"
        closes.to_csv(path)
    return path


def load_sp500() -> pd.Series:
    """Daily closing values of the S&P 500 price index, indexed by date."""
    return pd.read_csv(fetch_index(SP500, "%5EGSPC"), index_col="date", parse_dates=["date"])["close"]


def load_sp500_total_return() -> pd.Series:
    """Daily closing values of the S&P 500 with dividends reinvested, indexed by date."""
    path = fetch_index(SP500_TOTAL_RETURN, "%5ESP500TR")
    return pd.read_csv(path, index_col="date", parse_dates=["date"])["close"]


if __name__ == "__main__":
    for name in NETWORKS:
        links = load_links(name)
        print(f"{name}: {len(np.unique(links))} people, {len(links)} links ({fetch(name).relative_to(ROOT)})")
    closes = load_sp500()
    print(f"S&P 500: {closes.index[0].date()} to {closes.index[-1].date()}, {len(closes)} days ({SP500.relative_to(ROOT)})")
    total = load_sp500_total_return()
    print(f"S&P 500 total return: {total.index[0].date()} to {total.index[-1].date()}, {len(total)} days "
          f"({SP500_TOTAL_RETURN.relative_to(ROOT)})")
