#!/usr/bin/env python3
"""Bind the stock-compared terminal UI registry callback."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/terminal_ui_event_handler_5e44f6.c"
BASE = G2 / "build/c-firmware/20261016/main-terminal-event-names-ram/apollo-main-terminal-event-names-ram-bound.o"
ORACLE = G2 / "build/c-firmware/20261016/main-terminal-ui-event-5e44f6/oracle-receipt.json"
OUT = G2 / "build/c-firmware/20261016/main-terminal-ui-event-5e44f6"
SYMBOL = "audio_uart_registry_callback_5e44f6"
CHILDREN = {"audio_terminal_ui_status_5e7b74", "audio_terminal_ui_tick_5e8008",
            "audio_terminal_ui_stop_5e720c", "audio_terminal_ui_start_5e716c",
            "audio_terminal_ui_exit_sync_5e42ec"}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def imports(path):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-u", str(path)], text=True).splitlines()}


def main():
    oracle = json.loads(ORACLE.read_text())
    if (oracle["status"] != "PASS_EXPERIMENTAL_TERMINAL_UI_EVENT_C_ORACLE"
            or oracle["cases"] != 224 or oracle["source_sha256"] != sha(SOURCE)):
        raise RuntimeError("terminal UI oracle changed")
    before = imports(BASE)
    if len(before) != 165 or SYMBOL not in before:
        raise RuntimeError("Apollo terminal UI frontier changed")
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "terminal_ui_event_handler.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                    "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    linked = OUT / "apollo-main-terminal-ui-event-bound.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), "-o",
                    str(linked)], check=True)
    after = imports(linked)
    if before-after != {SYMBOL} or after-before != CHILDREN or len(after) != 169:
        raise RuntimeError("terminal UI binding frontier changed")
    result = {"status": "PASS_EXPERIMENTAL_MAIN_TERMINAL_UI_EVENT_C",
              "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
              "oracle_receipt": str(ORACLE.relative_to(ROOT)), "oracle_receipt_sha256": sha(ORACLE),
              "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj),
              "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
              "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
              "unresolved_before": 165, "unresolved_after": 169,
              "imports_resolved": [SYMBOL], "imports_added": sorted(CHILDREN),
              "source_complete": False, "full_payload_linked": False, "hardware_proof": False,
              "limits": oracle["limits"] + ["Five exposed terminal child calls require C bodies."]}
    receipt = OUT / "receipt.json"
    receipt.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["status"], sha(receipt))


if __name__ == "__main__":
    main()
