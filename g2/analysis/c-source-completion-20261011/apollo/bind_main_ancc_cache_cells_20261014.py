#!/usr/bin/env python3
"""Bind native ANCC cache, registration cells, and connection tick."""
import json
import struct
import subprocess
from pathlib import Path

from verify_main_master_dispatch_children_20261014 import image, names, sha

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/master_dispatch_candidate_20261014/ancc_cache_cells.c"
USER = G2 / "components/audio/uart_thread_source_candidate/display_ble_ancc_init.c"
NATIVE = G2 / "analysis/shortcut-arm-tools-20261009-agent3/main-analysis-only.elf"
BASE = G2 / "build/c-firmware/20261014/main-comm-wsf-state/apollo-main-comm-wsf-state.o"
OUT = G2 / "build/c-firmware/20261014/main-ancc-cache-cells"
STATES = {
    "audio_ble_ancc_cache": (0x2006ddd4, 0x4bf900, 0x2fc),
    "audio_ble_ancc_controller": (0x20074898, 0x4bf974, 4),
    "audio_ble_ancc_mode": (0x2007489c, 0x4bf978, 4),
    "audio_ble_ancc_service_context": (0x200748a0, 0x4bf8f0, 4),
    "audio_ble_ancc_connection_tick": (0x200742f4, 0x4b82d4, 4),
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
            raise RuntimeError(f"native ANCC RAM literal changed: {name}")
    if "audio_uart_buffer_zero(audio_ble_ancc_cache,0x2fcu,0u);" not in USER.read_text():
        raise RuntimeError("ANCC cache initialization range changed")
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "ancc_cache_cells.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                    "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    if names(obj, "-g", "--defined-only") != set(STATES) or names(obj, "-u"):
        raise RuntimeError("ANCC cache C symbol contract changed")
    output = subprocess.check_output(["arm-none-eabi-nm", "-g", "-S", str(obj)], text=True)
    sizes = {parts[-1]: int(parts[1], 16) for line in output.splitlines()
             if len(parts := line.split()) == 4 and parts[-1] in STATES}
    if sizes != {name: size for name, (_, _, size) in STATES.items()}:
        raise RuntimeError(f"ANCC cache cell sizes changed: {sizes}")
    before = names(BASE, "-u")
    if not set(STATES) <= before:
        raise RuntimeError(f"Apollo Main ANCC imports changed: {set(STATES)-before}")
    linked = OUT / "apollo-main-ancc-cache-cells.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), "-o", str(linked)], check=True)
    after = names(linked, "-u")
    if before - after != set(STATES) or after - before:
        raise RuntimeError(f"unexpected import delta: {before-after}, {after-before}")
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_ANCC_CACHE_CELLS_C",
               "native_elf": str(NATIVE.relative_to(ROOT)), "native_elf_sha256": sha(NATIVE),
               "native_states": {name: {"ram": hex(ram), "literal": hex(literal),
                                        "source_bytes": size}
                                 for name, (ram, literal, size) in STATES.items()},
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "user_source": str(USER.relative_to(ROOT)), "user_source_sha256": sha(USER),
               "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj),
               "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
               "linked_object": str(linked.relative_to(ROOT)),
               "linked_object_sha256": sha(linked),
               "unresolved_before": len(before), "unresolved_after": len(after),
               "imports_resolved": sorted(before-after), "imports_added": sorted(after-before),
               "source_complete": False, "full_payload_linked": False,
               "limits": ["The cache covers its observed initialization range; dynamic parser lengths and the complete native allocation span remain open.",
                          "Pointer values are populated by runtime initialization; connection tick startup and final RAM placement remain open.",
                          "Whole-image and hardware behavior remain open."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(path))


if __name__ == "__main__":
    main()
