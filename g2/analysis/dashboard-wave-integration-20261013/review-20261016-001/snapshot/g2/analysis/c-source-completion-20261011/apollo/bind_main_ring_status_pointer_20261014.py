#!/usr/bin/env python3
"""Bind native ring-status pointer to the existing packed BLE status byte."""
import hashlib
import json
import struct
import subprocess
from pathlib import Path

from elftools.elf.elffile import ELFFile

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
NATIVE = G2 / "analysis/shortcut-arm-tools-20261009-agent3/main-analysis-only.elf"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/ring_status_pointer.c"
USER = G2 / "components/audio/uart_thread_source_candidate/ring_sync.c"
RAM_OWNER = G2 / "components/audio/uart_thread_source_candidate/ux_ble_status.c"
BASE = G2 / "build/c-firmware/20261014/main-onboarding-imu-cells/apollo-main-onboarding-imu-cells.o"
OUT = G2 / "build/c-firmware/20261014/main-ring-status-pointer"
LITERAL = 0x47d900
RAM = 0x20075043


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def names(path, *args):
    output = subprocess.check_output(["arm-none-eabi-nm", *args, str(path)], text=True)
    return {row.split()[-1] for row in output.splitlines() if row.strip()}


def main():
    with NATIVE.open("rb") as stream:
        elf = ELFFile(stream)
        segment = next(item for item in elf.iter_segments() if item["p_type"] == "PT_LOAD")
        found = struct.unpack_from("<I", segment.data(), LITERAL - segment["p_vaddr"])[0]
        if found != RAM:
            raise RuntimeError(f"native ring pointer changed: {found:#x}")
    if "audio_uart_ring_status_word" not in USER.read_text() or "audio_ota_packed_status" not in RAM_OWNER.read_text():
        raise RuntimeError("ring pointer source consumers changed")
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "ring_status_pointer.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2",
                    "-Wall", "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    if names(obj, "-g", "--defined-only") != {"audio_uart_ring_status_word"} or names(obj, "-u") != {"audio_ota_packed_status"}:
        raise RuntimeError("compiled ring pointer symbol set changed")
    with obj.open("rb") as stream:
        elf = ELFFile(stream)
        symbol = next(item for item in elf.get_section_by_name(".symtab").iter_symbols()
                      if item.name == "audio_uart_ring_status_word")
        section = elf.get_section(symbol["st_shndx"])
        if symbol["st_size"] != 4 or section["sh_size"] != 4:
            raise RuntimeError("ring pointer is not exactly one native word")
        relocs = [item for item in elf.iter_sections() if item["sh_type"] == "SHT_REL"
                  and item["sh_info"] == symbol["st_shndx"]]
        if len(relocs) != 1 or relocs[0].num_relocations() != 1:
            raise RuntimeError("ring pointer RAM relocation changed")
    before = names(BASE, "-u")
    if "audio_uart_ring_status_word" not in before or "audio_ota_packed_status" in before:
        raise RuntimeError("Main ring status import/owner changed")
    linked = OUT / "apollo-main-ring-status-pointer.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), "-o", str(linked)], check=True)
    after = names(linked, "-u")
    if before-after != {"audio_uart_ring_status_word"} or after-before:
        raise RuntimeError(f"unexpected import delta: {before-after}, {after-before}")
    receipt = {
        "status": "PASS_EXPERIMENTAL_MAIN_RING_STATUS_POINTER_C",
        "native_elf": str(NATIVE.relative_to(ROOT)), "native_elf_sha256": sha(NATIVE),
        "native_literal": hex(LITERAL), "native_ram_target": hex(RAM),
        "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
        "user_source": str(USER.relative_to(ROOT)), "user_source_sha256": sha(USER),
        "ram_owner_source": str(RAM_OWNER.relative_to(ROOT)), "ram_owner_source_sha256": sha(RAM_OWNER),
        "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj),
        "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
        "linked_object": str(linked.relative_to(ROOT)), "linked_object_sha256": sha(linked),
        "unresolved_before": len(before), "unresolved_after": len(after),
        "imports_resolved": sorted(before-after), "imports_added": sorted(after-before),
        "source_complete": False, "full_payload_linked": False,
        "limits": ["Final ROM/RAM placement and packed status startup/runtime producers remain open.",
                   "Whole-image and hardware behavior remain unproved."],
    }
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(path))


if __name__ == "__main__":
    main()
