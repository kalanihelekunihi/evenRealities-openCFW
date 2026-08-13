#!/usr/bin/env bash
# Run independent headless Ghidra projects with bounded concurrency.

set -uo pipefail

: "${GHIDRA_HEADLESS:?set GHIDRA_HEADLESS}"
: "${JAVA_HOME:?set JAVA_HOME}"
: "${FIRMWARE:?set FIRMWARE}"
: "${GHIDRA_SCRIPT_DIR:?set GHIDRA_SCRIPT_DIR}"
: "${MANIFEST:?set MANIFEST}"
: "${OUTPUT_DIR:?set OUTPUT_DIR}"

JOBS="${JOBS:-16}"
PROCESSOR="${PROCESSOR:-ARCompact:LE:32:default}"
LOADER="${LOADER:-BinaryLoader}"
BASE_ADDRESS="${BASE_ADDRESS:-0x301fdc}"
ANALYSIS_TIMEOUT="${ANALYSIS_TIMEOUT:-120}"
FULL_ANALYSIS="${FULL_ANALYSIS:-0}"

if [[ ! "$JOBS" =~ ^[1-9][0-9]*$ ]]; then
    echo "JOBS must be a positive integer" >&2
    exit 2
fi
if [[ "$FULL_ANALYSIS" != 0 && "$FULL_ANALYSIS" != 1 ]]; then
    echo "FULL_ANALYSIS must be 0 (targeted scripts only) or 1" >&2
    exit 2
fi
analysis_args=(-noanalysis)
if [[ "$FULL_ANALYSIS" == 1 ]]; then
    analysis_args=()
fi
for path in "$GHIDRA_HEADLESS" "$FIRMWARE" "$MANIFEST"; do
    if [[ ! -f "$path" ]]; then
        echo "required file missing: $path" >&2
        exit 2
    fi
done
if [[ ! -d "$GHIDRA_SCRIPT_DIR" ]]; then
    echo "required script directory missing: $GHIDRA_SCRIPT_DIR" >&2
    exit 2
fi
required_scripts=(
    DisassembleArcompactRange.java
    DumpInstructionsAround.java
    CreateAndDumpFunctions.java
)
for script in "${required_scripts[@]}"; do
    if [[ ! -f "$GHIDRA_SCRIPT_DIR/$script" ]]; then
        echo "required Ghidra script missing: $GHIDRA_SCRIPT_DIR/$script" >&2
        exit 2
    fi
done
if [[ -d "$OUTPUT_DIR" ]] && find "$OUTPUT_DIR" -mindepth 1 -print -quit | grep -q .; then
    echo "OUTPUT_DIR must be absent or empty: $OUTPUT_DIR" >&2
    exit 2
fi
if ! awk -F '\t' '
    /^#/ || NF == 0 { next }
    NF != 4 || $1 !~ /^[A-Za-z0-9._-]+$/ ||
        $2 !~ /^0x[0-9A-Fa-f]+$/ || $3 !~ /^0x[0-9A-Fa-f]+$/ ||
        $4 !~ /^0x[0-9A-Fa-f]+$/ || seen[$1]++ { exit 1 }
' "$MANIFEST"; then
    echo "manifest must contain unique safe IDs and three hexadecimal addresses" >&2
    exit 2
fi

if command -v sha256sum >/dev/null 2>&1; then
    sha256_file() { sha256sum "$1" | awk '{print $1}'; }
elif command -v shasum >/dev/null 2>&1; then
    sha256_file() { shasum -a 256 "$1" | awk '{print $1}'; }
else
    echo "sha256sum or shasum is required" >&2
    exit 2
fi

timestamp_ns() {
    local value
    value="$(date +%s%N)"
    if [[ "$value" =~ ^[0-9]+$ ]]; then
        printf '%s\n' "$value"
    else
        python3 -c 'import time; print(time.time_ns())'
    fi
}

