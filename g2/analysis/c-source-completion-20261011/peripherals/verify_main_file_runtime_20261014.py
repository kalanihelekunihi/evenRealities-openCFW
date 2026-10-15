#!/usr/bin/env python3
"""Rebuild source-owned file and page providers in refreshed Apollo Main."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
OUT = ROOT / "g2/build/c-firmware/20261014/main-root-source-refresh2"
BUILD = OUT / "apollo_main"
BASE_RECEIPT = OUT / "main-rom-runtime-receipt.json"
BASE = BUILD / "candidate-rom-runtime.o"
FINAL = BUILD / "candidate-file-runtime.o"
RECEIPT = OUT / "main-file-runtime-receipt.json"
SOURCES = {
    "heap-free": ROOT / "g2/components/audio/file_heap_free_candidate/file_heap_free.c",
    "lfs-memcpy": ROOT / "g2/components/audio/file_sync_candidate/byte_copy.c",
    "file-close-error": ROOT / "g2/components/audio/semihost_error_candidate/error.c",
    "mlist-isopen": ROOT / "g2/components/audio/file_backend_close_candidate/mlist_isopen.c",
    "mlist-remove": ROOT / "g2/components/audio/file_backend_close_candidate/mlist_remove.c",
    "page-layer": ROOT / "g2/components/main/page_layer_candidate_20261014/page_layer.c",
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def imports(path):
    output = subprocess.check_output(["arm-none-eabi-nm", "-u", str(path)], text=True)
    return {line.split()[-1] for line in output.splitlines()}


def main():
    base = json.loads(BASE_RECEIPT.read_text())
    assert base["status"] == "PASS_MAIN_ROM_RUNTIME_SOURCE_RELOCATABLE"
    assert base["linked_object_sha256"] == sha(BASE)
    prior_dir = ROOT / "g2/build/c-firmware/20261014/main-root-dependencies"
    prior_paths = [prior_dir / f"{name}-current-receipt.json" for name in
                   ("file-heap-free", "littlefs-lowers", "page-layer")]
    prior = [json.loads(path.read_text()) for path in prior_paths]
    assert [row["status"] for row in prior] == [
        "PASS_CURRENT_MAIN_FILE_HEAP_FREE", "PASS_CURRENT_MAIN_LITTLEFS_LOWERS",
        "PASS_CURRENT_MAIN_PAGE_LAYER_C"]
    provider_sources = {row["source"]: row["source_sha256"]
                        for receipt in prior[:2] for row in receipt["providers"]}
    provider_sources[prior[2]["source"]] = prior[2]["source_sha256"]
    for path in SOURCES.values():
        assert provider_sources[str(path.relative_to(ROOT))] == sha(path)
    for receipt in prior[:2]:
        for provider in receipt["providers"]:
            if "oracle" in provider:
                assert sha(ROOT / provider["oracle"]) == provider["oracle_sha256"]
    objects = []
    for label, source in SOURCES.items():
        obj = BUILD / f"refresh-{label}.o"
        subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m55",
                        "-mthumb", "-std=c11", "-ffreestanding", "-fno-builtin",
                        "-O2", "-Wall", "-Wextra", "-Werror", "-c", str(source),
                        "-o", str(obj)], check=True)
        objects.append(obj)
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), *map(str, objects),
                    "-o", str(FINAL)], check=True)
    before, after = imports(BASE), imports(FINAL)
    resolved = sorted(before - after)
    assert len(before) == 581 and len(after) == 575
    assert resolved == ["audio_file_heap_free", "audio_uart_page_44e3ca",
                        "g2_file_close_error", "g2_lfs_memcpy",
                        "g2_lfs_mlist_isopen", "g2_lfs_mlist_remove"]
    assert not after - before
    receipt = {
        "status": "PASS_MAIN_FILE_RUNTIME_SOURCE_RELOCATABLE",
        "base_receipt": str(BASE_RECEIPT.relative_to(ROOT)),
        "base_receipt_sha256": sha(BASE_RECEIPT),
        "prior_receipts": {str(p.relative_to(ROOT)): sha(p) for p in prior_paths},
        "sources": {str(p.relative_to(ROOT)): sha(p) for p in SOURCES.values()},
        "objects": {str(p.relative_to(ROOT)): sha(p) for p in objects},
        "linked_object": str(FINAL.relative_to(ROOT)), "linked_object_sha256": sha(FINAL),
        "unresolved_before": len(before), "unresolved_after": len(after),
        "imports_resolved": resolved, "imports_added": [],
        "whole_image_complete": False, "hardware_proof": False,
        "gates": ["Provider sources and recorded bounded oracles are hash bound; this link does not re-run all native behavior comparisons.",
                  "Other Main imports, final placement, complete filesystem behavior and physical hardware remain open."],
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(RECEIPT))


if __name__ == "__main__":
    main()
