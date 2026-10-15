#!/usr/bin/env python3
"""Compare native/C slave resolution branching and security arguments."""
import json
import struct
import subprocess
import tempfile
from pathlib import Path

from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn.arm_const import (UC_ARM_REG_LR, UC_ARM_REG_PC, UC_ARM_REG_R0,
                               UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_R3,
                               UC_ARM_REG_SP)

from verify_main_master_dispatch_children_20261014 import image, names, sha

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/master_dispatch_candidate_20261014/slave_resolve.c"
NATIVE = G2 / "analysis/shortcut-arm-tools-20261009-agent3/main-analysis-only.elf"
BASE = G2 / "build/c-firmware/20261014/main-pair-record-identity/apollo-main-pair-record-identity.o"
OUT = G2 / "build/c-firmware/20261014/main-slave-resolve"
ENTRY = "audio_ble_slave_resolve_4b36b2"
SELECT, SECURITY = 0x47ae78, 0x52bb20
ROW, STOP = 0x20020000, 0x10010000


def run(segments, entry, handle, link, selected, busy, connection):
    uc = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
    for address, size in ((0x100000, 0x100000), (0x400000, 0x400000),
                          (0x10000000, 0x20000), (0x20000000, 0x100000)):
        uc.mem_map(address, size)
    for address, data in segments:
        uc.mem_write(address, data)
    row = bytearray(0x30)
    row[:4] = struct.pack("<I", handle)
    row[4], row[5], row[6] = connection, busy, 0xa5
    uc.mem_write(ROW, bytes(row))
    uc.reg_write(UC_ARM_REG_R0, ROW)
    uc.reg_write(UC_ARM_REG_SP, 0x200ff000)
    uc.reg_write(UC_ARM_REG_LR, STOP | 1)
    calls = []

    def hook(cpu, address, size, _):
        if address == STOP:
            cpu.emu_stop()
            return
        r0, r1, r2, r3 = (cpu.reg_read(reg) for reg in
                          (UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_R3))
        if address == SELECT:
            calls.append(("select", r0, r1))
            cpu.mem_write(r2, bytes([selected]))
            cpu.reg_write(UC_ARM_REG_R0, link)
        elif address == SECURITY:
            calls.append(("security", r0, r1, r2, r3))
            cpu.reg_write(UC_ARM_REG_R0, 0)
        else:
            return
        cpu.reg_write(UC_ARM_REG_PC, cpu.reg_read(UC_ARM_REG_LR))

    uc.hook_add(UC_HOOK_CODE, hook)
    uc.emu_start(entry | 1, STOP + 2, count=200)
    return calls, bytes(uc.mem_read(ROW, 0x30))


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "slave_resolve.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                    "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    if names(obj, "-g", "--defined-only") != {ENTRY} or names(obj, "-u") != \
       {"audio_ble_link_mask_select_47ae78", "audio_ble_dm_sec_resolve_52bb20"}:
        raise RuntimeError("slave resolve source symbol contract changed")
    with tempfile.TemporaryDirectory() as directory:
        trial = Path(directory) / "resolve.elf"
        subprocess.run(["arm-none-eabi-ld", "-Ttext=0x110000", "-e", ENTRY,
                        f"--defsym=audio_ble_link_mask_select_47ae78={SELECT | 1}",
                        f"--defsym=audio_ble_dm_sec_resolve_52bb20={SECURITY | 1}",
                        str(obj), "-o", str(trial)], check=True, capture_output=True)
        native_segments, _ = image(NATIVE)
        source_segments, symbols = image(trial)
        cases = [(handle, link, selected, busy, connection)
                 for handle in (0, 0x20043000) for link in (0, 0x20043034)
                 for selected in (0, 1, 0xff) for busy in (0, 1)
                 for connection in (0, 3)]
        for case in cases:
            native = run(native_segments, 0x4b36b2, *case)
            compiled = run(native_segments + source_segments, symbols[ENTRY], *case)
            if native != compiled:
                raise RuntimeError(f"slave resolve mismatch {case}: {native} != {compiled}")
    before = names(BASE, "-u")
    if ENTRY not in before or \
       "audio_ble_link_mask_select_47ae78" not in names(BASE, "-g", "--defined-only"):
        raise RuntimeError("Apollo Main slave resolve base contract changed")
    linked = OUT / "apollo-main-slave-resolve.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), "-o", str(linked)], check=True)
    after = names(linked, "-u")
    if before - after != {ENTRY} or after - before != {"audio_ble_dm_sec_resolve_52bb20"}:
        raise RuntimeError(f"unexpected import delta: {before-after}, {after-before}")
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_SLAVE_RESOLVE_C",
               "native_elf": str(NATIVE.relative_to(ROOT)), "native_elf_sha256": sha(NATIVE),
               "native_entry": "0x4b36b2", "source": str(SOURCE.relative_to(ROOT)),
               "source_sha256": sha(SOURCE), "object": str(obj.relative_to(ROOT)),
               "object_sha256": sha(obj), "base_object": str(BASE.relative_to(ROOT)),
               "base_sha256": sha(BASE), "linked_object": str(linked.relative_to(ROOT)),
               "linked_object_sha256": sha(linked), "bounded_native_c_cases": len(cases),
               "unresolved_before": len(before), "unresolved_after": len(after),
               "imports_resolved": sorted(before-after), "imports_added": sorted(after-before),
               "source_complete": False, "full_payload_linked": False,
               "limits": ["Security request 0x52bb20 remains a lower C contract.",
                          "Provider effects beyond arguments are not covered.",
                          "Whole-image and hardware behavior remain open."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(cases), len(before), len(after), sha(path))


if __name__ == "__main__":
    main()
