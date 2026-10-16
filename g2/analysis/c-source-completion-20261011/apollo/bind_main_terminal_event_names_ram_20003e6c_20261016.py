#!/usr/bin/env python3
"""Bind the stock terminal event-name array's observed RAM extent."""
import hashlib
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/terminal_event_names_ram_20003e6c.c"
LINKER = G2 / "components/audio/uart_thread_source_candidate/terminal_event_names_ram_20003e6c.ld"
PAYLOAD = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
BASE = G2 / "build/c-firmware/20261016/main-fault-lookup-overrun/apollo-main-fault-lookup-overrun-bound.o"
OUT = G2 / "build/c-firmware/20261016/main-terminal-event-names-ram"
PIN = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
SYMBOL = "audio_terminal_event_names"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def imports(path):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-u", str(path)], text=True).splitlines()}


def main():
    blob = PAYLOAD.read_bytes()[32:]
    if hashlib.sha256(blob).hexdigest() != PIN or \
            int.from_bytes(blob[0x5ea200-0x438000:0x5ea204-0x438000], "little") != 0x20003e6c:
        raise RuntimeError("terminal event-name stock pointer changed")
    before = imports(BASE)
    if len(before) != 166 or SYMBOL not in before:
        raise RuntimeError("Apollo terminal event-name frontier changed")
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "terminal_event_names_ram.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                    "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    placed = OUT / "terminal-event-names-placement.o"
    subprocess.run(["arm-none-eabi-ld", "-r", "-T", str(LINKER), str(obj),
                    "-o", str(placed)], check=True)
    nm = subprocess.check_output(["arm-none-eabi-nm", "-S", str(placed)], text=True)
    if not re.search(r"^20003e6c 00000034 B audio_terminal_event_names$", nm, re.M):
        raise RuntimeError("terminal event-name RAM placement or extent changed")
    linked = OUT / "apollo-main-terminal-event-names-ram-bound.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), "-o",
                    str(linked)], check=True)
    after = imports(linked)
    if before - after != {SYMBOL} or after - before or len(after) != 165:
        raise RuntimeError("terminal event-name binding did not reduce exactly one import")
    result = {"status": "PASS_EXPERIMENTAL_MAIN_TERMINAL_EVENT_NAMES_RAM_C",
              "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
              "linker_fragment": str(LINKER.relative_to(ROOT)), "linker_sha256": sha(LINKER),
              "payload_sha256": PIN, "stock_pointer_literal": "0x20003e6c",
              "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj),
              "placement_object": str(placed.relative_to(ROOT)), "placement_sha256": sha(placed),
              "placement_address": "0x20003e6c", "section_bytes": 52,
              "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
              "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
              "unresolved_before": 166, "unresolved_after": 165,
              "imports_resolved": [SYMBOL], "imports_added": [],
              "source_complete": False, "full_payload_linked": False, "hardware_proof": False,
              "limits": ["Only the thirteen pointer slots are source-owned; their runtime initialization and strings remain open.",
                         "Final RAM collision and whole-image placement remain open."]}
    receipt = OUT / "receipt.json"
    receipt.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["status"], sha(receipt))


if __name__ == "__main__":
    main()
