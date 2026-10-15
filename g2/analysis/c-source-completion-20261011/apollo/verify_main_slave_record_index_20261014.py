#!/usr/bin/env python3
"""Compare native and C DM connection indexing for every byte ID."""
import json
import subprocess
import tempfile
from pathlib import Path

from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_LR, UC_ARM_REG_PC, UC_ARM_REG_R0, UC_ARM_REG_SP

from verify_main_master_dispatch_children_20261014 import image, names, sha

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/master_dispatch_candidate_20261014/slave_record_index.c"
NATIVE = G2 / "analysis/shortcut-arm-tools-20261009-agent3/main-analysis-only.elf"
BASE = G2 / "build/c-firmware/20261014/main-slave-finish-connect/apollo-main-slave-finish-connect.o"
OUT = G2 / "build/c-firmware/20261014/main-slave-record-index"
TABLE, STOP = 0x200712a4, 0x10010000
ENTRIES = {"audio_ble_slave_record_kind_4b6ed8": 0x4b6ed8,
           "audio_ble_slave_record_key_4b6eea": 0x4b6eea}


def run(segments, entry, connection):
    uc = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
    for address, size in ((0x100000, 0x100000), (0x400000, 0x400000),
                          (0x10000000, 0x20000), (0x20000000, 0x100000)):
        uc.mem_map(address, size)
    for address, data in segments:
        uc.mem_write(address, data)
    # Both sides read the same native RAM coordinates, including ID zero.
    for index in range(256):
        uc.mem_write(TABLE + index * 0x30 - 0x1d,
                     bytes([(index * 37 + 11) & 0xff]))
    uc.reg_write(UC_ARM_REG_R0, connection | 0x123400)
    uc.reg_write(UC_ARM_REG_SP, 0x200ff000)
    uc.reg_write(UC_ARM_REG_LR, STOP | 1)

    def hook(cpu, address, size, _):
        if address == STOP:
            cpu.emu_stop()

    uc.hook_add(UC_HOOK_CODE, hook)
    uc.emu_start(entry | 1, STOP + 2, count=80)
    return uc.reg_read(UC_ARM_REG_R0)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "slave_record_index.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                    "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    if names(obj, "-g", "--defined-only") != set(ENTRIES) or \
       names(obj, "-u") != {"audio_ble_dm_conn_rows_200712a4"}:
        raise RuntimeError("record-index source symbol contract changed")
    with tempfile.TemporaryDirectory() as directory:
        trial = Path(directory) / "record_index.elf"
        subprocess.run(["arm-none-eabi-ld", "-Ttext=0x110000", "-e",
                        "audio_ble_slave_record_kind_4b6ed8",
                        f"--defsym=audio_ble_dm_conn_rows_200712a4={TABLE}",
                        str(obj), "-o", str(trial)], check=True, capture_output=True)
        native_segments, _ = image(NATIVE)
        source_segments, symbols = image(trial)
        for name, address in ENTRIES.items():
            for connection in range(256):
                native = run(native_segments, address, connection)
                compiled = run(native_segments + source_segments, symbols[name], connection)
                if native != compiled:
                    raise RuntimeError(f"record-index mismatch {name} {connection}: {native:#x} != {compiled:#x}")
    before = names(BASE, "-u")
    if not set(ENTRIES) <= before or \
       "audio_ble_dm_conn_rows_200712a4" not in names(BASE, "-g", "--defined-only"):
        raise RuntimeError("Apollo Main record-index contracts changed")
    linked = OUT / "apollo-main-slave-record-index.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), "-o", str(linked)], check=True)
    after = names(linked, "-u")
    if before - after != set(ENTRIES) or after - before:
        raise RuntimeError(f"unexpected import delta: {before-after}, {after-before}")
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_SLAVE_RECORD_INDEX_C",
               "native_elf": str(NATIVE.relative_to(ROOT)), "native_elf_sha256": sha(NATIVE),
               "native_entries": {name: hex(address) for name, address in ENTRIES.items()},
               "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
               "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj),
               "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
               "linked_object": str(linked.relative_to(ROOT)),
               "linked_object_sha256": sha(linked), "bounded_native_c_cases": 512,
               "unresolved_before": len(before), "unresolved_after": len(after),
               "imports_resolved": sorted(before-after), "imports_added": sorted(after-before),
               "source_complete": False, "full_payload_linked": False,
               "limits": ["The oracle places the source table at native RAM 0x200712a4; final linker placement remains open.",
                          "ID zero reads RAM before the three source-owned connection rows.",
                          "Whole-image and hardware behavior remain separate gates."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], 512, len(before), len(after), sha(path))


if __name__ == "__main__":
    main()