mkdir -p "$OUTPUT_DIR/logs" "$OUTPUT_DIR/projects" "$OUTPUT_DIR/status"
{
    printf 'jobs\t%s\n' "$JOBS"
    printf 'processor\t%s\n' "$PROCESSOR"
    printf 'loader\t%s\n' "$LOADER"
    printf 'base_address\t%s\n' "$BASE_ADDRESS"
    printf 'analysis_timeout_seconds\t%s\n' "$ANALYSIS_TIMEOUT"
    printf 'full_analysis\t%s\n' "$FULL_ANALYSIS"
} >"$OUTPUT_DIR/CONFIG.tsv"
{
    printf '%s\trunner\n' "$(sha256_file "$0")"
    printf '%s\tfirmware\n' "$(sha256_file "$FIRMWARE")"
    printf '%s\tmanifest\n' "$(sha256_file "$MANIFEST")"
    printf '%s\tconfiguration\n' "$(sha256_file "$OUTPUT_DIR/CONFIG.tsv")"
    for script in "${required_scripts[@]}"; do
        printf '%s\t%s\n' "$(sha256_file "$GHIDRA_SCRIPT_DIR/$script")" "$script"
    done
} >"$OUTPUT_DIR/INPUTS.tsv"

run_shard() {
    local shard_id="$1"
    local entry="$2"
    local start="$3"
    local end="$4"
    local project_dir="$OUTPUT_DIR/projects/$shard_id"
    local log="$OUTPUT_DIR/logs/$shard_id.log"
    local began ended status
    began="$(timestamp_ns)"
    mkdir -p "$project_dir"
    (
        export JAVA_HOME
        "$GHIDRA_HEADLESS" "$project_dir" "$shard_id" \
            -import "$FIRMWARE" \
            -overwrite \
            -processor "$PROCESSOR" \
            -loader "$LOADER" \
            -loader-baseAddr "$BASE_ADDRESS" \
            -analysisTimeoutPerFile "$ANALYSIS_TIMEOUT" \
            "${analysis_args[@]}" \
            -scriptPath "$GHIDRA_SCRIPT_DIR" \
            -postScript DisassembleArcompactRange.java "$start" "$end" \
            -postScript DumpInstructionsAround.java 64 "$entry" \
            -postScript CreateAndDumpFunctions.java "$entry" \
            -deleteProject
    ) >"$log" 2>&1
    status=$?
    ended="$(timestamp_ns)"
    printf '%s\t%s\t%s\t%s\t%s\t%s\n' \
        "$shard_id" "$entry" "$start" "$end" "$status" "$((ended - began))" \
        >"$OUTPUT_DIR/status/$shard_id.tsv"
    return "$status"
}

active=0
pids=()
while IFS=$'\t' read -r shard_id entry start end; do
    [[ -z "$shard_id" || "$shard_id" == \#* ]] && continue
    run_shard "$shard_id" "$entry" "$start" "$end" &
    pids+=("$!")
    active=$((active + 1))
    if (( active >= JOBS )); then
        wait "${pids[0]}" || true
        pids=("${pids[@]:1}")
        active=$((active - 1))
    fi
done <"$MANIFEST"
for pid in "${pids[@]}"; do
    wait "$pid" || true
done

{
    printf 'shard_id\tentry\tstart\tend\texit_status\tduration_ns\n'
    find "$OUTPUT_DIR/status" -type f -name '*.tsv' -print0 \
        | sort -z \
        | xargs -0 -r cat
} >"$OUTPUT_DIR/results.tsv"

(
    cd "$OUTPUT_DIR" || exit 1
    while IFS= read -r -d '' file; do
        printf '%s  %s\n' "$(sha256_file "$file")" "$file"
    done < <(find logs status -type f -print0 | sort -z)
    printf '%s  %s\n' "$(sha256_file CONFIG.tsv)" CONFIG.tsv
    printf '%s  %s\n' "$(sha256_file INPUTS.tsv)" INPUTS.tsv
    printf '%s  %s\n' "$(sha256_file results.tsv)" results.tsv
) >"$OUTPUT_DIR/SHA256SUMS"

failed="$(awk -F '\t' 'NR > 1 && $5 != 0 { count += 1 } END { print count + 0 }' "$OUTPUT_DIR/results.tsv")"
printf 'GHIDRA_SHARD_BATCH shards=%s failed=%s jobs=%s output=%s\n' \
    "$(( $(wc -l <"$OUTPUT_DIR/results.tsv") - 1 ))" "$failed" "$JOBS" "$OUTPUT_DIR"
if (( failed != 0 )); then
    exit 1
fi
