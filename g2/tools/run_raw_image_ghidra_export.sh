#!/bin/sh
# SPDX-License-Identifier: MIT
# Headless Ghidra whole-image export for a raw Cortex-M image.
#
# usage: run_raw_image_ghidra_export.sh <image.bin> <expected-sha256> <base> \
#            <language-id> <vector-words> <output-dir>
#
#   language-id   e.g. ARM:LE:32:Cortex (v6-M/v7-M) or ARM:LE:32:v8-m
#   vector-words  Cortex-M vector-table length in 32-bit words (0 for non-ARM
#                 images such as C-SKY: no vector seeding)
#
# Set OPENCFW_SEEDS to a g2/symbols/<payload>.tsv file to create and name the
# seeded functions before export.
#
# Needs GHIDRA_INSTALL_DIR (a Ghidra 12.1.x install) and Java 21. The image
# hash is checked first. Output: functions-*.jsonl, decomp/<entry>.c,
# census.txt, a copy of the analysis log, and SHA256SUMS.
set -eu

[ "$#" -eq 6 ] || { sed -n '3,12p' "$0" >&2; exit 2; }
image=$1; expected=$2; base=$3; language=$4; vectors=$5; out=$6
: "${GHIDRA_INSTALL_DIR:?set GHIDRA_INSTALL_DIR to a Ghidra install}"
headless=$GHIDRA_INSTALL_DIR/support/analyzeHeadless
scripts=$(CDPATH= cd -- "$(dirname -- "$0")/ghidra_scripts" && pwd)

actual=$(sha256sum "$image" | awk '{print $1}')
[ "$actual" = "$expected" ] || { echo "refusing image: expected $expected, got $actual" >&2; exit 2; }
size=$(wc -c < "$image")
end=$(printf '0x%X' $((base + size)))

project=$(mktemp -d "${TMPDIR:-/tmp}/opencfw-ghidra.XXXXXX")
trap 'rm -rf "$project"' EXIT HUP INT TERM
mkdir -p "$out"
set --
if [ "$vectors" -gt 0 ]; then
    set -- -preScript SeedCortexMVectorTable.java "$base" "$end" "$vectors"
fi
if [ -n "${OPENCFW_SEEDS:-}" ]; then
    set -- "$@" -postScript ApplySymbolSeeds.java "$OPENCFW_SEEDS"
fi

"$headless" "$project" export -import "$image" \
    -processor "$language" -loader BinaryLoader -loader-baseAddr "$base" \
    -scriptPath "$scripts" \
    "$@" \
    -postScript ReportProgramCensus.java \
    -postScript ExportAllFunctionDecomp.java "$out" \
    -deleteProject > "$out/analysis.log" 2>&1 || { tail -40 "$out/analysis.log" >&2; exit 1; }

grep -h "ReportProgramCensus.java>\\|ApplySymbolSeeds.java>" "$out/analysis.log" | sed "s/.*> //" > "$out/census.txt" || true
# Drop run-specific paths from the log so the evidence is host-independent.
repo=$(CDPATH= cd -- "$(dirname -- "$0")/../.." && pwd)
image_dir=$(CDPATH= cd -- "$(dirname -- "$image")" && pwd)
sed -i "s|$project|<project>|g; s|$GHIDRA_INSTALL_DIR|<ghidra>|g; s|$image_dir/|<image-dir>/|g; s|$repo/|<repo>/|g" "$out/analysis.log"
seeds_name=
if [ -n "${OPENCFW_SEEDS:-}" ]; then seeds_name=$(basename "$OPENCFW_SEEDS"); fi
cat > "$out/RUN.json" <<EOF
{"image_sha256": "$expected", "image_size": $size, "base": "$base", "language": "$language",
 "vector_words": $vectors, "ghidra": "$(basename "$GHIDRA_INSTALL_DIR")",
 "seeds": "$seeds_name"}
EOF
( cd "$out" && find . -type f ! -name SHA256SUMS ! -name analysis.log | sed 's|^\./||' | LC_ALL=C sort | xargs sha256sum > SHA256SUMS )
echo "exported $(ls "$out"/decomp | wc -l) functions to $out"
