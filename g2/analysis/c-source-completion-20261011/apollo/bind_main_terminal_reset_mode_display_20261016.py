#!/usr/bin/env python3
"""Bind two stock-compared Terminal reset children into Apollo Main."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
BASE = G2 / "build/c-firmware/20261016/main-terminal-ui-action-reset-pair-5e5290/apollo-main-terminal-ui-action-reset-pair-bound.o"
OUT = G2 / "build/c-firmware/20261016/main-terminal-reset-mode-display"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/terminal_reset_mode_display_20261016.c"
ORACLE = OUT / "oracle-receipt.json"
RESOLVED = {"audio_terminal_reset_mode_5eae2c", "audio_terminal_reset_display_5e4c84"}
ADDED = {"audio_terminal_mode_set_5eae1e"}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def imports(path):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-u", str(path)], text=True).splitlines()}


def main():
    oracle = json.loads(ORACLE.read_text())
    if oracle["status"] != "PASS_EXPERIMENTAL_TERMINAL_RESET_MODE_DISPLAY_C_ORACLE" or \
            oracle["cases"] != 31 or oracle["source_sha256"] != sha(SOURCE):
        raise RuntimeError("Terminal reset-mode/display oracle changed")
    before = imports(BASE)
    if len(before) != 223 or not RESOLVED <= before:
        raise RuntimeError("Apollo Terminal reset-mode/display frontier changed")
    obj = OUT / "terminal_reset_mode_display.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                    "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    linked = OUT / "apollo-main-terminal-reset-mode-display-bound.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj),
                    "-o", str(linked)], check=True)
    after = imports(linked)
    if before-after != RESOLVED or after-before != ADDED or len(after) != 222:
        raise RuntimeError(f"Terminal reset-mode/display frontier changed: {len(after)} "
                           f"{before-after=} {after-before=}")
    result = {"status": "PASS_EXPERIMENTAL_MAIN_TERMINAL_RESET_MODE_DISPLAY_C",
              "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
              "oracle_receipt": str(ORACLE.relative_to(ROOT)), "oracle_receipt_sha256": sha(ORACLE),
              "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj),
              "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
              "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
              "unresolved_before": 223, "unresolved_after": 222,
              "imports_resolved": sorted(RESOLVED), "imports_added": sorted(ADDED),
              "source_complete": False, "full_payload_linked": False, "hardware_proof": False,
              "limits": ["Mode-set and LVGL child effects remain open."]}
    receipt = OUT / "receipt.json"
    receipt.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["status"], sha(receipt))


if __name__ == "__main__":
    main()
