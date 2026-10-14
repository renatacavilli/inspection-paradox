"""Figure 2: Facebook users by number of friends, counted as people and counted as friends."""
import matplotlib.pyplot as plt

import paradox
import style
from data import ROOT, load_links
from run_analysis import friend_shares

FIGURE = ROOT / "figures" / "friend_shares.png"


def main() -> None:
    counts = paradox.friend_counts(load_links("Facebook"))
    counts = counts[counts > 0]
    shares = friend_shares(counts)
    colours = [style.BLUE] * (len(shares) - 1) + [style.RED]
    rows = range(len(shares) - 1, -1, -1)          # fewest friends on top

    style.apply()
    fig, (left, right) = plt.subplots(1, 2, figsize=(12.5, 5.6), sharey=True, gridspec_kw={"wspace": 0.42})

    panels = [(left, "share_of_people", "Counting people: few are very popular"),
              (right, "share_of_friendships", "Counting friends: the popular are everywhere")]
    for ax, column, title in panels:
        values = shares[column] * 100
        ax.barh(rows, values, height=0.62, color=colours)
        for y, value in zip(rows, values):
            ax.text(value + 1.5, y, f"{value:.0f}%", va="center", ha="right" if ax is left else "left",
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

    fig.suptitle(f"Who are your friends? {len(counts):,} Facebook users by number of friends",
                 x=0.01, ha="left", fontsize=18, fontweight="bold")
    fig.text(0.01, 0.005, "Left: share of the people. Right: share of all the places in somebody's list of friends. "
             "Data: McAuley and Leskovec (2012), SNAP.", fontsize=9.5, color=style.MUTED)
    fig.subplots_adjust(top=0.82, bottom=0.08, left=0.02, right=0.98)
    FIGURE.parent.mkdir(exist_ok=True)
    fig.savefig(FIGURE)
    print(f"Saved {FIGURE.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
