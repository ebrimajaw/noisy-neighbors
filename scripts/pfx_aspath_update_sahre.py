from pathlib import Path
import gc
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

"""
AS-path and prefix cumulative update-share
from precomputed sorted update-count vectors.

noisy-neighbors/data/cache/asp_vals.sorted.npy
    Sorted descending vector of update counts for all unique AS paths.
    Computed from all observed announcements in Route Views update files.
    Reproduce the AS-path cumulative update-share figure.

noisy-neighbors/data/cache/prefix_vals.sorted.npy
    Sorted descending vector of update counts for all unique prefixes.
    Computed from all observed announcements in Route Views update files.
    Reproduce the prefix cumulative update-share figure.
"""

CACHE_DIR = Path("/noisy-neighbors/data/cache")
FIG_DIR = Path("/noisy-neighbors/figures")

ASP_CACHE = CACHE_DIR / "asp_vals.sorted.npy"
PREFIX_CACHE = CACHE_DIR / "prefix_vals.sorted.npy"

ASPATH_FIG = FIG_DIR / "aspath_share.png"
PREFIX_FIG = FIG_DIR / "prefix_share.png"

AS_COLOR, PREFIX_COLOR = "#dd1c77", "purple"
AS_MARKER, PREFIX_MARKER = "o", "x"
LINE_COLOR = "gray"
LINE_STYLE = "dashed"

ASPATH_PERCENTILES = [0.25, 0.75]
PREFIX_PERCENTILES = [0.25, 0.75]
PREFIX_FRACTION = 0.02

YTICKS = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
YTICK_LABELS = ["0.0", "0.2", "0.4", "0.6", "0.8", "1.0"]
FIG_DIR.mkdir(parents=True, exist_ok=True)

def human_format(x, _):
    if x >= 1e6:
        return f"{x / 1e6:.0f}M"
    if x >= 1e3:
        return f"{x / 1e3:.0f}K"
    return str(int(x))

def compact_number(n):
    if n >= 1e6:
        return f"{n / 1e6:.2f}M"
    if n >= 1e3:
        return f"{n / 1e3:.2f}K"
    return f"{n:.2f}"

def plot_single_ecdf(vals, label, color, marker, markevery, output_path, update_percentiles=None, show_top_fraction=False, top_fraction=0.02):
    cdf = np.cumsum(vals) / vals.sum()
    xvals = np.arange(1, len(cdf) + 1)
    fig, ax = plt.subplots(figsize=(10, 3))
    ax.plot(xvals, cdf, label=label, color=color, linewidth=4, marker=marker, markersize=4.5, markevery=markevery)

    if update_percentiles:
        for p in update_percentiles:
            idx = np.searchsorted(cdf, p, side="left") + 1
            x, y = idx, cdf[idx - 1]
            ax.plot([x, x], [0, y], color=LINE_COLOR, linestyle=LINE_STYLE, linewidth=1)
            ax.plot([1, x], [y, y], color=LINE_COLOR, linestyle=LINE_STYLE, linewidth=1)
            ax.plot(x, y, "s", color=LINE_COLOR, markersize=5)

    if show_top_fraction:
        idx = max(1, int(np.ceil(top_fraction * len(cdf))))
        x, y = idx, cdf[idx - 1]
        ax.plot([x, x], [0, y], color=LINE_COLOR, linestyle=LINE_STYLE, linewidth=1)
        ax.plot([1, x], [y, y], color=LINE_COLOR, linestyle=LINE_STYLE, linewidth=1)
        ax.plot(x, y, "s", color=LINE_COLOR, markersize=6)
        ax.annotate(f"Top {top_fraction * 100:.0f}% prefixes\n→ {y * 100:.2f}% of updates",xy=(x, y),xytext=(12, -35),
                    textcoords="offset points",fontsize=13,ha="left",va="top",
                    arrowprops=dict(arrowstyle="->", color=LINE_COLOR, linewidth=1),)
    ax.set_xlabel("Ranked by update volume (log scale)", fontsize=14)
    ax.set_ylabel("Cumulative update\nshare", fontsize=14)
    ax.grid(True, linestyle="--", linewidth=0.25, which="both")
    ax.legend(loc="lower right", fontsize=14, frameon=True)
    ax.set_yticks(YTICKS)
    ax.set_yticklabels(YTICK_LABELS, fontsize=14.5)
    ax.tick_params(axis="x", labelsize=14.5)
    ax.xaxis.set_major_formatter(FuncFormatter(human_format))
    ax.margins(y=0.01, x=0.01)
    ax.set_xscale("log")
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.show()
    plt.close(fig)
    del cdf, xvals
    gc.collect()

if not ASP_CACHE.exists():
    raise FileNotFoundError(f"Missing AS-path cache file: {ASP_CACHE}")
if not PREFIX_CACHE.exists():
    raise FileNotFoundError(f"Missing prefix cache file: {PREFIX_CACHE}")
asp_vals = np.load(ASP_CACHE, mmap_mode="r")
prefix_vals = np.load(PREFIX_CACHE, mmap_mode="r")

plot_single_ecdf(vals=asp_vals,label=f"All AS paths ({compact_number(len(asp_vals))} paths)",color=AS_COLOR,marker=AS_MARKER,markevery=400,
                 output_path=ASPATH_FIG,update_percentiles=ASPATH_PERCENTILES,show_top_fraction=False,)

plot_single_ecdf(vals=prefix_vals,label=f"All updates ({compact_number(len(prefix_vals))} prefixes)",color=PREFIX_COLOR,marker=PREFIX_MARKER,markevery=300,
                 output_path=PREFIX_FIG,update_percentiles=PREFIX_PERCENTILES,show_top_fraction=True,top_fraction=PREFIX_FRACTION,)

del asp_vals, prefix_vals
gc.collect()