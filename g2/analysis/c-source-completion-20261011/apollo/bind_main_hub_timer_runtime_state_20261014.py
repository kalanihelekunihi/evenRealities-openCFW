#!/usr/bin/env python3
"""Bind authenticated hub timer cells and timeout template to C."""
import json
import struct
import subprocess
from pathlib import Path

from verify_main_master_dispatch_children_20261014 import image, names, sha

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/master_dispatch_candidate_20261014/hub_timer_runtime_state.c"
INIT = G2 / "components/audio/uart_thread_source_candidate/display_hub_resource_init.c"
CALLBACK = G2 / "components/audio/uart_thread_source_candidate/display_hub_timer_callback.c"
NATIVE = G2 / "analysis/shortcut-arm-tools-20261009-agent3/main-analysis-only.elf"
BASE = G2 / "build/c-firmware/20261014/main-input-identity-relink/apollo-main-input-identity-relink.o"
OUT = G2 / "build/c-firmware/20261014/main-hub-timer-runtime-state"
CONTRACTS = {
    "audio_hub_timer_handle": (0x20074908, 0x4a7158, 4),
    "audio_hub_timer_control_block": (0x20073650, 0x788668, 44),
    "audio_hub_timeout_message_template": (0x78e47c, 0x4a735c, 8),
}


def bytes_at(segments, address, count=4):
    for base, data in segments:
        if base <= address and address + count <= base + len(data):
            return data[address-base:address-base+count]
    raise RuntimeError(f"unmapped native address {address:#x}")


def main():
    segments, _ = image(NATIVE)
    source, init, callback = SOURCE.read_text(), INIT.read_text(), CALLBACK.read_text()
    for name, (address, literal, size) in CONTRACTS.items():
        if struct.unpack("<I", bytes_at(segments, literal))[0] != address:
            raise RuntimeError(f"native hub literal changed: {name}")
        if name not in source or f"{address:08x}" not in source:
            raise RuntimeError(f"hub C source name/section changed: {name}")
    if bytes_at(segments, 0x78e47c, 8) != bytes(8) or \
       "audio_hub_timer_control_block[44]" not in init or \
       "extern const uint8_t audio_hub_timeout_message_template[8];" not in callback:
        raise RuntimeError("hub timer source/native template changed")
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "hub_timer_runtime_state.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                    "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    if names(obj, "-g", "--defined-only") != set(CONTRACTS) or names(obj, "-u"):
        raise RuntimeError("hub timer C symbol contract changed")
    sizes = {}
    for line in subprocess.check_output(["arm-none-eabi-nm", "-g", "-S", str(obj)], text=True).splitlines():
        parts = line.split()
        if len(parts) == 4 and parts[-1] in CONTRACTS:
            sizes[parts[-1]] = int(parts[1], 16)
    if sizes != {name: row[2] for name, row in CONTRACTS.items()}:
        raise RuntimeError(f"hub timer C storage sizes changed: {sizes}")
    before = names(BASE, "-u")
    if not set(CONTRACTS) <= before:
        raise RuntimeError("Apollo Main hub timer imports changed")
    linked = OUT / "apollo-main-hub-timer-runtime-state.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), "-o", str(linked)], check=True)
    after = names(linked, "-u")
    if before - after != set(CONTRACTS) or after - before:
        raise RuntimeError(f"unexpected import delta: {before-after}, {after-before}")
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_HUB_TIMER_RUNTIME_STATE_C",
               "native_elf": str(NATIVE.relative_to(ROOT)), "native_elf_sha256": sha(NATIVE),
               "native_contracts": {name: {"address": hex(address), "literal": hex(literal),
                                            "source_bytes": size}
                                    for name, (address, literal, size) in CONTRACTS.items()},
               "native_template_bytes": "0000000000000000",
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "user_sources": {str(p.relative_to(ROOT)): sha(p) for p in (INIT, CALLBACK)},
               "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj),
               "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
               "linked_object": str(linked.relative_to(ROOT)), "linked_object_sha256": sha(linked),
               "unresolved_before": len(before), "unresolved_after": len(after),
               "imports_resolved": sorted(before-after), "imports_added": sorted(after-before),
               "source_complete": False, "full_payload_linked": False,
               "limits": ["The hub send queue at commented RAM 0x20003670 has no matched native literal here and remains unresolved.",
                          "CMSIS timer internals/lifetime, final RAM/ROM placement, whole-image and hardware behavior remain open."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(path))


if __name__ == "__main__":
    main()
