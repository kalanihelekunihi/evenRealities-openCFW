#!/usr/bin/env python3
"""Bind stock-compared text-stream validation and interval providers."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/text_stream_decision_helpers_5533cc_5532f8.c"
BASE = G2 / "build/c-firmware/20261016/main-text-stream-set-text/apollo-main-text-stream-set-text-bound.o"
OUT = G2 / "build/c-firmware/20261016/main-text-stream-decision-helpers"
ORACLE = OUT / "oracle-receipt.json"
PROVIDERS = {"audio_text_stream_validate_5533cc", "audio_text_stream_next_interval_5532f8"}

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def names(path, flag):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-g", flag, str(path)], text=True).splitlines()}

def main():
    oracle = json.loads(ORACLE.read_text())
    if oracle["status"] != "PASS_EXPERIMENTAL_TEXT_STREAM_DECISION_HELPERS_C_ORACLE" or \
            oracle["cases"] != 120 or oracle["source_sha256"] != sha(SOURCE):
        raise RuntimeError("text-stream decision oracle changed")
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "text_stream_decision_helpers_5533cc_5532f8.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                    "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    if names(obj, "--defined-only") != PROVIDERS:
        raise RuntimeError("text-stream decision symbols changed")
    before = names(BASE, "-u")
    if len(before) != 177 or not PROVIDERS <= before:
        raise RuntimeError("Apollo decision base frontier changed")
    linked = OUT / "apollo-main-text-stream-decision-helpers-bound.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), "-o", str(linked)], check=True)
    after = names(linked, "-u")
    if before - after != PROVIDERS or after - before or len(after) != 175:
        raise RuntimeError(f"Apollo decision frontier changed: {sorted(before-after)}, {sorted(after-before)}")
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_TEXT_STREAM_DECISION_HELPERS_C",
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "oracle_receipt": str(ORACLE.relative_to(ROOT)), "oracle_receipt_sha256": sha(ORACLE),
               "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj),
               "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
               "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
               "unresolved_before": 177, "unresolved_after": 175,
               "imports_resolved": sorted(PROVIDERS), "imports_added": [],
               "source_complete": False, "full_payload_linked": False, "hardware_proof": False,
               "limits": ["String internals and malformed pointers remain external.",
                          "Whole-image link and hardware execution remain open."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, sort_keys=True, indent=2) + "\n")
    print(receipt["status"], 177, 175, sha(path))

if __name__ == "__main__":
    main()
