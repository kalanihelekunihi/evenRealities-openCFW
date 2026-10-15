#!/usr/bin/env python3
"""Bind bounded DM hash and DMA row RAM contracts to compiled C storage."""
import json
import struct
import subprocess
from pathlib import Path

from verify_main_master_dispatch_children_20261014 import image, names, sha

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/master_dispatch_candidate_20261014/dm_hash_dma_state.c"
HASH_USER = G2 / "components/audio/uart_thread_source_candidate/display_ble_dm_short.c"
DMA_USER = G2 / "components/audio/uart_thread_source_candidate/display_ble_hci_dma_queue.c"
NATIVE = G2 / "analysis/shortcut-arm-tools-20261009-agent3/main-analysis-only.elf"
BASE = G2 / "build/c-firmware/20261014/main-encrypt-tick-alias/apollo-main-encrypt-tick-alias.o"
OUT = G2 / "build/c-firmware/20261014/main-dm-hash-dma-state"
CONTRACTS = {
    "audio_ble_dm_database_hash_20068215": (0x20068215, 0x47bc14, 16),
    "audio_ble_dma_channel_rows_2006ef28": (0x2006ef28, 0x539244, 12 * 0x2c),
}


def bytes_at(segments, address):
    for base, data in segments:
        if base <= address and address + 4 <= base + len(data):
            return data[address-base:address-base+4]
    raise RuntimeError(f"unmapped native address {address:#x}")


def main():
    segments, _ = image(NATIVE)
    for name, (ram, literal, _) in CONTRACTS.items():
        if struct.unpack("<I", bytes_at(segments, literal))[0] != ram:
            raise RuntimeError(f"native RAM literal changed: {name}")
    hash_user, dma_user = HASH_USER.read_text(), DMA_USER.read_text()
    if "i < 16u" not in hash_user or "audio_ble_dm_database_hash_20068215[i]" not in hash_user:
        raise RuntimeError("database hash bounded copy changed")
    if "id>=12u" not in dma_user or "(uint32_t)id*0x2cu" not in dma_user:
        raise RuntimeError("DMA channel bounds or row stride changed")
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "dm_hash_dma_state.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                    "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    if names(obj, "-g", "--defined-only") != set(CONTRACTS) or names(obj, "-u"):
        raise RuntimeError("C symbol contract changed")
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
    linked = OUT / "apollo-main-dm-hash-dma-state.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), "-o", str(linked)], check=True)
    after = names(linked, "-u")
    if before - after != set(CONTRACTS) or after - before:
        raise RuntimeError(f"unexpected import delta: {before-after}, {after-before}")
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_DM_HASH_DMA_STATE_C",
               "native_elf": str(NATIVE.relative_to(ROOT)), "native_elf_sha256": sha(NATIVE),
               "native_contracts": {name: {"ram": hex(ram), "literal": hex(literal),
                                            "selected_source_bytes": size}
                                    for name, (ram, literal, size) in CONTRACTS.items()},
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "user_sources": {str(p.relative_to(ROOT)): sha(p) for p in (HASH_USER, DMA_USER)},
               "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj),
               "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
               "linked_object": str(linked.relative_to(ROOT)), "linked_object_sha256": sha(linked),
               "unresolved_before": len(before), "unresolved_after": len(after),
               "imports_resolved": sorted(before-after), "imports_added": sorted(after-before),
               "source_complete": False, "full_payload_linked": False,
               "limits": ["These sizes cover bounded access in the selected C paths; full native allocation and startup contents remain open.",
                          "Final SRAM placement, whole-image and hardware behavior remain open."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(path))


if __name__ == "__main__":
    main()
