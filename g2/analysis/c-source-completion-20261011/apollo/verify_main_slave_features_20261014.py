#!/usr/bin/env python3
"""Compare native and C slave feature packet construction."""
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
SOURCE = G2 / "components/audio/master_dispatch_candidate_20261014/slave_features.c"
NATIVE = G2 / "analysis/shortcut-arm-tools-20261009-agent3/main-analysis-only.elf"
BASE = G2 / "build/c-firmware/20261014/main-pair-record-lookup/apollo-main-pair-record-lookup.o"
OUT = G2 / "build/c-firmware/20261014/main-slave-features"
ENTRY = "audio_ble_slave_set_features_52bacc"
PROVIDERS = {"audio_ble_message_alloc_4bf99e": 0x4bf99e,
             "audio_ble_message_send_537bd6": 0x537bd6}
PACKET, STOP = 0x20050000, 0x10010000


def run(segments, entry, allocated, connection, event, policy, flags, supported):
    uc = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
    for address, size in ((0x100000, 0x100000), (0x400000, 0x400000),
                          (0x10000000, 0x20000), (0x20000000, 0x100000)):
        uc.mem_map(address, size)
    for address, data in segments:
        uc.mem_write(address, data)
    uc.mem_write(PACKET, b"\xa5" * 8)
    sp = 0x200ff000
    uc.mem_write(sp, struct.pack("<I", supported))
    for reg, value in zip((UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_R3),
                          (connection, event, policy, flags)):
        uc.reg_write(reg, value)
    uc.reg_write(UC_ARM_REG_SP, sp)
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
        if address == 0x4bf99e:
            calls.append((name, cpu.reg_read(UC_ARM_REG_R0)))
            cpu.reg_write(UC_ARM_REG_R0, PACKET if allocated else 0)
        else:
            pointer = cpu.reg_read(UC_ARM_REG_R0)
            calls.append((name, pointer, bytes(cpu.mem_read(pointer, 8))))
            cpu.reg_write(UC_ARM_REG_R0, 0)
        cpu.reg_write(UC_ARM_REG_PC, cpu.reg_read(UC_ARM_REG_LR))

    uc.hook_add(UC_HOOK_CODE, hook)
    uc.emu_start(entry | 1, STOP + 2, count=500)
    return calls, bytes(uc.mem_read(PACKET, 8))


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "slave_features.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                    "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    if names(obj, "-g", "--defined-only") != {ENTRY} or \
       names(obj, "-u") != set(PROVIDERS):
        raise RuntimeError("slave feature C symbol contract changed")
    with tempfile.TemporaryDirectory() as directory:
        trial = Path(directory) / "features.elf"
        subprocess.run(["arm-none-eabi-ld", "-Ttext=0x110000", "-e", ENTRY,
                        *(f"--defsym={name}={address | 1}" for name, address in PROVIDERS.items()),
                        str(obj), "-o", str(trial)], check=True, capture_output=True)
        native_segments, _ = image(NATIVE)
        source_segments, symbols = image(trial)
        cases = [(allocated, connection, event, policy, flags, supported)
                 for allocated in (0, 1) for connection in (0, 1, 0x123456ff)
                 for event in (0, 0x83) for policy in (0, 0xa7)
                 for flags in (0, 7, 0x123456fa)
                 for supported in (0, 7, 0xabcdef04)]
        for case in cases:
            native = run(native_segments, 0x52bacc, *case)
            compiled = run(native_segments + source_segments, symbols[ENTRY], *case)
            if native != compiled:
                raise RuntimeError(f"slave feature mismatch {case}: {native} != {compiled}")
    before = names(BASE, "-u")
    if ENTRY not in before:
        raise RuntimeError("Apollo Main slave feature import changed")
    linked = OUT / "apollo-main-slave-features.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), "-o", str(linked)], check=True)
    after = names(linked, "-u")
    if before - after != {ENTRY} or after - before != set(PROVIDERS):
        raise RuntimeError(f"unexpected import delta: {before-after}, {after-before}")
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_SLAVE_FEATURES_C",
               "native_elf": str(NATIVE.relative_to(ROOT)), "native_elf_sha256": sha(NATIVE),
               "native_entry": "0x52bacc", "source": str(SOURCE.relative_to(ROOT)),
               "source_sha256": sha(SOURCE), "object": str(obj.relative_to(ROOT)),
               "object_sha256": sha(obj), "base_object": str(BASE.relative_to(ROOT)),
               "base_sha256": sha(BASE), "linked_object": str(linked.relative_to(ROOT)),
               "linked_object_sha256": sha(linked), "bounded_native_c_cases": len(cases),
               "unresolved_before": len(before), "unresolved_after": len(after),
               "imports_resolved": sorted(before-after), "imports_added": sorted(after-before),
               "source_complete": False, "full_payload_linked": False,
               "limits": ["Allocator and message-send providers remain separate lower contracts.",
                          "Packet bytes and call order are bounded; whole-image and hardware behavior remain open."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(cases), len(before), len(after), sha(path))


if __name__ == "__main__":
    main()
