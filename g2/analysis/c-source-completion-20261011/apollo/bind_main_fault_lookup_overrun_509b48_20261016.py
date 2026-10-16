#!/usr/bin/env python3
"""Bind the stock-byte-backed wrapping fault lookup provider."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/fault_lookup_overrun_509b48.c"
BASE = G2 / "build/c-firmware/20261016/main-tracepoint-slave-file-list/apollo-main-tracepoint-slave-file-list-bound.o"
ORACLE = G2 / "build/c-firmware/20261016/fault-lookup-overrun-509b48/oracle-receipt.json"
OUT = G2 / "build/c-firmware/20261016/main-fault-lookup-overrun"
SYMBOL = "audio_fault_unmapped_code_message_509b48"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def imports(path):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-u", str(path)], text=True).splitlines()}


def main():
    oracle = json.loads(ORACLE.read_text())
    if (oracle["status"] != "PASS_EXPERIMENTAL_FAULT_LOOKUP_OVERRUN_C_ORACLE"
            or oracle["matchable_codes"] != 195
            or oracle["source_sha256"] != sha(SOURCE)):
        raise RuntimeError("fault lookup oracle changed")
    before = imports(BASE)
    if len(before) != 167 or SYMBOL not in before:
        raise RuntimeError("Apollo fault frontier changed")
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "fault_lookup_overrun.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                    "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    linked = OUT / "apollo-main-fault-lookup-overrun-bound.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), "-o",
                    str(linked)], check=True)
    after = imports(linked)
    if before - after != {SYMBOL} or after - before or len(after) != 166:
        raise RuntimeError("fault lookup binding did not reduce exactly one import")
    result = {"status": "PASS_EXPERIMENTAL_MAIN_FAULT_LOOKUP_OVERRUN_C",
              "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
              "oracle_receipt": str(ORACLE.relative_to(ROOT)), "oracle_receipt_sha256": sha(ORACLE),
              "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj),
              "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
              "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
              "unresolved_before": 167, "unresolved_after": 166,
              "imports_resolved": [SYMBOL], "imports_added": [],
              "source_complete": False, "full_payload_linked": False, "hardware_proof": False,
              "limits": oracle["limits"]}
    receipt = OUT / "receipt.json"
    receipt.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["status"], sha(receipt))


if __name__ == "__main__":
    main()
