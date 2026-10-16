#!/usr/bin/env python3
"""Bind stock-compared FSM name lookups and observed RAM extents."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/terminal_ui_fsm_names_5e7b10.c"
SCRIPT = G2 / "components/audio/uart_thread_source_candidate/terminal_ui_fsm_names_20003ea4.ld"
BASE = G2 / "build/c-firmware/20261016/main-terminal-ui-status-5e7b74/apollo-main-terminal-ui-status-bound.o"
ORACLE = G2 / "build/c-firmware/20261016/main-terminal-ui-fsm-names-5e7b10/oracle-receipt.json"
OUT = G2 / "build/c-firmware/20261016/main-terminal-ui-fsm-names-5e7b10"
RESOLVED = {"audio_terminal_ui_state_name_5e7b10",
            "audio_terminal_ui_event_name_5e7b2a"}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def imports(path):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-u", str(path)], text=True).splitlines()}


def main():
    oracle = json.loads(ORACLE.read_text())
    if (oracle["status"] != "PASS_EXPERIMENTAL_TERMINAL_UI_FSM_NAMES_C_ORACLE"
            or oracle["cases"] != 2048 or oracle["source_sha256"] != sha(SOURCE)):
        raise RuntimeError("Terminal FSM name oracle changed")
    before = imports(BASE)
    if len(before) != 217 or not RESOLVED <= before:
        raise RuntimeError("Apollo Terminal FSM name frontier changed")
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "terminal_ui_fsm_names.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                    "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    placed = OUT / "terminal_ui_fsm_names_placed.o"
    subprocess.run(["arm-none-eabi-ld", "-r", "-T", str(SCRIPT), str(obj),
                    "-o", str(placed)], check=True)
    nm = subprocess.check_output(["arm-none-eabi-nm", "-S", str(placed)], text=True)
    expected = {("20003ea4", "00000034", "audio_terminal_ui_state_names"),
                ("20003edc", "000000a0", "audio_terminal_ui_event_names")}
    actual = {tuple(line.split()[i] for i in (0, 1, -1)) for line in nm.splitlines()
              if len(line.split()) >= 4}
    if not expected <= actual:
        raise RuntimeError("Terminal FSM name RAM placement changed")
    linked = OUT / "apollo-main-terminal-ui-fsm-names-bound.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(placed), "-o",
                    str(linked)], check=True)
    after = imports(linked)
    if before-after != RESOLVED or after-before or len(after) != 215:
        raise RuntimeError("Terminal FSM name binding frontier changed")
    result = {"status": "PASS_EXPERIMENTAL_MAIN_TERMINAL_UI_FSM_NAMES_C",
              "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
              "placement_script": str(SCRIPT.relative_to(ROOT)), "placement_script_sha256": sha(SCRIPT),
              "oracle_receipt": str(ORACLE.relative_to(ROOT)), "oracle_receipt_sha256": sha(ORACLE),
              "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj),
              "placed_object": str(placed.relative_to(ROOT)), "placed_sha256": sha(placed),
              "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
              "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
              "state_names_ram": "0x20003ea4", "event_names_ram": "0x20003edc",
              "unresolved_before": 217, "unresolved_after": 215,
              "imports_resolved": sorted(RESOLVED), "imports_added": [],
              "source_complete": False, "full_payload_linked": False, "hardware_proof": False,
              "limits": oracle["limits"]}
    receipt = OUT / "receipt.json"
    receipt.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["status"], sha(receipt))


if __name__ == "__main__":
    main()
