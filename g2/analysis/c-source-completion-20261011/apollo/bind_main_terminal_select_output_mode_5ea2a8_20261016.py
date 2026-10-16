#!/usr/bin/env python3
"""Bind stock-compared Terminal output phrase selector into Apollo Main."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
BASE = G2 / "build/c-firmware/20261016/main-terminal-set-label-style-5e482a/apollo-main-terminal-set-label-style-bound.o"
OUT = G2 / "build/c-firmware/20261016/main-terminal-select-output-mode-5ea2a8"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/terminal_select_output_mode_5ea2a8.c"
ORACLE = OUT / "oracle-receipt.json"
RESOLVED = {"audio_terminal_select_output_mode_5ea2a8"}
ADDITIONAL = {"audio_terminal_select_output_mode_core_5ea270",
              "audio_terminal_output_hash_5ea256"}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def imports(path):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-u", str(path)], text=True).splitlines()}


def main():
    oracle = json.loads(ORACLE.read_text())
    if oracle["status"] != "PASS_EXPERIMENTAL_TERMINAL_SELECT_OUTPUT_MODE_C_ORACLE" or \
            oracle["cases"] != 240 or oracle["source_sha256"] != sha(SOURCE):
        raise RuntimeError("Terminal output-mode oracle changed")
    before = imports(BASE)
    if len(before) != 222 or not RESOLVED <= before:
        raise RuntimeError("Apollo Terminal output-mode frontier changed")
    obj = OUT / "terminal_select_output_mode_5ea2a8.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                    "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    names = {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-g", str(obj)], text=True).splitlines()}
    if not RESOLVED|ADDITIONAL <= names:
        raise RuntimeError("Terminal output-mode C symbols missing")
    linked = OUT / "apollo-main-terminal-select-output-mode-bound.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj),
                    "-o", str(linked)], check=True)
    after = imports(linked)
    if before-after != RESOLVED or after-before or len(after) != 221:
        raise RuntimeError(f"Terminal output-mode frontier changed: {len(after)} "
                           f"{before-after=} {after-before=}")
    result = {"status": "PASS_EXPERIMENTAL_MAIN_TERMINAL_SELECT_OUTPUT_MODE_C",
              "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
              "oracle_receipt": str(ORACLE.relative_to(ROOT)), "oracle_receipt_sha256": sha(ORACLE),
              "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj),
              "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
              "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
              "unresolved_before": 222, "unresolved_after": 221,
              "imports_resolved": sorted(RESOLVED), "imports_added": [],
              "additional_providers": sorted(ADDITIONAL),
              "source_complete": False, "full_payload_linked": False, "hardware_proof": False,
              "limits": ["LVGL text effects, phrase ROM placement and shared Terminal RAM placement remain open."]}
    receipt = OUT / "receipt.json"
    receipt.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["status"], sha(receipt))


if __name__ == "__main__":
    main()
