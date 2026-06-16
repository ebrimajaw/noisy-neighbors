from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

"""
Reproduce Figure 5a (December 2021) and Figure 5b (December 2024)
from the precomputed origin-AS prefix-variability CSV files.
"""

DATA_DIR = Path("/home/ebrima/disk2/noisy-neighbors/data/cache")
FIG_DIR = Path("/home/ebrima/disk2/noisy-neighbors/figures")
FIG_DIR.mkdir(parents=True, exist_ok=True)

INPUTS = {"2021": DATA_DIR / "origin_as_prefix_variability_2021.csv", "2024": DATA_DIR / "origin_as_prefix_variability_2024.csv"}
OUTPUTS = {"2021": FIG_DIR / "origin_as_prefix_variability_2021.png", "2024": FIG_DIR / "origin_as_prefix_variability_2024.png"}

def human_fmt(x, _):
    if x >= 1_000_000_000:
        return f"{x / 1_000_000_000:.1f}B"
    if x >= 1_000_000:
        return f"{x / 1_000_000:.1f}M"
    if x >= 1_000:
        return f"{x / 1_000:.1f}K"
    return str(int(x))

for year, path in INPUTS.items():
    if not path.exists():
        raise FileNotFoundError(f"Missing input file: {path}")

    df = pd.read_csv(path,usecols=["as_prefix_cv_stddev", "total_updates"]).dropna()
    fig, ax = plt.subplots(figsize=(12, 4))

    ax.scatter(df["as_prefix_cv_stddev"],df["total_updates"],color="#034C53",
               edgecolors="white",linewidths=0.8,alpha=1,s=120,)
    ax.set_yscale("log")
    ax.yaxis.set_major_formatter(FuncFormatter(human_fmt))

    if year == "2021":
        xlabel = ("Heterogeneity of per-prefix update patterns within origin ASes (December 2021)")
    else:
        xlabel = ("Variation in prefix update patterns within origin ASes (December 2024)")
    ax.set_xlabel(xlabel, fontsize=16)
    ax.set_ylabel("Total updates per origin AS", fontsize=14.5)
    ax.tick_params(axis="x", labelsize=14)
    ax.tick_params(axis="y", labelsize=12)
    ax.grid(True,which="both",linestyle="--",linewidth=0.35,alpha=0.40,)
    ax.margins(x=0.01, y=0.01)
    plt.tight_layout()
    plt.savefig(OUTPUTS[year], dpi=300, bbox_inches="tight")
    plt.show()
    plt.close(fig)