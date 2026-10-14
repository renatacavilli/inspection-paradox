"""Every number reported in the post and in the README.

Writes data/processed/sp500_drawdowns.csv (one row per drawdown) and seven tables in results/:
summary.csv, friend_shares.csv, networks.csv, drawdown_shares.csv, drawdown_robustness.csv,
drawdown_waiting.csv and drawdown_dividends.csv.
"""
import numpy as np
import pandas as pd

import drawdowns
import paradox
from data import NETWORKS, ROOT, load_links, load_sp500, load_sp500_total_return

RESULTS = ROOT / "results"
DRAWDOWNS = ROOT / "data" / "processed" / "sp500_drawdowns.csv"

BUS_GAPS = [5, 15]                                  # minutes, alternating
BUCKET_EDGES = [0, 9, 49, 99, np.inf]               # number of friends
BUCKET_LABELS = ["Under 10 friends", "10 to 49", "50 to 99", "100 or more"]

DURATION_EDGES = [0, 30, 365, 5 * 365, np.inf]      # calendar days
DURATION_LABELS = ["Under 1 month", "1 to 12 months", "1 to 5 years", "Over 5 years"]
DEPRESSION_RECOVERY = "1954-09-22"                  # the S&P 500 regains its 1929 high
ELAPSED = [0, 7, 30, 90, 365, 3 * 365]              # days a drawdown has already lasted


def friend_shares(counts: np.ndarray) -> pd.DataFrame:
    """Share of people and share of friendships in each bucket of number of friends."""
    counts = pd.Series(counts[counts > 0])
    bucket = pd.cut(counts, BUCKET_EDGES, labels=BUCKET_LABELS)
    grouped = counts.groupby(bucket, observed=False).agg(people="count", friendships="sum")
    grouped["share_of_people"] = grouped["people"] / grouped["people"].sum()
    grouped["share_of_friendships"] = grouped["friendships"] / grouped["friendships"].sum()
    grouped.index.name = "friends"
    return grouped


def load_drawdowns() -> pd.DataFrame:
    """Load the table of S&P 500 drawdowns, building and saving it on first use."""
    if not DRAWDOWNS.exists():
        DRAWDOWNS.parent.mkdir(parents=True, exist_ok=True)
        drawdowns.find_drawdowns(load_sp500()).to_csv(DRAWDOWNS, index=False)
    return pd.read_csv(DRAWDOWNS, parse_dates=["peak_date", "trough_date", "recovery_date"])


def duration_shares(table: pd.DataFrame) -> pd.DataFrame:
    """Share of drawdowns and share of days in each bucket of duration."""
    bucket = pd.cut(table["days"], DURATION_EDGES, labels=DURATION_LABELS)
    grouped = table.groupby(bucket, observed=False)["days"].agg(drawdowns="count", days="sum")
    grouped["share_of_drawdowns"] = grouped["drawdowns"] / grouped["drawdowns"].sum()
    grouped["share_of_days"] = grouped["days"] / grouped["days"].sum()
    grouped.index.name = "duration"
    return grouped


def recovery_share(table: pd.DataFrame) -> float:
    """Share of the days of these drawdowns that come after the trough."""
    return float((table["recovery_date"] - table["trough_date"]).dt.days.sum() / table["days"].sum())


def summarise_lengths(days) -> dict[str, float]:
    """Count of drawdowns and their length averaged per drawdown and per day."""
    return {
        "count": len(days),
        "mean_per_drawdown": paradox.plain_mean(days),
        "mean_per_day": paradox.weighted_mean(days),
        "median_per_drawdown": paradox.plain_median(days),
        "median_per_day": paradox.weighted_median(days),
    }


def waiting_table(days) -> pd.DataFrame:
    """For drawdowns that have already lasted a number of days, how much of them is left."""
    table = pd.DataFrame({elapsed: drawdowns.wait_after(days, elapsed) for elapsed in ELAPSED}).T
    table.index.name = "days_already_below_the_record"
    return table.astype({"drawdowns_still_open": int}).round({"share_recovering_within_30_days": 4,
                                                             "median_days_left": 1, "mean_days_left": 1})


def dividends_table(price: pd.Series, total_return: pd.Series) -> pd.DataFrame:
    """The drawdown lengths of the price index and of the total return index, over the same days."""
    price = price[price.index >= total_return.index[0]]
    rows = {}
    for name, closes in [("Price index", price), ("With dividends reinvested", total_return)]:
        days = drawdowns.find_drawdowns(closes)["days"]
        rows[name] = {**summarise_lengths(days),
                      "share_of_trading_days_below_the_record": drawdowns.share_of_days_below_record(closes),
                      "longest": days.max()}
    table = pd.DataFrame(rows).T
    table["ratio_of_means"] = table["mean_per_day"] / table["mean_per_drawdown"]
    table = table.round({column: 4 if column.startswith("share") else 1 for column in table.columns})
    table.index.name = f"{price.index[0].date()} to {price.index[-1].date()}"
    return table.astype({"count": int, "longest": int})


