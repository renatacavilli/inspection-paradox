"""Figure 4: the average person and the average friend in four different networks."""
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import FuncFormatter

import style
from data import ROOT

FIGURE = ROOT / "figures" / "four_networks.png"
RESULTS = ROOT / "results" / "networks.csv"


def main() -> None:
    networks = pd.read_csv(RESULTS, index_col="network")       # written by run_analysis.py
    rows = range(len(networks) - 1, -1, -1)

    style.apply()
    fig, ax = plt.subplots(figsize=(12.5, 4.8))
    person, friend = networks["mean_friends_of_a_person"], networks["mean_friends_of_a_friend"]
    ax.hlines(rows, person, friend, color=style.GREY, lw=2.5, zorder=2)
    ax.scatter(person, rows, s=130, color=style.BLUE, zorder=3, label="Average person")
    ax.scatter(friend, rows, s=130, color=style.RED, zorder=3, label="Average friend")
    for y, a, b in zip(rows, person, friend):
        ax.text(a / 1.18, y, f"{a:.0f}", ha="right", va="center", color=style.DARK, fontweight="bold")
        ax.text(b * 1.18, y, f"{b:.0f}", ha="left", va="center", color=style.DARK, fontweight="bold")
    labels = [f"{name}\n{people:,} people" for name, people in zip(networks.index, networks["people"])]
    ax.set_yticks(rows, labels)
    ax.set_ylim(-0.6, len(networks) - 0.4)
    ax.set_xscale("log")
    ax.set_xlim(3, 1000)
    ax.xaxis.set_major_formatter(FuncFormatter(lambda value, _: f"{value:,.0f}"))
    ax.set_xlabel("Number of friends or mutual followers (log scale)")
    ax.tick_params(axis="y", length=0)
    ax.grid(axis="x", alpha=0.25, zorder=0)
    ax.legend(frameon=False, loc="upper right")

    fig.suptitle("The same gap in four networks", x=0.01, ha="left", fontsize=18, fontweight="bold")
    fig.text(0.01, 0.005, "Data: Stanford Network Analysis Project. Facebook: McAuley and Leskovec (2012). "
             "Deezer, Last.fm, GitHub: Rozemberczki et al.", fontsize=9.5, color=style.MUTED)
    fig.tight_layout(rect=(0, 0.04, 1, 0.99))
    FIGURE.parent.mkdir(exist_ok=True)
    fig.savefig(FIGURE)
    print(f"Saved {FIGURE.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
