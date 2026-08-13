#!/bin/sh
# Compare the live R1 bootloader with a locally built, symbol-bearing Nordic
# nRF5 SDK 17.1.0 secure-bootloader ELF. The SDK/toolchain are intentionally
# external inputs; see Docs/r1-bootloader-reconstruction/SDK-SOURCE-MANIFEST.md.

set -eu

script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
repo_root=$(CDPATH= cd -- "$script_dir/../.." && pwd)
reference_elf=${1:?usage: run_r1_bootloader_source_correlation.sh /path/reference.elf [output-dir]}
output_dir=${2:-$repo_root/docs/r1-bootloader-reconstruction/generated}
input_image=$repo_root/firmware/analysis/r1-live-2026-08-10/r1-bootloader-live.bin

expected_sha256=566cd2a50cd173680d314643e498202b364e4f8f8b6fd79b12ca71035e34ab8b
actual_sha256=$(shasum -a 256 "$input_image" | awk '{print $1}')
if [ "$actual_sha256" != "$expected_sha256" ]; then
    echo "refusing unknown R1 image: $actual_sha256" >&2
    exit 2
fi
if [ ! -f "$reference_elf" ]; then
    echo "reference ELF does not exist: $reference_elf" >&2
    exit 2
fi

if [ -n "${R1_GHIDRA_HEADLESS:-}" ]; then
    ghidra_headless=$R1_GHIDRA_HEADLESS
elif [ -x /opt/homebrew/opt/ghidra/libexec/support/analyzeHeadless ]; then
    ghidra_headless=/opt/homebrew/opt/ghidra/libexec/support/analyzeHeadless
else
    echo "set R1_GHIDRA_HEADLESS to Ghidra's support/analyzeHeadless" >&2
    exit 2
fi

if [ -n "${R1_JAVA_RUNTIME:-}" ]; then
    java_runtime=$R1_JAVA_RUNTIME
elif [ -x /opt/homebrew/opt/openjdk@21/bin/java ]; then
    java_runtime=/opt/homebrew/opt/openjdk@21
else
    echo "set R1_JAVA_RUNTIME to a Java 21 home" >&2
    exit 2
fi

project_dir=$(mktemp -d /tmp/r1-source-correlation.XXXXXX)
cleanup() {
    rm -rf -- "$project_dir"
}
trap cleanup EXIT HUP INT TERM

mkdir -p "$output_dir"
isolated_scripts=$project_dir/scripts
mkdir -p "$isolated_scripts"
cp "$repo_root/openCFW/tools/ghidra/SeedCortexMVectorTable.java" "$isolated_scripts/"
cp "$script_dir/R1BootloaderSeedKnownFunctions.java" "$isolated_scripts/"
cp "$script_dir/R1BootloaderApplyNames.java" "$isolated_scripts/"
cp "$script_dir/R1BootloaderBSimCompare.java" "$isolated_scripts/"

reference_name=$(basename -- "$reference_elf")

JAVA_HOME=$java_runtime "$ghidra_headless" \
    "$project_dir" r1_source_correlation \
    -import "$reference_elf" \
    -overwrite \
    -analysisTimeoutPerFile 300 \
    -max-cpu 8 \
    -log "$project_dir/reference-headless.log" \
    -scriptlog "$project_dir/reference-script.log"

JAVA_HOME=$java_runtime "$ghidra_headless" \
    "$project_dir" r1_source_correlation \
    -import "$input_image" \
    -overwrite \
    -loader BinaryLoader \
    -loader-baseAddr 0x000f8000 \
    -processor ARM:LE:32:Cortex \
    -cspec default \
    -scriptPath "$isolated_scripts" \
    -preScript SeedCortexMVectorTable.java 0x000f8000 0x000fe000 64 \
    -preScript R1BootloaderSeedKnownFunctions.java \
    -analysisTimeoutPerFile 300 \
    -max-cpu 8 \
    -postScript R1BootloaderApplyNames.java "$output_dir/function-names.csv" \
    -postScript R1BootloaderBSimCompare.java "/$reference_name" "$output_dir/source-correlations-raw.csv" \
    -log "$project_dir/correlation-headless.log" \
    -scriptlog "$project_dir/correlation-script.log"

cp "$project_dir/reference-headless.log" "$output_dir/reference-headless.log"
cp "$project_dir/reference-script.log" "$output_dir/reference-script.log"
cp "$project_dir/correlation-headless.log" "$output_dir/correlation-headless.log"
cp "$project_dir/correlation-script.log" "$output_dir/correlation-script.log"

perl -pi -e 's/[ \t]+$//' \
    "$output_dir/reference-headless.log" \
    "$output_dir/reference-script.log" \
    "$output_dir/correlation-headless.log" \
    "$output_dir/correlation-script.log"

python3 - "$output_dir/source-correlations-raw.csv" <<'PY'
import csv
import sys

path = sys.argv[1]
rows = list(csv.DictReader(open(path, encoding="utf-8")))
sources = {row["r1_entry"] for row in rows}
if len(rows) < 3000 or len(sources) < 250:
    raise SystemExit(
        f"suspiciously small BSim export: {len(rows)} rows for {len(sources)} functions"
    )
print(f"verified source correlation: {len(rows)} rows for {len(sources)} functions")
PY

shasum -a 256 \
    "$input_image" \
    "$reference_elf" \
    "$output_dir/source-correlations-raw.csv" \
    "$output_dir/function-names.csv" \
    > "$output_dir/source-correlation-sha256.txt"
