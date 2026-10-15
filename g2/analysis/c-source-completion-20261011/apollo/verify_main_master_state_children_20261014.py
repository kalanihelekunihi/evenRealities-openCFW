#!/usr/bin/env python3
"""Verify two BLE master state child bodies and compose them into Main."""
import json
import struct
import subprocess
import tempfile
from pathlib import Path

from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_LR, UC_ARM_REG_PC, UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_SP

from verify_main_master_dispatch_children_20261014 import image, names, sha

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/master_dispatch_candidate_20261014/children_state.c"
NATIVE = G2 / "analysis/shortcut-arm-tools-20261009-agent3/main-analysis-only.elf"
BASE = G2 / "build/c-firmware/20261014/main-master-dispatch-children/apollo-main-master-children.o"
OUT = G2 / "build/c-firmware/20261014/main-master-state-children"
ENTRIES = {"audio_ble_master_event_503880": 0x503880,
           "audio_ble_master_event_50389e": 0x50389e}
SETTER = 0x47b4ce
MESSAGE, ROW, STOP = 0x20010000, 0x20020000, 0x10010000


def run(segments, entry, status, handle, null_row):
    uc = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
    for address, size in ((0x100000, 0x100000), (0x400000, 0x400000),
                          (0x10000000, 0x20000), (0x20000000, 0x100000)):
        uc.mem_map(address, size)
    for address, data in segments:
        uc.mem_write(address, data)
    message = bytearray(16)
    message[3] = status
    uc.mem_write(MESSAGE, bytes(message))
    row = bytearray([0x5a] * 0x30)
    row[:4] = struct.pack("<I", handle)
    uc.mem_write(ROW, bytes(row))
    uc.reg_write(UC_ARM_REG_R0, MESSAGE)
    uc.reg_write(UC_ARM_REG_R1, 0 if null_row else ROW)
    uc.reg_write(UC_ARM_REG_SP, 0x200ff000)
    uc.reg_write(UC_ARM_REG_LR, STOP | 1)
    calls = []

    def hook(cpu, address, size, _):
        if address == STOP:
            cpu.emu_stop()
        elif address == SETTER:
            calls.append((cpu.reg_read(UC_ARM_REG_R0), cpu.reg_read(UC_ARM_REG_R1)))
            cpu.reg_write(UC_ARM_REG_PC, cpu.reg_read(UC_ARM_REG_LR))

    uc.hook_add(UC_HOOK_CODE, hook)
    uc.emu_start(entry | 1, STOP + 2, count=500)
    return calls, bytes(uc.mem_read(ROW, 0x30))


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "children_state.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m55", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2",
                    "-Wall", "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    if names(obj, "-g", "--defined-only") != set(ENTRIES):
        raise RuntimeError("state child C definitions changed")
    with tempfile.TemporaryDirectory() as directory:
        trial = Path(directory) / "state.elf"
        subprocess.run(["arm-none-eabi-ld", "-Ttext=0x110000", "-e",
                        "audio_ble_master_event_503880",
                        f"--defsym=audio_ble_connection_state_set_47b4ce={SETTER | 1}",
                        str(obj), "-o", str(trial)], check=True, capture_output=True)
        native_segments, _ = image(NATIVE)
        source_segments, symbols = image(trial)
        cases = [(name, status, handle, null_row)
                 for name in ENTRIES for status in (0, 1, 0x80)
                 for handle in (0, 0x20012000, 0xffffffff)
                 for null_row in (False, True)
                 if not (name.endswith("50389e") and null_row)]
        for name, status, handle, null_row in cases:
            native = run(native_segments, ENTRIES[name], status, handle, null_row)
            compiled = run(native_segments + source_segments, symbols[name],
                           status, handle, null_row)
            if native != compiled:
                raise RuntimeError(f"state child differs: {(name, status, handle, null_row)} {native} {compiled}")
    before = names(BASE, "-u")
    if not set(ENTRIES) <= before or "audio_ble_connection_state_set_47b4ce" not in names(BASE, "-g", "--defined-only"):
        raise RuntimeError("Main state child contracts changed")
    linked = OUT / "apollo-main-master-state-children.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), "-o", str(linked)], check=True)
    after = names(linked, "-u")
    if len(before) != 487 or len(after) != 485 or before - after != set(ENTRIES) or after - before:
        raise RuntimeError("unexpected Main state child import delta")
    receipt = {
        "status": "PASS_EXPERIMENTAL_MAIN_MASTER_STATE_CHILDREN_C",
        "native_elf": str(NATIVE.relative_to(ROOT)), "native_elf_sha256": sha(NATIVE),
        "native_entries": {name: hex(address) for name, address in ENTRIES.items()},
        "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
        "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj),
        "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
        "linked_object": str(linked.relative_to(ROOT)), "linked_object_sha256": sha(linked),
        "bounded_native_c_cases": len(cases), "unresolved_before": len(before),
        "unresolved_after": len(after), "imports_resolved": sorted(before - after),
        "imports_added": [], "source_complete": False, "full_payload_linked": False,
        "limits": ["The state setter is cut in bounded cases, though its C body is already linked in Main.",
                   "Other BLE master child handlers and live radio behavior remain open."],
    }
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(cases), len(before), len(after), sha(path))


if __name__ == "__main__":
    main()
