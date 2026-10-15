#!/usr/bin/env python3
"""Compose existing LittleFS C providers into the current Apollo Main graph."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
OUT = G2 / "build/c-firmware/20261014/main-littlefs-provider-closure"
BASE = G2 / "build/c-firmware/20261014/main-root-source-refresh2/apollo_main/candidate-scheduler-closure.o"
SOURCES = (
    "g2/components/audio/file_sync_candidate/bd_cmp.c",
    "g2/components/audio/file_sync_candidate/cache_fill.c",
    "g2/components/audio/file_sync_candidate/bd_flush_leaves.c",
    "g2/components/audio/file_sync_candidate/ctz_index.c",
    "g2/components/audio/file_sync_candidate/dir_commit.c",
    "g2/components/audio/file_sync_candidate/dir_fetch.c",
    "g2/components/audio/file_sync_candidate/dir_getslice.c",
    "g2/components/audio/file_backend_close_candidate/file_close.c",
    "g2/components/audio/file_sync_candidate/file_flush.c",
    "g2/components/audio/file_sync_candidate/file_flushedread.c",
    "g2/components/audio/file_sync_candidate/file_flushedwrite.c",
    "g2/components/audio/file_sync_candidate/fs_deorphan.c",
    "g2/components/audio/file_sync_candidate/fs_state_helpers.c",
    "g2/components/audio/file_sync_candidate/alloc_checkpoint.c",
    "g2/components/audio/file_sync_candidate/bd_flush.c",
    "g2/components/audio/file_sync_candidate/bd_program.c",
    "g2/components/audio/file_sync_candidate/bd_read.c",
    "g2/components/audio/file_sync_candidate/cache_drop.c",
    "g2/components/audio/file_sync_candidate/ctz_extend.c",
    "g2/components/audio/file_sync_candidate/ctz_find.c",
    "g2/components/audio/file_sync_candidate/bad_block_debug.c",
    "g2/components/audio/file_sync_candidate/dir_getread.c",
    "g2/components/audio/file_sync_candidate/dir_orphaningcommit.c",
    "g2/components/audio/file_sync_candidate/file_outline.c",
    "g2/components/audio/file_sync_candidate/file_relocate.c",
    "g2/components/audio/file_sync_candidate/file_sync.c",
    "g2/components/audio/file_backend_close_candidate/lfs_free.c",
    "g2/components/audio/file_sync_candidate/fs_parent.c",
    "g2/components/audio/file_sync_candidate/gstate_hasmovehere.c",
    "g2/components/audio/file_sync_candidate/alloc.c",
    "g2/components/audio/file_sync_candidate/bd_erase.c",
    "g2/components/audio/file_sync_candidate/bd_sync.c",
    "g2/components/audio/file_sync_candidate/file_sync_leaves.c",
    "g2/components/audio/file_sync_candidate/dir_relocatingcommit.c",
    "g2/components/audio/file_sync_candidate/fs_pred.c",
    "g2/components/audio/file_sync_candidate/tortoise_detectcycles.c",
    "g2/components/audio/file_sync_candidate/alloc_scan.c",
    "g2/components/audio/file_sync_candidate/dir_commitattr.c",
    "g2/components/audio/file_sync_candidate/dir_commitcrc.c",
    "g2/components/audio/file_sync_candidate/dir_splittingcompact.c",
    "g2/components/audio/file_sync_candidate/dir_traverse.c",
    "g2/components/audio/file_sync_candidate/no_space_log.c",
    "g2/components/audio/file_sync_candidate/bd_crc.c",
    "g2/components/audio/file_sync_candidate/dir_compact.c",
    "g2/components/audio/file_sync_candidate/dir_split.c",
    "g2/components/audio/file_sync_candidate/fs_size.c",
    "g2/components/audio/file_sync_candidate/fs_traverse.c",
    "g2/components/audio/file_sync_candidate/ctz_traverse.c",
    "g2/components/audio/file_sync_candidate/dir_alloc.c",
)
EXPECTED = {
    "g2_lfs_bd_cmp", "g2_lfs_cache_fill", "g2_lfs_cache_zero",
    "g2_lfs_ctz_index", "g2_lfs_dir_commit", "g2_lfs_dir_fetch",
    "g2_lfs_dir_fetchmatch", "g2_lfs_dir_getslice", "g2_lfs_file_close",
    "g2_lfs_file_flush", "g2_lfs_file_flushedread",
    "g2_lfs_file_flushedwrite", "g2_lfs_fs_deorphan", "g2_lfs_fs_prepmove",
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def imports(path):
    output = subprocess.check_output(["arm-none-eabi-nm", "-u", str(path)], text=True)
    return {line.split()[-1] for line in output.splitlines() if line.strip()}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    before = imports(BASE)
    if not EXPECTED <= before:
        raise RuntimeError("LittleFS import set changed")
    objects = []
    for source_name in SOURCES:
        source = ROOT / source_name
        obj = OUT / (source.stem + ".o")
        subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m55",
                        "-mthumb", "-std=c11", "-ffreestanding", "-fno-builtin",
                        "-O2", "-Wall", "-Wextra", "-Werror", "-c", str(source),
                        "-o", str(obj)], check=True)
        objects.append(obj)
    linked = OUT / "apollo-main-littlefs-providers.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), *map(str, objects),
                    "-o", str(linked)], check=True)
    after = imports(linked)
    if not EXPECTED <= before - after:
        raise RuntimeError("a selected LittleFS provider did not resolve")
    if after - before:
        raise RuntimeError(f"LittleFS closure introduced imports: {sorted(after - before)}")
    if len(before) != 558 or len(after) != 544:
        raise RuntimeError("Main LittleFS closure count changed")
    receipt = {
        "status": "PASS_MAIN_LITTLEFS_PROVIDER_SOURCE_COMPOSITION",
        "upstream_littlefs": "third-party/upstream/littlefs/lfs.c",
        "upstream_littlefs_sha256": sha(ROOT / "third-party/upstream/littlefs/lfs.c"),
        "base_object": str(BASE.relative_to(ROOT)),
        "base_object_sha256": sha(BASE),
        "sources": {name: sha(ROOT / name) for name in SOURCES},
        "objects": {str(p.relative_to(ROOT)): sha(p) for p in objects},
        "linked_object": str(linked.relative_to(ROOT)),
        "linked_object_sha256": sha(linked),
        "unresolved_before": len(before),
        "unresolved_after": len(after),
        "imports_resolved": sorted(before - after),
        "imports_added": sorted(after - before),
        "source_complete": False,
        "full_payload_linked": False,
        "limits": ["LittleFS native behavior and flash effects remain unqualified.",
                   "Other Main imports and final placement remain open."],
    }
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(path))


if __name__ == "__main__":
    main()
