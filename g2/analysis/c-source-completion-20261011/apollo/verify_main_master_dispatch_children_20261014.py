#!/usr/bin/env python3
"""Verify two BLE master child bodies and bind them into Apollo Main."""
import hashlib
import json
import struct
import subprocess
import tempfile
from pathlib import Path

from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE, UC_HOOK_MEM_WRITE
from unicorn.arm_const import UC_ARM_REG_LR, UC_ARM_REG_PC, UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_SP

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/master_dispatch_candidate_20261014/children.c"
NATIVE = G2 / "analysis/shortcut-arm-tools-20261009-agent3/main-analysis-only.elf"
BASE = G2 / "build/c-firmware/20261014/main-master-dispatch-b/apollo-main-master-dispatch-b.o"
OUT = G2 / "build/c-firmware/20261014/main-master-dispatch-children"
MESSAGE = 0x20010000
ROW = 0x20020000
STOP = 0x10010000
ENTRIES = {"audio_ble_master_event_50390c": 0x50390c,
           "audio_ble_master_event_50391c": 0x50391c}
DISCONNECT = 0x4bb04a


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def names(path, *options):
    rows = subprocess.check_output(["arm-none-eabi-nm", *options, str(path)], text=True)
    return {row.split()[-1] for row in rows.splitlines() if row.strip()}


def image(path):
    with path.open("rb") as stream:
        elf = ELFFile(stream)
        segments = [(segment["p_vaddr"], segment.data()) for segment in elf.iter_segments()
                    if segment["p_type"] == "PT_LOAD"]
        symbols = {symbol.name: symbol["st_value"]
                   for symbol in elf.get_section_by_name(".symtab").iter_symbols()}
    return segments, symbols


def run(segments, entry, connection, status, row6, row8):
    uc = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
    uc.mem_map(0x100000, 0x100000)
    uc.mem_map(0x400000, 0x400000)
    uc.mem_map(0x10000000, 0x20000)
    uc.mem_map(0x20000000, 0x100000)
    for address, data in segments:
        uc.mem_write(address, data)
    message = bytearray(16)
    message[0:2] = struct.pack("<H", connection)
    message[4] = status
    row = bytearray([0x5a] * 0x30)
    row[6], row[8] = row6, row8
    uc.mem_write(MESSAGE, bytes(message))
    uc.mem_write(ROW, bytes(row))
    uc.reg_write(UC_ARM_REG_R0, MESSAGE)
    uc.reg_write(UC_ARM_REG_R1, ROW)
    uc.reg_write(UC_ARM_REG_SP, 0x200ff000)
    uc.reg_write(UC_ARM_REG_LR, STOP | 1)
    calls, writes = [], []

    def code_hook(cpu, address, size, _):
        if address == STOP:
            cpu.emu_stop()
        elif address == DISCONNECT:
            calls.append((address, cpu.reg_read(UC_ARM_REG_R0)))
            cpu.reg_write(UC_ARM_REG_PC, cpu.reg_read(UC_ARM_REG_LR))

    def write_hook(cpu, access, address, size, value, _):
        if ROW <= address < ROW + 0x30:
            writes.append((address - ROW, size, value & ((1 << (8 * size)) - 1)))

    uc.hook_add(UC_HOOK_CODE, code_hook)
    uc.hook_add(UC_HOOK_MEM_WRITE, write_hook)
    uc.emu_start(entry | 1, STOP + 2, count=1000)
    return bytes(uc.mem_read(ROW, 0x30)), calls, writes


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "children.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m55", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2",
                    "-Wall", "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    if names(obj, "-g", "--defined-only") != set(ENTRIES):
        raise RuntimeError("child C definitions changed")
    with tempfile.TemporaryDirectory() as directory:
        trial = Path(directory) / "children.elf"
        subprocess.run(["arm-none-eabi-ld", "-Ttext=0x110000", "-e",
                        "audio_ble_master_event_50390c",
                        f"--defsym=audio_ble_slave_disconnect_event={DISCONNECT | 1}",
                        str(obj), "-o", str(trial)], check=True, capture_output=True)
        original_segments, _ = image(NATIVE)
        source_segments, source_symbols = image(trial)
        cases = [(name, connection, status, row6, row8)
                 for name in ENTRIES for connection in (0, 1, 3, 0x102)
                 for status in (0, 1, 0x80) for row6 in (0, 1)
                 for row8 in (0, 0xa5)]
        for name, connection, status, row6, row8 in cases:
            original = run(original_segments, ENTRIES[name], connection, status, row6, row8)
            source = run(original_segments + source_segments, source_symbols[name],
                         connection, status, row6, row8)
            if original != source:
                raise RuntimeError(f"native/C child differs: {(name, connection, status, row6, row8)} {original[1:]} {source[1:]}")
    before = names(BASE, "-u")
    if not set(ENTRIES) <= before:
        raise RuntimeError("Main child imports absent")
    linked = OUT / "apollo-main-master-children.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), "-o", str(linked)], check=True)
    after = names(linked, "-u")
    if len(before) != 489 or len(after) != 487 or before - after != set(ENTRIES) or after - before:
        raise RuntimeError("unexpected Main child import delta")
    receipt = {
        "status": "PASS_EXPERIMENTAL_MAIN_MASTER_DISPATCH_CHILDREN_C",
        "native_elf": str(NATIVE.relative_to(ROOT)), "native_elf_sha256": sha(NATIVE),
        "native_entries": {name: hex(address) for name, address in ENTRIES.items()},
        "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
        "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj),
        "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
        "linked_object": str(linked.relative_to(ROOT)), "linked_object_sha256": sha(linked),
        "bounded_native_c_cases": len(cases), "unresolved_before": len(before),
        "unresolved_after": len(after), "imports_resolved": sorted(before - after),
        "imports_added": [], "source_complete": False, "full_payload_linked": False,
        "limits": ["Disconnect callee is a bounded call boundary, though an existing C provider is linked in Main.",
                   "Remaining master-dispatch child handlers and live BLE state remain open."],
    }
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(cases), len(before), len(after), sha(path))


if __name__ == "__main__":
    main()
