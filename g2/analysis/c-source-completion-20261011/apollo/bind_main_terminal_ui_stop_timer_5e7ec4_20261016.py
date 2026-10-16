#!/usr/bin/env python3
"""Bind the stock-compared terminal timer clear and observed RAM extent."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/terminal_ui_stop_timer_5e7ec4.c"
SCRIPT = G2 / "components/audio/uart_thread_source_candidate/terminal_ui_timer_state_20073c38.ld"
BASE = G2 / "build/c-firmware/20261016/main-terminal-list-anim-stop-5896b4/apollo-main-terminal-list-anim-stop-bound.o"
ORACLE = G2 / "build/c-firmware/20261016/main-terminal-ui-stop-timer-5e7ec4/oracle-receipt.json"
OUT = G2 / "build/c-firmware/20261016/main-terminal-ui-stop-timer-5e7ec4"
SYMBOL = "audio_terminal_ui_stop_timer_5e7ec4"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def imports(path):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-u", str(path)], text=True).splitlines()}


def main():
    oracle = json.loads(ORACLE.read_text())
    if (oracle["status"] != "PASS_EXPERIMENTAL_TERMINAL_UI_STOP_TIMER_C_ORACLE"
            or oracle["cases"] != 4 or oracle["source_sha256"] != sha(SOURCE)):
        raise RuntimeError("terminal timer oracle changed")
    before = imports(BASE)
    if len(before) != 172 or SYMBOL not in before:
        raise RuntimeError("Apollo terminal timer frontier changed")
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "terminal_ui_stop_timer.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                    "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    placed = OUT / "terminal_ui_stop_timer_placed.o"
    subprocess.run(["arm-none-eabi-ld", "-r", "-T", str(SCRIPT), str(obj),
                    "-o", str(placed)], check=True)
    nm = subprocess.check_output(["arm-none-eabi-nm", "-S", str(placed)], text=True)
    if not any(line.split()[:2] == ["20073c38", "00000018"] and
               line.split()[-1] == "audio_terminal_ui_timer_state_20073c38"
               for line in nm.splitlines()):
        raise RuntimeError("terminal timer RAM placement changed")
    linked = OUT / "apollo-main-terminal-ui-stop-timer-bound.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(placed), "-o",
                    str(linked)], check=True)
    after = imports(linked)
    if before-after != {SYMBOL} or after-before or len(after) != 171:
        raise RuntimeError("terminal timer binding frontier changed")
    result = {"status": "PASS_EXPERIMENTAL_MAIN_TERMINAL_UI_STOP_TIMER_C",
              "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
              "placement_script": str(SCRIPT.relative_to(ROOT)), "placement_script_sha256": sha(SCRIPT),
              "oracle_receipt": str(ORACLE.relative_to(ROOT)), "oracle_receipt_sha256": sha(ORACLE),
              "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj),
              "placed_object": str(placed.relative_to(ROOT)), "placed_sha256": sha(placed),
              "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
              "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
              "ram_base": "0x20073c38", "ram_extent": "0x18",
              "unresolved_before": 172, "unresolved_after": 171,
              "imports_resolved": [SYMBOL], "imports_added": [],
              "source_complete": False, "full_payload_linked": False, "hardware_proof": False,
              "limits": oracle["limits"]}
    receipt = OUT / "receipt.json"
    receipt.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["status"], sha(receipt))


if __name__ == "__main__":
    main()
