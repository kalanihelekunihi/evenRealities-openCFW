#!/usr/bin/env python3
"""Compare close and address-resolution slave child C bodies to native."""
import json
import struct
import subprocess
import tempfile
from pathlib import Path

from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_LR, UC_ARM_REG_PC, UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_SP

from verify_main_master_dispatch_children_20261014 import image, names, sha

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/master_dispatch_candidate_20261014/slave_finish_children_c.c"
NATIVE = G2 / "analysis/shortcut-arm-tools-20261009-agent3/main-analysis-only.elf"
BASE = G2 / "build/c-firmware/20261014/main-slave-finish-children-b/apollo-main-slave-finish-children-b.o"
OUT = G2 / "build/c-firmware/20261014/main-slave-finish-children-c"
ENTRIES = {"audio_ble_slave_finish_4b39de": 0x4b39de,
           "audio_ble_slave_finish_4b3b4c": 0x4b3b4c}
PROVIDERS = {"audio_ble_master_child_47a5c0": 0x47a5c0,
             "g2_lfs_memcmp": 0x4751c8,
             "audio_ble_pair_record_find_47add4": 0x47add4,
             "audio_ble_slave_resolve_4b36b2": 0x4b36b2}
MESSAGE, ROW, STATE, OPEN_FLAG, STOP = 0x20010000, 0x20020000, 0x200719c8, 0x20074f93, 0x10010000


def run(segments, entry, handle, pending, address_type, address_nonzero, found):
    uc = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
    for address, size in ((0x100000, 0x100000), (0x400000, 0x400000),
                          (0x10000000, 0x20000), (0x20000000, 0x100000)):
        uc.mem_map(address, size)
    for address, data in segments:
        uc.mem_write(address, data)
    message = bytearray(20)
    if address_nonzero:
        message[6] = 0x12
    message[14:16] = struct.pack("<H", address_type)
    uc.mem_write(MESSAGE, bytes(message))
    uc.mem_write(ROW, struct.pack("<I", handle) + bytes(44))
    state = bytearray(0x80)
    state[0x74], state[0x6c] = pending, 0xa5
    uc.mem_write(STATE, bytes(state))
    uc.mem_write(OPEN_FLAG, b"\xa5")
    uc.reg_write(UC_ARM_REG_R0, MESSAGE)
    uc.reg_write(UC_ARM_REG_R1, ROW)
    uc.reg_write(UC_ARM_REG_SP, 0x200ff000)
    uc.reg_write(UC_ARM_REG_LR, STOP | 1)
    calls = []
    targets = {address: name for name, address in PROVIDERS.items()}

    def code_hook(cpu, address, size, _):
        if address == STOP:
            cpu.emu_stop()
            return
        if address not in targets:
            return
        name = targets[address]
        r0, r1, r2 = (cpu.reg_read(reg) for reg in
                      (UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2))
        if address == 0x4751c8:
            left, right = bytes(cpu.mem_read(r0, r2)), bytes(cpu.mem_read(r1, r2))
            calls.append((name, left, right, r2))
            cpu.reg_write(UC_ARM_REG_R0, 0 if left == right else 1)
        elif address == 0x47add4:
            calls.append((name, r0, r1))
            cpu.reg_write(UC_ARM_REG_R0, found)
        else:
            calls.append((name, r0))
            cpu.reg_write(UC_ARM_REG_R0, 0)
        cpu.reg_write(UC_ARM_REG_PC, cpu.reg_read(UC_ARM_REG_LR))

    uc.hook_add(UC_HOOK_CODE, code_hook)
    uc.emu_start(entry | 1, STOP + 2, count=1000)
    return (calls, bytes(uc.mem_read(ROW, 0x30)), bytes(uc.mem_read(STATE, 0x80)),
            bytes(uc.mem_read(OPEN_FLAG, 1)))


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "slave_finish_children_c.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                    "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    if names(obj, "-g", "--defined-only") != set(ENTRIES) | {"audio_ble_slave_open_flag_20074f93"} or \
       names(obj, "-u") != set(PROVIDERS) | {"audio_ble_subsystem_link_state_200719c8"}:
        raise RuntimeError("slave child C symbol contract changed")
    with tempfile.TemporaryDirectory() as directory:
        trial = Path(directory) / "children_c.elf"
        subprocess.run(["arm-none-eabi-ld", "-Ttext=0x110000", "-Tbss=0x20074f93", "-e",
                        "audio_ble_slave_finish_4b39de",
                        *(f"--defsym={name}={address | 1}" for name, address in PROVIDERS.items()),
                        f"--defsym=audio_ble_subsystem_link_state_200719c8={STATE}",
                        str(obj), "-o", str(trial)], check=True, capture_output=True)
        native_segments, _ = image(NATIVE)
        source_segments, symbols = image(trial)
        if symbols["audio_ble_slave_open_flag_20074f93"] != OPEN_FLAG:
            raise RuntimeError("test open-flag placement changed")
        cases = [(name, handle, pending, address_type, address_nonzero, found)
                 for name in ENTRIES for handle in (0, 0x20043000)
                 for pending in (0, 1) for address_type in (0, 1)
                 for address_nonzero in (0, 1) for found in (0, 0x20044000)]
        for name, *args in cases:
            native = run(native_segments, ENTRIES[name], *args)
            compiled = run(native_segments + source_segments, symbols[name], *args)
            if native != compiled:
                raise RuntimeError(f"slave child C differs: {(name, *args)} {native[0]} {compiled[0]}")
    before = names(BASE, "-u")
    base_defined = names(BASE, "-g", "--defined-only")
    expected_added = {"audio_ble_pair_record_find_47add4", "audio_ble_slave_resolve_4b36b2"}
    if not set(ENTRIES) <= before or not (set(PROVIDERS) - expected_added) <= base_defined or \
       "audio_ble_subsystem_link_state_200719c8" not in base_defined:
        raise RuntimeError("Main child C contracts or C providers absent")
    linked = OUT / "apollo-main-slave-finish-children-c.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), "-o", str(linked)], check=True)
    after = names(linked, "-u")
    if len(before) != 477 or len(after) != 477 or before - after != set(ENTRIES) or \
       after - before != expected_added:
        raise RuntimeError(f"unexpected Main child C import delta {before-after} {after-before}")
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_SLAVE_FINISH_CHILDREN_C_C",
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
               "limits": ["Record lookup and slave resolve remain separate lower C contracts.",
                          "Native and C compare provider calls and RAM effects, not provider internals.",
                          "Four slave-finish child bodies remain open, plus whole-image and hardware gates."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(cases), len(before), len(after), sha(path))


if __name__ == "__main__":
    main()
