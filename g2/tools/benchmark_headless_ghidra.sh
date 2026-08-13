#!/usr/bin/env bash
# Benchmark independent openCFW raw-firmware decompilation batches.
#
# Required environment:
#   GHIDRA_HEADLESS  path to Ghidra's support/analyzeHeadless
#   JAVA_HOME        JDK 21 home
# Optional environment:
#   FIRMWARE         stock raw image
#   GHIDRA_SCRIPT_DIR directory containing DumpFunctionDecomp.java
#   TASKS            number of independent projects (default: 1)
#   JOBS             maximum concurrent projects (default: 1)

set -u

repo_root=$(cd "$(dirname "$0")/../.." && pwd)
firmware=${FIRMWARE:-"$repo_root/openCFW/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"}
script_dir=${GHIDRA_SCRIPT_DIR:-"$repo_root/openCFW/tools/ghidra"}
tasks=${TASKS:-1}
jobs=${JOBS:-1}

: "${GHIDRA_HEADLESS:?set GHIDRA_HEADLESS to support/analyzeHeadless}"
: "${JAVA_HOME:?set JAVA_HOME to a JDK 21 installation}"

case $tasks in
    ''|*[!0-9]*|0) echo "TASKS must be a positive integer" >&2; exit 2 ;;
esac
case $jobs in
    ''|*[!0-9]*|0) echo "JOBS must be a positive integer" >&2; exit 2 ;;
esac

if [ ! -x "$GHIDRA_HEADLESS" ]; then
    echo "GHIDRA_HEADLESS is not executable: $GHIDRA_HEADLESS" >&2
    exit 2
fi
if [ ! -f "$firmware" ]; then
    echo "firmware is missing: $firmware" >&2
    exit 2
fi
if [ ! -f "$script_dir/DumpFunctionDecomp.java" ]; then
    echo "DumpFunctionDecomp.java is missing from: $script_dir" >&2
    exit 2
fi

run_root=$(mktemp -d "${TMPDIR:-/tmp}/opencfw-ghidra-bench.XXXXXX")

run_one() {
    task_id=$1
    task_dir="$run_root/task-$task_id"
    mkdir "$task_dir"
    env JAVA_HOME="$JAVA_HOME" "$GHIDRA_HEADLESS" \
        "$task_dir" "opencfw_bench_$task_id" \
        -import "$firmware" \
        -processor ARM:LE:32:Cortex \
        -loader BinaryLoader \
        -loader-baseAddr 0x437fe0 \
        -scriptPath "$script_dir" \
        -postScript DumpFunctionDecomp.java \
        0x48f7f4 0x48f968 0x48fb1c 0x48fb30 0x49053c \
        -noanalysis \
        -deleteProject \
        >/dev/null 2>&1
    status=$?
    rmdir "$task_dir" 2>/dev/null || true
    return "$status"
}

next_task=1
status=0
while [ "$next_task" -le "$tasks" ]; do
    pids=""
    launched=0
    while [ "$launched" -lt "$jobs" ] && [ "$next_task" -le "$tasks" ]; do
        run_one "$next_task" &
        pids="$pids $!"
        launched=$((launched + 1))
        next_task=$((next_task + 1))
    done
    for pid in $pids; do
        if ! wait "$pid"; then
            status=1
        fi
    done
done

rmdir "$run_root" 2>/dev/null || true
exit "$status"
