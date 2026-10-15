#!/usr/bin/env python3
"""Verify Apollo BLE master row transitions and compose two C handlers."""
import json
import struct
import subprocess
import tempfile
from pathlib import Path

from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE, UC_HOOK_MEM_WRITE
from unicorn.arm_const import UC_ARM_REG_LR, UC_ARM_REG_PC, UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_SP

from verify_main_master_dispatch_children_20261014 import image, names, sha

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/master_dispatch_candidate_20261014/children_row.c"
NATIVE = G2 / "analysis/shortcut-arm-tools-20261009-agent3/main-analysis-only.elf"
BASE = G2 / "build/c-firmware/20261014/main-master-close-chain/apollo-main-master-close-chain.o"
OUT = G2 / "build/c-firmware/20261014/main-master-row-children"
ENTRIES = {"audio_ble_master_event_5037ea": 0x5037ea,
           "audio_ble_master_event_503820": 0x503820}
LEVEL, DISPATCH = 0x4b71b2, 0x503498
MESSAGE, ROW, PROFILE, SLOT, STOP = 0x20010000, 0x20020000, 0x20030000, 0x20074358, 0x10010000


def run(segments, entry, connection, security, profile_mode, row8):
    uc = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
    for address, size in ((0x100000, 0x100000), (0x400000, 0x400000),
                          (0x10000000, 0x20000), (0x20000000, 0x100000)):
        uc.mem_map(address, size)
    for address, data in segments:
        uc.mem_write(address, data)
    message = bytearray(16)
    message[:2] = struct.pack("<H", connection)
    row = bytearray([0x5a] * 0x30)
    row[8] = row8
    profile = bytearray(16)
    profile[4] = profile_mode
    uc.mem_write(MESSAGE, bytes(message))
    uc.mem_write(ROW, bytes(row))
    uc.mem_write(PROFILE, bytes(profile))
    uc.mem_write(SLOT, struct.pack("<I", PROFILE))
    uc.reg_write(UC_ARM_REG_R0, MESSAGE)
    uc.reg_write(UC_ARM_REG_R1, ROW)
    uc.reg_write(UC_ARM_REG_SP, 0x200ff000)
    uc.reg_write(UC_ARM_REG_LR, STOP | 1)
    calls, writes = [], []

    def code_hook(cpu, address, size, _):
        if address == STOP:
            cpu.emu_stop()
        elif address == LEVEL:
            calls.append(("level", cpu.reg_read(UC_ARM_REG_R0)))
            cpu.reg_write(UC_ARM_REG_R0, security)
            cpu.reg_write(UC_ARM_REG_PC, cpu.reg_read(UC_ARM_REG_LR))
        elif address == DISPATCH:
            calls.append(("dispatch", cpu.reg_read(UC_ARM_REG_R0),
                          cpu.reg_read(UC_ARM_REG_R1), cpu.reg_read(UC_ARM_REG_R2)))
            cpu.reg_write(UC_ARM_REG_PC, cpu.reg_read(UC_ARM_REG_LR))

    def write_hook(cpu, access, address, size, value, _):
        if ROW <= address < ROW + 0x30:
            writes.append((address - ROW, size, value & ((1 << (size * 8)) - 1)))

    uc.hook_add(UC_HOOK_CODE, code_hook)
    uc.hook_add(UC_HOOK_MEM_WRITE, write_hook)
    uc.emu_start(entry | 1, STOP + 2, count=500)
    return calls, writes, bytes(uc.mem_read(ROW, 0x30))


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "children_row.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m55", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2",
                    "-Wall", "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    if names(obj, "-g", "--defined-only") != set(ENTRIES):
        raise RuntimeError("row child C definitions changed")
    with tempfile.TemporaryDirectory() as directory:
        trial = Path(directory) / "row.elf"
        subprocess.run(["arm-none-eabi-ld", "-Ttext=0x110000", "-e",
                        "audio_ble_master_event_5037ea",
                        f"--defsym=audio_ble_comm_profile_slot={SLOT}",
                        f"--defsym=audio_ble_dm_sec_level_4b71b2={LEVEL | 1}",
                        f"--defsym=audio_ble_master_row_dispatch_503498={DISPATCH | 1}",
                        str(obj), "-o", str(trial)], check=True, capture_output=True)
        native_segments, _ = image(NATIVE)
        source_segments, symbols = image(trial)
        cases = [(name, connection, security, profile_mode, row8)
                 for name in ENTRIES for connection in (0, 1, 0x102)
                 for security in (0, 1) for profile_mode in (0, 1)
                 for row8 in (0, 1)]
        for name, connection, security, profile_mode, row8 in cases:
            native = run(native_segments, ENTRIES[name], connection, security, profile_mode, row8)
            compiled = run(native_segments + source_segments, symbols[name],
                           connection, security, profile_mode, row8)
            if native != compiled:
                raise RuntimeError(f"row child differs: {(name, connection, security, profile_mode, row8)} {native[:2]} {compiled[:2]}")
    before = names(BASE, "-u")
    if not set(ENTRIES) <= before or "audio_ble_dm_sec_level_4b71b2" not in names(BASE, "-g", "--defined-only"):
        raise RuntimeError("Main row child contracts changed")
    linked = OUT / "apollo-main-master-row-children.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), "-o", str(linked)], check=True)
    after = names(linked, "-u")
    if len(before) != 486 or len(after) != 485 or before - after != set(ENTRIES) or \
       after - before != {"audio_ble_master_row_dispatch_503498"}:
        raise RuntimeError("unexpected Main row child import delta")
    receipt = {
        "status": "PASS_EXPERIMENTAL_MAIN_MASTER_ROW_CHILDREN_C",
        "native_elf": str(NATIVE.relative_to(ROOT)), "native_elf_sha256": sha(NATIVE),
        "native_entries": {name: hex(address) for name, address in ENTRIES.items()},
        "shared_child": hex(DISPATCH), "profile_pointer_cell": hex(SLOT),
        "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
        "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj),
        "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
        "linked_object": str(linked.relative_to(ROOT)), "linked_object_sha256": sha(linked),
        "bounded_native_c_cases": len(cases), "unresolved_before": len(before),
        "unresolved_after": len(after), "imports_resolved": sorted(before - after),
        "imports_added": sorted(after - before), "source_complete": False,
        "full_payload_linked": False,
        "limits": ["Shared row-dispatch body 0x503498 is still an unimplemented C provider.",
                   "The profile pointer cell lacks source-owned storage and live BLE validation."],
    }
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(cases), len(before), len(after), sha(path))


if __name__ == "__main__":
    main()
