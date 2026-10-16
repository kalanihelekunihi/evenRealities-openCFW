#!/usr/bin/env python3
"""Bind stock-compared Terminal query-dismiss FSM action into Apollo Main."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
BASE = G2 / "build/c-firmware/20261016/main-terminal-select-output-mode-5ea2a8/apollo-main-terminal-select-output-mode-bound.o"
OUT = G2 / "build/c-firmware/20261016/main-terminal-ui-action-dismiss-query-5e68b4"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/terminal_ui_action_dismiss_query_5e68b4.c"
ORACLE = OUT / "oracle-receipt.json"
RESOLVED = {"audio_terminal_ui_action_5e68b4"}
ADDED = {"audio_terminal_ui_restore_query_5e6620"}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def imports(path):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-u", str(path)], text=True).splitlines()}


def main():
    oracle = json.loads(ORACLE.read_text())
    if oracle["status"] != "PASS_EXPERIMENTAL_TERMINAL_UI_ACTION_DISMISS_QUERY_C_ORACLE" or \
            oracle["cases"] != 160 or oracle["source_sha256"] != sha(SOURCE):
        raise RuntimeError("Terminal query-dismiss action oracle changed")
    before = imports(BASE)
    if len(before) != 221 or not RESOLVED <= before:
        raise RuntimeError("Apollo Terminal query-dismiss frontier changed")
    obj = OUT / "terminal_ui_action_dismiss_query_5e68b4.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                    "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    linked = OUT / "apollo-main-terminal-ui-action-dismiss-query-bound.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj),
                    "-o", str(linked)], check=True)
    after = imports(linked)
    if before-after != RESOLVED or after-before != ADDED or len(after) != 221:
        raise RuntimeError(f"Terminal query-dismiss frontier changed: {len(after)} "
                           f"{before-after=} {after-before=}")
    result = {"status": "PASS_EXPERIMENTAL_MAIN_TERMINAL_UI_ACTION_DISMISS_QUERY_C",
              "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
              "oracle_receipt": str(ORACLE.relative_to(ROOT)), "oracle_receipt_sha256": sha(ORACLE),
              "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj),
              "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
              "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
              "unresolved_before": 221, "unresolved_after": 221,
              "imports_resolved": sorted(RESOLVED), "imports_added": sorted(ADDED),
              "source_complete": False, "full_payload_linked": False, "hardware_proof": False,
              "limits": ["Query-restore child effect and final shared Terminal RAM placement remain open."]}
    receipt = OUT / "receipt.json"
    receipt.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["status"], sha(receipt))


if __name__ == "__main__":
    main()
