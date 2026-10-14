"""Figure 5: S&P 500 drawdowns by duration, counted by drawdown and counted by day."""
import matplotlib.pyplot as plt

import style
from data import ROOT
from run_analysis import duration_shares, load_drawdowns

FIGURE = ROOT / "figures" / "drawdown_shares.png"


def label(share: float) -> str:
    return f"{share:.1f}%" if share < 1 else f"{share:.0f}%"


def main() -> None:
    table = load_drawdowns()
    shares = duration_shares(table)
    colours = [style.BLUE] * (len(shares) - 1) + [style.RED]
    rows = range(len(shares) - 1, -1, -1)          # shortest bucket on top

    style.apply()
    fig, (left, right) = plt.subplots(1, 2, figsize=(12.5, 5.6), sharey=True, gridspec_kw={"wspace": 0.42})

    panels = [(left, "share_of_drawdowns", "Counting drawdowns: almost all are short"),
              (right, "share_of_days", "Counting days: most are spent in long ones")]
    for ax, column, title in panels:
        values = shares[column] * 100
        ax.barh(rows, values, height=0.62, color=colours)
        for y, value in zip(rows, values):
            ax.text(value + 1.5, y, label(value), va="center", ha="right" if ax is left else "left",
                    fontsize=15, fontweight="bold", color=style.DARK)
        ax.set_xlim(0, 100)
        ax.set_xticks([])
        ax.spines["bottom"].set_visible(False)
        ax.tick_params(axis="y", length=0)
        ax.set_title(title, loc="right" if ax is left else "left", fontsize=14, fontweight="bold")
    left.invert_xaxis()
    left.spines["left"].set_visible(False)
    left.spines["right"].set_visible(True)
    left.yaxis.tick_right()
    left.set_yticks(rows, shares.index, ha="center")
    left.tick_params(axis="y", pad=62, labelsize=12)

    first, last = table["peak_date"].min().year, table["recovery_date"].max().year
    fig.suptitle(f"How long does an S&P 500 drawdown last? {len(table)} drawdowns, {first} to {last}",
                 x=0.01, ha="left", fontsize=18, fontweight="bold")
    fig.text(0.01, 0.005, "A drawdown runs from a record close to the next close at least as high. "
             "Data: S&P 500 price index, daily closes (Yahoo Finance).", fontsize=9.5, color=style.MUTED)
    fig.subplots_adjust(top=0.82, bottom=0.08, left=0.02, right=0.98)
    FIGURE.parent.mkdir(exist_ok=True)
    fig.savefig(FIGURE)
    print(f"Saved {FIGURE.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
