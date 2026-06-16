from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import distinctipy

"""
Reproduce the top-1% noisy-prefix collector comparison figure.
Reads precomputed ECDF files from:
    data/cache/top1pct_prefix_ecdf/
"""

DATA_DIR = Path("/noisy-neighbors/data/cache/top1pct_prefix_ecdf")
OUT_FIG = Path("/noisy-neighbors/figures/top1pct_prefix_ecdf.png")
OUT_FIG.parent.mkdir(parents=True, exist_ok=True)

grouped_ecdf = {}
for csv_file in sorted(DATA_DIR.glob("ecdf_update_counts_*.csv")):
    label = (csv_file.stem.replace("ecdf_update_counts_", "").replace("_", "."))
    grouped_ecdf[label] = pd.read_csv(csv_file)

print(f"Loaded {len(grouped_ecdf)} ECDF files")

label_stats = {label: df["update_count"].sum() for label, df in grouped_ecdf.items()}
all_labels = sorted(label_stats,key=lambda x: (-label_stats[x], x == "rest"))
colors = distinctipy.get_colors(len(all_labels))

def human_format(x, pos):
    if x >= 1_000_000:
        return f"{int(x/1_000_000)}M"
    elif x >= 1_000:
        return f"{int(x/1_000)}K"
    return str(int(x))

plt.figure(figsize=(10, 3))
for label, color in zip(all_labels, colors):
    df = grouped_ecdf[label]
    plt.plot(df["update_count"],df["ecdf"],label=label,linewidth=2.5,color=color)
plt.xscale("log")
plt.xlabel("Update Counts per (Prefix, Collector) Pair")
plt.ylabel("ECDF")
plt.grid(True,which="both",linestyle="--",linewidth=0.5)
plt.legend(loc="upper left",fontsize="small",ncol=2)
plt.gca().xaxis.set_major_formatter(mticker.FuncFormatter(human_format))
plt.tight_layout()
plt.savefig(OUT_FIG,dpi=300)
plt.show()