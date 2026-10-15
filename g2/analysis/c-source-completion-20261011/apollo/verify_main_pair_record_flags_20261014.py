#!/usr/bin/env python3
"""Compare native and C record-flag output parameters."""
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
SOURCE = G2 / "components/audio/master_dispatch_candidate_20261014/pair_record_flags.c"
NATIVE = G2 / "analysis/shortcut-arm-tools-20261009-agent3/main-analysis-only.elf"
BASE = G2 / "build/c-firmware/20261014/main-slave-record-index/apollo-main-slave-record-index.o"
OUT = G2 / "build/c-firmware/20261014/main-pair-record-flags"
ENTRY, RECORD, FLAG, FEATURES, STOP = "audio_ble_pair_record_flags_47b40c", 0x20043000, 0x20044000, 0x20045000, 0x10010000


def run(segments, entry, flag):
    uc = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
    for address, size in ((0x100000, 0x100000), (0x400000, 0x400000),
                          (0x10000000, 0x20000), (0x20000000, 0x100000)):
        uc.mem_map(address, size)
    for address, data in segments:
        uc.mem_write(address, data)
    uc.mem_write(RECORD + 0x84, bytes([flag]))
    uc.mem_write(FLAG, b"\xa5\xa5\xa5\xa5")
    uc.mem_write(FEATURES, b"\xa5\xa5\xa5\xa5")
    uc.reg_write(UC_ARM_REG_R0, RECORD)
    uc.reg_write(UC_ARM_REG_R1, FLAG)
    uc.reg_write(UC_ARM_REG_R2, FEATURES)
    uc.reg_write(UC_ARM_REG_SP, 0x200ff000)
    uc.reg_write(UC_ARM_REG_LR, STOP | 1)

    def hook(cpu, address, size, _):
        if address == STOP:
            cpu.emu_stop()

    uc.hook_add(UC_HOOK_CODE, hook)
    uc.emu_start(entry | 1, STOP + 2, count=80)
    return (bytes(uc.mem_read(FLAG, 4)), bytes(uc.mem_read(FEATURES, 4)),
            bytes(uc.mem_read(RECORD + 0x84, 2)))


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "pair_record_flags.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                    "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    if names(obj, "-g", "--defined-only") != {ENTRY} or names(obj, "-u"):
        raise RuntimeError("record flags C symbol contract changed")
    with tempfile.TemporaryDirectory() as directory:
        trial = Path(directory) / "flags.elf"
        subprocess.run(["arm-none-eabi-ld", "-Ttext=0x110000", "-e", ENTRY,
                        str(obj), "-o", str(trial)], check=True, capture_output=True)
        native_segments, _ = image(NATIVE)
        source_segments, symbols = image(trial)
        for flag in range(256):
            native = run(native_segments, 0x47b40c, flag)
            compiled = run(native_segments + source_segments, symbols[ENTRY], flag)
            if native != compiled:
                raise RuntimeError(f"record flag mismatch {flag}: {native} != {compiled}")
    before = names(BASE, "-u")
    if ENTRY not in before:
        raise RuntimeError("Apollo Main record flag contract changed")
    linked = OUT / "apollo-main-pair-record-flags.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), "-o", str(linked)], check=True)
    after = names(linked, "-u")
    if before - after != {ENTRY} or after - before:
        raise RuntimeError(f"unexpected import delta: {before-after}, {after-before}")
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_PAIR_RECORD_FLAGS_C",
               "native_elf": str(NATIVE.relative_to(ROOT)), "native_elf_sha256": sha(NATIVE),
               "native_entry": "0x47b40c", "source": str(SOURCE.relative_to(ROOT)),
               "source_sha256": sha(SOURCE), "object": str(obj.relative_to(ROOT)),
               "object_sha256": sha(obj), "base_object": str(BASE.relative_to(ROOT)),
               "base_sha256": sha(BASE), "linked_object": str(linked.relative_to(ROOT)),
               "linked_object_sha256": sha(linked), "bounded_native_c_cases": 256,
               "unresolved_before": len(before), "unresolved_after": len(after),
               "imports_resolved": sorted(before-after), "imports_added": sorted(after-before),
               "source_complete": False, "full_payload_linked": False,
               "limits": ["The helper's bounded outputs are verified against native code.",
                          "Record ownership, absolute placement, and hardware remain separate gates."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], 256, len(before), len(after), sha(path))


if __name__ == "__main__":
    main()
