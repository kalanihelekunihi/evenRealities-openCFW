#!/usr/bin/env python3
"""Bind source-backed QuickList frame parser and expose native child contracts."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/quicklist_frame_process_55894c.c"
BASE = G2 / "build/c-firmware/20261014/main-quicklist-tick-alias/apollo-main-quicklist-tick-alias.o"
OUT = G2 / "build/c-firmware/20261014/main-quicklist-frame-process"
ORACLE = Path(__file__).with_name("verify_main_quicklist_frame_process_oracle_20261015.py")
CHILDREN = {"audio_quicklist_pb_descriptor", "audio_quicklist_one_validate", "audio_quicklist_one_dispatch",
            "audio_quicklist_many_validate", "audio_quicklist_many_dispatch",
            "audio_quicklist_event_validate", "audio_quicklist_event_dispatch"}
SHARED = {"audio_quicklist_rx_state", "audio_uart_buffer_zero", "audio_uart_pb_stream_init",
          "audio_uart_checksum_copy", "audio_uart_pb_decode", "audio_log_flags",
          "audio_log_extended", "compressed_log_output"}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def names(path, *args):
    output = subprocess.check_output(["arm-none-eabi-nm", *args, str(path)], text=True)
    return {row.split()[-1] for row in output.splitlines() if row.strip()}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "quicklist_frame_process_55894c.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2",
                    "-Wall", "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    if names(obj, "-g", "--defined-only") != {"audio_quicklist_frame_process_55894c"}:
        raise RuntimeError("QuickList frame definition changed")
    if names(obj, "-u") != CHILDREN | SHARED:
        raise RuntimeError("QuickList frame lower contract changed")
    before = names(BASE, "-u")
    providers = names(BASE, "-g", "--defined-only")
    if "audio_quicklist_frame_process_55894c" not in before or not SHARED <= providers:
        raise RuntimeError("QuickList frame Main boundary changed")
    linked = OUT / "apollo-main-quicklist-frame-process.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), "-o", str(linked)], check=True)
    after = names(linked, "-u")
    if before - after != {"audio_quicklist_frame_process_55894c"} or after - before != CHILDREN:
        raise RuntimeError("QuickList frame import delta changed")
    subprocess.run([sys.executable, str(ORACLE)], check=True, capture_output=True, text=True)
    oracle_path = OUT / "oracle.json"
    oracle = json.loads(oracle_path.read_text())
    if oracle["status"] != "PASS_EXPERIMENTAL_MAIN_QUICKLIST_FRAME_PROCESS_ORACLE" or len(oracle["cases"]) != 10:
        raise RuntimeError("QuickList frame oracle changed")
    receipt = {
        "status": "PASS_EXPERIMENTAL_MAIN_QUICKLIST_FRAME_PROCESS_C",
        "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
        "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj),
        "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
        "linked_object": str(linked.relative_to(ROOT)), "linked_object_sha256": sha(linked),
        "oracle": str(oracle_path.relative_to(ROOT)), "oracle_sha256": sha(oracle_path),
        "oracle_script": str(ORACLE.relative_to(ROOT)), "oracle_script_sha256": sha(ORACLE),
        "unresolved_before": len(before), "unresolved_after": len(after),
        "imports_resolved": sorted(before - after), "imports_added": sorted(after - before),
        "source_complete": False, "full_payload_linked": False,
        "limits": ["Native/C comparison covers intercepted decode and command dispatch with logging disabled.",
                   "QuickList schema descriptor and six validator/encode child bodies remain unresolved.",
                   "Final data placement, startup and device behavior remain unproved."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(path))


if __name__ == "__main__":
    main()
