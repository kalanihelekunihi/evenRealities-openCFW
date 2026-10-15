#!/usr/bin/env python3
"""Bind native ring-handler and three-cell AppUi callback state."""
import json
import struct
import subprocess
from pathlib import Path

from verify_main_master_dispatch_children_20261014 import image, names, sha

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/master_dispatch_candidate_20261014/ring_ui_state.c"
UI_USER = G2 / "components/audio/uart_thread_source_candidate/display_ble_app_ui_action.c"
NATIVE = G2 / "analysis/shortcut-arm-tools-20261009-agent3/main-analysis-only.elf"
BASE = G2 / "build/c-firmware/20261014/main-ancc-runtime-state/apollo-main-ancc-runtime-state.o"
OUT = G2 / "build/c-firmware/20261014/main-ring-ui-state"
STATES = {
    "audio_ble_ring_handler_state": (0x20074074, 0x4c4c68, 12),
    "audio_ble_ui_callback_cells": (0x20073f60, 0x4bdb1c, 12),
}


def bytes_at(segments, address):
    for base, data in segments:
        if base <= address and address + 4 <= base + len(data):
            return data[address-base:address-base+4]
    raise RuntimeError(f"unmapped native address {address:#x}")


def main():
    segments, _ = image(NATIVE)
    for name, (ram, literal, _) in STATES.items():
        if struct.unpack("<I", bytes_at(segments, literal))[0] != ram:
            raise RuntimeError(f"native ring/UI RAM literal changed: {name}")
    if "audio_ble_ui_callback_cells[3]" not in UI_USER.read_text():
        raise RuntimeError("AppUi callback declaration changed")
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "ring_ui_state.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                    "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    if names(obj, "-g", "--defined-only") != set(STATES) or names(obj, "-u"):
        raise RuntimeError("ring/UI C symbol contract changed")
    output = subprocess.check_output(["arm-none-eabi-nm", "-g", "-S", str(obj)], text=True)
    sizes = {parts[-1]: int(parts[1], 16) for line in output.splitlines()
             if len(parts := line.split()) == 4 and parts[-1] in STATES}
    if sizes != {name: size for name, (_, _, size) in STATES.items()}:
        raise RuntimeError(f"ring/UI source sizes changed: {sizes}")
    before = names(BASE, "-u")
    if not set(STATES) <= before:
        raise RuntimeError(f"Apollo Main ring/UI imports changed: {set(STATES)-before}")
    linked = OUT / "apollo-main-ring-ui-state.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), "-o", str(linked)], check=True)
    after = names(linked, "-u")
    if before - after != set(STATES) or after - before:
        raise RuntimeError(f"unexpected import delta: {before-after}, {after-before}")
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_RING_UI_STATE_C",
               "native_elf": str(NATIVE.relative_to(ROOT)), "native_elf_sha256": sha(NATIVE),
               "native_states": {name: {"ram": hex(ram), "literal": hex(literal),
                                        "source_bytes": size}
                                 for name, (ram, literal, size) in STATES.items()},
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "ui_user_source": str(UI_USER.relative_to(ROOT)), "ui_user_sha256": sha(UI_USER),
               "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj),
               "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
               "linked_object": str(linked.relative_to(ROOT)),
               "linked_object_sha256": sha(linked),
               "unresolved_before": len(before), "unresolved_after": len(after),
               "imports_resolved": sorted(before-after), "imports_added": sorted(after-before),
               "source_complete": False, "full_payload_linked": False,
               "limits": ["Ring and callback source objects cover observed layout; initialization and unobserved native tails remain open.",
                          "The linked AppUi user predates the corrected three-cell declaration and requires a root source rebuild for freshness.",
                          "Final SRAM placement, whole-image and hardware behavior remain open."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(path))


if __name__ == "__main__":
    main()
