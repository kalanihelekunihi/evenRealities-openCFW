#!/usr/bin/env bash
# Analyze Apollo main once, reflink the project, and decompile address chunks in parallel.

set -uo pipefail

: "${GHIDRA_HEADLESS:?set GHIDRA_HEADLESS}"
: "${JAVA_HOME:?set JAVA_HOME}"
: "${FIRMWARE:?set FIRMWARE}"
: "${GHIDRA_SCRIPT_DIR:?set GHIDRA_SCRIPT_DIR}"
: "${MANIFEST:?set MANIFEST}"
: "${OUTPUT_DIR:?set OUTPUT_DIR}"

JOBS="${JOBS:-16}"
PROCESSOR="${PROCESSOR:-ARM:LE:32:Cortex}"
LOADER="${LOADER:-BinaryLoader}"
BASE_ADDRESS="${BASE_ADDRESS:-0x437fe0}"
VECTOR_BASE="${VECTOR_BASE:-0x438000}"
IMAGE_END="${IMAGE_END:-0x794324}"
VECTOR_WORDS="${VECTOR_WORDS:-256}"
ANALYSIS_TIMEOUT="${ANALYSIS_TIMEOUT:-1800}"
DECOMPILE_TIMEOUT="${DECOMPILE_TIMEOUT:-60}"
TEMPLATE_PROJECT="${TEMPLATE_PROJECT:-}"
KEEP_PROJECTS="${KEEP_PROJECTS:-0}"
SHARD_LIMIT="${SHARD_LIMIT:-0}"
PROJECT_NAME="apollo_main_template"
PROGRAM_NAME="$(basename "$FIRMWARE")"

for value_name in JOBS VECTOR_WORDS ANALYSIS_TIMEOUT DECOMPILE_TIMEOUT; do
    value="${!value_name}"
    if [[ ! "$value" =~ ^[1-9][0-9]*$ ]]; then
        echo "$value_name must be a positive integer" >&2
        exit 2
    fi
done
if [[ ! "$SHARD_LIMIT" =~ ^[0-9]+$ ]]; then
    echo "SHARD_LIMIT must be zero (all) or a positive integer" >&2
    exit 2
fi
if [[ "$KEEP_PROJECTS" != 0 && "$KEEP_PROJECTS" != 1 ]]; then
    echo "KEEP_PROJECTS must be 0 or 1" >&2
    exit 2
fi
for path in "$GHIDRA_HEADLESS" "$FIRMWARE" "$MANIFEST"; do
    if [[ ! -f "$path" ]]; then
        echo "required file missing: $path" >&2
        exit 2
    fi
done
required_scripts=(SeedCortexMVectorTable.java DumpDecompilationChunk.java)
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
    NF != 5 || $1 !~ /^[A-Za-z0-9._-]+$/ ||
        $2 !~ /^0x[0-9A-Fa-f]+$/ || $3 !~ /^0x[0-9A-Fa-f]+$/ ||
        $4 !~ /^0x[0-9A-Fa-f]+$/ || $5 !~ /^0x[0-9A-Fa-f]+$/ ||
        seen[$1]++ { exit 1 }
' "$MANIFEST"; then
    echo "manifest must contain unique safe IDs and four hexadecimal bounds" >&2
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
    if [[ "$value" =~ ^[0-9]+$ ]]; then printf '%s\n' "$value";
    else python3 -c 'import time; print(time.time_ns())'; fi
}

