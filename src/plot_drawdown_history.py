"""Figure 6: the S&P 500 since 1928 with its four longest drawdowns highlighted."""
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

import style
from data import ROOT, load_sp500
from run_analysis import load_drawdowns

FIGURE = ROOT / "figures" / "sp500_drawdowns.png"


def main() -> None:
    closes = load_sp500()
    table = load_drawdowns()
    longest = table.nlargest(4, "days").sort_values("peak_date")
    share = longest["days"].sum() / table["days"].sum() * 100

    style.apply()
    fig, ax = plt.subplots(figsize=(12.5, 6))
    ax.plot(closes.index, closes, color=style.DARK, lw=1.4)
    for height, row in zip([0.97, 0.97, 0.97, 0.86], longest.itertuples()):   # last label lower, the spans touch
        ax.axvspan(row.peak_date, row.recovery_date, color=style.RED, alpha=0.18, lw=0)
        middle = row.peak_date + (row.recovery_date - row.peak_date) / 2
        ax.text(middle, height, f"{row.peak_date.year}–{row.recovery_date.year}\n{row.days / 365.25:.1f} years",
                transform=ax.get_xaxis_transform(), ha="center", va="top", fontsize=10.5,
                fontweight="bold", color=style.DARK)
    ax.set_yscale("log")
    ax.yaxis.set_major_formatter(FuncFormatter(lambda value, _: f"{value:,.0f}"))
    ax.set_ylabel("S&P 500 (log scale)")
    ax.set_xlim(closes.index[0], closes.index[-1])
    ax.set_ylim(top=closes.max() * 6)
    ax.grid(alpha=0.25)
    ax.set_title("The shaded periods run from a record close to the day the index got back to it",
                 loc="left", fontsize=12, color=style.DARK)

    fig.suptitle(f"Four drawdowns out of {len(table)} hold {share:.0f}% of all the days spent in a drawdown",
                 x=0.01, ha="left", fontsize=18, fontweight="bold")
    fig.text(0.01, 0.005, "Data: S&P 500 price index, daily closes, without dividends (Yahoo Finance).",
             fontsize=9.5, color=style.MUTED)
    fig.tight_layout(rect=(0, 0.03, 1, 0.99))
    FIGURE.parent.mkdir(exist_ok=True)
    fig.savefig(FIGURE)
    print(f"Saved {FIGURE.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
