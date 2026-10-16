#!/usr/bin/env python3
"""Bind stock-compared file-heap realloc wrapper into Apollo Main."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/file_heap_realloc_474d54.c"
BASE = G2 / "build/c-firmware/20261016/main-text-stream-buffer-create/apollo-main-text-stream-buffer-create-bound.o"
OUT = G2 / "build/c-firmware/20261016/main-file-heap-realloc"
ORACLE = OUT / "oracle-receipt.json"
PROVIDER = "audio_file_heap_realloc"

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def names(path, flag):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-g", flag, str(path)], text=True).splitlines()}

def main():
    oracle = json.loads(ORACLE.read_text())
    if oracle["status"] != "PASS_EXPERIMENTAL_FILE_HEAP_REALLOC_C_ORACLE" or \
            oracle["cases"] != 16 or oracle["source_sha256"] != sha(SOURCE):
        raise RuntimeError("file-heap realloc oracle changed")
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "file_heap_realloc_474d54.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                    "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    if names(obj, "--defined-only") != {PROVIDER}:
        raise RuntimeError("file-heap realloc symbols changed")
    before = names(BASE, "-u")
    if len(before) != 179 or PROVIDER not in before:
        raise RuntimeError("Apollo heap realloc base frontier changed")
    linked = OUT / "apollo-main-file-heap-realloc-bound.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), "-o", str(linked)], check=True)
    after = names(linked, "-u")
    if before - after != {PROVIDER} or after - before or len(after) != 178:
        raise RuntimeError(f"Apollo heap realloc frontier changed: {sorted(before-after)}, {sorted(after-before)}")
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_FILE_HEAP_REALLOC_C",
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "oracle_receipt": str(ORACLE.relative_to(ROOT)), "oracle_receipt_sha256": sha(ORACLE),
               "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj),
               "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
               "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
               "unresolved_before": 179, "unresolved_after": 178,
               "imports_resolved": [PROVIDER], "imports_added": [],
               "source_complete": False, "full_payload_linked": False, "hardware_proof": False,
               "limits": ["Heap mutex and pool cells still need final RAM ownership and placement.",
                          "Whole-image link and hardware validation remain open."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, sort_keys=True, indent=2) + "\n")
    print(receipt["status"], 179, 178, sha(path))

if __name__ == "__main__":
    main()
