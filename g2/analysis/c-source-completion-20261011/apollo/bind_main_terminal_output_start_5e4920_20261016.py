#!/usr/bin/env python3
"""Bind stock-compared output-start provider into Apollo Main."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
BASE = G2 / "build/c-firmware/20261016/main-terminal-control-flags-5e4a6e/apollo-main-terminal-control-flags-bound.o"
OUT = G2 / "build/c-firmware/20261016/main-terminal-output-start-5e4920"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/terminal_output_start_5e4920.c"
ORACLE = OUT / "oracle-receipt.json"
RESOLVED = {"audio_terminal_output_start_5e4920"}
ADDED = {"audio_terminal_processing_prepare_5ea30c", "audio_terminal_processing_hide_5e4878", "audio_lv_anim_start_49942e", "audio_terminal_elapsed_refresh_5e4902"}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def imports(path):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-u", str(path)], text=True).splitlines()}


def main():
    oracle = json.loads(ORACLE.read_text())
    if oracle["status"] != "PASS_EXPERIMENTAL_TERMINAL_OUTPUT_START_C_ORACLE" or \
            oracle["cases"] != 25 or oracle["source_sha256"] != sha(SOURCE):
        raise RuntimeError("Terminal output-start oracle changed")
    before = imports(BASE)
    if len(before) != 213 or not RESOLVED <= before:
        raise RuntimeError("Apollo Terminal output-start frontier changed")
    obj = OUT / "terminal_output_start_5e4920.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                    "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    linked = OUT / "apollo-main-terminal-output-start-bound.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj),
                    "-o", str(linked)], check=True)
    after = imports(linked)
    if before-after != RESOLVED or after-before != ADDED or len(after) != 216:
        raise RuntimeError(f"Terminal output-start binding frontier changed: {len(after)} "
                           f"{before-after=} {after-before=}")
    result = {"status": "PASS_EXPERIMENTAL_MAIN_TERMINAL_OUTPUT_START_C",
              "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
              "oracle_receipt": str(ORACLE.relative_to(ROOT)), "oracle_receipt_sha256": sha(ORACLE),
              "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj),
              "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
              "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
              "unresolved_before": 213, "unresolved_after": 216,
              "imports_resolved": sorted(RESOLVED), "imports_added": sorted(ADDED),
              "source_complete": False, "full_payload_linked": False, "hardware_proof": False,
              "limits": ["Processing and animation children, elapsed refresh, logging sinks and hardware remain open."]}
    receipt = OUT / "receipt.json"
    receipt.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["status"], sha(receipt))


if __name__ == "__main__":
    main()
