from pathlib import Path
import warnings
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
import seaborn as sns
from mpl_toolkits.axes_grid1 import make_axes_locatable

"""
Reproduce the MRT-file repetition-vs-prefix-count figure from the
precomputed artifact CSV file.
"""

DATA_FILE = Path("/home/ebrima/disk2/noisy-neighbors/data/rvs_results.gt10.pfxs.csv")
OUT_FIG = Path("/home/ebrima/disk2/noisy-neighbors/figures/rvs_balanced_fixed_annotated.png")
OUT_FIG.parent.mkdir(parents=True, exist_ok=True)

BIN_LABELS = ["≤100", "101–1K", "1K–10K", "10K–100K", "100K–1M", ">1M"]
BIN_EDGES = [-float("inf"), 100, 1_000, 10_000, 100_000, 1_000_000, float("inf")]

def human_fmt(x):
    if x >= 1_000_000:
        return f"{x / 1_000_000:.1f}M"
    if x >= 1_000:
        return f"{x / 1_000:.0f}K"
    return f"{x:.0f}"

if not DATA_FILE.exists():
    raise FileNotFoundError(f"Missing input file: {DATA_FILE}")

df = pd.read_csv(DATA_FILE)
df = df.replace([float("inf"), -float("inf")], pd.NA)
df = df[df["avg_rep_per_pfx"].notna() & (df["avg_rep_per_pfx"] >= 0)].copy()

df["prefix_bin"] = pd.cut(
    df["uniq_prefixes"],
    bins=BIN_EDGES,
    labels=BIN_LABELS,
    include_lowest=True,
    right=True,
).cat.set_categories(BIN_LABELS, ordered=True)

score_min = df["rep_vol_score"].min()
score_max = df["rep_vol_score"].max()
df["rep_vol_score_norm"] = (df["rep_vol_score"] - score_min) / (score_max - score_min)

stats = (df.groupby("prefix_bin", observed=True)["avg_rep_per_pfx"]
         .agg(n_files="size", mean_rep="mean").reindex(BIN_LABELS))

fig, ax = plt.subplots(figsize=(10.6, 3.6))

with warnings.catch_warnings():
    warnings.simplefilter("ignore", category=FutureWarning)

    sns.stripplot(data=df,x="prefix_bin",y="avg_rep_per_pfx",hue="rep_vol_score_norm",
                  palette="viridis_r",dodge=False,alpha=1,size=5,jitter=0.25,zorder=1,order=BIN_LABELS,ax=ax,)

    sns.boxplot(data=df,x="prefix_bin",y="avg_rep_per_pfx", showcaps=True,showfliers=False,
                boxprops={"facecolor": "none", "linewidth": 1.5, "zorder": 2},
                medianprops={"color": "black", "linewidth": 2, "zorder": 3},
                whiskerprops={"linewidth": 2, "zorder": 2}, order=BIN_LABELS,ax=ax,)

if ax.get_legend() is not None:
    ax.get_legend().remove()
ax.set_yscale("log")

ymax = float(df["avg_rep_per_pfx"].max()) if not df.empty else 1.0
y_bottom = 0.7
y_top = max(16_000.0, 1.1 * ymax)
ax.set_ylim(y_bottom, y_top)

ticks = [1, 2, 4, 10, 20, 50, 150, 300, 800, 1500, 
         3000, 6000, 13_000, 20_000, 30_000]
ticks = [t for t in ticks if y_bottom < t <= y_top]
ax.set_yticks(ticks)
ax.set_yticklabels([human_fmt(y) for y in ticks])

norm = mpl.colors.Normalize(vmin=0, vmax=1)
sm = plt.cm.ScalarMappable(cmap="viridis_r", norm=norm)
sm.set_array([])

divider = make_axes_locatable(ax)
cax = divider.append_axes("right", size="2.5%", pad=0.1)
cbar = fig.colorbar(sm, cax=cax)
cbar.set_label("Normalized repetition volume score")

x_positions = np.arange(len(BIN_LABELS))
ax.scatter(x_positions,stats["mean_rep"].values,marker="D",s=40,c="black",zorder=4,)
top_ax = ax.secondary_xaxis("top")
top_ax.set_xlim(ax.get_xlim())
top_ax.set_xticks(x_positions)
top_ax.set_xticklabels(
    [f"N={int(n):,}" if not np.isnan(n) 
     else "N=0" for n in stats["n_files"].values],fontsize=9,)
top_ax.tick_params(length=0)
top_ax.set_xlabel("")

ax.set_ylabel("Average prefix repetitions per MRT file")
ax.set_xlabel("MRT update files grouped by unique prefix counts")
ax.grid(True, which="both", linestyle="--", alpha=0.15)
plt.savefig(OUT_FIG, dpi=300, bbox_inches="tight", pad_inches=0.05)
plt.show()