#!/usr/bin/env python3
"""Bounded native/C comparison for the slave-open finish child."""
import json
import struct
import subprocess
import tempfile
from pathlib import Path

from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn.arm_const import (UC_ARM_REG_LR, UC_ARM_REG_PC, UC_ARM_REG_R0,
                               UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_SP)

from verify_main_master_dispatch_children_20261014 import image, names, sha

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/master_dispatch_candidate_20261014/slave_finish_open.c"
NATIVE = G2 / "analysis/shortcut-arm-tools-20261009-agent3/main-analysis-only.elf"
BASE = G2 / "build/c-firmware/20261014/main-slave-ccc-providers/apollo-main-slave-ccc-providers.o"
OUT = G2 / "build/c-firmware/20261014/main-slave-finish-open"
ENTRY = "audio_ble_slave_finish_4b3944"
PROVIDERS = {
    "audio_ble_pair_record_find_47ad74": 0x47ad74,
    "audio_ble_subsystem_child_479418": 0x479418,
    "audio_ble_slave_open_fallback_4b3606": 0x4b3606,
    "audio_ble_slave_apply_record_52c244": 0x52c244,
    "audio_ble_pair_record_flags_47b40c": 0x47b40c,
    "audio_ble_slave_apply_flags_52d370": 0x52d370,
    "AppDbCheckBonded": 0x47a600,
    "audio_ble_dm_sec_slave_req": 0x52bb00,
}
MESSAGE, ROW, PROFILE, PROFILE_PTR = 0x20010000, 0x20020000, 0x20050000, 0x20074358
OPEN_FLAG, PAIR_RECORD, STOP = 0x20074f93, 0x20043000, 0x10010000


