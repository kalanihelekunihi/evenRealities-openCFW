#!/usr/bin/env python3
"""Compare native and C AppDb first-match lookup with privacy remapping."""
import json
import struct
import subprocess
import tempfile
from pathlib import Path

from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn.arm_const import (UC_ARM_REG_LR, UC_ARM_REG_PC, UC_ARM_REG_R0,
                               UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_SP)

from verify_main_master_dispatch_children_20261014 import image, names, sha

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/master_dispatch_candidate_20261014/pair_record_lookup.c"
NATIVE = G2 / "analysis/shortcut-arm-tools-20261009-agent3/main-analysis-only.elf"
BASE = G2 / "build/c-firmware/20261014/main-privacy-rows-alias/apollo-main-privacy-rows-alias.o"
OUT = G2 / "build/c-firmware/20261014/main-pair-record-lookup"
ENTRIES = {"audio_ble_pair_record_find_47ad74": 0x47ad74,
           "audio_ble_pair_address_type_4d2aa8": 0x4d2aa8,
           "audio_ble_pair_address_equal_4d294a": 0x4d294a}
TABLE, PRIVACY, COUNTER = 0x20067a30, 0x20073b78, 0x20074344
ADDRESS, STOP = 0x20010000, 0x10010000


def run(segments, entry, kind, target, mode, enabled, duplicates, initial):
    uc = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
    for address, size in ((0x100000, 0x100000), (0x400000, 0x400000),
                          (0x10000000, 0x20000), (0x20000000, 0x100000)):
        uc.mem_map(address, size)
    for address, data in segments:
        uc.mem_write(address, data)
    sought = bytes((0x11, 0x22, 0x33, 0x44, 0x55, 0x66))
    uc.mem_write(ADDRESS, sought)
    rows = bytearray(2000)
    for index in range(10):
        row = index * 200
        rows[row:row+6] = bytes([index + 1] * 6)
        rows[row+6] = (0 if kind == 2 and mode else
                       1 if kind == 3 and mode else kind) & 0xff
        rows[row+0x2f] = enabled if index == target else 0
        rows[row+0xc4:row+0xc8] = struct.pack("<I", 0xa0 + index)
    if target < 10:
        rows[target*200:target*200+6] = sought
    if duplicates and target < 9:
        rows[(target+1)*200:(target+1)*200+6] = sought
        rows[(target+1)*200+0x2f] = 1
    uc.mem_write(TABLE, bytes(rows))
    uc.mem_write(PRIVACY + 0x16, bytes([mode]))
    uc.mem_write(COUNTER, struct.pack("<I", initial))
    uc.reg_write(UC_ARM_REG_R0, kind | 0x123400)
    uc.reg_write(UC_ARM_REG_R1, ADDRESS)
    uc.reg_write(UC_ARM_REG_SP, 0x200ff000)
    uc.reg_write(UC_ARM_REG_LR, STOP | 1)
    compares = []

    def hook(cpu, address, size, _):
        if address == STOP:
            cpu.emu_stop()
        elif address == 0x4751c8:
            left = cpu.reg_read(UC_ARM_REG_R0)
            right = cpu.reg_read(UC_ARM_REG_R1)
            length = cpu.reg_read(UC_ARM_REG_R2)
            a, b = bytes(cpu.mem_read(left, length)), bytes(cpu.mem_read(right, length))
            compares.append((left, right, length, a, b))
            result = next((x-y for x, y in zip(a, b) if x != y), 0)
            cpu.reg_write(UC_ARM_REG_R0, result & 0xffffffff)
            cpu.reg_write(UC_ARM_REG_PC, cpu.reg_read(UC_ARM_REG_LR))

    uc.hook_add(UC_HOOK_CODE, hook)
    uc.emu_start(entry | 1, STOP + 2, count=4000)
    return (uc.reg_read(UC_ARM_REG_R0), compares,
            bytes(uc.mem_read(TABLE, 2000)), bytes(uc.mem_read(COUNTER, 4)))


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "pair_record_lookup.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                    "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    defined = names(obj, "-g", "--defined-only")
    imported = names(obj, "-u")
    storage = {"audio_ble_dm_privacy_state", "audio_ble_dm_conn_state_table_20067a30",
               "audio_ble_pair_timestamp_counter_20074344", "g2_lfs_memcmp"}
    if defined != set(ENTRIES) or imported != storage:
        raise RuntimeError(f"pair lookup C contract changed: {defined}, {imported}")
    with tempfile.TemporaryDirectory() as directory:
        trial = Path(directory) / "lookup.elf"
        subprocess.run(["arm-none-eabi-ld", "-Ttext=0x110000", "-e",
                        "audio_ble_pair_record_find_47ad74",
                        f"--defsym=audio_ble_dm_privacy_state={PRIVACY}",
                        f"--defsym=audio_ble_dm_conn_state_table_20067a30={TABLE}",
                        f"--defsym=audio_ble_pair_timestamp_counter_20074344={COUNTER}",
                        "--defsym=g2_lfs_memcmp=0x4751c9", str(obj), "-o", str(trial)],
                       check=True, capture_output=True)
        native_segments, _ = image(NATIVE)
        source_segments, symbols = image(trial)
        cases = [(kind, target, mode, enabled, duplicates, initial)
                 for kind in (0, 1, 2, 3, 4) for target in (0, 5, 9, 10)
                 for mode in (0, 1) for enabled in (0, 1)
                 for duplicates in (0, 1) for initial in (0, 0xffffffff)]
        for case in cases:
            native = run(native_segments, 0x47ad74, *case)
            compiled = run(native_segments + source_segments,
                           symbols["audio_ble_pair_record_find_47ad74"], *case)
            if native != compiled:
                raise RuntimeError(f"pair lookup mismatch {case}: {native[:2]} != {compiled[:2]}")
    before = names(BASE, "-u")
    if "audio_ble_pair_record_find_47ad74" not in before or \
       not storage <= names(BASE, "-g", "--defined-only"):
        raise RuntimeError("Apollo Main pair lookup base contract changed")
    linked = OUT / "apollo-main-pair-record-lookup.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), "-o", str(linked)], check=True)
    after = names(linked, "-u")
    if before - after != {"audio_ble_pair_record_find_47ad74"} or after - before:
        raise RuntimeError(f"unexpected import delta: {before-after}, {after-before}")
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_PAIR_RECORD_LOOKUP_C",
               "native_elf": str(NATIVE.relative_to(ROOT)), "native_elf_sha256": sha(NATIVE),
               "native_entries": {name: hex(address) for name, address in ENTRIES.items()},
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj),
               "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
               "linked_object": str(linked.relative_to(ROOT)),
               "linked_object_sha256": sha(linked), "bounded_native_c_cases": len(cases),
               "unresolved_before": len(before), "unresolved_after": len(after),
               "imports_resolved": sorted(before-after), "imports_added": sorted(after-before),
               "source_complete": False, "full_payload_linked": False,
               "limits": ["Memcpy comparison is a bounded provider hook shared by native and C.",
                          "Absolute RAM placement and startup state remain separate gates.",
                          "Whole-image and hardware behavior remain separate gates."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(cases), len(before), len(after), sha(path))


if __name__ == "__main__":
    main()
