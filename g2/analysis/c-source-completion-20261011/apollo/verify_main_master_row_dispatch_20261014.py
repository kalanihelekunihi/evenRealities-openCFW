#!/usr/bin/env python3
"""Compare Apollo master row dispatch C with the complete native entry."""
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
SOURCE = G2 / "components/audio/master_dispatch_candidate_20261014/row_dispatch.c"
NATIVE = G2 / "analysis/shortcut-arm-tools-20261009-agent3/main-analysis-only.elf"
BASE = G2 / "build/c-firmware/20261014/main-master-row-children/apollo-main-master-row-children.o"
OUT = G2 / "build/c-firmware/20261014/main-master-row-dispatch"
ENTRY = 0x503498
CALLS = {
    "audio_ble_link_mask_select_47ae78": 0x47ae78,
    "DmConnPeerAddr": 0x4b6eea,
    "DmConnPeerAddrType": 0x4b6ed8,
    "audio_ble_pair_record_create_47a71c": 0x47a71c,
    "audio_ble_vendor_link_activate_55bc1e": 0x55bc1e,
    "audio_ble_vendor_link_start_55bbea": 0x55bbea,
}
ROW, PROFILE, SLOT, ADDRESS, CREATED, STOP = (
    0x20020000, 0x20030000, 0x20074358, 0x20031000, 0x20042000, 0x10010000)


def run(segments, entry, connection, mode, handle, link_result, profile_flag, address_type):
    uc = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
    for address, size in ((0x100000, 0x100000), (0x400000, 0x400000),
                          (0x10000000, 0x20000), (0x20000000, 0x100000)):
        uc.mem_map(address, size)
    for address, data in segments:
        uc.mem_write(address, data)
    row = bytearray([0x5a] * 0x30)
    row[:4] = struct.pack("<I", handle)
    profile = bytes([profile_flag, 0x12, 0x20, 0x34]) + bytes(12)
    uc.mem_write(ROW, bytes(row))
    uc.mem_write(PROFILE, profile)
    uc.mem_write(SLOT, struct.pack("<I", PROFILE))
    uc.reg_write(UC_ARM_REG_R0, connection)
    uc.reg_write(UC_ARM_REG_R1, mode)
    uc.reg_write(UC_ARM_REG_R2, ROW)
    uc.reg_write(UC_ARM_REG_SP, 0x200ff000)
    uc.reg_write(UC_ARM_REG_LR, STOP | 1)
    trace, writes = [], []
    target_names = {address: name for name, address in CALLS.items()}

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
        r3 = cpu.reg_read(UC_ARM_REG_R3)
        if name == "audio_ble_link_mask_select_47ae78":
            trace.append((name, r0, r1))
            cpu.mem_write(r2, b"\x6d")
            cpu.reg_write(UC_ARM_REG_R0, link_result)
        elif name == "DmConnPeerAddr":
            trace.append((name, r0))
            cpu.reg_write(UC_ARM_REG_R0, ADDRESS)
        elif name == "DmConnPeerAddrType":
            trace.append((name, r0))
            cpu.reg_write(UC_ARM_REG_R0, address_type)
        elif name == "audio_ble_pair_record_create_47a71c":
            trace.append((name, r0, r1, r2))
            cpu.reg_write(UC_ARM_REG_R0, CREATED)
        elif name == "audio_ble_vendor_link_activate_55bc1e":
            trace.append((name, r0, r1, r2))
        else:
            fifth = struct.unpack("<I", cpu.mem_read(cpu.reg_read(UC_ARM_REG_SP), 4))[0]
            trace.append((name, r0, r1, r2, r3, fifth))
        cpu.reg_write(UC_ARM_REG_PC, cpu.reg_read(UC_ARM_REG_LR))

    def write_hook(cpu, access, address, size, value, _):
        if ROW <= address < ROW + 0x30:
            writes.append((address - ROW, size, value & ((1 << (size * 8)) - 1)))

    uc.hook_add(UC_HOOK_CODE, code_hook)
    uc.hook_add(UC_HOOK_MEM_WRITE, write_hook)
    uc.emu_start(entry | 1, STOP + 2, count=1000)
    return trace, writes, bytes(uc.mem_read(ROW, 0x30))


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "row_dispatch.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m55", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2",
                    "-Wall", "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    if names(obj, "-g", "--defined-only") != {"audio_ble_master_row_dispatch_503498"}:
        raise RuntimeError("row dispatch C definition changed")
    with tempfile.TemporaryDirectory() as directory:
        trial = Path(directory) / "row_dispatch.elf"
        subprocess.run(["arm-none-eabi-ld", "-Ttext=0x110000", "-e",
                        "audio_ble_master_row_dispatch_503498",
                        f"--defsym=audio_ble_comm_profile_slot={SLOT}",
                        *(f"--defsym={name}={address | 1}" for name, address in CALLS.items()),
                        str(obj), "-o", str(trial)], check=True, capture_output=True)
        native_segments, _ = image(NATIVE)
        source_segments, symbols = image(trial)
        cases = [(connection, mode, handle, link_result, profile_flag, address_type)
                 for connection in (1, 0x102) for mode in (0, 1)
                 for handle in (0, 0x20043000)
                 for link_result in (0, 0x20043050)
                 for profile_flag in (0, 1) for address_type in (0, 1)]
        for args in cases:
            native = run(native_segments, ENTRY, *args)
            compiled = run(native_segments + source_segments,
                           symbols["audio_ble_master_row_dispatch_503498"], *args)
            if native != compiled:
                raise RuntimeError(f"row dispatch differs: {args} {native[:2]} {compiled[:2]}")
    before = names(BASE, "-u")
    if "audio_ble_master_row_dispatch_503498" not in before:
        raise RuntimeError("Main row dispatch import absent")
    linked = OUT / "apollo-main-master-row-dispatch.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), "-o", str(linked)], check=True)
    after = names(linked, "-u")
    added = {"audio_ble_vendor_link_activate_55bc1e", "audio_ble_vendor_link_start_55bbea"}
    if len(before) != 485 or len(after) != 486 or \
       before - after != {"audio_ble_master_row_dispatch_503498"} or after - before != added:
        raise RuntimeError("unexpected Main row dispatch import delta")
    receipt = {
        "status": "PASS_EXPERIMENTAL_MAIN_MASTER_ROW_DISPATCH_C",
        "native_elf": str(NATIVE.relative_to(ROOT)), "native_elf_sha256": sha(NATIVE),
        "native_entry": hex(ENTRY), "source": str(SOURCE.relative_to(ROOT)),
        "source_sha256": sha(SOURCE), "object": str(obj.relative_to(ROOT)),
        "object_sha256": sha(obj), "base_object": str(BASE.relative_to(ROOT)),
        "base_sha256": sha(BASE), "linked_object": str(linked.relative_to(ROOT)),
        "linked_object_sha256": sha(linked), "bounded_native_c_cases": len(cases),
        "unresolved_before": len(before), "unresolved_after": len(after),
        "imports_resolved": sorted(before - after), "imports_added": sorted(after - before),
        "source_complete": False, "full_payload_linked": False,
        "limits": ["Existing C callees and two vendor operations were cut at their entries in bounded comparisons.",
                   "The vendor operation bodies, profile storage, and live BLE timing remain open."],
    }
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(cases), len(before), len(after), sha(path))


if __name__ == "__main__":
    main()
