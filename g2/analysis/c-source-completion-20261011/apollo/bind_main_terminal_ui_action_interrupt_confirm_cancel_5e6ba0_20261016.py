#!/usr/bin/env python3
"""Bind stock-compared Terminal interrupt-confirm-cancel action."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
BASE = G2 / "build/c-firmware/20261016/main-terminal-ui-action-interrupt-confirm-show-5e6b18/apollo-main-terminal-ui-interrupt-confirm-show-bound.o"
OUT = G2 / "build/c-firmware/20261016/main-terminal-ui-action-interrupt-confirm-cancel-5e6ba0"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/terminal_ui_action_interrupt_confirm_cancel_5e6ba0.c"
ORACLE = OUT / "oracle-receipt.json"
RESOLVED = {"audio_terminal_ui_action_5e6ba0"}

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def imports(path):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-u", str(path)], text=True).splitlines()}

def main():
    oracle = json.loads(ORACLE.read_text())
    if oracle["status"] != "PASS_EXPERIMENTAL_TERMINAL_INTERRUPT_CONFIRM_CANCEL_C_ORACLE" or \
            oracle["cases"] != 192 or oracle["source_sha256"] != sha(SOURCE):
        raise RuntimeError("Terminal interrupt-confirm-cancel oracle changed")
    before = imports(BASE)
    if len(before) != 205 or not RESOLVED <= before:
        raise RuntimeError("Terminal interrupt-confirm-cancel frontier changed")
    obj = OUT / "terminal_ui_action_interrupt_confirm_cancel_5e6ba0.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                    "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    linked = OUT / "apollo-main-terminal-ui-interrupt-confirm-cancel-bound.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), "-o", str(linked)], check=True)
    after = imports(linked)
    if before - after != RESOLVED or after - before or len(after) != 204:
        raise RuntimeError(f"Terminal interrupt-confirm-cancel frontier changed: {len(after)} {before-after=} {after-before=}")
    result = {"status": "PASS_EXPERIMENTAL_MAIN_TERMINAL_INTERRUPT_CONFIRM_CANCEL_C",
              "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
              "oracle_receipt": str(ORACLE.relative_to(ROOT)), "oracle_receipt_sha256": sha(ORACLE),
              "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj),
              "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
              "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
              "unresolved_before": 205, "unresolved_after": 204,
              "imports_resolved": sorted(RESOLVED), "imports_added": [],
              "source_complete": False, "full_payload_linked": False, "hardware_proof": False,
              "limits": ["Cleanup and logger lower effects remain isolated; final placement open."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["status"], sha(path))

if __name__ == "__main__":
    main()
