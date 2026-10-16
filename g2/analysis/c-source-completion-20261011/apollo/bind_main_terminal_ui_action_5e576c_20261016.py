#!/usr/bin/env python3
"""Bind stock-compared Terminal BLE display-request action into Apollo Main."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
BASE = G2 / "build/c-firmware/20261016/main-terminal-ui-action-5e54a2/apollo-main-terminal-ui-action-5e54a2-bound.o"
OUT = G2 / "build/c-firmware/20261016/main-terminal-ui-action-5e576c"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/terminal_ui_action_5e576c.c"
ORACLE = OUT / "oracle-receipt.json"
RESOLVED = {"audio_terminal_ui_action_5e576c"}

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def imports(path):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-u", str(path)], text=True).splitlines()}

def main():
    oracle = json.loads(ORACLE.read_text())
    if oracle["status"] != "PASS_EXPERIMENTAL_TERMINAL_UI_ACTION_5E576C_C_ORACLE" or \
            oracle["cases"] != 336 or oracle["source_sha256"] != sha(SOURCE):
        raise RuntimeError("Terminal action 5e576c oracle changed")
    before = imports(BASE)
    if len(before) != 210 or not RESOLVED <= before:
        raise RuntimeError("Terminal action 5e576c frontier changed")
    obj = OUT / "terminal_ui_action_5e576c.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                    "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    linked = OUT / "apollo-main-terminal-ui-action-5e576c-bound.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), "-o", str(linked)], check=True)
    after = imports(linked)
    if before - after != RESOLVED or after - before != {"audio_terminal_fsm_prepare_5eae94", "audio_terminal_display_fallback_5ecafa"} or len(after) != 211:
        raise RuntimeError(f"Terminal action 5e576c frontier changed: {len(after)} {before-after=} {after-before=}")
    result = {"status": "PASS_EXPERIMENTAL_MAIN_TERMINAL_UI_ACTION_5E576C_C",
              "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
              "oracle_receipt": str(ORACLE.relative_to(ROOT)), "oracle_receipt_sha256": sha(ORACLE),
              "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj),
              "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
              "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
              "unresolved_before": 210, "unresolved_after": 211,
              "imports_resolved": sorted(RESOLVED), "imports_added": sorted({"audio_terminal_fsm_prepare_5eae94", "audio_terminal_display_fallback_5ecafa"}),
              "source_complete": False, "full_payload_linked": False, "hardware_proof": False,
              "limits": ["Child effects and final placement remain open."]}
    receipt = OUT / "receipt.json"
    receipt.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["status"], sha(receipt))

if __name__ == "__main__":
    main()
