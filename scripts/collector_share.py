from pathlib import Path
import numpy as np
import pandas as pd
import polars as pl
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import FuncFormatter, MultipleLocator, LogLocator, NullFormatter

"""
Reproduce the collector-level update-share figure using
collector_peer_daily_bins.parquet.
"""

DATA = Path("/home/savymik/noisy-neighbors/data/collector_peer_daily_bins.parquet")
OUT_FIG = Path("/home/savymik/noisy-neighbors/figures/collector_share_plot.png")
OUT_DATA = Path("/home/savymik/noisy-neighbors/data/monthly_aggregated_collector_updates.csv")
OUT_TOP = Path("/home/savymik/noisy-neighbors/data/top_collectors_75percent.csv")

TOP_N = 11
START_X = pd.Timestamp("2011-11-01")
END_X = pd.Timestamp("2026-01-01")

COLORS = ["#1C2B3A", "#F8075C", "maroon", "#F11F07", "#2E4057", "#0197FB", 
          "#040404", "navy", "darkgreen", "goldenrod", "purple", "#D3D3D3",]

OUT_FIG.parent.mkdir(parents=True, exist_ok=True)
def human_fmt(x, _):
    if x >= 1e9:
        return f"{x / 1e9:.0f}B" if x % 1e9 == 0 else f"{x / 1e9:.1f}B"
    if x >= 1e6:
        return f"{x / 1e6:.0f}M"
    if x >= 1e3:
        return f"{x / 1e3:.0f}K"
    return str(int(x))

collector_daily = (pl.scan_parquet(DATA).group_by("date", "collector").agg(pl.sum("update_count").alias("updates")).with_columns(pl.col("collector").str.replace_all("routeviews.", "rvs.", 
                                                    literal=True).str.replace_all("rvs.routeviews", "rvs", 
                                                    literal=True).alias("collector")).collect().to_pandas())
collector_daily["date"] = pd.to_datetime(collector_daily["date"])
collector_pivot = (collector_daily.pivot(index="date", columns="collector", 
                    values="updates").fillna(0).sort_index())
collector_resampled = collector_pivot.resample("6M").sum()
collector_resampled.to_csv(OUT_DATA)

collector_avg = collector_resampled.mean().sort_values(ascending=False)
top_collectors = collector_avg.head(TOP_N).index.tolist()
df_top = collector_resampled[top_collectors].copy()
df_top["rest"] = collector_resampled[[c for c in collector_resampled.columns if c not in top_collectors]].sum(axis=1)
cutoff = collector_avg.cumsum() <= 0.75 * collector_avg.sum()
top_75 = list(collector_avg[cutoff].index)

if len(top_75) < len(collector_avg): top_75.append(collector_avg.index[len(top_75)])

pd.DataFrame({"collector": top_75,"mean_updates_per_6month_bin": [collector_avg[c] for c in top_75],
              "percentage_share": [collector_avg[c] / collector_avg.sum() * 100 for c in top_75],}).to_csv(OUT_TOP, index=False)
df_percent = df_top.divide(df_top.sum(axis=1), axis=0).fillna(0) * 100
timestamps = df_top.index
bar_width = ((timestamps[1:] - timestamps[:-1]).median()if len(timestamps) > 1 else pd.Timedelta(days=180)) / 1.35
colors = COLORS[: len(df_top.columns)]

plt.rcParams.update({"font.size": 10.5,"axes.labelsize": 11,"axes.titlesize": 12,"legend.fontsize": 9,})
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 5), sharex=True, gridspec_kw={"height_ratios": [1.15, 1]})
bottom = np.zeros(len(df_top))
for col, color in zip(df_top.columns, colors):
    ax1.bar(timestamps, df_top[col], bottom=bottom, width=bar_width,label=col, color=color, align="center", linewidth=0)
    bottom += df_top[col].values
ax1.set_ylabel("Update count per\n collector (log)")
ax1.set_yscale("log")
ax1.yaxis.set_major_locator(LogLocator(base=10, subs=(1, 2, 5), numticks=10))
ax1.yaxis.set_minor_formatter(NullFormatter())
ax1.yaxis.set_major_formatter(FuncFormatter(human_fmt))
ax1.grid(True, which="major", linestyle="--", linewidth=0.35, alpha=0.2)

bottom = np.zeros(len(df_percent))
for col, color in zip(df_percent.columns, colors):
    ax2.bar(timestamps, df_percent[col], bottom=bottom, width=bar_width,color=color, align="center", linewidth=0)
    bottom += df_percent[col].values

ax2.set_ylabel("Collector share (%)")
ax2.set_xlabel("Date")
ax2.set_ylim(0, 100)
ax2.yaxis.set_major_locator(MultipleLocator(20))
ax2.yaxis.set_minor_locator(MultipleLocator(10))
ax2.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{int(v)}%"))
ax2.grid(True, which="major", linestyle="--", linewidth=0.35, alpha=0.2)

ax2.xaxis.set_major_locator(mdates.YearLocator(1))
ax2.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
ax2.xaxis.set_minor_locator(mdates.MonthLocator(bymonth=[6, 12]))
ax2.set_xlim(START_X, END_X)

plt.setp(ax2.xaxis.get_majorticklabels(), rotation=0, ha="center")
handles, labels = ax1.get_legend_handles_labels()
fig.legend(handles, labels,loc="upper left",bbox_to_anchor=(0.05, 0.99),ncol=6,
           frameon=True,columnspacing=0.9,handlelength=1.2,fontsize=14.5,)
plt.subplots_adjust(top=0.83, left=0.06, right=0.99, hspace=0.16)
plt.margins(x=0.01)
plt.savefig(OUT_FIG, dpi=300, bbox_inches="tight", pad_inches=0.05)
plt.show()