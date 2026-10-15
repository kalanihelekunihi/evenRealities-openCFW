#!/usr/bin/env python3
"""Compare native 0x4b3aec CCC replay routing to C."""
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
SOURCE = G2 / "components/audio/master_dispatch_candidate_20261014/slave_finish_ccc.c"
NATIVE = G2 / "analysis/shortcut-arm-tools-20261009-agent3/main-analysis-only.elf"
BASE = G2 / "build/c-firmware/20261014/main-slave-finish-pairing/apollo-main-slave-finish-pairing.o"
OUT = G2 / "build/c-firmware/20261014/main-slave-finish-ccc"
ENTRY, MESSAGE, ROW, TABLE, HANDLE, FLAG, STOP = (
    0x4b3aec, 0x20010000, 0x20020000, 0x200717b0,
    0x20045000, 0x20074f93, 0x10010000)
COUNT, SETTER = 0x52c664, 0x52c60e


def run(segments, entry, connection, row6, status4, flag, count):
    uc = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
    for address, size in ((0x100000, 0x100000), (0x400000, 0x400000),
                          (0x10000000, 0x20000), (0x20000000, 0x100000)):
        uc.mem_map(address, size)
    for address, data in segments:
        uc.mem_write(address, data)
    message = bytearray(16)
    message[0], message[4] = connection, status4
    uc.mem_write(MESSAGE, bytes(message))
    row = bytearray([0x5a] * 0x30)
    row[6] = row6
    uc.mem_write(ROW, bytes(row))
    uc.mem_write(TABLE, struct.pack("<I", HANDLE) * 36)
    uc.mem_write(HANDLE + 0x6c, struct.pack("<HHH", 0x1111, 0, 0x3333))
    uc.mem_write(FLAG, bytes([flag]))
    uc.reg_write(UC_ARM_REG_R0, MESSAGE)
    uc.reg_write(UC_ARM_REG_R1, ROW)
    uc.reg_write(UC_ARM_REG_SP, 0x200ff000)
    uc.reg_write(UC_ARM_REG_LR, STOP | 1)
    calls, writes = [], []

    def code_hook(cpu, address, size, _):
        if address == STOP:
            cpu.emu_stop()
        elif address == COUNT:
            calls.append(("count",))
            cpu.reg_write(UC_ARM_REG_R0, count)
            cpu.reg_write(UC_ARM_REG_PC, cpu.reg_read(UC_ARM_REG_LR))
        elif address == SETTER:
            calls.append(("set", cpu.reg_read(UC_ARM_REG_R0),
                          cpu.reg_read(UC_ARM_REG_R1), cpu.reg_read(UC_ARM_REG_R2)))
            cpu.reg_write(UC_ARM_REG_PC, cpu.reg_read(UC_ARM_REG_LR))

    def write_hook(cpu, access, address, size, value, _):
        if ROW <= address < ROW + 0x30:
            writes.append((address - ROW, size, value & ((1 << (size * 8)) - 1)))

    uc.hook_add(UC_HOOK_CODE, code_hook)
    uc.hook_add(UC_HOOK_MEM_WRITE, write_hook)
    uc.emu_start(entry | 1, STOP + 2, count=1200)
    return calls, writes, bytes(uc.mem_read(ROW, 0x30))


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "slave_finish_ccc.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                    "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    providers = {"audio_ble_slave_ccc_count_52c664": COUNT,
                 "audio_ble_slave_ccc_set_52c60e": SETTER}
    if names(obj, "-g", "--defined-only") != {"audio_ble_slave_finish_4b3aec"} or \
       names(obj, "-u") != set(providers) | {
           "audio_ble_discovery_connection_records_200717b0",
           "audio_ble_slave_open_flag_20074f93"}:
        raise RuntimeError("CCC C symbol contract changed")
    with tempfile.TemporaryDirectory() as directory:
        trial = Path(directory) / "slave_ccc.elf"
        subprocess.run(["arm-none-eabi-ld", "-Ttext=0x110000", "-e",
                        "audio_ble_slave_finish_4b3aec",
                        *(f"--defsym={name}={address | 1}" for name, address in providers.items()),
                        f"--defsym=audio_ble_discovery_connection_records_200717b0={TABLE}",
                        f"--defsym=audio_ble_slave_open_flag_20074f93={FLAG}",
                        str(obj), "-o", str(trial)], check=True, capture_output=True)
        native_segments, _ = image(NATIVE)
        source_segments, symbols = image(trial)
        cases = [(connection, row6, status4, flag, count)
                 for connection in (1, 2, 3) for row6 in (0, 1)
                 for status4 in (0, 1) for flag in (0, 1)
                 for count in (0, 1, 3)]
        for args in cases:
            native = run(native_segments, ENTRY, *args)
            compiled = run(native_segments + source_segments,
                           symbols["audio_ble_slave_finish_4b3aec"], *args)
            if native != compiled:
                raise RuntimeError(f"slave CCC differs: {args} {native[:2]} {compiled[:2]}")
    before = names(BASE, "-u")
    base_defined = names(BASE, "-g", "--defined-only")
    if "audio_ble_slave_finish_4b3aec" not in before or not {
        "audio_ble_discovery_connection_records_200717b0",
        "audio_ble_slave_open_flag_20074f93"} <= base_defined:
        raise RuntimeError("Main CCC child or RAM state absent")
    linked = OUT / "apollo-main-slave-finish-ccc.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), "-o", str(linked)], check=True)
    after = names(linked, "-u")
    if len(before) != 476 or len(after) != 477 or \
       before - after != {"audio_ble_slave_finish_4b3aec"} or after - before != set(providers):
        raise RuntimeError(f"unexpected Main CCC import delta {before-after} {after-before}")
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_SLAVE_FINISH_CCC_C",
               "native_elf": str(NATIVE.relative_to(ROOT)), "native_elf_sha256": sha(NATIVE),
               "native_entry": hex(ENTRY), "lower_providers": {n: hex(a) for n, a in providers.items()},
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj),
               "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
               "linked_object": str(linked.relative_to(ROOT)),
               "linked_object_sha256": sha(linked), "bounded_native_c_cases": len(cases),
               "unresolved_before": len(before), "unresolved_after": len(after),
               "imports_resolved": sorted(before - after), "imports_added": sorted(after - before),
               "source_complete": False, "full_payload_linked": False,
               "limits": ["CCC count and setter remain lower C contracts, cut at native entries.",
                          "Only valid connection IDs 1..3 are compared when replay flag is set.",
                          "Two slave-finish children remain, plus whole-image and hardware gates."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(cases), len(before), len(after), sha(path))


if __name__ == "__main__":
    main()
