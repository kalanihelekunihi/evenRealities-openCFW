#!/usr/bin/env python3
"""Bounded native/C comparison for the slave-connect finish child."""
import json
import struct
import subprocess
import tempfile
from pathlib import Path

from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn.arm_const import (UC_ARM_REG_LR, UC_ARM_REG_PC, UC_ARM_REG_R0,
                               UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_R3,
                               UC_ARM_REG_SP)

from verify_main_master_dispatch_children_20261014 import image, names, sha

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/master_dispatch_candidate_20261014/slave_finish_connect.c"
NATIVE = G2 / "analysis/shortcut-arm-tools-20261009-agent3/main-analysis-only.elf"
BASE = G2 / "build/c-firmware/20261014/main-slave-finish-open/apollo-main-slave-finish-open.o"
OUT = G2 / "build/c-firmware/20261014/main-slave-finish-connect"
ENTRY = "audio_ble_slave_finish_4b39f6"
PROVIDERS = {"audio_ble_slave_record_key_4b6eea": 0x4b6eea,
             "audio_ble_slave_record_kind_4b6ed8": 0x4b6ed8,
             "audio_ble_pair_record_create_47a71c": 0x47a71c,
             "audio_ble_slave_set_features_52bacc": 0x52bacc}
MESSAGE, ROW, PROFILE, PROFILE_PTR = 0x20010000, 0x20020000, 0x20050000, 0x20074358
STATE, STOP = 0x200719c8, 0x10010000


def run(segments, entry, handle, connect, enabled, kind, policy):
    uc = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
    for address, size in ((0x100000, 0x100000), (0x400000, 0x400000),
                          (0x10000000, 0x20000), (0x20000000, 0x100000)):
        uc.mem_map(address, size)
    for address, data in segments:
        uc.mem_write(address, data)
    message = bytearray(20)
    message[4], message[6], message[7] = connect, 0x27, 0x36
    uc.mem_write(MESSAGE, bytes(message))
    row = bytearray(0x30)
    row[:4] = struct.pack("<I", handle)
    row[4], row[7], row[11] = 3, 0xa5, 0xa5
    uc.mem_write(ROW, bytes(row))
    uc.mem_write(PROFILE_PTR, struct.pack("<I", PROFILE))
    profile = bytearray(8)
    profile[:4] = bytes((enabled, policy, 0x5a, 0x93))
    uc.mem_write(PROFILE, bytes(profile))
    uc.mem_write(STATE, bytes([0xa5] * 0x80))
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
        r0, r1, r2, r3 = (cpu.reg_read(reg) for reg in
                          (UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_R3))
        if address == 0x4b6eea:
            calls.append((name, r0))
            result = 0x12345678
        elif address == 0x4b6ed8:
            calls.append((name, r0))
            result = kind
        elif address == 0x47a71c:
            calls.append((name, r0, r1, r2))
            result = 0x20043000
        else:
            fifth = struct.unpack("<I", cpu.mem_read(cpu.reg_read(UC_ARM_REG_SP), 4))[0]
            calls.append((name, r0, r1, r2, r3, fifth))
            result = 0
        cpu.reg_write(UC_ARM_REG_R0, result)
        cpu.reg_write(UC_ARM_REG_PC, cpu.reg_read(UC_ARM_REG_LR))

    uc.hook_add(UC_HOOK_CODE, hook)
    uc.emu_start(entry | 1, STOP + 2, count=1200)
    return calls, bytes(uc.mem_read(ROW, 0x30)), bytes(uc.mem_read(STATE, 0x80))


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "slave_finish_connect.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                    "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    if names(obj, "-g", "--defined-only") != {ENTRY}:
        raise RuntimeError("unexpected child source symbols")
    with tempfile.TemporaryDirectory() as directory:
        trial = Path(directory) / "connect.elf"
        subprocess.run(["arm-none-eabi-ld", "-Ttext=0x110000", "-e", ENTRY,
                        *(f"--defsym={name}={address | 1}" for name, address in PROVIDERS.items()),
                        f"--defsym=audio_ble_comm_profile_slot={PROFILE_PTR}",
                        f"--defsym=audio_ble_subsystem_link_state_200719c8={STATE}",
                        str(obj), "-o", str(trial)], check=True, capture_output=True)
        native_segments, _ = image(NATIVE)
        source_segments, symbols = image(trial)
        cases = [(handle, connect, enabled, kind, policy)
                 for handle in (0, 0x20044000) for connect in (0, 1, 2)
                 for enabled in (0, 1, 3) for kind in (0, 1, 2)
                 for policy in (0, 1, 2)]
        for case in cases:
            native = run(native_segments, 0x4b39f6, *case)
            compiled = run(native_segments + source_segments, symbols[ENTRY], *case)
            if native != compiled:
                raise RuntimeError(f"slave-connect mismatch {case}: {native} != {compiled}")
    before = names(BASE, "-u")
    added = set(PROVIDERS) - {"audio_ble_pair_record_create_47a71c"}
    if ENTRY not in before or not {"audio_ble_comm_profile_slot",
                                    "audio_ble_subsystem_link_state_200719c8"} <= before | names(BASE, "-g", "--defined-only"):
        raise RuntimeError("Apollo Main base contract changed")
    linked = OUT / "apollo-main-slave-finish-connect.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), "-o", str(linked)], check=True)
    after = names(linked, "-u")
    if before - after != {ENTRY} or after - before != added:
        raise RuntimeError(f"unexpected import delta: {before-after}, {after-before}")
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_SLAVE_FINISH_CONNECT_C",
               "native_elf": str(NATIVE.relative_to(ROOT)), "native_elf_sha256": sha(NATIVE),
               "native_entry": "0x4b39f6", "source": str(SOURCE.relative_to(ROOT)),
               "source_sha256": sha(SOURCE), "object": str(obj.relative_to(ROOT)),
               "object_sha256": sha(obj), "base_object": str(BASE.relative_to(ROOT)),
               "base_sha256": sha(BASE), "linked_object": str(linked.relative_to(ROOT)),
               "linked_object_sha256": sha(linked), "bounded_native_c_cases": len(cases),
               "unresolved_before": len(before), "unresolved_after": len(after),
               "imports_resolved": sorted(before-after), "imports_added": sorted(after-before),
               "source_complete": False, "full_payload_linked": False,
               "limits": ["Record construction and feature update remain lower C contracts.",
                          "Bounded calls and RAM effects do not prove whole-image or hardware behavior.",
                          "All eleven direct slave-finish child bodies are C-backed; downstream providers remain open."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(cases), len(before), len(after), sha(path))


if __name__ == "__main__":
    main()