def run(segments, entry, found, msg_type, addr_flags, profile_policy, bonded, conn):
    uc = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
    for address, size in ((0x100000, 0x100000), (0x400000, 0x400000),
                          (0x10000000, 0x20000), (0x20000000, 0x100000)):
        uc.mem_map(address, size)
    for address, data in segments:
        uc.mem_write(address, data)
    msg = bytearray(20)
    msg[0], msg[9], msg[15] = conn, msg_type, addr_flags
    uc.mem_write(MESSAGE, bytes(msg))
    row = bytearray(0x30)
    row[4], row[6], row[7] = 3, 0xa5, 0xa5
    uc.mem_write(ROW, bytes(row))
    uc.mem_write(PROFILE_PTR, struct.pack("<I", PROFILE))
    profile = bytearray(8)
    profile[0], profile[4] = 7, profile_policy
    uc.mem_write(PROFILE, bytes(profile))
    uc.mem_write(OPEN_FLAG, b"\xa5")
    uc.reg_write(UC_ARM_REG_R0, MESSAGE)
    uc.reg_write(UC_ARM_REG_R1, ROW)
    uc.reg_write(UC_ARM_REG_SP, 0x200ff000)
    uc.reg_write(UC_ARM_REG_LR, STOP | 1)
    targets = {address: name for name, address in PROVIDERS.items()}
    calls = []

    def hook(cpu, address, size, _):
        if address == STOP:
            cpu.emu_stop()
            return
        if address not in targets:
            return
        name = targets[address]
        r0, r1, r2 = (cpu.reg_read(reg) for reg in
                      (UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2))
        if address == 0x47ad74:
            calls.append((name, r0, bytes(cpu.mem_read(r1, 6))))
            result = PAIR_RECORD if found else 0
        elif address == 0x47b40c:
            calls.append((name, r0))
            cpu.mem_write(r1, struct.pack("<I", 0x123456ab))
            cpu.mem_write(r2, struct.pack("<I", 0x89abcdef))
            result = 0
        elif address == 0x52c244:
            calls.append((name, r0, r1))
            result = 0
        elif address == 0x52d370:
            calls.append((name, r0, r1, r2))
            result = 0
        elif address == 0x4b3606:
            calls.append((name, r0))
            result = 0
        elif address == 0x47a600:
            calls.append((name,))
            result = bonded
        elif address == 0x52bb00:
            calls.append((name, r0, r1))
            result = 0
        else:
            calls.append((name,))
            result = 0
        cpu.reg_write(UC_ARM_REG_R0, result)
        cpu.reg_write(UC_ARM_REG_PC, cpu.reg_read(UC_ARM_REG_LR))

    uc.hook_add(UC_HOOK_CODE, hook)
    uc.emu_start(entry | 1, STOP + 2, count=1200)
    return calls, bytes(uc.mem_read(ROW, 0x30)), bytes(uc.mem_read(OPEN_FLAG, 1))


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "slave_finish_open.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                    "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    if names(obj, "-g", "--defined-only") != {ENTRY}:
        raise RuntimeError("unexpected child source symbols")
    with tempfile.TemporaryDirectory() as directory:
        trial = Path(directory) / "open.elf"
        subprocess.run(["arm-none-eabi-ld", "-Ttext=0x110000", "-e", ENTRY,
                        *(f"--defsym={name}={address | 1}" for name, address in PROVIDERS.items()),
                        f"--defsym=audio_ble_comm_profile_slot={PROFILE_PTR}",
                        f"--defsym=audio_ble_slave_open_flag_20074f93={OPEN_FLAG}",
                        str(obj), "-o", str(trial)], check=True, capture_output=True)
        native_segments, _ = image(NATIVE)
        source_segments, symbols = image(trial)
        cases = [(found, msg_type, addr_flags, policy, bonded, conn)
                 for found in (0, 1) for msg_type in (0, 1, 2)
                 for addr_flags in (0, 0x40, 0x80)
                 for policy in (0, 1) for bonded in (0, 1)
                 for conn in (0, 0x93)]
        for case in cases:
            native = run(native_segments, 0x4b3944, *case)
            compiled = run(native_segments + source_segments, symbols[ENTRY], *case)
            if native != compiled:
                raise RuntimeError(f"slave-open mismatch {case}: {native} != {compiled}")
    before = names(BASE, "-u")
    defined = names(BASE, "-g", "--defined-only")
    added = {"audio_ble_pair_record_find_47ad74", "audio_ble_slave_open_fallback_4b3606",
             "audio_ble_slave_apply_record_52c244", "audio_ble_pair_record_flags_47b40c",
             "audio_ble_slave_apply_flags_52d370"}
    if ENTRY not in before or not set(PROVIDERS) - added <= defined or \
       not {"audio_ble_comm_profile_slot", "audio_ble_slave_open_flag_20074f93"} <= before | defined:
        raise RuntimeError("Apollo Main base contract changed")
    linked = OUT / "apollo-main-slave-finish-open.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), "-o", str(linked)], check=True)
    after = names(linked, "-u")
    if before - after != {ENTRY} or after - before != added:
        raise RuntimeError(f"unexpected import delta: {before-after}, {after-before}")
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_SLAVE_FINISH_OPEN_C",
               "native_elf": str(NATIVE.relative_to(ROOT)), "native_elf_sha256": sha(NATIVE),
               "native_entry": "0x4b3944", "source": str(SOURCE.relative_to(ROOT)),
               "source_sha256": sha(SOURCE), "object": str(obj.relative_to(ROOT)),
               "object_sha256": sha(obj), "base_object": str(BASE.relative_to(ROOT)),
               "base_sha256": sha(BASE), "linked_object": str(linked.relative_to(ROOT)),
               "linked_object_sha256": sha(linked), "bounded_native_c_cases": len(cases),
               "unresolved_before": len(before), "unresolved_after": len(after),
               "imports_resolved": sorted(before-after), "imports_added": sorted(after-before),
               "source_complete": False, "full_payload_linked": False,
               "limits": ["Record lookup and policy calls remain lower C contracts.",
                          "Bounded calls and RAM effects do not prove whole-image or hardware behavior.",
                          "One slave finish child remains open."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(cases), len(before), len(after), sha(path))


if __name__ == "__main__":
    main()
