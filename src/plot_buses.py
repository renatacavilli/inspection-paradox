"""Figure 1: buses in gaps of 5 and 15 minutes, counted by gap and counted by minute."""
import matplotlib.pyplot as plt

import style
from data import ROOT

FIGURE = ROOT / "figures" / "buses.png"
GAPS = [5, 15, 5, 15, 5, 15]          # one hour of buses
LABELS = {5: "Short gaps (5 minutes)", 15: "Long gaps (15 minutes)"}
COLOURS = {5: style.BLUE, 15: style.RED}


def main() -> None:
    style.apply()
    fig, (timeline, bars) = plt.subplots(2, 1, figsize=(12.5, 6.6), height_ratios=[1, 1.25])

    start = 0
    for gap in GAPS:
        timeline.barh(0, gap, left=start, height=0.5, color=COLOURS[gap], edgecolor="white", linewidth=3)
        timeline.text(start + gap / 2, 0, f"{gap} min", ha="center", va="center", color="white", fontweight="bold")
        start += gap
    arrivals = [0]
    for gap in GAPS:
        arrivals.append(arrivals[-1] + gap)
    timeline.scatter(arrivals, [0.52] * len(arrivals), marker="v", s=110, color=style.DARK, zorder=3)
    timeline.text(6.2, 0.52, "a bus arrives at each mark", color=style.DARK, ha="left", va="center", fontsize=11)
    timeline.set_xlim(-0.5, 60.5)
    timeline.set_ylim(-0.4, 0.8)
    timeline.set_xticks(range(0, 61, 10))
    timeline.set_xlabel("Minutes")
    timeline.set_yticks([])
    timeline.spines["left"].set_visible(False)
    timeline.set_title("One hour at the stop: six gaps, three short and three long",
                       loc="left", fontsize=14, fontweight="bold")

    minutes = {gap: sum(g for g in GAPS if g == gap) / sum(GAPS) * 100 for gap in LABELS}
    counts = {gap: GAPS.count(gap) / len(GAPS) * 100 for gap in LABELS}
    rows = [("Share of the gaps\n(what the timetable counts)", counts),
            ("Share of the minutes\n(what the passenger lives)", minutes)]
    for y, (label, shares) in zip([1, 0], rows):
        left = 0
        for gap in LABELS:
            bars.barh(y, shares[gap], left=left, height=0.55, color=COLOURS[gap], edgecolor="white",
                      linewidth=3, label=LABELS[gap] if y == 1 else None)
            bars.text(left + shares[gap] / 2, y, f"{shares[gap]:.0f}%", ha="center", va="center",
                      color="white", fontsize=16, fontweight="bold")
            left += shares[gap]
    bars.set_yticks([1, 0], [label for label, _ in rows])
    bars.set_xlim(0, 100)
    bars.set_ylim(-0.5, 1.9)
    bars.set_xticks([])
    bars.spines["bottom"].set_visible(False)
    bars.spines["left"].set_visible(False)
    bars.tick_params(axis="y", length=0)
    bars.legend(frameon=False, loc="upper left", ncols=2, bbox_to_anchor=(0, 1.08))

    fig.suptitle("Why the bus always seems late", x=0.01, ha="left", fontsize=18, fontweight="bold")
    fig.text(0.01, 0.005, "Illustrative timetable: the average gap is 10 minutes, but the gap you arrive in "
             "lasts 12.5 minutes on average.", fontsize=9.5, color=style.MUTED)
    fig.tight_layout(rect=(0, 0.03, 1, 0.99))
    FIGURE.parent.mkdir(exist_ok=True)
    fig.savefig(FIGURE)
    print(f"Saved {FIGURE.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
