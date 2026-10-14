"""Figure 7: the longer an S&P 500 drawdown has lasted, the longer it still has to go."""
import matplotlib.pyplot as plt

import style
from data import ROOT
from run_analysis import load_drawdowns, waiting_table

FIGURE = ROOT / "figures" / "drawdown_waiting.png"
LABELS = ["It has just\nstarted", "1 week", "1 month", "3 months", "1 year", "3 years"]


def duration(days: float) -> str:
    if days < 60:
        return f"{days:.0f} days"
    if days < 730:
        return f"{days / 30.44:.0f} months"
    return f"{days / 365.25:.1f} years"


def main() -> None:
    table = load_drawdowns()
    waiting = waiting_table(table["days"])
    positions = range(len(waiting))
    colours = [style.BLUE] * 3 + [style.RED] * 3

    style.apply()
    fig, ax = plt.subplots(figsize=(12.5, 6))
    ax.bar(positions, waiting["median_days_left"], width=0.62, color=colours)
    for x, row in zip(positions, waiting.itertuples()):
        ax.text(x, row.median_days_left * 1.12, duration(row.median_days_left), ha="center",
                va="bottom", fontsize=14, fontweight="bold", color=style.DARK)
        ax.text(x, 1.9, f"{row.share_recovering_within_30_days:.0%}\nback within\na month",
                ha="center", va="bottom", fontsize=10, color="white", fontweight="bold")
    ax.set_yscale("log")
    ax.set_ylim(1.5, 6000)
    ax.set_yticks([], minor=True)
    ax.set_yticks([])
    ax.spines["left"].set_visible(False)
    ax.tick_params(axis="x", length=0, labelsize=12, pad=8)
    ax.set_xticks(list(positions), LABELS)
    ax.set_xlabel("How long the S&P 500 has already been below its record", fontsize=12, labelpad=10)

    fig.suptitle("The longer a drawdown has lasted, the longer it still has to go",
                 x=0.01, ha="left", fontsize=18, fontweight="bold")
    fig.text(0.01, 0.905, "Median time left until a new record (log scale), over the drawdowns "
             f"of {table['peak_date'].min().year}–{table['recovery_date'].max().year} that had "
             "already lasted that long", fontsize=12, color=style.DARK)
    fig.text(0.01, 0.005, "Data: S&P 500 price index, daily closes (Yahoo Finance). "
             f"{len(table)} completed drawdowns; only 5 lasted more than 3 years.",
             fontsize=9.5, color=style.MUTED)
    fig.subplots_adjust(top=0.84, bottom=0.17, left=0.02, right=0.98)
    FIGURE.parent.mkdir(exist_ok=True)
    fig.savefig(FIGURE)
    print(f"Saved {FIGURE.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
