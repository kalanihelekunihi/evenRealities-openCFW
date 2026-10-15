#!/usr/bin/env python3
"""Compare slave state children and one-byte RAM transfer to native entries."""
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
SOURCE = G2 / "components/audio/master_dispatch_candidate_20261014/slave_finish_children_b.c"
NATIVE = G2 / "analysis/shortcut-arm-tools-20261009-agent3/main-analysis-only.elf"
BASE = G2 / "build/c-firmware/20261014/main-slave-finish-children-a/apollo-main-slave-finish-children-a.o"
OUT = G2 / "build/c-firmware/20261014/main-slave-finish-children-b"
ENTRIES = {"audio_ble_slave_finish_4b3bb4": 0x4b3bb4,
           "audio_ble_slave_finish_4b3bd2": 0x4b3bd2,
           "audio_ble_slave_finish_4b3ba0": 0x4b3ba0}
MESSAGE, ROW, DM, STATUS, STOP = 0x20010000, 0x20020000, 0x20073b78, 0x20075020, 0x10010000
SETTER = 0x47b4ce


def run(segments, entry, message_status, handle, source_byte):
    uc = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
    for address, size in ((0x100000, 0x100000), (0x400000, 0x400000),
                          (0x10000000, 0x20000), (0x20000000, 0x100000)):
        uc.mem_map(address, size)
    for address, data in segments:
        uc.mem_write(address, data)
    message = bytearray(16)
    message[3] = message_status
    uc.mem_write(MESSAGE, bytes(message))
    uc.mem_write(ROW, struct.pack("<I", handle) + bytes(44))
    uc.mem_write(DM + 0x16, bytes([source_byte]))
    uc.mem_write(STATUS, b"\xa5")
    uc.reg_write(UC_ARM_REG_R0, MESSAGE)
    uc.reg_write(UC_ARM_REG_R1, ROW)
    uc.reg_write(UC_ARM_REG_SP, 0x200ff000)
    uc.reg_write(UC_ARM_REG_LR, STOP | 1)
    calls, writes = [], []

    def code_hook(cpu, address, size, _):
        if address == STOP:
            cpu.emu_stop()
        elif address == SETTER:
            calls.append((cpu.reg_read(UC_ARM_REG_R0), cpu.reg_read(UC_ARM_REG_R1)))
            cpu.reg_write(UC_ARM_REG_PC, cpu.reg_read(UC_ARM_REG_LR))

    def write_hook(cpu, access, address, size, value, _):
        if address == STATUS:
            writes.append((size, value & ((1 << (size * 8)) - 1)))

    uc.hook_add(UC_HOOK_CODE, code_hook)
    uc.hook_add(UC_HOOK_MEM_WRITE, write_hook)
    uc.emu_start(entry | 1, STOP + 2, count=500)
    return calls, writes, bytes(uc.mem_read(STATUS, 1))


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "slave_finish_children_b.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m55", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                    "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    if names(obj, "-g", "--defined-only") != set(ENTRIES) | {"audio_ble_slave_status_20075020"} or \
       names(obj, "-u") != {"audio_ble_connection_state_set_47b4ce", "audio_ble_dm_privacy_state"}:
        raise RuntimeError("slave child B C symbol contract changed")
    with tempfile.TemporaryDirectory() as directory:
        trial = Path(directory) / "children_b.elf"
        subprocess.run(["arm-none-eabi-ld", "-Ttext=0x110000", "-Tbss=0x20075020",
                        "-e", "audio_ble_slave_finish_4b3bb4",
                        f"--defsym=audio_ble_connection_state_set_47b4ce={SETTER | 1}",
                        f"--defsym=audio_ble_dm_privacy_state={DM}",
                        str(obj), "-o", str(trial)], check=True, capture_output=True)
        native_segments, _ = image(NATIVE)
        source_segments, symbols = image(trial)
        if symbols["audio_ble_slave_status_20075020"] != STATUS:
            raise RuntimeError("test RAM cell placement changed")
        cases = [(name, message_status, handle, source_byte)
                 for name in ENTRIES for message_status in (0, 1, 0xff)
                 for handle in (0, 0x20043000)
                 for source_byte in (0, 1, 0xa7)]
        for name, *args in cases:
            native = run(native_segments, ENTRIES[name], *args)
            compiled = run(native_segments + source_segments, symbols[name], *args)
            if native != compiled:
                raise RuntimeError(f"slave child B differs: {(name, *args)} {native} {compiled}")
    before = names(BASE, "-u")
    base_defined = names(BASE, "-g", "--defined-only")
    if not set(ENTRIES) <= before or not {"audio_ble_connection_state_set_47b4ce",
                                        "audio_ble_dm_privacy_state"} <= base_defined:
        raise RuntimeError("Main child B contracts or lower C providers absent")
    linked = OUT / "apollo-main-slave-finish-children-b.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), "-o", str(linked)], check=True)
    after = names(linked, "-u")
    if len(before) != 480 or len(after) != 477 or before - after != set(ENTRIES) or after - before:
        raise RuntimeError("unexpected Main child B import delta")
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_SLAVE_FINISH_CHILDREN_B_C",
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
               "limits": ["Connection-state setter is cut at its entry; its C body is already linked.",
                          "Test-only RAM placement matches native 0x20075020; whole-image linker placement remains open.",
                          "Six slave-finish child bodies remain open, plus whole-image and hardware gates."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(cases), len(before), len(after), sha(path))


if __name__ == "__main__":
    main()
