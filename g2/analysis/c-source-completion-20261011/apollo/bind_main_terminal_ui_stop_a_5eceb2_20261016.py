#!/usr/bin/env python3
"""Bind the stock-compared terminal timer/object cleanup leaf."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/terminal_ui_stop_service_a_5eceb2.c"
BASE = G2 / "build/c-firmware/20261016/main-terminal-ui-stop-e-5ec9c0/apollo-main-terminal-ui-stop-e-bound.o"
ORACLE = G2 / "build/c-firmware/20261016/main-terminal-ui-stop-a-5eceb2/oracle-receipt.json"
OUT = G2 / "build/c-firmware/20261016/main-terminal-ui-stop-a-5eceb2"
SYMBOL = "audio_terminal_ui_stop_service_a_5eceb2"
CHILD = "audio_terminal_ui_object_valid_43e2ea"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def imports(path):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-u", str(path)], text=True).splitlines()}


def main():
    oracle = json.loads(ORACLE.read_text())
    if (oracle["status"] != "PASS_EXPERIMENTAL_TERMINAL_UI_STOP_A_C_ORACLE"
            or oracle["cases"] != 27 or oracle["source_sha256"] != sha(SOURCE)):
        raise RuntimeError("terminal timer cleanup oracle changed")
    before = imports(BASE)
    if len(before) != 174 or SYMBOL not in before:
        raise RuntimeError("Apollo terminal timer cleanup frontier changed")
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "terminal_ui_stop_a.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                    "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    linked = OUT / "apollo-main-terminal-ui-stop-a-bound.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), "-o",
                    str(linked)], check=True)
    after = imports(linked)
    if before-after != {SYMBOL} or after-before != {CHILD} or len(after) != 174:
        raise RuntimeError("terminal timer cleanup binding frontier changed")
    result = {"status": "PASS_EXPERIMENTAL_MAIN_TERMINAL_UI_STOP_A_C",
              "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
              "oracle_receipt": str(ORACLE.relative_to(ROOT)), "oracle_receipt_sha256": sha(ORACLE),
              "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj),
              "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
              "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
              "unresolved_before": 174, "unresolved_after": 174,
              "imports_resolved": [SYMBOL], "imports_added": [CHILD],
              "source_complete": False, "full_payload_linked": False, "hardware_proof": False,
              "limits": oracle["limits"]}
    receipt = OUT / "receipt.json"
    receipt.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["status"], sha(receipt))


if __name__ == "__main__":
    main()
