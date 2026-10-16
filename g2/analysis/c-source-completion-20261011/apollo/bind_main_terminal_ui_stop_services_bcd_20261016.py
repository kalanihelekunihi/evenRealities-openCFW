#!/usr/bin/env python3
"""Bind three stock-compared terminal cleanup children."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/terminal_ui_stop_services_bcd_5ec268.c"
BASE = G2 / "build/c-firmware/20261016/main-terminal-ui-stop-timer-5e7ec4/apollo-main-terminal-ui-stop-timer-bound.o"
ORACLE = G2 / "build/c-firmware/20261016/main-terminal-ui-stop-services-bcd/oracle-receipt.json"
OUT = G2 / "build/c-firmware/20261016/main-terminal-ui-stop-services-bcd"
RESOLVED = {"audio_terminal_ui_stop_service_b_5ec268",
            "audio_terminal_ui_stop_service_c_5ebbc6",
            "audio_terminal_ui_stop_service_d_5ec770"}
ADDED = {"audio_terminal_ui_event_5e5484"}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def imports(path):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-u", str(path)], text=True).splitlines()}


def main():
    oracle = json.loads(ORACLE.read_text())
    if (oracle["status"] != "PASS_EXPERIMENTAL_TERMINAL_UI_STOP_SERVICES_BCD_C_ORACLE"
            or oracle["cases"] != 24 or oracle["source_sha256"] != sha(SOURCE)):
        raise RuntimeError("terminal cleanup child oracle changed")
    before = imports(BASE)
    if len(before) != 171 or not RESOLVED <= before:
        raise RuntimeError("Apollo terminal cleanup child frontier changed")
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "terminal_ui_stop_services_bcd.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                    "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    linked = OUT / "apollo-main-terminal-ui-stop-services-bcd-bound.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), "-o",
                    str(linked)], check=True)
    after = imports(linked)
    if before-after != RESOLVED or after-before != ADDED or len(after) != 169:
        raise RuntimeError(f"terminal cleanup child binding frontier changed: {len(after)} {after-before}")
    result = {"status": "PASS_EXPERIMENTAL_MAIN_TERMINAL_UI_STOP_SERVICES_BCD_C",
              "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
              "oracle_receipt": str(ORACLE.relative_to(ROOT)), "oracle_receipt_sha256": sha(ORACLE),
              "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj),
              "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
              "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
              "unresolved_before": 171, "unresolved_after": 169,
              "imports_resolved": sorted(RESOLVED), "imports_added": sorted(ADDED),
              "source_complete": False, "full_payload_linked": False, "hardware_proof": False,
              "limits": oracle["limits"]}
    receipt = OUT / "receipt.json"
    receipt.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["status"], sha(receipt))


if __name__ == "__main__":
    main()
