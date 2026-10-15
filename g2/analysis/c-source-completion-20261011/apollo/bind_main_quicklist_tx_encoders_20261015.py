#!/usr/bin/env python3
"""Bind three native-compared QuickList transmit encoders into Apollo Main."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/quicklist_tx_encoders_558d9e.c"
BASE = G2 / "build/c-firmware/20261014/main-quicklist-pb-descriptor/apollo-main-quicklist-pb-descriptor.o"
OUT = G2 / "build/c-firmware/20261014/main-quicklist-tx-encoders"
ORACLE = Path(__file__).with_name("verify_main_quicklist_tx_encoders_oracle_20261015.py")
DEFINITIONS = {"audio_quicklist_one_dispatch", "audio_quicklist_many_dispatch",
               "audio_quicklist_event_dispatch", "audio_quicklist_tx_state",
               "audio_quicklist_tx_packet"}
CHILDREN = {"audio_quicklist_pb_descriptor", "audio_pb_ostream_from_buffer",
            "audio_uart_checksum_copy", "audio_uart_buffer_zero", "audio_pb_encode",
            "audio_ring_pb_tx_ble_475b14", "audio_ring_pb_assert_509b48",
            "audio_log_flags", "audio_log_extended", "compressed_log_output"}
IMPORTS = {"audio_quicklist_one_dispatch", "audio_quicklist_many_dispatch",
           "audio_quicklist_event_dispatch"}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def names(path, *args):
    output = subprocess.check_output(["arm-none-eabi-nm", *args, str(path)], text=True)
    return {row.split()[-1] for row in output.splitlines() if row.strip()}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "quicklist_tx_encoders_558d9e.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2",
                    "-Wall", "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    if names(obj, "-g", "--defined-only") != DEFINITIONS or names(obj, "-u") != CHILDREN:
        raise RuntimeError("QuickList transmit provider set changed")
    before = names(BASE, "-u")
    providers = names(BASE, "-g", "--defined-only")
    if not IMPORTS <= before or not CHILDREN <= providers:
        raise RuntimeError("QuickList transmit Main boundary changed")
    linked = OUT / "apollo-main-quicklist-tx-encoders.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), "-o", str(linked)], check=True)
    after = names(linked, "-u")
    if before-after != IMPORTS or after-before:
        raise RuntimeError("QuickList transmit import delta changed")
    subprocess.run([sys.executable, str(ORACLE)], check=True, capture_output=True, text=True)
    oracle_path = OUT / "oracle.json"
    oracle = json.loads(oracle_path.read_text())
    if oracle["status"] != "PASS_EXPERIMENTAL_MAIN_QUICKLIST_TX_ENCODERS_ORACLE" or len(oracle["cases"]) != 9:
        raise RuntimeError("QuickList transmit oracle changed")
    receipt = {
        "status": "PASS_EXPERIMENTAL_MAIN_QUICKLIST_TX_ENCODERS_C",
        "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
        "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj),
        "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
        "linked_object": str(linked.relative_to(ROOT)), "linked_object_sha256": sha(linked),
        "oracle": str(oracle_path.relative_to(ROOT)), "oracle_sha256": sha(oracle_path),
        "oracle_script": str(ORACLE.relative_to(ROOT)), "oracle_script_sha256": sha(ORACLE),
        "unresolved_before": len(before), "unresolved_after": len(after),
        "imports_resolved": sorted(before-after), "imports_added": sorted(after-before),
        "source_complete": False, "full_payload_linked": False,
        "limits": ["Nine native/C comparisons cover null, encode-failure and success paths with logging disabled.",
                   "Nanopb encode, BLE send and assertion use selected lower providers; final BSS placement and hardware behavior remain open."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(path))


if __name__ == "__main__":
    main()
