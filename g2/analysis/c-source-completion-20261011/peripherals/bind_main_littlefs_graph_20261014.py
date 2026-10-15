#!/usr/bin/env python3
"""Compile the connected recovered LittleFS graph into current Apollo Main."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
OUT = G2 / "build/c-firmware/20261014/main-root-dependencies"
BASE = OUT / "apollo-main-file-heap-free.o"
PRIOR = OUT / "file-heap-free-current-receipt.json"
OBJECTS = OUT / "littlefs-current"
BOUND = OUT / "apollo-main-littlefs-graph.o"
RECEIPT = OUT / "littlefs-graph-current-receipt.json"
STEMS = """alloc alloc_checkpoint alloc_scan bad_block_debug bd_cmp bd_crc bd_erase
bd_flush bd_flush_leaves bd_program bd_read bd_sync cache_drop cache_fill
ctz_extend ctz_find ctz_index ctz_traverse dir_alloc dir_commit dir_commitattr
dir_commitcrc dir_compact dir_fetch dir_getread dir_getslice dir_orphaningcommit
dir_relocatingcommit dir_split dir_splittingcompact dir_traverse file_close
file_flush file_flushedread file_flushedwrite file_outline file_relocate file_sync
file_sync_leaves fs_deorphan fs_parent fs_pred fs_size fs_state_helpers fs_traverse
gstate_hasmovehere lfs_free no_space_log tortoise_detectcycles""".split()
BACKEND = {"file_close", "lfs_free"}
ORACLES = {
    "verify_file_sync.py": "PASS_FILE_SYNC_BOUNDED 20",
    "verify_lfs_file_close.py": "PASS_LFS_FILE_CLOSE_BOUNDED 4",
    "verify_dir_commit.py": "PASS_DIR_COMMIT 20",
    "verify_dir_commitcrc.py": "PASS_DIR_COMMITCRC 6",
    "verify_bd_read.py": "PASS_BD_READ 40",
    "verify_file_flush.py": "PASS_FILE_FLUSH 30",
    "verify_file_flushedread.py": "PASS_FILE_FLUSHEDREAD 24",
    "verify_file_flushedwrite.py": "PASS_FILE_FLUSHEDWRITE 24",
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def symbols(path, flag):
    output = subprocess.check_output(["arm-none-eabi-nm", flag, str(path)], text=True)
    return {line.split()[-1] for line in output.splitlines() if line.split()}


def globals_defined(path):
    output = subprocess.check_output(["arm-none-eabi-nm", "--defined-only", str(path)], text=True)
    return {parts[2] for line in output.splitlines() if len(parts := line.split()) == 3
            and parts[1].isupper()}


def main():
    prior = json.loads(PRIOR.read_text())
    assert prior["status"] == "PASS_CURRENT_MAIN_FILE_HEAP_FREE"
    assert sha(BASE) == prior["output_sha256"]
    before = symbols(BASE, "-u")
    assert len(before) == 627 and len(STEMS) == 49 and len(set(STEMS)) == 49
    OBJECTS.mkdir(parents=True, exist_ok=True)
    rows = []
    objects = []
    seen = globals_defined(BASE)
    for stem in STEMS:
        folder = "file_backend_close_candidate" if stem in BACKEND else "file_sync_candidate"
        source = G2 / "components/audio" / folder / (stem + ".c")
        obj = OBJECTS / (stem + ".o")
        subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m55", "-mthumb",
                        "-std=c11", "-ffreestanding", "-fno-builtin", "-O2",
                        "-Wall", "-Wextra", "-Werror", "-c", str(source), "-o", str(obj)],
                       cwd=ROOT, check=True)
        defined = globals_defined(obj)
        assert defined and not defined & seen, (stem, defined & seen)
        seen |= defined
        objects.append(obj)
        rows.append({"source": str(source.relative_to(ROOT)), "source_sha256": sha(source),
                     "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj),
                     "defined": sorted(defined)})
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), *map(str, objects), "-o", str(BOUND)],
                   cwd=ROOT, check=True)
    after = symbols(BOUND, "-u")
    assert not after - before
    assert len(before - after) == 14 and len(after) == 613
    assert globals_defined(BOUND) == seen
    oracle_rows = []
    for name, expected in ORACLES.items():
        path = G2 / "analysis/c-source-completion-20261011/peripherals" / name
        result = subprocess.run([sys.executable, str(path)], cwd=ROOT,
                                text=True, capture_output=True, check=True)
        assert result.stdout.strip().splitlines()[-1] == expected, (name, result.stdout)
        oracle_rows.append({"path": str(path.relative_to(ROOT)), "sha256": sha(path),
                            "observed": expected})
    receipt = {
        "status": "PASS_CURRENT_MAIN_LITTLEFS_GRAPH_COMPILE",
        "base_receipt": str(PRIOR.relative_to(ROOT)), "base_receipt_sha256": sha(PRIOR),
        "source_units": rows,
        "source_unit_count": len(rows),
        "bounded_oracles_rerun": oracle_rows,
        "imports_resolved": sorted(before - after), "imports_added": sorted(after - before),
        "unresolved_before": len(before), "unresolved_after": len(after),
        "output": str(BOUND.relative_to(ROOT)), "output_sha256": sha(BOUND),
        "source_complete": False, "full_payload_linked": False,
        "limits": ["Compilation and relocatable linkage do not establish full stock behavior for every LittleFS body",
                   "Individual bounded oracles and pinned LittleFS provenance remain separate evidence",
                   "Filesystem storage configuration, final placement, and hardware behavior remain unqualified"],
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({"status": receipt["status"], "units": len(rows),
                      "unresolved_after": len(after), "receipt_sha256": sha(RECEIPT)}))


if __name__ == "__main__":
    main()
