"""Figure 3: each Facebook user's number of friends against that of their friends."""
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

import paradox
import style
from data import ROOT, load_links

FIGURE = ROOT / "figures" / "friends_of_friends.png"


def main() -> None:
    links = load_links("Facebook")
    own = paradox.friend_counts(links)
    theirs = paradox.mean_friends_of_friends(links)
    connected = own > 0
    own, theirs = own[connected], theirs[connected]
    fewer = own < theirs
    share = fewer.mean() * 100

    style.apply()
    fig, ax = plt.subplots(figsize=(12.5, 6.4))
    limits = (0.8, own.max() * 1.3)
    ax.plot(limits, limits, color=style.DARK, lw=1.2, zorder=2)
    ax.scatter(own[fewer], theirs[fewer], s=14, color=style.RED, alpha=0.45, linewidth=0, zorder=3,
               label=f"Their friends have more friends than they do: {share:.0f}% of people")
    ax.scatter(own[~fewer], theirs[~fewer], s=14, color=style.BLUE, alpha=0.7, linewidth=0, zorder=3,
               label=f"They have more friends than their friends: {100 - share:.0f}%")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(limits)
    ax.set_ylim(limits)
    for axis in (ax.xaxis, ax.yaxis):
        axis.set_major_formatter(FuncFormatter(lambda value, _: f"{value:,.0f}"))
    ax.set_xlabel("Number of friends a person has (log scale)")
    ax.set_ylabel("Average number of friends\nof that person's friends (log scale)")
    ax.text(420, 330, "equal", rotation=27, color=style.DARK, fontsize=10.5, ha="center", va="top")
    legend = ax.legend(frameon=False, loc="lower right", markerscale=2.5)
    for handle in legend.legend_handles:
        handle.set_alpha(1)
    ax.grid(alpha=0.25, zorder=0)
    ax.set_title("Each dot is one person. Above the line, the person's friends are more popular than the person",
                 loc="left", fontsize=12, color=style.DARK)

    fig.suptitle(f"{share:.0f}% of people have fewer friends than their friends do",
                 x=0.01, ha="left", fontsize=18, fontweight="bold")
    fig.text(0.01, 0.005, f"Data: {len(own):,} Facebook users and {len(links):,} friendships, "
             "McAuley and Leskovec (2012), Stanford Network Analysis Project.", fontsize=9.5, color=style.MUTED)
    fig.tight_layout(rect=(0, 0.03, 1, 0.99))
    FIGURE.parent.mkdir(exist_ok=True)
    fig.savefig(FIGURE)
    print(f"Saved {FIGURE.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
