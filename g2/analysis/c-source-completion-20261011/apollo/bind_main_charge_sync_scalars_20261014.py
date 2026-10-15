#!/usr/bin/env python3
"""Bind five observed charge sync RAM scalars to C definitions."""
import json
import struct
import subprocess
from pathlib import Path

from verify_main_master_dispatch_children_20261014 import image, names, sha

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/master_dispatch_candidate_20261014/charge_sync_scalar_state.c"
USER = G2 / "components/audio/uart_thread_source_candidate/display_charge_battery_sync_init.c"
NATIVE = G2 / "analysis/shortcut-arm-tools-20261009-agent3/main-analysis-only.elf"
BASE = G2 / "build/c-firmware/20261014/main-dm-hash-dma-state/apollo-main-dm-hash-dma-state.o"
OUT = G2 / "build/c-firmware/20261014/main-charge-sync-scalars"
CONTRACTS = {
    "audio_charge_sync_flag_20074f97": (0x20074f97, 0x4ad934, 1),
    "audio_charge_sync_flag_20074f98": (0x20074f98, 0x4ad7c8, 1),
    "audio_charge_sync_flag_20074f99": (0x20074f99, 0x4ad874, 1),
    "audio_charge_sync_mode_20074f1a": (0x20074f1a, 0x4ad7d8, 2),
    "audio_charge_sync_phase_20074f1c": (0x20074f1c, 0x4ad878, 2),
}


def bytes_at(segments, address):
    for base, data in segments:
        if base <= address and address + 4 <= base + len(data):
            return data[address-base:address-base+4]
    raise RuntimeError(f"unmapped native address {address:#x}")


def main():
    segments, _ = image(NATIVE)
    source, user = SOURCE.read_text(), USER.read_text()
    for name, (ram, literal, size) in CONTRACTS.items():
        if struct.unpack("<I", bytes_at(segments, literal))[0] != ram:
            raise RuntimeError(f"native RAM literal changed: {name}")
        c_type = "uint8_t" if size == 1 else "uint16_t"
        if f"volatile {c_type} {name};" not in source or f"extern volatile {c_type} {name};" not in user:
            raise RuntimeError(f"C scalar type changed: {name}")
        if f"{name}=" not in user:
            raise RuntimeError(f"selected initializer no longer writes {name}")
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "charge_sync_scalar_state.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                    "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    if names(obj, "-g", "--defined-only") != set(CONTRACTS) or names(obj, "-u"):
        raise RuntimeError("charge sync C symbol contract changed")
    sizes = {}
    for line in subprocess.check_output(["arm-none-eabi-nm", "-g", "-S", str(obj)], text=True).splitlines():
        parts = line.split()
        if len(parts) == 4 and parts[-1] in CONTRACTS:
            sizes[parts[-1]] = int(parts[1], 16)
    if sizes != {name: row[2] for name, row in CONTRACTS.items()}:
        raise RuntimeError(f"C scalar sizes changed: {sizes}")
    before = names(BASE, "-u")
    if not set(CONTRACTS) <= before:
        raise RuntimeError("Apollo Main expected imports changed")
    linked = OUT / "apollo-main-charge-sync-scalars.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), "-o", str(linked)], check=True)
    after = names(linked, "-u")
    if before - after != set(CONTRACTS) or after - before:
        raise RuntimeError(f"unexpected import delta: {before-after}, {after-before}")
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_CHARGE_SYNC_SCALARS_C",
               "native_elf": str(NATIVE.relative_to(ROOT)), "native_elf_sha256": sha(NATIVE),
               "native_contracts": {name: {"ram": hex(ram), "literal": hex(literal),
                                            "scalar_bytes": size}
                                    for name, (ram, literal, size) in CONTRACTS.items()},
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "user_source": str(USER.relative_to(ROOT)), "user_source_sha256": sha(USER),
               "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj),
               "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
               "linked_object": str(linked.relative_to(ROOT)), "linked_object_sha256": sha(linked),
               "unresolved_before": len(before), "unresolved_after": len(after),
               "imports_resolved": sorted(before-after), "imports_added": sorted(after-before),
               "source_complete": False, "full_payload_linked": False,
               "limits": ["Scalar sizes and selected initializer writes are covered; full native allocation and startup contents remain open.",
                          "Relative native addresses are not reproduced by the relocatable object; final SRAM placement remains open.",
                          "Whole-image and hardware behavior remain open."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(path))


if __name__ == "__main__":
    main()
