#!/usr/bin/env python3
"""Compare native/C CCC callback event bytes and invocation."""
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
SOURCE = G2 / "components/audio/master_dispatch_candidate_20261014/atts_ccc_update.c"
NATIVE = G2 / "analysis/shortcut-arm-tools-20261009-agent3/main-analysis-only.elf"
BASE = G2 / "build/c-firmware/20261014/main-atts-ccc-init/apollo-main-atts-ccc-init.o"
OUT = G2 / "build/c-firmware/20261014/main-atts-ccc-update"
ENTRY, STATE, CALLBACK, STOP = "audio_ble_atts_ccc_update_52bb64", 0x20073b00, 0x10010020, 0x10010000


def run(segments, entry, connection, route, operation, value):
    uc = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
    for address, size in ((0x100000, 0x100000), (0x400000, 0x400000),
                          (0x10000000, 0x20000), (0x20000000, 0x100000)):
        uc.mem_map(address, size)
    for address, data in segments:
        uc.mem_write(address, data)
    uc.mem_write(STATE + 0x10, struct.pack("<I", CALLBACK | 1))
    for reg, arg in zip((UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_R3),
                        (connection, route, operation, value)):
        uc.reg_write(reg, arg)
    uc.reg_write(UC_ARM_REG_SP, 0x200ff000)
    uc.reg_write(UC_ARM_REG_LR, STOP | 1)
    callbacks = []

    def hook(cpu, address, size, _):
        if address == STOP:
            cpu.emu_stop()
        elif address == CALLBACK:
            pointer = cpu.reg_read(UC_ARM_REG_R0)
            callbacks.append(bytes(cpu.mem_read(pointer, 9)))
            cpu.reg_write(UC_ARM_REG_PC, cpu.reg_read(UC_ARM_REG_LR))

    uc.hook_add(UC_HOOK_CODE, hook)
    uc.emu_start(entry | 1, STOP + 2, count=200)
    return callbacks


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "atts_ccc_update.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                    "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    if names(obj, "-g", "--defined-only") != {ENTRY} or \
       names(obj, "-u") != {"audio_ble_atts_ccc_runtime_20073b00"}:
        raise RuntimeError("CCC callback source symbol contract changed")
    with tempfile.TemporaryDirectory() as directory:
        trial = Path(directory) / "callback.elf"
        subprocess.run(["arm-none-eabi-ld", "-Ttext=0x110000", "-e", ENTRY,
                        f"--defsym=audio_ble_atts_ccc_runtime_20073b00={STATE:#x}",
                        str(obj), "-o", str(trial)], check=True, capture_output=True)
        native_segments, _ = image(NATIVE)
        source_segments, symbols = image(trial)
        cases = [(connection, route, operation, value)
                 for connection in (0, 3, 0x123456ff)
                 for route in (0, 2, 0x123400ff)
                 for operation in (0, 0x1234, 0x12345678)
                 for value in (0, 1, 0x8001, 0x12345678)]
        for case in cases:
            native = run(native_segments, 0x52bb64, *case)
            compiled = run(native_segments + source_segments, symbols[ENTRY], *case)
            if native != compiled:
                raise RuntimeError(f"CCC callback mismatch {case}: {native} != {compiled}")
    before = names(BASE, "-u")
    if ENTRY not in before or \
       "audio_ble_atts_ccc_runtime_20073b00" not in names(BASE, "-g", "--defined-only"):
        raise RuntimeError("Apollo Main CCC callback base contract changed")
    linked = OUT / "apollo-main-atts-ccc-update.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), "-o", str(linked)], check=True)
    after = names(linked, "-u")
    if before - after != {ENTRY} or after - before:
        raise RuntimeError(f"unexpected import delta: {before-after}, {after-before}")
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_ATTS_CCC_UPDATE_C",
               "native_elf": str(NATIVE.relative_to(ROOT)), "native_elf_sha256": sha(NATIVE),
               "native_entry": "0x52bb64", "source": str(SOURCE.relative_to(ROOT)),
               "source_sha256": sha(SOURCE), "object": str(obj.relative_to(ROOT)),
               "object_sha256": sha(obj), "base_object": str(BASE.relative_to(ROOT)),
               "base_sha256": sha(BASE), "linked_object": str(linked.relative_to(ROOT)),
               "linked_object_sha256": sha(linked), "bounded_native_c_cases": len(cases),
               "unresolved_before": len(before), "unresolved_after": len(after),
               "imports_resolved": sorted(before-after), "imports_added": sorted(after-before),
               "source_complete": False, "full_payload_linked": False,
               "limits": ["Callback payload and invocation are bounded; callback internals are separate.",
                          "Absolute CCC RAM placement, whole-image and hardware behavior remain open."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(cases), len(before), len(after), sha(path))


if __name__ == "__main__":
    main()
