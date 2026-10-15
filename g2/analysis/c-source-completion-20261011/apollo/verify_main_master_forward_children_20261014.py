#!/usr/bin/env python3
"""Check two BLE master child wrappers against native and expose their callees."""
import json
import struct
import subprocess
import tempfile
from pathlib import Path

from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE, UC_HOOK_MEM_WRITE
from unicorn.arm_const import UC_ARM_REG_LR, UC_ARM_REG_PC, UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_SP

from verify_main_master_dispatch_children_20261014 import image, names, sha

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/master_dispatch_candidate_20261014/children_forward.c"
NATIVE = G2 / "analysis/shortcut-arm-tools-20261009-agent3/main-analysis-only.elf"
BASE = G2 / "build/c-firmware/20261014/main-master-state-children/apollo-main-master-state-children.o"
OUT = G2 / "build/c-firmware/20261014/main-master-forward-children"
ENTRIES = {"audio_ble_master_event_503810": 0x503810,
           "audio_ble_master_event_5038b8": 0x5038b8}
CHILDREN = {"audio_ble_master_child_47a5c0": 0x47a5c0,
            "audio_ble_master_child_47aed4": 0x47aed4}
MESSAGE, ROW, STOP = 0x20010000, 0x20020000, 0x10010000


def run(segments, entry, handle, row7, row11, byte30):
    uc = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
    for address, size in ((0x100000, 0x100000), (0x400000, 0x400000),
                          (0x10000000, 0x20000), (0x20000000, 0x100000)):
        uc.mem_map(address, size)
    for address, data in segments:
        uc.mem_write(address, data)
    message = bytearray(40)
    message[30] = byte30
    uc.mem_write(MESSAGE, bytes(message))
    row = bytearray([0x5a] * 0x30)
    row[:4] = struct.pack("<I", handle)
    row[7], row[11] = row7, row11
    uc.mem_write(ROW, bytes(row))
    uc.reg_write(UC_ARM_REG_R0, MESSAGE)
    uc.reg_write(UC_ARM_REG_R1, ROW)
    uc.reg_write(UC_ARM_REG_SP, 0x200ff000)
    uc.reg_write(UC_ARM_REG_LR, STOP | 1)
    calls, writes = [], []
    targets = {address: name for name, address in CHILDREN.items()}

    def code_hook(cpu, address, size, _):
        if address == STOP:
            cpu.emu_stop()
        elif address in targets:
            name = targets[address]
            calls.append((name, cpu.reg_read(UC_ARM_REG_R0),
                          cpu.reg_read(UC_ARM_REG_R1) if address == 0x47aed4 else 0))
            cpu.reg_write(UC_ARM_REG_PC, cpu.reg_read(UC_ARM_REG_LR))

    def write_hook(cpu, access, address, size, value, _):
        if ROW <= address < ROW + 0x30:
            writes.append((address - ROW, size, value & ((1 << (8 * size)) - 1)))

    uc.hook_add(UC_HOOK_CODE, code_hook)
    uc.hook_add(UC_HOOK_MEM_WRITE, write_hook)
    uc.emu_start(entry | 1, STOP + 2, count=500)
    return calls, writes, bytes(uc.mem_read(ROW, 0x30))


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "children_forward.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m55", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2",
                    "-Wall", "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    if names(obj, "-g", "--defined-only") != set(ENTRIES):
        raise RuntimeError("forward child C definitions changed")
    with tempfile.TemporaryDirectory() as directory:
        trial = Path(directory) / "forward.elf"
        subprocess.run(["arm-none-eabi-ld", "-Ttext=0x110000", "-e",
                        "audio_ble_master_event_503810",
                        *(f"--defsym={name}={address | 1}" for name, address in CHILDREN.items()),
                        str(obj), "-o", str(trial)], check=True, capture_output=True)
        native_segments, _ = image(NATIVE)
        source_segments, symbols = image(trial)
        cases = [(name, handle, row7, row11, byte30)
                 for name in ENTRIES for handle in (0, 0x20012000)
                 for row7 in (0, 1) for row11 in (0, 0x52, 0xff)
                 for byte30 in (0, 0x04, 0x80)]
        for name, handle, row7, row11, byte30 in cases:
            native = run(native_segments, ENTRIES[name], handle, row7, row11, byte30)
            compiled = run(native_segments + source_segments, symbols[name],
                           handle, row7, row11, byte30)
            if native != compiled:
                raise RuntimeError(f"forward child differs: {(name, handle, row7, row11, byte30)} {native[:2]} {compiled[:2]}")
    before = names(BASE, "-u")
    if not set(ENTRIES) <= before:
        raise RuntimeError("Main forward child imports absent")
    linked = OUT / "apollo-main-master-forward-children.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), "-o", str(linked)], check=True)
    after = names(linked, "-u")
    if len(before) != 485 or len(after) != 485 or before - after != set(ENTRIES) or \
       after - before != set(CHILDREN):
        raise RuntimeError("unexpected Main forward child import delta")
    receipt = {
        "status": "PASS_EXPERIMENTAL_MAIN_MASTER_FORWARD_CHILDREN_C",
        "native_elf": str(NATIVE.relative_to(ROOT)), "native_elf_sha256": sha(NATIVE),
        "native_entries": {name: hex(address) for name, address in ENTRIES.items()},
        "child_contracts": {name: hex(address) for name, address in CHILDREN.items()},
        "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
        "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj),
        "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
        "linked_object": str(linked.relative_to(ROOT)), "linked_object_sha256": sha(linked),
        "bounded_native_c_cases": len(cases), "unresolved_before": len(before),
        "unresolved_after": len(after), "imports_resolved": sorted(before - after),
        "imports_added": sorted(after - before), "source_complete": False,
        "full_payload_linked": False,
        "limits": ["Two child bodies are now C, but their lower native callees remain unimplemented.",
                   "Bounded comparisons cut at lower callees; live BLE state remains open."],
    }
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(cases), len(before), len(after), sha(path))


if __name__ == "__main__":
    main()
