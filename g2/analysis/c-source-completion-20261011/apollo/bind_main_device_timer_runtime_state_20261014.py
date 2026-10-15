#!/usr/bin/env python3
"""Bind six selected timer handle/control-block RAM contracts to C."""
import json
import struct
import subprocess
from pathlib import Path

from verify_main_master_dispatch_children_20261014 import image, names, sha

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/master_dispatch_candidate_20261014/device_timer_runtime_state.c"
BOX = G2 / "components/audio/uart_thread_source_candidate/display_box_detect_init.c"
DEVICE = G2 / "components/audio/uart_thread_source_candidate/display_device_resource_init.c"
NATIVE = G2 / "analysis/shortcut-arm-tools-20261009-agent3/main-analysis-only.elf"
BASE = G2 / "build/c-firmware/20261014/main-event-loop-runtime-state/apollo-main-event-loop-runtime-state.o"
OUT = G2 / "build/c-firmware/20261014/main-device-timer-runtime-state"
CONTRACTS = {
    "audio_box_detect_timer": (0x20074920, 0x4aca98, 4),
    "audio_box_detect_timer_control_block": (0x2007367c, 0x788758, 44),
    "audio_box_reconnect_timer": (0x20074924, 0x4acb08, 4),
    "audio_box_reconnect_timer_control_block": (0x200736a8, 0x788768, 44),
    "audio_device_manager_timer": (0x200744c0, 0x4c6c34, 4),
    "audio_device_manager_timer_control_block": (0x200735a0, 0x785a78, 44),
}


def bytes_at(segments, address):
    for base, data in segments:
        if base <= address and address + 4 <= base + len(data):
            return data[address-base:address-base+4]
    raise RuntimeError(f"unmapped native address {address:#x}")


def main():
    segments, _ = image(NATIVE)
    source, box, device = SOURCE.read_text(), BOX.read_text(), DEVICE.read_text()
    for name, (ram, literal, size) in CONTRACTS.items():
        if struct.unpack("<I", bytes_at(segments, literal))[0] != ram:
            raise RuntimeError(f"native timer RAM literal changed: {name}")
        user = box if name.startswith("audio_box_") else device
        source_declaration = f"void *{name} " if size == 4 else f"uint8_t {name}[44u]"
        user_declaration = f"extern void *{name};" if size == 4 else f"extern uint8_t {name}[44];"
        if source_declaration not in source or user_declaration not in user or \
           f".g2_ram_{ram:08x}" not in source:
            raise RuntimeError(f"timer source/user declaration changed: {name}")
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "device_timer_runtime_state.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                    "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    if names(obj, "-g", "--defined-only") != set(CONTRACTS) or names(obj, "-u"):
        raise RuntimeError("timer C symbol contract changed")
    sizes = {}
    for line in subprocess.check_output(["arm-none-eabi-nm", "-g", "-S", str(obj)], text=True).splitlines():
        parts = line.split()
        if len(parts) == 4 and parts[-1] in CONTRACTS:
            sizes[parts[-1]] = int(parts[1], 16)
    if sizes != {name: row[2] for name, row in CONTRACTS.items()}:
        raise RuntimeError(f"timer C storage sizes changed: {sizes}")
    before = names(BASE, "-u")
    if not set(CONTRACTS) <= before:
        raise RuntimeError("Apollo Main timer imports changed")
    linked = OUT / "apollo-main-device-timer-runtime-state.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), "-o", str(linked)], check=True)
    after = names(linked, "-u")
    if before - after != set(CONTRACTS) or after - before:
        raise RuntimeError(f"unexpected import delta: {before-after}, {after-before}")
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_DEVICE_TIMER_RUNTIME_STATE_C",
               "native_elf": str(NATIVE.relative_to(ROOT)), "native_elf_sha256": sha(NATIVE),
               "native_contracts": {name: {"ram": hex(ram), "literal": hex(literal),
                                            "source_bytes": size}
                                    for name, (ram, literal, size) in CONTRACTS.items()},
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "user_sources": {str(p.relative_to(ROOT)): sha(p) for p in (BOX, DEVICE)},
               "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj),
               "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
               "linked_object": str(linked.relative_to(ROOT)), "linked_object_sha256": sha(linked),
               "unresolved_before": len(before), "unresolved_after": len(after),
               "imports_resolved": sorted(before-after), "imports_added": sorted(after-before),
               "source_complete": False, "full_payload_linked": False,
               "limits": ["Selected timer initializer handle/control-block sizes are covered; CMSIS timer internals and lifetime remain external.",
                          "Final SRAM placement, whole-image and hardware behavior remain open."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(path))


if __name__ == "__main__":
    main()
