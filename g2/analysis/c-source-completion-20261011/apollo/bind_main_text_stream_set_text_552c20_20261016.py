#!/usr/bin/env python3
"""Bind stock-compared text-stream set/append provider into Apollo Main."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/text_stream_set_text_552c20.c"
BASE = G2 / "build/c-firmware/20261016/main-text-stream-copy-bytes/apollo-main-text-stream-copy-bytes-bound.o"
OUT = G2 / "build/c-firmware/20261016/main-text-stream-set-text"
ORACLE = OUT / "oracle-receipt.json"
PROVIDER = "audio_text_stream_set_text_552c20"
CHILDREN = {"audio_text_stream_validate_5533cc", "audio_text_stream_restart_552db2",
            "audio_text_stream_dispatch_552df0", "audio_text_stream_next_interval_5532f8"}

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def names(path, flag):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-g", flag, str(path)], text=True).splitlines()}

def main():
    oracle = json.loads(ORACLE.read_text())
    if oracle["status"] != "PASS_EXPERIMENTAL_TEXT_STREAM_SET_TEXT_C_ORACLE" or \
            oracle["cases"] != 288 or oracle["source_sha256"] != sha(SOURCE):
        raise RuntimeError("text-stream set-text oracle changed")
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "text_stream_set_text_552c20.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                    "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    if names(obj, "--defined-only") != {PROVIDER}:
        raise RuntimeError("text-stream set-text symbols changed")
    before = names(BASE, "-u")
    if len(before) != 174 or PROVIDER not in before or CHILDREN & before:
        raise RuntimeError("Apollo set-text base frontier changed")
    linked = OUT / "apollo-main-text-stream-set-text-bound.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), "-o", str(linked)], check=True)
    after = names(linked, "-u")
    if before - after != {PROVIDER} or after - before != CHILDREN or len(after) != 177:
        raise RuntimeError(f"Apollo set-text frontier changed: {sorted(before-after)}, {sorted(after-before)}")
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_TEXT_STREAM_SET_TEXT_C",
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "oracle_receipt": str(ORACLE.relative_to(ROOT)), "oracle_receipt_sha256": sha(ORACLE),
               "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj),
               "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
               "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
               "unresolved_before": 174, "unresolved_after": 177,
               "imports_resolved": [PROVIDER], "imports_added": sorted(CHILDREN),
               "source_complete": False, "full_payload_linked": False, "hardware_proof": False,
               "limits": ["Four helper routines are explicit unresolved imports.",
                          "Helper effects, malformed inputs, whole-image link and hardware remain open."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, sort_keys=True, indent=2) + "\n")
    print(receipt["status"], 174, 177, sha(path))

if __name__ == "__main__":
    main()