def main() -> None:
    links = load_links("Facebook")
    counts = paradox.friend_counts(links)
    counts = counts[counts > 0]
    facebook = paradox.summarise_network(links)

    rows = [
        ("Buses", "Mean gap (minutes)", paradox.plain_mean(BUS_GAPS)),
        ("Buses", "Mean gap you land in (minutes)", paradox.weighted_mean(BUS_GAPS)),
        ("Buses", "Mean gap you land in, from the formula (minutes)", paradox.weighted_mean_from_formula(BUS_GAPS)),
        ("Facebook", "People", facebook["people"]),
        ("Facebook", "Friendships", facebook["links"]),
        ("Facebook", "Mean number of friends of a person", round(facebook["mean_friends_of_a_person"], 1)),
        ("Facebook", "Mean number of friends of a friend", round(facebook["mean_friends_of_a_friend"], 1)),
        ("Facebook", "Mean number of friends of a friend, from the formula",
         round(paradox.weighted_mean_from_formula(counts), 1)),
        ("Facebook", "Ratio of the two means", round(facebook["mean_friends_of_a_friend"] / facebook["mean_friends_of_a_person"], 2)),
        ("Facebook", "Median number of friends of a person", facebook["median_friends_of_a_person"]),
        ("Facebook", "Median number of friends of a friend", facebook["median_friends_of_a_friend"]),
        ("Facebook", "Most friends of one person", facebook["most_friends"]),
        ("Facebook", "Share of people with fewer friends than their friends have on average",
         round(facebook["share_with_fewer_friends_than_their_friends"], 4)),
    ]
    closes = load_sp500()
    DRAWDOWNS.parent.mkdir(parents=True, exist_ok=True)
    drawdowns.find_drawdowns(closes).to_csv(DRAWDOWNS, index=False)
    table = load_drawdowns()
    days = table["days"]
    rows += [
        ("S&P 500", "Trading days", len(closes)),
        ("S&P 500", "Share of trading days below the record", round(drawdowns.share_of_days_below_record(closes), 4)),
        ("S&P 500", "Completed drawdowns", len(table)),
        ("S&P 500", "Median length, per drawdown (days)", paradox.plain_median(days)),
        ("S&P 500", "Median length, per day (days)", paradox.weighted_median(days)),
        ("S&P 500", "Mean length, per drawdown (days)", round(paradox.plain_mean(days), 1)),
        ("S&P 500", "Mean length, per day (days)", round(paradox.weighted_mean(days), 1)),
        ("S&P 500", "Mean length, per day, from the formula (days)", round(paradox.weighted_mean_from_formula(days), 1)),
        ("S&P 500", "Ratio of the two means", round(paradox.weighted_mean(days) / paradox.plain_mean(days), 1)),
        ("S&P 500", "Share of days in the four longest drawdowns", round(days.nlargest(4).sum() / days.sum(), 4)),
        ("S&P 500", "Mean days left until the record, on a random day inside a drawdown",
         round(drawdowns.days_left(days).mean(), 1)),
        ("S&P 500", "Median days left until the record, on a random day inside a drawdown",
         float(np.median(drawdowns.days_left(days)))),
        ("S&P 500", "Share of days inside a drawdown with more than a year left",
         round((drawdowns.days_left(days) > 365).mean(), 4)),
        ("S&P 500", "Share of the time in falls of more than 20% spent climbing back from the trough",
         round(recovery_share(table[table["depth_pct"] <= -20]), 4)),
    ]
    samples = {
        "All drawdowns": table,
        "From the 1954 recovery onwards": table[table["peak_date"] >= DEPRESSION_RECOVERY],
        "Deeper than 5%": table[table["depth_pct"] <= -5],
        "Deeper than 10%": table[table["depth_pct"] <= -10],
        "Deeper than 20%": table[table["depth_pct"] <= -20],
    }
    robustness = pd.DataFrame({name: summarise_lengths(sample["days"]) for name, sample in samples.items()}).T
    robustness["ratio_of_means"] = robustness["mean_per_day"] / robustness["mean_per_drawdown"]
    robustness = robustness.round(1).astype({"count": int})
    robustness.index.name = "sample"

    rows = [(dataset, statistic, int(value) if float(value).is_integer() else value)
            for dataset, statistic, value in rows]
    summary = pd.DataFrame(rows, columns=["dataset", "statistic", "value"], dtype=object)

    networks = pd.DataFrame({name: paradox.summarise_network(load_links(name)) for name in NETWORKS}).T
    networks.insert(0, "link", [NETWORKS[name][3] for name in networks.index])
    networks = networks.astype({"people": int, "links": int, "most_friends": int,
                                "median_friends_of_a_person": int, "median_friends_of_a_friend": int})
    networks = networks.round({"mean_friends_of_a_person": 1, "mean_friends_of_a_friend": 1,
                               "share_with_fewer_friends_than_their_friends": 4})
    networks.index.name = "network"

    shares = friend_shares(counts).round(4)

    RESULTS.mkdir(exist_ok=True)
    summary.to_csv(RESULTS / "summary.csv", index=False)
    shares.to_csv(RESULTS / "friend_shares.csv")
    networks.to_csv(RESULTS / "networks.csv")
    duration_shares(table).round(4).to_csv(RESULTS / "drawdown_shares.csv")
    robustness.to_csv(RESULTS / "drawdown_robustness.csv")
    waiting = waiting_table(days)
    waiting.to_csv(RESULTS / "drawdown_waiting.csv")
    dividends = dividends_table(closes, load_sp500_total_return())
    dividends.to_csv(RESULTS / "drawdown_dividends.csv")
    print(summary.to_string(index=False), shares.to_string(), networks.T.to_string(),
          duration_shares(table).round(4).to_string(), robustness.to_string(), waiting.to_string(),
          dividends.T.to_string(), sep="\n\n")


if __name__ == "__main__":
    main()