mkdir -p "$OUTPUT_DIR/logs" "$OUTPUT_DIR/projects" "$OUTPUT_DIR/status"
overall_began="$(timestamp_ns)"
{
    printf 'jobs\t%s\n' "$JOBS"
    printf 'processor\t%s\n' "$PROCESSOR"
    printf 'loader\t%s\n' "$LOADER"
    printf 'base_address\t%s\n' "$BASE_ADDRESS"
    printf 'vector_base\t%s\n' "$VECTOR_BASE"
    printf 'image_end\t%s\n' "$IMAGE_END"
    printf 'vector_words\t%s\n' "$VECTOR_WORDS"
    printf 'analysis_timeout_seconds\t%s\n' "$ANALYSIS_TIMEOUT"
    printf 'decompile_timeout_seconds\t%s\n' "$DECOMPILE_TIMEOUT"
    printf 'template_project\t%s\n' "${TEMPLATE_PROJECT:-generated}"
    printf 'keep_projects\t%s\n' "$KEEP_PROJECTS"
    printf 'shard_limit\t%s\n' "$SHARD_LIMIT"
} >"$OUTPUT_DIR/CONFIG.tsv"
template_ns=0
if [[ -n "$TEMPLATE_PROJECT" ]]; then
    template_dir="$TEMPLATE_PROJECT"
    if [[ ! -f "$template_dir/$PROJECT_NAME.gpr" || ! -d "$template_dir/$PROJECT_NAME.rep" ]]; then
        echo "TEMPLATE_PROJECT is not a complete $PROJECT_NAME project: $template_dir" >&2
        exit 2
    fi
else
    template_dir="$OUTPUT_DIR/template"
    mkdir -p "$template_dir"
    template_began="$(timestamp_ns)"
    (
        export JAVA_HOME
        "$GHIDRA_HEADLESS" "$template_dir" "$PROJECT_NAME" \
            -import "$FIRMWARE" -overwrite \
            -processor "$PROCESSOR" -loader "$LOADER" \
            -loader-baseAddr "$BASE_ADDRESS" \
            -analysisTimeoutPerFile "$ANALYSIS_TIMEOUT" \
            -scriptPath "$GHIDRA_SCRIPT_DIR" \
            -preScript SeedCortexMVectorTable.java \
                "$VECTOR_BASE" "$IMAGE_END" "$VECTOR_WORDS"
    ) >"$OUTPUT_DIR/template-analysis.log" 2>&1
    template_status=$?
    template_ended="$(timestamp_ns)"
    template_ns=$((template_ended - template_began))
    printf 'exit_status\tduration_ns\n%s\t%s\n' \
        "$template_status" "$template_ns" >"$OUTPUT_DIR/template-status.tsv"
    if (( template_status != 0 )); then
        echo "template analysis failed; see $OUTPUT_DIR/template-analysis.log" >&2
        exit 1
    fi
fi

(
    cd "$template_dir" || exit 1
    while IFS= read -r file; do
        printf '%s  %s\n' "$(sha256_file "$file")" "$file"
    done < <(
        find "$PROJECT_NAME.gpr" "$PROJECT_NAME.rep" -type f -print | sort
    )
) >"$OUTPUT_DIR/template-files.tsv"
{
    printf '%s\trunner\n' "$(sha256_file "$0")"
    printf '%s\tfirmware\n' "$(sha256_file "$FIRMWARE")"
    printf '%s\tmanifest\n' "$(sha256_file "$MANIFEST")"
    printf '%s\tconfiguration\n' "$(sha256_file "$OUTPUT_DIR/CONFIG.tsv")"
    printf '%s\ttemplate_file_manifest\n' \
        "$(sha256_file "$OUTPUT_DIR/template-files.tsv")"
    for script in "${required_scripts[@]}"; do
        printf '%s\t%s\n' "$(sha256_file "$GHIDRA_SCRIPT_DIR/$script")" "$script"
    done
} >"$OUTPUT_DIR/INPUTS.tsv"

