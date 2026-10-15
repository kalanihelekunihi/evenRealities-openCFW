#!/usr/bin/env python3
"""Rebuild the source-backed TLSF lower graph in refreshed Apollo Main."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
OUT = ROOT / "g2/build/c-firmware/20261014/main-root-source-refresh2"
BUILD = OUT / "apollo_main"
BASE_RECEIPT = OUT / "main-file-runtime-receipt.json"
BASE = BUILD / "candidate-file-runtime.o"
FINAL = BUILD / "candidate-tlsf-runtime.o"
RECEIPT = OUT / "main-tlsf-runtime-receipt.json"
PRIOR_DIR = ROOT / "g2/build/c-firmware/20261014/main-root-dependencies"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def imports(path):
    output = subprocess.check_output(["arm-none-eabi-nm", "-u", str(path)], text=True)
    return {line.split()[-1] for line in output.splitlines()}


def main():
    base = json.loads(BASE_RECEIPT.read_text())
    assert base["status"] == "PASS_MAIN_FILE_RUNTIME_SOURCE_RELOCATABLE"
    assert base["linked_object_sha256"] == sha(BASE)
    tlsf_receipt = PRIOR_DIR / "tlsf-lowers-current-receipt.json"
    heap_receipt = PRIOR_DIR / "file-heap-free-current-receipt.json"
    tlsf = json.loads(tlsf_receipt.read_text())
    heap = json.loads(heap_receipt.read_text())
    assert tlsf["status"] == "PASS_CURRENT_MAIN_TLSF_LOWERS"
    assert heap["status"] == "PASS_CURRENT_MAIN_FILE_HEAP_FREE"
    sources = []
    for row in tlsf["sources"]:
        source = ROOT / row["path"]
        assert sha(source) == row["sha256"]
        sources.append(source)
    pool_row, = [row for row in heap["providers"] if row["symbol"] == "g2_file_pool_free"]
    pool_source = ROOT / pool_row["source"]
    assert sha(pool_source) == pool_row["source_sha256"]
    sources.append(pool_source)
    for oracle in tlsf["bounded_oracles"]:
        assert sha(ROOT / oracle["path"]) == oracle["sha256"]
    if "oracle" in pool_row:
        assert sha(ROOT / pool_row["oracle"]) == pool_row["oracle_sha256"]
    objects = []
    for source in sources:
        obj = BUILD / f"refresh-tlsf-{source.stem}.o"
        subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m55",
                        "-mthumb", "-std=c11", "-ffreestanding", "-fno-builtin",
                        "-O2", "-Wall", "-Wextra", "-Werror", "-c", str(source),
                        "-o", str(obj)], check=True)
        objects.append(obj)
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), *map(str, objects),
                    "-o", str(FINAL)], check=True)
    before, after = imports(BASE), imports(FINAL)
    resolved = sorted(before - after)
    assert len(before) == 575 and len(after) == 561
    assert set(resolved) == set(tlsf["imports_resolved"]) | {"g2_file_pool_free"}
    assert not after - before
    receipt = {
        "status": "PASS_MAIN_TLSF_RUNTIME_SOURCE_RELOCATABLE",
        "base_receipt": str(BASE_RECEIPT.relative_to(ROOT)),
        "base_receipt_sha256": sha(BASE_RECEIPT),
        "prior_receipts": {str(p.relative_to(ROOT)): sha(p)
                           for p in (tlsf_receipt, heap_receipt)},
        "sources": {str(p.relative_to(ROOT)): sha(p) for p in sources},
        "objects": {str(p.relative_to(ROOT)): sha(p) for p in objects},
        "linked_object": str(FINAL.relative_to(ROOT)), "linked_object_sha256": sha(FINAL),
        "unresolved_before": len(before), "unresolved_after": len(after),
        "imports_resolved": resolved, "imports_added": [],
        "whole_image_complete": False, "hardware_proof": False,
        "gates": ["Bounded TLSF oracle records and provider source hashes are bound; not all allocator states are qualified.",
                  "Other Main imports, final placement, full filesystem behavior, and physical hardware remain open."],
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(RECEIPT))


if __name__ == "__main__":
    main()
