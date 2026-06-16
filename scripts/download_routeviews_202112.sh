#!/usr/bin/env bash

set -euo pipefail

BASE_URL="https://archive.routeviews.org"
MONTH="2021.12"
START_DATE="2021-12-01"
END_DATE="2021-12-31"
OUTDIR="/home/ebrima/disk2/noisy-neighbors/data/raw/routeviews_202112"
JOBS=8

mkdir -p "$OUTDIR"

declare -A COLLECTORS=(
  ["routeviews2"]="bgpdata"
  ["routeviews.amsix"]="route-views.amsix/bgpdata"
  ["routeviews.eqix"]="route-views.eqix/bgpdata"
  ["routeviews.isc"]="route-views.isc/bgpdata"
  ["routeviews.jinx"]="route-views.jinx/bgpdata"
  ["routeviews.kixp"]="route-views.kixp/bgpdata"
  ["routeviews.linx"]="route-views.linx/bgpdata"
  ["routeviews.napafrica"]="route-views.napafrica/bgpdata"
  ["routeviews.nwax"]="route-views.nwax/bgpdata"
  ["routeviews.perth"]="route-views.perth/bgpdata"
  ["routeviews.phoix"]="route-views.phoix/bgpdata"
  ["routeviews.saopaulo"]="route-views.saopaulo/bgpdata"
  ["routeviews.saopaulo2"]="route-views.saopaulo2/bgpdata"
  ["routeviews.sg"]="route-views.sg/bgpdata"
  ["routeviews.sfmix"]="route-views.sfmix/bgpdata"
  ["routeviews.soxrs"]="route-views.soxrs/bgpdata"
  ["routeviews.sydney"]="route-views.sydney/bgpdata"
  ["routeviews.telxatl"]="route-views.telxatl/bgpdata"
  ["routeviews.wide"]="route-views.wide/bgpdata"
  ["routeviews.routeviews3"]="route-views.routeviews3/bgpdata"
  ["routeviews.routeviews4"]="route-views.routeviews4/bgpdata"
  ["routeviews.routeviews5"]="route-views.routeviews5/bgpdata"
  ["routeviews.routeviews6"]="route-views.routeviews6/bgpdata")

MANIFEST="$OUTDIR/download_manifest.txt"
: > "$MANIFEST"

current="$START_DATE"

while [[ "$current" < "$(date -I -d "$END_DATE + 1 day")" ]]; do
  ymd=$(date -d "$current" +%Y%m%d)

  for hh in {00..23}; do
    for mm in 00 15 30 45; do
      file="updates.${ymd}.${hh}${mm}.bz2"

      for collector in "${!COLLECTORS[@]}"; do
        relpath="${COLLECTORS[$collector]}"
        url="${BASE_URL}/${relpath}/${MONTH}/UPDATES/${file}"
        outdir="${OUTDIR}/${collector}"
        outfile="${outdir}/${file}"

        mkdir -p "$outdir"
        [[ -f "$outfile" ]] && continue

        printf '%s\t%s\n' "$url" "$outfile" >> "$MANIFEST"
      done
    done
  done
  current=$(date -I -d "$current + 1 day")
done

echo "Download manifest: $MANIFEST"
echo "Files to download: $(wc -l < "$MANIFEST")"
echo "Output directory: $OUTDIR"

cat "$MANIFEST" | xargs -P "$JOBS" -n 2 bash -c '
  url="$1"
  outfile="$2"
  tmp="${outfile}.tmp"

  wget -q -c -O "$tmp" "$url" && mv "$tmp" "$outfile" || {
    rm -f "$tmp"
    echo "Failed: $url" >&2
  }
' _

echo "Done."