run_shard() {
    local shard_id="$1" start="$2" end="$3" file_start="$4" file_end="$5"
    local project_dir="$OUTPUT_DIR/projects/$shard_id"
    local log="$OUTPUT_DIR/logs/$shard_id.log"
    local clone_began clone_ended began ended status summary functions completed failed
    mkdir -p "$project_dir"
    clone_began="$(timestamp_ns)"
    # GNU cp can request a reflink opportunistically; macOS cp exposes the
    # equivalent clonefile operation through -c.  Keep a plain archive-copy
    # fallback so the authenticated runner also works on other hosts.
    if cp --help 2>&1 | grep -q -- '--reflink'; then
        cp -a --reflink=auto "$template_dir/." "$project_dir/"
    elif cp -cR "$template_dir/." "$project_dir/" 2>/dev/null; then
        :
    else
        cp -a "$template_dir/." "$project_dir/"
    fi
    clone_ended="$(timestamp_ns)"
    began="$(timestamp_ns)"
    (
        export JAVA_HOME
        "$GHIDRA_HEADLESS" "$project_dir" "$PROJECT_NAME" \
            -process "$PROGRAM_NAME" -noanalysis \
            -scriptPath "$GHIDRA_SCRIPT_DIR" \
            -postScript DumpDecompilationChunk.java \
                "$start" "$end" "$DECOMPILE_TIMEOUT"
    ) >"$log" 2>&1
    status=$?
    ended="$(timestamp_ns)"
    summary="$(grep 'OPENCFW_CHUNK_SUMMARY' "$log" | tail -1 || true)"
    functions="$(sed -n 's/.* functions=\([0-9][0-9]*\).*/\1/p' <<<"$summary")"
    completed="$(sed -n 's/.* completed=\([0-9][0-9]*\).*/\1/p' <<<"$summary")"
    failed="$(sed -n 's/.* failed=\([0-9][0-9]*\).*/\1/p' <<<"$summary")"
    printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
        "$shard_id" "$start" "$end" "$file_start" "$file_end" "$status" \
        "$((clone_ended - clone_began))" "$((ended - began))" \
        "${functions:-0}" "${completed:-0}" "${failed:-0}" \
        >"$OUTPUT_DIR/status/$shard_id.tsv"
    if [[ "$KEEP_PROJECTS" == 0 ]]; then
        rm -rf -- "$project_dir"
    fi
    return "$status"
}

active=0
launched=0
pids=()
while IFS=$'\t' read -r shard_id start end file_start file_end; do
    [[ -z "$shard_id" || "$shard_id" == \#* ]] && continue
    if (( SHARD_LIMIT > 0 && launched >= SHARD_LIMIT )); then break; fi
    run_shard "$shard_id" "$start" "$end" "$file_start" "$file_end" &
    pids+=("$!")
    active=$((active + 1))
    launched=$((launched + 1))
    if (( active >= JOBS )); then
        wait "${pids[0]}" || true
        pids=("${pids[@]:1}")
        active=$((active - 1))
    fi
done <"$MANIFEST"
for pid in "${pids[@]}"; do wait "$pid" || true; done

{
    printf 'shard_id\tstart\tend_exclusive\tfile_offset_start\tfile_offset_end\texit_status\tclone_ns\tdecompile_ns\tfunctions\tcompleted\tfailed\n'
    find "$OUTPUT_DIR/status" -type f -name '*.tsv' -print0 | sort -z | xargs -0 -r cat
} >"$OUTPUT_DIR/results.tsv"
overall_ended="$(timestamp_ns)"
printf 'overall_ns\ttemplate_ns\n%s\t%s\n' \
    "$((overall_ended - overall_began))" "$template_ns" >"$OUTPUT_DIR/timing.tsv"
(
    cd "$OUTPUT_DIR" || exit 1
    while IFS= read -r -d '' file; do
        printf '%s  %s\n' "$(sha256_file "$file")" "$file"
    done < <(find logs status -type f -print0 | sort -z)
    for file in CONFIG.tsv INPUTS.tsv results.tsv timing.tsv template-files.tsv; do
        printf '%s  %s\n' "$(sha256_file "$file")" "$file"
    done
) >"$OUTPUT_DIR/SHA256SUMS"

failed_shards="$(awk -F '\t' 'NR > 1 && $6 != 0 { n++ } END { print n + 0 }' "$OUTPUT_DIR/results.tsv")"
failed_functions="$(awk -F '\t' 'NR > 1 { n += $11 } END { print n + 0 }' "$OUTPUT_DIR/results.tsv")"
printf 'GHIDRA_APOLLO_CHUNKS shards=%s failed_shards=%s failed_functions=%s jobs=%s output=%s\n' \
    "$(( $(wc -l <"$OUTPUT_DIR/results.tsv") - 1 ))" "$failed_shards" \
    "$failed_functions" "$JOBS" "$OUTPUT_DIR"
if (( failed_shards != 0 )); then exit 1; fi
