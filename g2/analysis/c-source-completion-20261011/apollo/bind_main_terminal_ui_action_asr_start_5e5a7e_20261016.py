#!/usr/bin/env python3
"""Bind two stock-compared Terminal FSM ASR actions."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/terminal_ui_action_asr_start_5e5a7e.c"
BASE = G2 / "build/c-firmware/20261016/main-terminal-ui-fsm-names-5e7b10/apollo-main-terminal-ui-fsm-names-bound.o"
ORACLE = G2 / "build/c-firmware/20261016/main-terminal-ui-action-asr-start-5e5a7e/oracle-receipt.json"
OUT = G2 / "build/c-firmware/20261016/main-terminal-ui-action-asr-start-5e5a7e"
RESOLVED = {"audio_terminal_ui_action_5e5a7e", "audio_terminal_ui_action_5e5a94"}
ADDED = {"audio_terminal_ui_notification_restore_5ebfae"}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def imports(path):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-u", str(path)], text=True).splitlines()}


def main():
    oracle = json.loads(ORACLE.read_text())
    if (oracle["status"] != "PASS_EXPERIMENTAL_TERMINAL_UI_ACTION_ASR_START_C_ORACLE"
            or oracle["cases"] != 54 or oracle["source_sha256"] != sha(SOURCE)):
        raise RuntimeError("ASR action oracle changed")
    before = imports(BASE)
    if len(before) != 215 or not RESOLVED <= before:
        raise RuntimeError("Apollo ASR action frontier changed")
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "terminal_ui_action_asr_start.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                    "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    linked = OUT / "apollo-main-terminal-ui-action-asr-start-bound.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), "-o",
                    str(linked)], check=True)
    after = imports(linked)
    if before-after != RESOLVED or after-before != ADDED or len(after) != 214:
        raise RuntimeError(f"ASR action binding frontier changed: {len(after)} {after-before}")
    result = {"status": "PASS_EXPERIMENTAL_MAIN_TERMINAL_UI_ACTION_ASR_START_C",
              "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
              "oracle_receipt": str(ORACLE.relative_to(ROOT)), "oracle_receipt_sha256": sha(ORACLE),
              "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj),
              "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
              "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
              "unresolved_before": 215, "unresolved_after": 214,
              "imports_resolved": sorted(RESOLVED), "imports_added": sorted(ADDED),
              "source_complete": False, "full_payload_linked": False, "hardware_proof": False,
              "limits": oracle["limits"]}
    receipt = OUT / "receipt.json"
    receipt.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["status"], sha(receipt))


if __name__ == "__main__":
    main()
