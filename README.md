# Noisy Neighbours: Keep the Neighbourhood Quiet

This repository contains the artifacts accompanying the paper:
**Noisy Neighbours: Keep the Neighbourhood Quiet**
Ebrima Jaw, Thomas Krenc, Moritz Müller, Kc Claffy, Lambert Nieuwenhuis, and Cristian Hesselman.
Published at the **21st International Conference on Network and Service Management (CNSM 2025)**.
Paper: https://ieeexplore.ieee.org/document/11297542/
DOI: https://doi.org/10.23919/CNSM67658.2025.11297542

---
## Overview

This repository provides the processed datasets and plotting scripts used to reproduce the analyses and figures presented in the paper.
The artifacts are derived from publicly available BGP update data collected by Route Views route collectors. 
We only provided processed artifacts rather than the complete raw MRT archives due storage requirements, 
Researchers interested in the full raw datasets, intermediate processing outputs, or additional artifacts can contact the authors.

---
## Repository Structure
```text
data/
├── collector_peer_daily_bins.parquet
├── collector_peer_bins/
└── cache/
    ├── asp_vals.sorted.npy
    ├── prefix_vals.sorted.npy
    ├── pivot_pct.session_share.minute.parquet
    ├── origin_as_prefix_variability_2021.csv
    ├── origin_as_prefix_variability_2024.csv
    └── top1pct_prefix_ecdf/
scripts/
├── collector_peer_share.py
├── collector_share.py
├── pfx.aspath_update_sahre.py
├── session_share.py
├── noisy_prefixes_py
├── rvs_score_py
├── origin_as_prefix_variability.py
└── download_routeviews_202112.sh
figures/
```
---

## Artifact Description

### collector_peer_daily_bins.parquet

Daily collector-peer rankings computed from Route Views update data.
Columns:
* `date`
* `collector`
* `peer_asn`
* `update_count`
* `daily_rank`
* `daily_percentile`
* `percentile_bin`

This dataset is used for the collector-peer concentration analysis presented in the paper.

---

### collector_peer_bins/
Precomputed percentile-bin datasets derived from `collector_peer_daily_bins.parquet`.
Files:
* `p95_100.parquet`
* `p75_95.parquet`
* `p50_75.parquet`
* `p00_50.parquet`

Each file contains all collector-peer pairs assigned to the corresponding percentile range across the entire observation period.
These files enable rapid exploration of collector-peer behaviour without repeatedly filtering the full dataset.

---

### cache/asp_vals.sorted.npy
Sorted update-count vector for all observed AS paths.
Each element represents the total number of updates associated with a unique AS path.
Computed from all observed announcements in Route Views update files.
Used to reproduce the AS-path update concentration analysis.

---

### cache/prefix_vals.sorted.npy
Sorted update-count vector for all observed prefixes.
Each element represents the total number of updates associated with a unique prefix.
Computed from all observed announcements in Route Views update files.
Used to reproduce the prefix update concentration analysis.

---
### cache/session_daily_update_share.parquet

Precomputed session-share matrix used to reproduce the session dominance analysis.
Rows correspond to observation dates.
Columns correspond to the most active BGP sessions together with an aggregated `Rest` category.
Values represent the percentage contribution of each session to the total update volume on a given day.

---

### cache/origin_as_prefix_variability_2021.csv

Per-origin-AS variability metrics for December 2021.
Columns:

* `origin_as`
* `prefix_count`
* `cv_mean_within_as`
* `as_prefix_cv_stddev`
* `as_prefix_cv_range`
* `total_updates`
Used to reproduce the December 2021 variability analysis.

---

### cache/origin_as_prefix_variability_2024.csv
Same metrics as above for December 2024.
Used to reproduce the December 2024 variability analysis.

---

### cache/top1pct_prefix_ecdf/
Precomputed ECDF datasets used to reproduce the noisy-prefix comparison across Route Views collectors
The datasets correspond to the top 1% noisiest prefixes identified from the Perth collector and subsequently evaluated across multiple collectors.

Files:
* `ecdf_update_counts_rvs3.csv`
* `ecdf_update_counts_rvs4.csv`
* `ecdf_update_counts_rvs_amsix.csv`
* `ecdf_update_counts_rvs_eqix.csv`
* `ecdf_update_counts_rvs_linx.csv`
* `ecdf_update_counts_rvs_napafrica.csv`
* `ecdf_update_counts_rvs_perth.csv`
* `ecdf_update_counts_rvs_saopaulo2.csv`
* `ecdf_update_counts_rvs_sg.csv`
* `ecdf_update_counts_rest.csv`
Columns:

* `update_count` — aggregated update count for a prefix–collector pair.
* `ecdf` — empirical cumulative distribution value.

These files are used to reproduce the collector comparison analysis presented in Figure 6.

### cache/ecdf_update_counts_*.csv
Precomputed ECDF datasets used for the noisy-prefix comparison across collectors.
Columns:
* `update_count`
* `ecdf`
These files are used to reproduce the collector comparison analysis presented in the paper.

---

### scripts/download_routeviews_202112.sh

Example downloader for obtaining the December 2021 Route Views
update archives used in this study. It downloads Route Views MRT update files 
archive and stores them in collector-specific directories.

Researchers requiring the complete raw dataset can use this script
as a starting point or contact the authors.

## Reproducing Figures

The repository contains plotting notebooks and scripts that operate directly on the supplied artifacts.
The provided datasets are sufficient to reproduce all figures presented in the paper without downloading the original MRT archives.

---

## Data Availability
All underlying BGP update data originate from the public Route Views project:
https://www.routeviews.org/

The processed artifacts distributed in this repository were derived from these publicly available datasets.
Researchers interested in the complete raw MRT files or additional processing outputs may contact the authors.

---
## Citation
If you use these artifacts, please cite:
```bibtex
@inproceedings{jaw_noisy_2025,
    title = {Noisy Neighbours: Keep the Neighbourhood Quiet},
    url = {https://ieeexplore.ieee.org/document/11297542/},
    doi = {10.23919/CNSM67658.2025.11297542},
    shorttitle = {Noisy Neighbours},
    eventtitle = {2025 21st International Conference on Network and Service Management (CNSM)},
    pages = {1--9},
    booktitle = {2025 21st International Conference on Network and Service Management (CNSM)},
    author = {Jaw, Ebrima and Krenc, Thomas and Müller, Moritz and Claffy, Kc and Nieuwenhuis, Lambert and Hesselman, Cristian},
    date = {2025-10}
}
```

---
## Contact
For questions regarding the artifacts, reproducibility, or access to additional datasets, please contact:
**Ebrima Jaw**
University of Twente
Email: [ejaw@utg.edu.gm](mailto:ejaw@utg.edu.gm)
