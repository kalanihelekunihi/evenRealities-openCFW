#!/usr/bin/env python3
"""Bind the bounded charge sync records and mutex cell to C storage."""
import json
import struct
import subprocess
from pathlib import Path

from verify_main_master_dispatch_children_20261014 import image, names, sha

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/master_dispatch_candidate_20261014/charge_sync_records_state.c"
USER = G2 / "components/audio/uart_thread_source_candidate/display_charge_battery_sync_init.c"
NATIVE = G2 / "analysis/shortcut-arm-tools-20261009-agent3/main-analysis-only.elf"
BASE = G2 / "build/c-firmware/20261014/main-ring-kernel-rtc-state/apollo-main-ring-kernel-rtc-state.o"
OUT = G2 / "build/c-firmware/20261014/main-charge-sync-records"
CONTRACTS = {
    "audio_charge_sync_mutex": (0x20074370, 0x4ad924, 4),
    "audio_charge_sync_record": (0x20073b30, 0x4ad908, 24),
    "audio_charge_sync_peer_record": (0x20074104, 0x4ad930, 8),
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
        declaration = f"void *{name};" if size == 4 else f"uint8_t {name}[{size}u];"
        if declaration not in source or f"extern {declaration}" not in user:
            raise RuntimeError(f"C storage declaration changed: {name}")
    if "audio_uart_buffer_zero(audio_charge_sync_record,24u,0u);" not in user or \
       "audio_uart_buffer_zero(audio_charge_sync_peer_record,8u,0u);" not in user or \
       "audio_charge_sync_mutex=audio_uart_mutex_new(0);" not in user:
        raise RuntimeError("selected charge initializer storage use changed")
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "charge_sync_records_state.o"
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
        raise RuntimeError(f"C storage sizes changed: {sizes}")
    before = names(BASE, "-u")
    if not set(CONTRACTS) <= before:
        raise RuntimeError("Apollo Main expected imports changed")
    linked = OUT / "apollo-main-charge-sync-records.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), "-o", str(linked)], check=True)
    after = names(linked, "-u")
    if before - after != set(CONTRACTS) or after - before:
        raise RuntimeError(f"unexpected import delta: {before-after}, {after-before}")
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_CHARGE_SYNC_RECORDS_C",
               "native_elf": str(NATIVE.relative_to(ROOT)), "native_elf_sha256": sha(NATIVE),
               "native_contracts": {name: {"ram": hex(ram), "literal": hex(literal),
                                            "selected_source_bytes": size}
                                    for name, (ram, literal, size) in CONTRACTS.items()},
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "user_source": str(USER.relative_to(ROOT)), "user_source_sha256": sha(USER),
               "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj),
               "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
               "linked_object": str(linked.relative_to(ROOT)), "linked_object_sha256": sha(linked),
               "unresolved_before": len(before), "unresolved_after": len(after),
               "imports_resolved": sorted(before-after), "imports_added": sorted(after-before),
               "source_complete": False, "full_payload_linked": False,
               "limits": ["The selected initializer covers these storage sizes; complete native allocations and all other users are not proved.",
                          "Final SRAM placement, whole-image and hardware behavior remain open."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(path))


if __name__ == "__main__":
    main()
