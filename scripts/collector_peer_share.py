from pathlib import Path
from datetime import datetime
import re
import polars as pl
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib.dates as mdates

"""
Reproduce the collector-peer update-share figure using the processed
collector_peer_daily_bins.parquet artifact file.
"""

DATA = Path("/home/savymik/noisy-neighbors/data/collector_peer_daily_bins.parquet")
OUT_FIG = Path("/home/savymik/noisy-neighbors/figures/collector_peers.png")

TOP_N = 11
START_DATE, END_DATE = datetime(2012, 1, 1), datetime(2025, 1, 1)

BIN_ORDER = ["Lower 50%", "50-75%", "75-95%", "95-100%"]
BIN_COLORS = {"95-100%": "maroon", "75-95%": "orange", "50-75%": "blue", "Lower 50%": "skyblue"}

PAIR_COLORS = ["#1C2B3A", "#D3D3D3", "maroon", "#F11F07", "#2E4057", "#0197FB", "#040404", "navy", "darkgreen", "goldenrod", "purple"]
OTHERS_COLOR = "#F8075C"

OUT_FIG.parent.mkdir(parents=True, exist_ok=True)

def simplify_label(label):
    label = re.sub(r"(routeviews\.)+", "rvs.", label)
    return re.sub(r"rvs\.routeviews(\d+)", r"rvs.rvs\1", label)

def human_fmt(x, _):
    if x >= 1e9:
        return f"{x / 1e9:.1f}B"
    if x >= 1e6:
        return f"{x / 1e6:.0f}M"
    if x >= 1e3:
        return f"{x / 1e3:.0f}K"
    return str(int(x))

data = pl.scan_parquet(DATA)
bin_daily = (data.group_by("date", "percentile_bin").agg(pl.sum("update_count").alias("updates")).collect().to_pandas())
upd_plot_df = (bin_daily.assign(date=pd.to_datetime(bin_daily["date"])).pivot(index="date", columns="percentile_bin", 
                        values="updates").fillna(0).sort_index()[BIN_ORDER])

top_pairs = (data.group_by("collector", "peer_asn").agg(pl.sum("update_count").alias("total_updates")).sort("total_updates", 
                        descending=True).limit(TOP_N).collect())

peer_share = (data.join(top_pairs.lazy(), on=["collector", "peer_asn"], 
                        how="left").with_columns(pl.when(pl.col("total_updates").is_not_null()).then(pl.concat_str("collector", 
                        pl.lit("-"), pl.col("peer_asn").cast(pl.Utf8))).otherwise(pl.lit("Others")).alias("pair_label")).group_by("date", "pair_label")
                        .agg(pl.sum("update_count").alias("updates")).with_columns(pl.sum("updates").over("date").alias("daily_total_updates"))
                        .with_columns((100 * pl.col("updates") / pl.col("daily_total_updates")).alias("share")).select("date", "pair_label", "share").collect().to_pandas())
top_labels = [f"{r['collector']}-{r['peer_asn']}" for r in top_pairs.to_dicts()] + ["Others"]
peer_plot_df = (peer_share.assign(date=pd.to_datetime(peer_share["date"])).pivot(index="date", 
                columns="pair_label", values="share").fillna(0).sort_index())
labels = [x for x in top_labels if x in peer_plot_df.columns]
peer_plot_df = peer_plot_df[labels]

plt.rcParams.update({"font.size": 11, "axes.labelsize": 12, "xtick.labelsize": 11, "ytick.labelsize": 11, "legend.fontsize": 10.5})
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 5.5), sharex=True, gridspec_kw={"height_ratios": [1.1, 1.0]})
upd_plot_df.plot.area(stacked=True, color=[BIN_COLORS[c] for c in upd_plot_df.columns], alpha=1, ax=ax1)
ax1.yaxis.set_major_locator(ticker.MultipleLocator(0.5e9))
ax1.yaxis.set_major_formatter(ticker.FuncFormatter(human_fmt))
ax1.set_ylabel("Total updates per day")
ax1.legend(title="Collector peers", loc="upper right", bbox_to_anchor=(0.682, 1.05), 
           ncol=4, frameon=False, fontsize=10.5, title_fontsize=11)
ax1.set_ylim(0, 4.5e9)

stack_colors = [PAIR_COLORS[i] if label != "Others" else OTHERS_COLOR for i, 
                label in enumerate(peer_plot_df.columns)]
ax2.stackplot(peer_plot_df.index, [peer_plot_df[c].values for c in peer_plot_df.columns], 
                labels=[simplify_label(x) for x in labels], colors=stack_colors, alpha=1)
ax2.yaxis.set_major_formatter(ticker.FuncFormatter(lambda y, _: f"{y:.0f}%"))
ax2.legend(loc="upper center", bbox_to_anchor=(0.24, 1.03), ncol=2, fontsize=9.8, frameon=True)
ax2.set_ylabel("Daily update share")
ax2.set_xlabel("Date")
ax2.set_ylim(0, 100)

locator = mdates.AutoDateLocator(maxticks=20)
ax2.xaxis.set_major_locator(locator)
ax2.xaxis.set_major_formatter(mdates.ConciseDateFormatter(locator))
ax2.set_xlim([START_DATE, END_DATE])

for ax, alpha in [(ax1, 0.35), (ax2, 0.15)]:
    ax.grid(True, which="both", linestyle="--", linewidth=0.35, alpha=alpha)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_position(("outward", 3))
    ax.spines["bottom"].set_position(("outward", 3))

ax1.tick_params(labelbottom=False)
plt.savefig(OUT_FIG, dpi=300, bbox_inches="tight", pad_inches=0.05)
plt.show()