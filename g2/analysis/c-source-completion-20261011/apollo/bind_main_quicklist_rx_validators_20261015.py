#!/usr/bin/env python3
"""Bind three native-matched QuickList receive validator C bodies."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/quicklist_rx_validators_558cb0.c"
BASE = G2 / "build/c-firmware/20261014/main-quicklist-frame-process/apollo-main-quicklist-frame-process.o"
OUT = G2 / "build/c-firmware/20261014/main-quicklist-rx-validators"
ORACLE = Path(__file__).with_name("verify_main_quicklist_rx_validators_oracle_20261015.py")
DEFINITIONS = {"audio_quicklist_one_validate", "audio_quicklist_many_validate",
               "audio_quicklist_event_validate"}
CHILDREN = {"audio_uart_checksum_copy", "audio_ring_pb_assert_509b48",
            "audio_log_flags", "audio_log_extended", "compressed_log_output"}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def names(path, *args):
    output = subprocess.check_output(["arm-none-eabi-nm", *args, str(path)], text=True)
    return {row.split()[-1] for row in output.splitlines() if row.strip()}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "quicklist_rx_validators_558cb0.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2",
                    "-Wall", "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    if names(obj, "-g", "--defined-only") != DEFINITIONS or names(obj, "-u") != CHILDREN:
        raise RuntimeError("QuickList receive validator provider set changed")
    before = names(BASE, "-u")
    providers = names(BASE, "-g", "--defined-only")
    if not DEFINITIONS <= before or not CHILDREN <= providers:
        raise RuntimeError("QuickList receive validator Main boundary changed")
    linked = OUT / "apollo-main-quicklist-rx-validators.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), "-o", str(linked)], check=True)
    after = names(linked, "-u")
    if before - after != DEFINITIONS or after - before:
        raise RuntimeError("QuickList receive validator import delta changed")
    subprocess.run([sys.executable, str(ORACLE)], check=True, capture_output=True, text=True)
    oracle_path = OUT / "oracle.json"
    oracle = json.loads(oracle_path.read_text())
    if oracle["status"] != "PASS_EXPERIMENTAL_MAIN_QUICKLIST_RX_VALIDATORS_ORACLE" or len(oracle["cases"]) != 6:
        raise RuntimeError("QuickList receive validator oracle changed")
    receipt = {
        "status": "PASS_EXPERIMENTAL_MAIN_QUICKLIST_RX_VALIDATORS_C",
        "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
        "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj),
        "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
        "linked_object": str(linked.relative_to(ROOT)), "linked_object_sha256": sha(linked),
        "oracle": str(oracle_path.relative_to(ROOT)), "oracle_sha256": sha(oracle_path),
        "oracle_script": str(ORACLE.relative_to(ROOT)), "oracle_script_sha256": sha(ORACLE),
        "unresolved_before": len(before), "unresolved_after": len(after),
        "imports_resolved": sorted(before - after), "imports_added": sorted(after - before),
        "source_complete": False, "full_payload_linked": False,
        "limits": ["Native/C comparison covers null and nonnull inputs with logging disabled.",
                   "QuickList schema and three transmit encoders remain unresolved; assertion body is a selected provider.",
                   "Whole image placement and hardware behavior remain unproved."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(path))


if __name__ == "__main__":
    main()
