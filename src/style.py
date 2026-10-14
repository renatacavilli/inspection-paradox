"""Shared colours and matplotlib settings so every figure looks the same."""
import matplotlib.pyplot as plt

BLUE = "#156082"     # short gaps, people with few friends, short drawdowns
RED = "#C8553D"      # long gaps, people with many friends, long drawdowns
DARK = "#374151"
GREY = "#9CA3AF"
MUTED = "#6B7280"    # source notes


def apply() -> None:
    plt.rcParams.update({
        "font.family": ["Helvetica Neue", "Helvetica", "Arial", "DejaVu Sans"],
        "font.size": 12,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "figure.dpi": 200,
        "savefig.facecolor": "white",
        "savefig.bbox": "tight",
    })
