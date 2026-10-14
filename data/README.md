# Data

## `raw/`: the lists of links

Each file has one pair of user ids per line: the two people are connected.

| File | Network | Link | Source |
|---|---|---|---|
| `facebook_combined.txt.gz` | 4,039 Facebook users, 88,234 links | Facebook friends | McAuley and Leskovec (2012), [SNAP](https://snap.stanford.edu/data/ego-Facebook.html) |
| `deezer_europe_edges.csv.gz` | 28,281 Deezer users in Europe, 92,752 links | Mutual followers | Rozemberczki and Sarkar (2020), [SNAP](https://snap.stanford.edu/data/feather-deezer-social.html) |
| `lastfm_asia_edges.csv.gz` | 7,624 Last.fm users in Asia, 27,806 links | Mutual followers | Rozemberczki and Sarkar (2020), [SNAP](https://snap.stanford.edu/data/feather-lastfm-social.html) |
| `musae_git_edges.csv.gz` | 37,700 GitHub developers, 289,003 links | Mutual followers | Rozemberczki, Allen and Sarkar (2021), [SNAP](https://snap.stanford.edu/data/github-social.html) |

All four come from the Stanford Network Analysis Project, which makes them free to use with
citation. The user ids are anonymous numbers. The files were downloaded on 8 October 2026.

The Facebook file is kept exactly as downloaded. The other three are distributed as zip
archives with extra files that this project does not use, so `src/data.py` keeps only the
list of links and compresses it. It downloads any file that is missing.

The Facebook network joins the friend lists of ten people who took part in a survey, so it is
a sample of ten circles of friends and not a random sample of Facebook.

## `raw/`: the S&P 500

`sp500_yahoo_daily.csv` has the daily closing value of the S&P 500 price index from
30 December 1927 to 7 October 2026, from [Yahoo Finance](https://finance.yahoo.com/quote/%5EGSPC/history/),
ticker `^GSPC`. It keeps only the date and the close, rounded to two decimals. Before March 1957
the series is the 90-stock composite that preceded the S&P 500.

The data are subject to Yahoo's terms of service, and the index belongs to S&P Dow Jones
Indices. The file is kept here so that the results can be reproduced exactly. The download in
`src/data.py` stops at 7 October 2026, so a fresh copy covers the same days.

## `processed/`: the table of drawdowns

`sp500_drawdowns.csv` has one row per completed drawdown, 651 in total.

| Column | Meaning |
|---|---|
| `peak_date` | Day of the record close that starts the drawdown |
| `trough_date` | Day of the lowest close inside the drawdown |
| `recovery_date` | First day with a close at least as high as the peak |
| `days` | Calendar days from `peak_date` to `recovery_date` |
| `depth_pct` | Fall from the peak to the trough, in percent |

Rebuild it with `python src/run_analysis.py`.
