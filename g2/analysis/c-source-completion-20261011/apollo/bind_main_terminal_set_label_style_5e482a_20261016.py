#!/usr/bin/env python3
"""Bind stock-compared Terminal output-label style wrapper into Apollo Main."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
BASE = G2 / "build/c-firmware/20261016/main-terminal-output-ram-cells/apollo-main-terminal-output-ram-bound.o"
OUT = G2 / "build/c-firmware/20261016/main-terminal-set-label-style-5e482a"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/terminal_set_label_style_5e482a.c"
ORACLE = OUT / "oracle-receipt.json"
RESOLVED = {"audio_terminal_set_label_style_5e482a"}
ADDED = {"audio_lv_label_style_call_597ea6", "audio_lv_label_style_call_597f10",
         "audio_lv_label_style_call_597f52", "audio_lv_label_style_call_597ee0"}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def imports(path):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-u", str(path)], text=True).splitlines()}


def main():
    oracle = json.loads(ORACLE.read_text())
    if oracle["status"] != "PASS_EXPERIMENTAL_TERMINAL_SET_LABEL_STYLE_C_ORACLE" or \
            oracle["cases"] != 16 or oracle["source_sha256"] != sha(SOURCE):
        raise RuntimeError("Terminal set-label-style oracle changed")
    before = imports(BASE)
    if len(before) != 219 or not RESOLVED <= before:
        raise RuntimeError("Apollo Terminal set-label-style frontier changed")
    obj = OUT / "terminal_set_label_style_5e482a.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                    "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    linked = OUT / "apollo-main-terminal-set-label-style-bound.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj),
                    "-o", str(linked)], check=True)
    after = imports(linked)
    if before-after != RESOLVED or after-before != ADDED or len(after) != 222:
        raise RuntimeError(f"Terminal set-label-style frontier changed: {len(after)} "
                           f"{before-after=} {after-before=}")
    result = {"status": "PASS_EXPERIMENTAL_MAIN_TERMINAL_SET_LABEL_STYLE_C",
              "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
              "oracle_receipt": str(ORACLE.relative_to(ROOT)), "oracle_receipt_sha256": sha(ORACLE),
              "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj),
              "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
              "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
              "unresolved_before": 219, "unresolved_after": 222,
              "imports_resolved": sorted(RESOLVED), "imports_added": sorted(ADDED),
              "source_complete": False, "full_payload_linked": False, "hardware_proof": False,
              "limits": ["Four LVGL style lower-call effects and style RAM extent remain open."]}
    receipt = OUT / "receipt.json"
    receipt.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["status"], sha(receipt))


if __name__ == "__main__":
    main()
