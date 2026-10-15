#!/usr/bin/env python3
"""Bind native ANCC state at its observed end boundary and service bytes."""
import json
import struct
import subprocess
from pathlib import Path

from verify_main_master_dispatch_children_20261014 import image, names, sha

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/master_dispatch_candidate_20261014/ancc_runtime_state.c"
RESET = G2 / "components/audio/uart_thread_source_candidate/display_ble_slave_reset_children.c"
NATIVE = G2 / "analysis/shortcut-arm-tools-20261009-agent3/main-analysis-only.elf"
BASE = G2 / "build/c-firmware/20261014/main-ble-pointer-cells/apollo-main-ble-pointer-cells.o"
OUT = G2 / "build/c-firmware/20261014/main-ancc-runtime-state"
STATES = {
    "audio_ble_ancc_state": (0x200695c8, 0x4bf6c0, 0x55c),
    "audio_ble_ancc_service_state": (0x200036c8, 0x497cec, 5),
}
NEXT_RAM, NEXT_LITERAL = 0x20069b24, 0x5bfa5c


def bytes_at(segments, address):
    for base, data in segments:
        if base <= address and address + 4 <= base + len(data):
            return data[address-base:address-base+4]
    raise RuntimeError(f"unmapped native address {address:#x}")


def main():
    segments, _ = image(NATIVE)
    for name, (ram, literal, _) in STATES.items():
        if struct.unpack("<I", bytes_at(segments, literal))[0] != ram:
            raise RuntimeError(f"native ANCC RAM literal changed: {name}")
    if struct.unpack("<I", bytes_at(segments, NEXT_LITERAL))[0] != NEXT_RAM or \
       STATES["audio_ble_ancc_state"][0] + STATES["audio_ble_ancc_state"][2] != NEXT_RAM:
        raise RuntimeError("native ANCC observed-range boundary changed")
    if "audio_uart_buffer_zero(audio_ble_ancc_state+0x35cu,0x200u,0u);" not in RESET.read_text():
        raise RuntimeError("ANCC reset end-range changed")
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "ancc_runtime_state.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                    "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    if names(obj, "-g", "--defined-only") != set(STATES) or names(obj, "-u"):
        raise RuntimeError("ANCC C symbol contract changed")
    output = subprocess.check_output(["arm-none-eabi-nm", "-g", "-S", str(obj)], text=True)
    sizes = {parts[-1]: int(parts[1], 16) for line in output.splitlines()
             if len(parts := line.split()) == 4 and parts[-1] in STATES}
    if sizes != {name: size for name, (_, _, size) in STATES.items()}:
        raise RuntimeError(f"ANCC source sizes changed: {sizes}")
    before = names(BASE, "-u")
    if not set(STATES) <= before:
        raise RuntimeError(f"Apollo Main ANCC imports changed: {set(STATES)-before}")
    linked = OUT / "apollo-main-ancc-runtime-state.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), "-o", str(linked)], check=True)
    after = names(linked, "-u")
    if before - after != set(STATES) or after - before:
        raise RuntimeError(f"unexpected import delta: {before-after}, {after-before}")
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_ANCC_RUNTIME_STATE_C",
               "native_elf": str(NATIVE.relative_to(ROOT)), "native_elf_sha256": sha(NATIVE),
               "native_states": {name: {"ram": hex(ram), "literal": hex(literal),
                                        "source_bytes": size}
                                 for name, (ram, literal, size) in STATES.items()},
               "native_adjacent_ram_reference": {"ram": hex(NEXT_RAM), "literal": hex(NEXT_LITERAL)},
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "reset_source": str(RESET.relative_to(ROOT)), "reset_source_sha256": sha(RESET),
               "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj),
               "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
               "linked_object": str(linked.relative_to(ROOT)),
               "linked_object_sha256": sha(linked),
               "unresolved_before": len(before), "unresolved_after": len(after),
               "imports_resolved": sorted(before-after), "imports_added": sorted(after-before),
               "source_complete": False, "full_payload_linked": False,
               "limits": ["ANCC RAM state covers the reset range through +0x55b; the following RAM reference does not prove a distinct allocation or the full span.",
                          "The compressed-RAM service state covers observed bytes only; its full native allocation span remains open.",
                          "Final SRAM placement, whole-image and hardware behavior remain open."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(path))


if __name__ == "__main__":
    main()
