#!/usr/bin/env python3
"""Compare BLE master pair-event C body to native 0x5038da."""
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
SOURCE = G2 / "components/audio/master_dispatch_candidate_20261014/child_pair_complete.c"
NATIVE = G2 / "analysis/shortcut-arm-tools-20261009-agent3/main-analysis-only.elf"
BASE = G2 / "build/c-firmware/20261014/main-master-vendor-ops/apollo-main-master-vendor-ops.o"
OUT = G2 / "build/c-firmware/20261014/main-master-pair-child"
ENTRY = 0x5038da
CHILDREN = {"audio_ble_master_pair_state_47a49c": 0x47a49c,
            "audio_ble_master_pair_event_4bb098": 0x4bb098}
MESSAGE, ROW, STOP = 0x20010000, 0x20020000, 0x10010000


def run(segments, entry, status, handle, row4, row11):
    uc = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
    for address, size in ((0x100000, 0x100000), (0x400000, 0x400000),
                          (0x10000000, 0x20000), (0x20000000, 0x100000)):
        uc.mem_map(address, size)
    for address, data in segments:
        uc.mem_write(address, data)
    message = bytearray(16)
    message[4] = status
    row = bytearray([0x5a] * 0x30)
    row[:4] = struct.pack("<I", handle)
    row[4], row[11] = row4, row11
    uc.mem_write(MESSAGE, bytes(message))
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
            calls.append((targets[address], cpu.reg_read(UC_ARM_REG_R0),
                          cpu.reg_read(UC_ARM_REG_R1)))
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
    obj = OUT / "child_pair_complete.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m55", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2",
                    "-Wall", "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    if names(obj, "-g", "--defined-only") != {"audio_ble_master_event_5038da"}:
        raise RuntimeError("pair child C definition changed")
    with tempfile.TemporaryDirectory() as directory:
        trial = Path(directory) / "pair.elf"
        subprocess.run(["arm-none-eabi-ld", "-Ttext=0x110000", "-e",
                        "audio_ble_master_event_5038da",
                        *(f"--defsym={name}={address | 1}" for name, address in CHILDREN.items()),
                        str(obj), "-o", str(trial)], check=True, capture_output=True)
        native_segments, _ = image(NATIVE)
        source_segments, symbols = image(trial)
        cases = [(status, handle, row4, row11)
                 for status in (0, 1, 2, 0xff)
                 for handle in (0, 0x20043000)
                 for row4 in (0, 0x55) for row11 in (0, 0xaa)]
        for args in cases:
            native = run(native_segments, ENTRY, *args)
            compiled = run(native_segments + source_segments,
                           symbols["audio_ble_master_event_5038da"], *args)
            if native != compiled:
                raise RuntimeError(f"pair child differs: {args} {native[:2]} {compiled[:2]}")
    before = names(BASE, "-u")
    if "audio_ble_master_event_5038da" not in before:
        raise RuntimeError("Main pair child import absent")
    linked = OUT / "apollo-main-master-pair-child.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), "-o", str(linked)], check=True)
    after = names(linked, "-u")
    if len(before) != 484 or len(after) != 485 or \
       before - after != {"audio_ble_master_event_5038da"} or \
       after - before != set(CHILDREN):
        raise RuntimeError("unexpected Main pair import delta")
    receipt = {
        "status": "PASS_EXPERIMENTAL_MAIN_MASTER_PAIR_CHILD_C",
        "native_elf": str(NATIVE.relative_to(ROOT)), "native_elf_sha256": sha(NATIVE),
        "native_entry": hex(ENTRY), "child_contracts": {name: hex(address) for name, address in CHILDREN.items()},
        "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
        "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj),
        "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
        "linked_object": str(linked.relative_to(ROOT)), "linked_object_sha256": sha(linked),
        "bounded_native_c_cases": len(cases), "unresolved_before": len(before),
        "unresolved_after": len(after), "imports_resolved": sorted(before - after),
        "imports_added": sorted(after - before), "source_complete": False,
        "full_payload_linked": False,
        "limits": ["Pair-state and pair-event callees remain separate C source contracts.",
                   "Bounded child comparisons cut at those lower entries; live pairing remains unqualified."],
    }
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(cases), len(before), len(after), sha(path))


if __name__ == "__main__":
    main()
