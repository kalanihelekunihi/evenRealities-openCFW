#!/usr/bin/env python3
"""Place three non-overlapping Terminal output RAM cells at stock addresses."""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
BASE = G2 / "build/c-firmware/20261016/main-terminal-set-output-5e49b0/apollo-main-terminal-set-output-bound.o"
OUT = G2 / "build/c-firmware/20261016/main-terminal-output-ram-cells"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/terminal_output_ram_cells_20261016.c"
SCRIPT = G2 / "components/audio/uart_thread_source_candidate/terminal_output_ram_cells_20261016.ld"
PAYLOAD = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
PIN = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
CELLS = {"audio_terminal_output_payload_20074a94": (0x20074a94, 4),
         "audio_terminal_output_active_2007502c": (0x2007502c, 1),
         "audio_terminal_output_mode_2007502d": (0x2007502d, 1)}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def imports(path):
    return {line.split()[-1] for line in subprocess.check_output(
        ["arm-none-eabi-nm", "-u", str(path)], text=True).splitlines()}


def main():
    blob = PAYLOAD.read_bytes()[32:]
    if hashlib.sha256(blob).hexdigest() != PIN:
        raise RuntimeError("Apollo stock payload changed")
    for literal, address in ((0x5e555c, 0x20074a94), (0x5e5560, 0x2007502d),
                             (0x5e5564, 0x2007502c)):
        if int.from_bytes(blob[literal-0x438000:literal-0x438000+4], "little") != address:
            raise RuntimeError(f"Terminal output RAM literal {literal:#x} changed")
    before = imports(BASE)
    if len(before) != 222 or not CELLS.keys() <= before:
        raise RuntimeError("Apollo Terminal output RAM frontier changed")
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "terminal_output_ram_cells.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                    "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    placed = OUT / "terminal_output_ram_cells_placed.o"
    subprocess.run(["arm-none-eabi-ld", "-r", "-T", str(SCRIPT), str(obj),
                    "-o", str(placed)], check=True)
    nm = subprocess.check_output(["arm-none-eabi-nm", "-S", str(placed)], text=True)
    found = {p[-1]: (int(p[0], 16), int(p[1], 16)) for line in nm.splitlines()
             if len(p := line.split()) >= 4}
    if any(found.get(name) != expected for name, expected in CELLS.items()):
        raise RuntimeError(f"Terminal output RAM addresses changed: {found}")
    linked = OUT / "apollo-main-terminal-output-ram-bound.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(placed),
                    "-o", str(linked)], check=True)
    after = imports(linked)
    if before-after != CELLS.keys() or after-before or len(after) != 219:
        raise RuntimeError(f"Terminal output RAM frontier changed: {len(after)}")
    result = {"status": "PASS_EXPERIMENTAL_MAIN_TERMINAL_OUTPUT_RAM_CELLS",
              "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
              "placement_script": str(SCRIPT.relative_to(ROOT)), "placement_script_sha256": sha(SCRIPT),
              "stock_payload_sha256": PIN, "stock_literals": {
                  "0x5e555c": "0x20074a94", "0x5e5560": "0x2007502d", "0x5e5564": "0x2007502c"},
              "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj),
              "placed_object": str(placed.relative_to(ROOT)), "placed_sha256": sha(placed),
              "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
              "linked_object": str(linked.relative_to(ROOT)), "linked_sha256": sha(linked),
              "cells": {name: {"address": f"0x{address:08x}", "size": size}
                        for name, (address, size) in CELLS.items()},
              "unresolved_before": 222, "unresolved_after": 219,
              "imports_resolved": sorted(CELLS), "imports_added": [],
              "source_complete": False, "full_payload_linked": False, "hardware_proof": False,
              "limits": ["Full RAM map and adjacent 0x20074a90 ownership remain to be checked in final image placement; style RAM 0x20003f80 extent remains open."]}
    receipt = OUT / "receipt.json"
    receipt.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["status"], sha(receipt))


if __name__ == "__main__":
    main()
