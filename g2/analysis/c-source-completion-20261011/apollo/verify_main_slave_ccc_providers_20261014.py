#!/usr/bin/env python3
"""Compare CCC count and setter C providers to native 0x52c664/0x52c60e."""
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
SOURCE = G2 / "components/audio/master_dispatch_candidate_20261014/slave_ccc_providers.c"
NATIVE = G2 / "analysis/shortcut-arm-tools-20261009-agent3/main-analysis-only.elf"
BASE = G2 / "build/c-firmware/20261014/main-slave-finish-ccc/apollo-main-slave-finish-ccc.o"
OUT = G2 / "build/c-firmware/20261014/main-slave-ccc-providers"
ENTRIES = {"audio_ble_slave_ccc_count_52c664": 0x52c664,
           "audio_ble_slave_ccc_set_52c60e": 0x52c60e}
RUNTIME, TABLE, STOP = 0x20073b00, 0x20046000, 0x10010000
GETTER = 0x52bcea


def run(segments, entry, is_count, connection, route, value, has_table, count):
    uc = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
    for address, size in ((0x100000, 0x100000), (0x400000, 0x400000),
                          (0x10000000, 0x20000), (0x20000000, 0x100000)):
        uc.mem_map(address, size)
    for address, data in segments:
        uc.mem_write(address, data)
    runtime = bytearray(0x18)
    for i in range(3):
        runtime[i * 4:i * 4 + 4] = struct.pack("<I", TABLE if has_table else 0)
    runtime[0x14] = count
    uc.mem_write(RUNTIME, bytes(runtime))
    uc.mem_write(TABLE, bytes([0xa5] * 0x20))
    uc.reg_write(UC_ARM_REG_R0, connection)
    uc.reg_write(UC_ARM_REG_R1, route)
    uc.reg_write(UC_ARM_REG_R2, value)
    uc.reg_write(UC_ARM_REG_SP, 0x200ff000)
    uc.reg_write(UC_ARM_REG_LR, STOP | 1)
    writes = []

    def code_hook(cpu, address, size, _):
        if address == STOP:
            cpu.emu_stop()

    def write_hook(cpu, access, address, size, written, _):
        if TABLE <= address < TABLE + 0x20:
            writes.append((address - TABLE, size, written & ((1 << (size * 8)) - 1)))

    uc.hook_add(UC_HOOK_CODE, code_hook)
    uc.hook_add(UC_HOOK_MEM_WRITE, write_hook)
    uc.emu_start(entry | 1, STOP + 2, count=500)
    return (uc.reg_read(UC_ARM_REG_R0) if is_count else None,
            writes, bytes(uc.mem_read(TABLE, 0x20)))


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "slave_ccc_providers.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                    "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    if names(obj, "-g", "--defined-only") != set(ENTRIES) or \
       names(obj, "-u") != {"audio_ble_atts_ccc_runtime_20073b00",
                           "audio_ble_atts_ccc_get_table_52bcea"}:
        raise RuntimeError("CCC provider C symbol contract changed")
    with tempfile.TemporaryDirectory() as directory:
        trial = Path(directory) / "ccc_providers.elf"
        subprocess.run(["arm-none-eabi-ld", "-Ttext=0x110000", "-e",
                        "audio_ble_slave_ccc_count_52c664",
                        f"--defsym=audio_ble_atts_ccc_runtime_20073b00={RUNTIME}",
                        f"--defsym=audio_ble_atts_ccc_get_table_52bcea={GETTER | 1}",
                        str(obj), "-o", str(trial)], check=True, capture_output=True)
        native_segments, _ = image(NATIVE)
        source_segments, symbols = image(trial)
        cases = [(name, connection, route, value, has_table, count)
                 for name in ENTRIES for connection in (1, 2, 3)
                 for route in (0, 1, 3) for value in (0, 0x1234)
                 for has_table in (0, 1) for count in (0, 1, 3)]
        for name, *args in cases:
            native = run(native_segments, ENTRIES[name], name.endswith("52c664"), *args)
            compiled = run(native_segments + source_segments, symbols[name],
                           name.endswith("52c664"), *args)
            if native != compiled:
                raise RuntimeError(f"CCC provider differs: {(name, *args)} {native[:2]} {compiled[:2]}")
    before = names(BASE, "-u")
    if not set(ENTRIES) <= before or "audio_ble_atts_ccc_get_table_52bcea" not in names(BASE, "-g", "--defined-only"):
        raise RuntimeError("Main CCC lower imports or table getter absent")
    linked = OUT / "apollo-main-slave-ccc-providers.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), "-o", str(linked)], check=True)
    after = names(linked, "-u")
    if len(before) != 477 or len(after) != 475 or before - after != set(ENTRIES) or after - before:
        raise RuntimeError("unexpected Main CCC provider import delta")
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_SLAVE_CCC_PROVIDERS_C",
               "native_elf": str(NATIVE.relative_to(ROOT)), "native_elf_sha256": sha(NATIVE),
               "native_entries": {n: hex(a) for n, a in ENTRIES.items()},
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj),
               "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
               "linked_object": str(linked.relative_to(ROOT)),
               "linked_object_sha256": sha(linked), "bounded_native_c_cases": len(cases),
               "unresolved_before": len(before), "unresolved_after": len(after),
               "imports_resolved": sorted(before - after), "imports_added": sorted(after - before),
               "source_complete": False, "full_payload_linked": False,
               "limits": ["The existing native table getter is called by both setter variants in this comparison.",
                          "ATT CCC runtime storage remains an unresolved Main import and RAM placement gate.",
                          "Two slave-finish children remain, plus whole-image and hardware gates."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(cases), len(before), len(after), sha(path))


if __name__ == "__main__":
    main()
