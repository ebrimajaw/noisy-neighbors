from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import FuncFormatter, NullLocator, NullFormatter
from matplotlib.patches import Patch

"""
noisy-neighbors/data/cache/session_daily_update_share.parquet
    Daily update-share table for the top 19 BGP sessions and
    the aggregate Rest category during December 2021.

    Computed from all observed announcements in Route Views
    update files during December 2021.

    Rows represent daily observations.
    Columns represent BGP sessions and Rest.
    Values represent percentage share of updates.

    Used to reproduce the session-share figure.
"""

CACHE_FILE = Path("/home/ebrima/disk2/noisy-neighbors/data/cache/session_daily_update_share.parquet")
OUT_FIG = Path("/home/ebrima/disk2/noisy-neighbors/figures/session_share.png")
OUT_FIG.parent.mkdir(parents=True, exist_ok=True)

XLAB_FONTSIZE = 24
YLAB_FONTSIZE = 24
XTICK_FONTSIZE = 20
YTICK_FONTSIZE = 20
LEGEND_FONTSIZE = 21
LEGEND_TITLE_SIZE = 20

COLORS = ["#1C2B3A", "#F8075C", "maroon", "#F11F07", "#2E4057","#0197FB", 
          "#040404", "navy", "darkgreen", "goldenrod","purple", "#D3D3D3", "#FF8C00", 
          "#008080", "#A52A2A", "#4B0082", "#228B22", "#FFD700", "#8B4513", "#708090",]

def compact_mask(session):
    if session == "Rest":
        return "Rest"
    try:
        asn, addr = session.split("-", 1)
    except ValueError:
        return session

    if ":" in addr:
        parts = [p for p in addr.split(":") if p]
        return f"{asn}-{parts[0]}.*.{parts[-1]}" if parts else session

    octs = addr.split(".")
    return f"{asn}-{octs[0]}.*.{octs[-1]}" if len(octs) >= 2 else session


if not CACHE_FILE.exists():
    raise FileNotFoundError(f"Missing cache file: {CACHE_FILE}")

pivot_pct = pd.read_parquet(CACHE_FILE)
pivot_pct.index = pd.to_datetime(pivot_pct.index)

col_means = pivot_pct.mean().sort_values(ascending=False)
cols_order = [c for c in col_means.index if c != "Rest"] + (["Rest"] if "Rest" in pivot_pct.columns else [])
pivot_pct = pivot_pct[cols_order]
color_map = {col: COLORS[i % len(COLORS)] for i, col in enumerate(pivot_pct.columns)}
display_labels = {col: compact_mask(col) for col in pivot_pct.columns}

fig, ax = plt.subplots(figsize=(20.1, 7.2))
pivot_pct.plot.area(ax=ax,stacked=True,linewidth=0,alpha=1.0,color=[color_map[c] for c in pivot_pct.columns],legend=False,)
ax.set_ylim(0, 100)
ax.set_yticks([0, 20, 40, 60, 80, 100])
ax.yaxis.set_major_formatter(FuncFormatter(lambda y, _: f"{y:.0f}%"))
ax.tick_params(axis="y", labelsize=YTICK_FONTSIZE)

xmin = max(pd.Timestamp("2021-12-03"), pivot_pct.index.min().normalize())
xmax = pivot_pct.index.max().normalize()

ax.set_xlim(xmin, xmax)
ax.xaxis.set_major_locator(mdates.DayLocator(interval=3))
ax.xaxis.set_major_formatter(mdates.DateFormatter("%b-%d"))
ax.xaxis.set_minor_locator(NullLocator())
ax.xaxis.set_minor_formatter(NullFormatter())
ax.tick_params(axis="x", labelsize=XTICK_FONTSIZE)

for lab in ax.get_xticklabels(which="major"): lab.set_rotation(0)
ax.set_ylabel("Update share of BGP sessions", fontsize=YLAB_FONTSIZE)
ax.set_xlabel("Date (December, 2021)", fontsize=XLAB_FONTSIZE)
pos = ax.get_position()
ax.set_position([pos.x0, pos.y0, pos.width, pos.height * 0.88])
handles = [Patch(facecolor=color_map[c], edgecolor="none", label=display_labels[c]) for c in pivot_pct.columns]

fig.legend(handles=handles,ncol=4,fontsize=LEGEND_FONTSIZE,title_fontsize=LEGEND_TITLE_SIZE,
           loc="upper right",bbox_to_anchor=(0.902, 1.19),bbox_transform=fig.transFigure,frameon=True,)
plt.savefig(OUT_FIG, dpi=300, bbox_inches="tight", pad_inches=0.05)
plt.show()