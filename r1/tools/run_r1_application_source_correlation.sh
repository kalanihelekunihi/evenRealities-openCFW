#!/bin/sh
# Compare the SHA-pinned R1 application with a symbol-bearing Nordic SDK
# reference ELF. Candidate matches are evidence only and require corroboration.

set -eu

script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
repo_root=$(CDPATH= cd -- "$script_dir/../.." && pwd)
reference_elf=${1:?usage: run_r1_application_source_correlation.sh /path/reference.elf [output-dir] [reference-start] [reference-end]}
output_dir=${2:-$repo_root/docs/r1-open-firmware/generated/application-source-correlation}
reference_start=${3:-0x000f8000}
reference_end=${4:-0x000fe000}
input_image=$repo_root/firmware/analysis/r1-2.2.6.0009/application.bin
function_inventory=$repo_root/research/decompilation/application/functions.csv

mkdir -p "$output_dir"
output_dir=$(CDPATH= cd -- "$output_dir" && pwd)

expected_sha256=0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a
actual_sha256=$(shasum -a 256 "$input_image" | awk '{print $1}')
if [ "$actual_sha256" != "$expected_sha256" ]; then
    echo "refusing unknown R1 application: $actual_sha256" >&2
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
elif [ -d /opt/homebrew/opt/openjdk@21/libexec/openjdk.jdk/Contents/Home ]; then
    java_runtime=/opt/homebrew/opt/openjdk@21/libexec/openjdk.jdk/Contents/Home
else
    echo "set R1_JAVA_RUNTIME to a Java 21 home" >&2
    exit 2
fi

project_dir=$(mktemp -d /tmp/r1-application-correlation.XXXXXX)
cleanup() {
    rm -rf -- "$project_dir"
}
trap cleanup EXIT HUP INT TERM

isolated_scripts=$project_dir/scripts
mkdir -p "$isolated_scripts"
cp "$script_dir/R1Init.java" "$isolated_scripts/"
cp "$script_dir/R1SeedFunctionsFromCsv.java" "$isolated_scripts/"
cp "$script_dir/R1BootloaderBSimCompare.java" "$isolated_scripts/"

reference_name=$(basename -- "$reference_elf")
JAVA_HOME=$java_runtime "$ghidra_headless" \
    "$project_dir" r1_application_correlation \
    -import "$reference_elf" \
    -overwrite \
    -analysisTimeoutPerFile 300 \
    -max-cpu 8 \
    -log "$project_dir/reference-headless.log" \
    -scriptlog "$project_dir/reference-script.log"

JAVA_HOME=$java_runtime "$ghidra_headless" \
    "$project_dir" r1_application_correlation \
    -import "$input_image" \
    -overwrite \
    -loader BinaryLoader \
    -loader-baseAddr 0x00027000 \
    -processor ARM:LE:32:Cortex \
    -cspec default \
    -scriptPath "$isolated_scripts" \
    -preScript R1Init.java \
    -preScript R1SeedFunctionsFromCsv.java "$function_inventory" \
    -analysisTimeoutPerFile 600 \
    -max-cpu 8 \
    -postScript R1BootloaderBSimCompare.java \
        "/$reference_name" "$output_dir/source-correlations-raw.csv" \
        0x00027000 0x000c4d08 "$reference_start" "$reference_end" \
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
if len(rows) < 20000 or len(sources) < 1800:
    raise SystemExit(
        f"suspiciously small application BSim export: {len(rows)} rows for {len(sources)} functions"
    )
print(f"verified application source correlation: {len(rows)} rows for {len(sources)} functions")
PY

shasum -a 256 \
    "$input_image" \
    "$reference_elf" \
    "$output_dir/source-correlations-raw.csv" \
    > "$output_dir/source-correlation-sha256.txt"
