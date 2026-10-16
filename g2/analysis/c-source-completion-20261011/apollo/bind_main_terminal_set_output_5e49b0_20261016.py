#!/usr/bin/env python3
"""Bind stock-compared Terminal output-content transition into Apollo Main."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
BASE = G2 / "build/c-firmware/20261016/main-terminal-elapsed-clear-5e4894/apollo-main-terminal-elapsed-clear-bound.o"
OUT = G2 / "build/c-firmware/20261016/main-terminal-set-output-5e49b0"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/terminal_set_output_5e49b0.c"
ORACLE = OUT / "oracle-receipt.json"
RESOLVED = {"audio_terminal_set_output_5e49b0"}
ADDED = {"audio_terminal_output_style_20003f80",
         "audio_terminal_output_payload_20074a94",
         "audio_terminal_output_mode_2007502d",
         "audio_terminal_output_active_2007502c",
         "audio_terminal_set_label_style_5e482a",
         "audio_terminal_select_output_mode_5ea2a8"}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def imports(path):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-u", str(path)], text=True).splitlines()}


def main():
    oracle = json.loads(ORACLE.read_text())
    if oracle["status"] != "PASS_EXPERIMENTAL_TERMINAL_SET_OUTPUT_C_ORACLE" or \
            oracle["cases"] != 100 or oracle["source_sha256"] != sha(SOURCE):
        raise RuntimeError("Terminal set-output oracle changed")
    before = imports(BASE)
    if len(before) != 217 or not RESOLVED <= before:
        raise RuntimeError("Apollo Terminal set-output frontier changed")
    obj = OUT / "terminal_set_output_5e49b0.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                    "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    linked = OUT / "apollo-main-terminal-set-output-bound.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj),
                    "-o", str(linked)], check=True)
    after = imports(linked)
    if before-after != RESOLVED or after-before != ADDED or len(after) != 222:
        raise RuntimeError(f"Terminal set-output frontier changed: {len(after)} "
                           f"{before-after=} {after-before=}")
    result = {"status": "PASS_EXPERIMENTAL_MAIN_TERMINAL_SET_OUTPUT_C",
              "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
              "oracle_receipt": str(ORACLE.relative_to(ROOT)), "oracle_receipt_sha256": sha(ORACLE),
              "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj),
              "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
              "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
              "unresolved_before": 217, "unresolved_after": 222,
              "imports_resolved": sorted(RESOLVED), "imports_added": sorted(ADDED),
              "source_complete": False, "full_payload_linked": False, "hardware_proof": False,
              "limits": ["Output-mode and style children, four RAM cells and shared Terminal RAM placement remain open."]}
    receipt = OUT / "receipt.json"
    receipt.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["status"], sha(receipt))


if __name__ == "__main__":
    main()
