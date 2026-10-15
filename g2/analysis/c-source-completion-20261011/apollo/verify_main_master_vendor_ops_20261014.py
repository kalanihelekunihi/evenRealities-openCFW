#!/usr/bin/env python3
"""Verify two native BLE vendor message constructors against C."""
import json
import struct
import subprocess
import tempfile
from pathlib import Path

from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE, UC_HOOK_MEM_WRITE
from unicorn.arm_const import (UC_ARM_REG_LR, UC_ARM_REG_PC, UC_ARM_REG_R0,
                               UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_R3,
                               UC_ARM_REG_SP)

from verify_main_master_dispatch_children_20261014 import image, names, sha

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/master_dispatch_candidate_20261014/vendor_ops.c"
NATIVE = G2 / "analysis/shortcut-arm-tools-20261009-agent3/main-analysis-only.elf"
BASE = G2 / "build/c-firmware/20261014/main-master-row-dispatch/apollo-main-master-row-dispatch.o"
OUT = G2 / "build/c-firmware/20261014/main-master-vendor-ops"
ENTRIES = {"audio_ble_vendor_link_start_55bbea": 0x55bbea,
           "audio_ble_vendor_link_activate_55bc1e": 0x55bc1e}
LOWER = {"WsfMsgAlloc": 0x4bf99e, "SmpDmMsgSend": 0x537bd6,
         "audio_queue_copy_bytes": 0x439be4, "WsfMsgSend": 0x4bf9ba}
MESSAGE, DESCRIPTOR, DM, STOP = 0x20040000, 0x20050000, 0x20073b78, 0x10010000


def run(segments, entry, is_start, connection, allocated, variant):
    uc = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
    for address, size in ((0x100000, 0x100000), (0x400000, 0x400000),
                          (0x10000000, 0x20000), (0x20000000, 0x100000)):
        uc.mem_map(address, size)
    for address, data in segments:
        uc.mem_write(address, data)
    uc.mem_write(MESSAGE, bytes([0xa5] * 40))
    uc.mem_write(DESCRIPTOR, bytes(range(40)))
    uc.mem_write(DM + 12, b"\x42")
    uc.reg_write(UC_ARM_REG_R0, connection)
    uc.reg_write(UC_ARM_REG_R1, 0x70 + variant)
    uc.reg_write(UC_ARM_REG_R2, (0x90 + variant) if is_start else DESCRIPTOR)
    uc.reg_write(UC_ARM_REG_R3, 0xa0 + variant)
    uc.reg_write(UC_ARM_REG_SP, 0x200ff000)
    uc.mem_write(0x200ff000, struct.pack("<I", variant))
    uc.reg_write(UC_ARM_REG_LR, STOP | 1)
    calls, writes = [], []
    target_names = {address: name for name, address in LOWER.items()}

    def code_hook(cpu, address, size, _):
        if address == STOP:
            cpu.emu_stop()
            return
        name = target_names.get(address)
        if name is None:
            return
        r0 = cpu.reg_read(UC_ARM_REG_R0)
        r1 = cpu.reg_read(UC_ARM_REG_R1)
        r2 = cpu.reg_read(UC_ARM_REG_R2)
        if name == "WsfMsgAlloc":
            calls.append((name, r0))
            cpu.reg_write(UC_ARM_REG_R0, MESSAGE if allocated else 0)
        elif name == "audio_queue_copy_bytes":
            calls.append((name, r0, r1, r2))
            cpu.mem_write(r0, bytes(cpu.mem_read(r1, r2)))
            cpu.reg_write(UC_ARM_REG_R0, r0)
        elif name == "WsfMsgSend":
            calls.append((name, r0, r1))
        else:
            calls.append((name, r0))
        cpu.reg_write(UC_ARM_REG_PC, cpu.reg_read(UC_ARM_REG_LR))

    def write_hook(cpu, access, address, size, value, _):
        if MESSAGE <= address < MESSAGE + 40:
            writes.append((address - MESSAGE, size, value & ((1 << (8 * size)) - 1)))

    uc.hook_add(UC_HOOK_CODE, code_hook)
    uc.hook_add(UC_HOOK_MEM_WRITE, write_hook)
    uc.emu_start(entry | 1, STOP + 2, count=500)
    return calls, writes, bytes(uc.mem_read(MESSAGE, 40))


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "vendor_ops.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m55", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2",
                    "-Wall", "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    if names(obj, "-g", "--defined-only") != set(ENTRIES):
        raise RuntimeError("vendor C definitions changed")
    with tempfile.TemporaryDirectory() as directory:
        trial = Path(directory) / "vendor.elf"
        subprocess.run(["arm-none-eabi-ld", "-Ttext=0x110000", "-e",
                        "audio_ble_vendor_link_start_55bbea",
                        f"--defsym=audio_ble_dm_handler_state={DM}",
                        *(f"--defsym={name}={address | 1}" for name, address in LOWER.items()),
                        str(obj), "-o", str(trial)], check=True, capture_output=True)
        native_segments, _ = image(NATIVE)
        source_segments, symbols = image(trial)
        cases = [(name, connection, allocated, variant)
                 for name in ENTRIES for connection in (0, 1, 0x102)
                 for allocated in (False, True) for variant in (0, 1, 0x1f)]
        for name, connection, allocated, variant in cases:
            native = run(native_segments, ENTRIES[name], name.endswith("55bbea"),
                         connection, allocated, variant)
            compiled = run(native_segments + source_segments, symbols[name],
                           name.endswith("55bbea"), connection, allocated, variant)
            if native != compiled:
                raise RuntimeError(f"vendor op differs: {(name, connection, allocated, variant)} {native[:2]} {compiled[:2]}")
    before = names(BASE, "-u")
    if not set(ENTRIES) <= before or not set(LOWER) <= names(BASE, "-g", "--defined-only"):
        raise RuntimeError("Main vendor contracts changed")
    linked = OUT / "apollo-main-master-vendor-ops.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), "-o", str(linked)], check=True)
    after = names(linked, "-u")
    if len(before) != 486 or len(after) != 484 or before - after != set(ENTRIES) or after - before:
        raise RuntimeError("unexpected Main vendor import delta")
    receipt = {
        "status": "PASS_EXPERIMENTAL_MAIN_MASTER_VENDOR_OPS_C",
        "native_elf": str(NATIVE.relative_to(ROOT)), "native_elf_sha256": sha(NATIVE),
        "native_entries": {name: hex(address) for name, address in ENTRIES.items()},
        "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
        "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj),
        "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
        "linked_object": str(linked.relative_to(ROOT)), "linked_object_sha256": sha(linked),
        "bounded_native_c_cases": len(cases), "unresolved_before": len(before),
        "unresolved_after": len(after), "imports_resolved": sorted(before - after),
        "imports_added": [], "source_complete": False, "full_payload_linked": False,
        "limits": ["Allocator, copy, and send callees are bounded cuts; C providers are present in Main.",
                   "Live BLE allocation and message delivery timing remain unqualified."],
    }
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(cases), len(before), len(after), sha(path))


if __name__ == "__main__":
    main()
