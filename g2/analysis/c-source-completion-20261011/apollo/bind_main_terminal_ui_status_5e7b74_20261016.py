#!/usr/bin/env python3
"""Bind stock-compared Terminal FSM dispatcher and exact table extent."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
DISPATCH = G2 / "components/audio/uart_thread_source_candidate/terminal_ui_status_5e7b74.c"
TABLE = G2 / "components/audio/uart_thread_source_candidate/terminal_ui_fsm_table_650430.c"
SCRIPT = G2 / "components/audio/uart_thread_source_candidate/terminal_ui_fsm_table_650430.ld"
BASE = G2 / "build/c-firmware/20261016/main-terminal-ui-tick-5e8008/apollo-main-terminal-ui-tick-bound.o"
ORACLE = G2 / "build/c-firmware/20261016/main-terminal-ui-status-5e7b74/oracle-receipt.json"
OUT = G2 / "build/c-firmware/20261016/main-terminal-ui-status-5e7b74"
SYMBOL = "audio_terminal_ui_status_5e7b74"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def imports(path):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-u", str(path)], text=True).splitlines()}


def compile_one(source, obj):
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                    "-Wextra", "-Werror", "-c", str(source), "-o", str(obj)], check=True)


def main():
    oracle = json.loads(ORACLE.read_text())
    if (oracle["status"] != "PASS_EXPERIMENTAL_TERMINAL_UI_STATUS_C_ORACLE"
            or oracle["cases"] != 775 or oracle["source_sha256"] != sha(DISPATCH)
            or oracle["table_source_sha256"] != sha(TABLE)
            or oracle["distinct_callback_targets"] != 50):
        raise RuntimeError("Terminal FSM oracle changed")
    before = imports(BASE)
    if len(before) != 166 or SYMBOL not in before:
        raise RuntimeError("Apollo Terminal FSM frontier changed")
    OUT.mkdir(parents=True, exist_ok=True)
    dispatch_obj = OUT / "terminal_ui_status.o"
    table_obj = OUT / "terminal_ui_fsm_table.o"
    compile_one(DISPATCH, dispatch_obj)
    compile_one(TABLE, table_obj)
    placed = OUT / "terminal_ui_fsm_table_placed.o"
    subprocess.run(["arm-none-eabi-ld", "-r", "-T", str(SCRIPT), str(table_obj),
                    "-o", str(placed)], check=True)
    nm = subprocess.check_output(["arm-none-eabi-nm", "-S", str(placed)], text=True)
    if not any(line.split()[:2] == ["00650430", "00001040"] and
               line.split()[-1] == "audio_terminal_ui_fsm_table"
               for line in nm.splitlines()):
        raise RuntimeError("Terminal FSM table placement changed")
    linked = OUT / "apollo-main-terminal-ui-status-bound.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(dispatch_obj),
                    str(placed), "-o", str(linked)], check=True)
    after = imports(linked)
    added = after-before
    callbacks = {name for name in added if name.startswith("audio_terminal_ui_action_")}
    names = {"audio_terminal_ui_state_name_5e7b10", "audio_terminal_ui_event_name_5e7b2a"}
    if before-after != {SYMBOL} or len(callbacks) != 50 or added != callbacks|names or \
            len(after) != 217:
        raise RuntimeError(f"Terminal FSM binding frontier changed: {len(after)} {added}")
    result = {"status": "PASS_EXPERIMENTAL_MAIN_TERMINAL_UI_STATUS_C",
              "source": str(DISPATCH.relative_to(ROOT)), "source_sha256": sha(DISPATCH),
              "table_source": str(TABLE.relative_to(ROOT)), "table_source_sha256": sha(TABLE),
              "placement_script": str(SCRIPT.relative_to(ROOT)), "placement_script_sha256": sha(SCRIPT),
              "oracle_receipt": str(ORACLE.relative_to(ROOT)), "oracle_receipt_sha256": sha(ORACLE),
              "dispatch_object": str(dispatch_obj.relative_to(ROOT)), "dispatch_object_sha256": sha(dispatch_obj),
              "table_object": str(table_obj.relative_to(ROOT)), "table_object_sha256": sha(table_obj),
              "placed_table_object": str(placed.relative_to(ROOT)), "placed_table_sha256": sha(placed),
              "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
              "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
              "table_base": "0x650430", "table_extent": "0x1040",
              "unresolved_before": 166, "unresolved_after": 217,
              "imports_resolved": [SYMBOL], "imports_added": sorted(added),
              "source_complete": False, "full_payload_linked": False, "hardware_proof": False,
              "limits": oracle["limits"]}
    receipt = OUT / "receipt.json"
    receipt.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["status"], sha(receipt))


if __name__ == "__main__":
    main()
