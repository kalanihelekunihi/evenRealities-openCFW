#!/usr/bin/env python3
"""Compare native/C AppDb identity-address search and timestamp effects."""
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
SOURCE = G2 / "components/audio/master_dispatch_candidate_20261014/pair_record_identity.c"
NATIVE = G2 / "analysis/shortcut-arm-tools-20261009-agent3/main-analysis-only.elf"
BASE = G2 / "build/c-firmware/20261014/main-slave-message/apollo-main-slave-message.o"
OUT = G2 / "build/c-firmware/20261014/main-pair-record-identity"
ENTRY = "audio_ble_pair_record_find_47add4"
TABLE, COUNTER, ADDRESS, STOP = 0x20067a30, 0x20074344, 0x20010000, 0x10010000


def run(segments, entry, kind, target, enabled, duplicate, initial):
    uc = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
    for address, size in ((0x100000, 0x100000), (0x400000, 0x400000),
                          (0x10000000, 0x20000), (0x20000000, 0x100000)):
        uc.mem_map(address, size)
    for address, data in segments:
        uc.mem_write(address, data)
    sought = bytes((0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77, 0x88))
    uc.mem_write(ADDRESS, sought)
    rows = bytearray(2000)
    for index in range(10):
        row = index * 200
        rows[row+0x44:row+0x4c] = bytes([index + 1] * 8)
        rows[row+0x4c:row+0x4e] = struct.pack("<H", kind & 0xffff)
        rows[row+0x2f] = enabled if index == target else 0
        rows[row+0xc4:row+0xc8] = struct.pack("<I", 0xa0 + index)
    if target < 10:
        rows[target*200+0x44:target*200+0x4c] = sought
    if duplicate and target < 9:
        rows[(target+1)*200+0x44:(target+1)*200+0x4c] = sought
        rows[(target+1)*200+0x2f] = 1
    uc.mem_write(TABLE, bytes(rows))
    uc.mem_write(COUNTER, struct.pack("<I", initial))
    uc.reg_write(UC_ARM_REG_R0, kind)
    uc.reg_write(UC_ARM_REG_R1, ADDRESS)
    uc.reg_write(UC_ARM_REG_SP, 0x200ff000)
    uc.reg_write(UC_ARM_REG_LR, STOP | 1)
    compares = []

    def hook(cpu, address, size, _):
        if address == STOP:
            cpu.emu_stop()
        elif address == 0x4751c8:
            left, right, length = (cpu.reg_read(reg) for reg in
                                   (UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2))
            a, b = bytes(cpu.mem_read(left, length)), bytes(cpu.mem_read(right, length))
            compares.append((left, right, length, a, b))
            result = next((x-y for x, y in zip(a, b) if x != y), 0)
            cpu.reg_write(UC_ARM_REG_R0, result & 0xffffffff)
            cpu.reg_write(UC_ARM_REG_PC, cpu.reg_read(UC_ARM_REG_LR))

    uc.hook_add(UC_HOOK_CODE, hook)
    uc.emu_start(entry | 1, STOP + 2, count=3000)
    return (uc.reg_read(UC_ARM_REG_R0), compares,
            bytes(uc.mem_read(TABLE, 2000)), bytes(uc.mem_read(COUNTER, 4)))


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "pair_record_identity.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                    "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    storage = {"audio_ble_dm_conn_state_table_20067a30",
               "audio_ble_pair_timestamp_counter_20074344", "g2_lfs_memcmp"}
    if names(obj, "-g", "--defined-only") != {ENTRY} or names(obj, "-u") != storage:
        raise RuntimeError("identity lookup source symbol contract changed")
    with tempfile.TemporaryDirectory() as directory:
        trial = Path(directory) / "identity.elf"
        subprocess.run(["arm-none-eabi-ld", "-Ttext=0x110000", "-e", ENTRY,
                        f"--defsym=audio_ble_dm_conn_state_table_20067a30={TABLE}",
                        f"--defsym=audio_ble_pair_timestamp_counter_20074344={COUNTER}",
                        "--defsym=g2_lfs_memcmp=0x4751c9", str(obj), "-o", str(trial)],
                       check=True, capture_output=True)
        native_segments, _ = image(NATIVE)
        source_segments, symbols = image(trial)
        cases = [(kind, target, enabled, duplicate, initial)
                 for kind in (0, 1, 0x3412, 0x12343412)
                 for target in (0, 5, 9, 10) for enabled in (0, 1)
                 for duplicate in (0, 1) for initial in (0, 0xffffffff)]
        for case in cases:
            native = run(native_segments, 0x47add4, *case)
            compiled = run(native_segments + source_segments, symbols[ENTRY], *case)
            if native != compiled:
                raise RuntimeError(f"identity lookup mismatch {case}: {native[:2]} != {compiled[:2]}")
    before = names(BASE, "-u")
    if ENTRY not in before or not storage <= names(BASE, "-g", "--defined-only"):
        raise RuntimeError("Apollo Main identity lookup base contract changed")
    linked = OUT / "apollo-main-pair-record-identity.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), "-o", str(linked)], check=True)
    after = names(linked, "-u")
    if before - after != {ENTRY} or after - before:
        raise RuntimeError(f"unexpected import delta: {before-after}, {after-before}")
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_PAIR_RECORD_IDENTITY_C",
               "native_elf": str(NATIVE.relative_to(ROOT)), "native_elf_sha256": sha(NATIVE),
               "native_entry": "0x47add4", "source": str(SOURCE.relative_to(ROOT)),
               "source_sha256": sha(SOURCE), "object": str(obj.relative_to(ROOT)),
               "object_sha256": sha(obj), "base_object": str(BASE.relative_to(ROOT)),
               "base_sha256": sha(BASE), "linked_object": str(linked.relative_to(ROOT)),
               "linked_object_sha256": sha(linked), "bounded_native_c_cases": len(cases),
               "unresolved_before": len(before), "unresolved_after": len(after),
               "imports_resolved": sorted(before-after), "imports_added": sorted(after-before),
               "source_complete": False, "full_payload_linked": False,
               "limits": ["Byte comparison is a bounded provider hook shared by native and C.",
                          "Absolute RAM placement, whole-image and hardware behavior remain open."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(cases), len(before), len(after), sha(path))


if __name__ == "__main__":
    main()
