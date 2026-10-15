#!/usr/bin/env python3
"""Bind the native singleton DM connection-update ROM dispatch table."""
import json
import struct
import subprocess
from pathlib import Path

from verify_main_master_dispatch_children_20261014 import image, names, sha

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/master_dispatch_candidate_20261014/dm_conn_update_dispatch.c"
PROVIDER = G2 / "components/audio/uart_thread_source_candidate/display_ble_dm_conn_update_executor.c"
NATIVE = G2 / "analysis/shortcut-arm-tools-20261009-agent3/main-analysis-only.elf"
BASE = G2 / "build/c-firmware/20261014/main-comm-mode-state/apollo-main-comm-mode-state.o"
OUT = G2 / "build/c-firmware/20261014/main-dm-conn-update-dispatch"
NAME, ENTRY = "audio_ble_dm_conn_state_table_b", "audio_ble_dm_conn_upd_execute_4b6532"
ROM, NATIVE_THUMB = 0x78efec, 0x4b6531


def bytes_at(segments, address):
    for base, data in segments:
        if base <= address and address + 4 <= base + len(data):
            return data[address-base:address-base+4]
    raise RuntimeError(f"unmapped native address {address:#x}")


def main():
    segments, _ = image(NATIVE)
    if struct.unpack("<I", bytes_at(segments, ROM))[0] != NATIVE_THUMB or \
       "void audio_ble_dm_conn_upd_execute_4b6532(void *ccb,const void *message)" not in PROVIDER.read_text():
        raise RuntimeError("native DM update table or selected C entry changed")
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "dm_conn_update_dispatch.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                    "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    if names(obj, "-g", "--defined-only") != {NAME} or names(obj, "-u") != {ENTRY}:
        raise RuntimeError("DM update dispatch C symbol contract changed")
    output = subprocess.check_output(["arm-none-eabi-nm", "-g", "-S", str(obj)], text=True)
    if not any(len(parts := line.split()) == 4 and parts[-1] == NAME and
               int(parts[1], 16) == 4 for line in output.splitlines()):
        raise RuntimeError("DM update singleton table size changed")
    reloc = subprocess.check_output(["arm-none-eabi-objdump", "-r", str(obj)], text=True)
    if reloc.count("R_ARM_ABS32") != 1 or ENTRY not in reloc:
        raise RuntimeError("DM update table entry is not relocatable C function pointer")
    before = names(BASE, "-u")
    if NAME not in before or ENTRY not in names(BASE, "-g", "--defined-only"):
        raise RuntimeError("Apollo Main DM update import/provider changed")
    linked = OUT / "apollo-main-dm-conn-update-dispatch.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), "-o", str(linked)], check=True)
    after = names(linked, "-u")
    if before - after != {NAME} or after - before:
        raise RuntimeError(f"unexpected import delta: {before-after}, {after-before}")
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_DM_CONN_UPDATE_DISPATCH_C",
               "native_elf": str(NATIVE.relative_to(ROOT)), "native_elf_sha256": sha(NATIVE),
               "native_rom": hex(ROM), "native_thumb_entry": hex(NATIVE_THUMB),
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "provider_source": str(PROVIDER.relative_to(ROOT)), "provider_source_sha256": sha(PROVIDER),
               "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj),
               "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
               "linked_object": str(linked.relative_to(ROOT)),
               "linked_object_sha256": sha(linked),
               "unresolved_before": len(before), "unresolved_after": len(after),
               "imports_resolved": sorted(before-after), "imports_added": sorted(after-before),
               "source_complete": False, "full_payload_linked": False,
               "limits": ["The singleton ROM table is source-owned; the other DM connection tables and their target bodies remain open.",
                          "Final ROM placement, whole-image and hardware behavior remain open."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(before), len(after), sha(path))


if __name__ == "__main__":
    main()
