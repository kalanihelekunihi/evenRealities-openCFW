#!/usr/bin/env python3
"""Bind native BLE profile pointer cells and radio mode selectors."""
import json
import struct
import subprocess
from pathlib import Path

from verify_main_master_dispatch_children_20261014 import image, names, sha

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/master_dispatch_candidate_20261014/ble_pointer_cells.c"
NATIVE = G2 / "analysis/shortcut-arm-tools-20261009-agent3/main-analysis-only.elf"
BASE = G2 / "build/c-firmware/20261014/main-task-vote-state/apollo-main-task-vote-state.o"
OUT = G2 / "build/c-firmware/20261014/main-ble-pointer-cells"
CELLS = {
    "audio_ble_msgtx_state": (0x20074338, 0x478718, 4),
    "audio_ble_msgtx_mode": (0x2007433c, 0x478700, 4),
    "audio_ble_msgtx_table_slot": (0x2007435c, 0x477754, 4),
    "audio_ble_profile_dispatch_slot": (0x20074360, 0x5355a0, 4),
    "audio_ble_profile_table_slot": (0x20074364, 0x5355a8, 4),
    "audio_ble_hci_radio_mode_cells_20074368": (0x20074368, 0x509494, 3),
}


def bytes_at(segments, address):
    for base, data in segments:
        if base <= address and address + 4 <= base + len(data):
            return data[address-base:address-base+4]
    raise RuntimeError(f"unmapped native address {address:#x}")


def main():
    segments, _ = image(NATIVE)
    for name, (ram, literal, _) in CELLS.items():
        if struct.unpack("<I", bytes_at(segments, literal))[0] != ram:
            raise RuntimeError(f"native BLE cell literal changed: {name}")
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "ble_pointer_cells.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                    "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    if names(obj, "-g", "--defined-only") != set(CELLS) or names(obj, "-u"):
        raise RuntimeError("BLE pointer cell C symbol contract changed")
    output = subprocess.check_output(["arm-none-eabi-nm", "-g", "-S", str(obj)], text=True)
    sizes = {parts[-1]: int(parts[1], 16) for line in output.splitlines()
             if len(parts := line.split()) == 4 and parts[-1] in CELLS}
    if sizes != {name: size for name, (_, _, size) in CELLS.items()}:
        raise RuntimeError(f"BLE pointer cell sizes changed: {sizes}")
    before = names(BASE, "-u")
    if not set(CELLS) <= before:
        raise RuntimeError(f"Apollo Main BLE cell imports changed: {set(CELLS)-before}")
    linked = OUT / "apollo-main-ble-pointer-cells.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), "-o", str(linked)], check=True)
    after = names(linked, "-u")
    if before - after != set(CELLS) or after - before:
        raise RuntimeError(f"unexpected import delta: {before-after}, {after-before}")
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_BLE_POINTER_CELLS_C",
               "native_elf": str(NATIVE.relative_to(ROOT)), "native_elf_sha256": sha(NATIVE),
               "native_cells": {name: {"ram": hex(ram), "literal": hex(literal),
                                       "source_bytes": size}
                                for name, (ram, literal, size) in CELLS.items()},
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj),
               "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
               "linked_object": str(linked.relative_to(ROOT)),
               "linked_object_sha256": sha(linked),
               "unresolved_before": len(before), "unresolved_after": len(after),
               "imports_resolved": sorted(before-after), "imports_added": sorted(after-before),
               "source_complete": False, "full_payload_linked": False,
               "limits": ["Runtime profile initializers remain the source of pointer values; startup values for radio mode cells remain open.",
                          "Each symbol is source-owned; native adjacency and final SRAM placement are not established by this relocatable link.",
                          "Whole-image and hardware behavior remain open."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(path))


if __name__ == "__main__":
    main()
