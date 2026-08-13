#!/bin/sh
# Reproduce the whole-image R1 bootloader census and mechanical C export.

set -eu

script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
repo_root=$(CDPATH= cd -- "$script_dir/../.." && pwd)
input_image=${1:-$repo_root/firmware/analysis/r1-live-2026-08-10/r1-bootloader-live.bin}
output_dir=${2:-$repo_root/docs/r1-bootloader-reconstruction/generated}

expected_sha256=566cd2a50cd173680d314643e498202b364e4f8f8b6fd79b12ca71035e34ab8b
actual_sha256=$(shasum -a 256 "$input_image" | awk '{print $1}')
if [ "$actual_sha256" != "$expected_sha256" ]; then
    echo "refusing unknown image: expected $expected_sha256, got $actual_sha256" >&2
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

project_dir=$(mktemp -d /tmp/r1-bootloader-ghidra.XXXXXX)
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
cp "$script_dir/R1BootloaderWholeImageExport.java" "$isolated_scripts/"

JAVA_HOME=$java_runtime "$ghidra_headless" \
    "$project_dir" r1_bootloader \
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
    -postScript R1BootloaderWholeImageExport.java "$output_dir" \
    -log "$project_dir/ghidra-headless.log" \
    -scriptlog "$project_dir/ghidra-script.log"

cp "$project_dir/ghidra-headless.log" "$output_dir/ghidra-headless.log"
cp "$project_dir/ghidra-script.log" "$output_dir/ghidra-script.log"

# Ghidra emits trailing spaces in C and logs. Normalize them so the durable
# corpus is diff-clean without changing any code or evidence content.
perl -pi -e 's/[ \t]+$//' \
    "$output_dir/r1_bootloader_ghidra.c" \
    "$output_dir/ghidra-headless.log" \
    "$output_dir/ghidra-script.log"

python3 - "$output_dir/summary.json" <<'PY'
import json
import sys

summary_path = sys.argv[1]
with open(summary_path, encoding="utf-8") as handle:
    summary = json.load(handle)

expected = {
    "image_base": "0x000f8000",
    "logical_end_exclusive": "0x000fdf64",
    "dump_end_exclusive": "0x000fe000",
    "logical_bytes": 24420,
    "dump_bytes": 24576,
    "decompile_failures": 0,
}
for key, value in expected.items():
    if summary.get(key) != value:
        raise SystemExit(f"unexpected {key}: {summary.get(key)!r} != {value!r}")
if summary.get("function_count", 0) < 250:
    raise SystemExit(f"suspiciously low function count: {summary.get('function_count')}")
print(
    "verified R1 export: "
    f"{summary['function_count']} functions, "
    f"{summary['decompile_failures']} decompiler failures"
)
PY

shasum -a 256 \
    "$input_image" \
    "$output_dir/summary.json" \
    "$output_dir/vectors.csv" \
    "$output_dir/functions.csv" \
    "$output_dir/callgraph.csv" \
    "$output_dir/instructions.tsv" \
    "$output_dir/defined-data.csv" \
    "$output_dir/symbols.csv" \
    "$output_dir/function-names.csv" \
    "$output_dir/r1_bootloader_ghidra.c" \
    > "$output_dir/artifact-sha256.txt"
