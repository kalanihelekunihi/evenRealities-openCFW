#!/usr/bin/env python3
"""Validate the BLE master close guard and ordered cleanup C chain."""
import json
import subprocess
import tempfile
from pathlib import Path

from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE, UC_HOOK_MEM_WRITE
from unicorn.arm_const import UC_ARM_REG_LR, UC_ARM_REG_PC, UC_ARM_REG_R0, UC_ARM_REG_SP

from verify_main_master_dispatch_children_20261014 import image, names, sha

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/master_dispatch_candidate_20261014/close_chain.c"
NATIVE = G2 / "analysis/shortcut-arm-tools-20261009-agent3/main-analysis-only.elf"
BASE = G2 / "build/c-firmware/20261014/main-master-forward-children/apollo-main-master-forward-children.o"
OUT = G2 / "build/c-firmware/20261014/main-master-close-chain"
ENTRIES = {"audio_ble_master_child_47a5c0": 0x47a5c0,
           "audio_ble_master_child_47a47c": 0x47a47c}
CHILDREN = {"audio_ble_master_close_child_479b74": 0x479b74,
            "audio_ble_master_close_child_47b730": 0x47b730}
ROW, STOP = 0x20020000, 0x10010000


def run(segments, entry, state2f, state30):
    uc = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
    for address, size in ((0x100000, 0x100000), (0x400000, 0x400000),
                          (0x10000000, 0x20000), (0x20000000, 0x100000)):
        uc.mem_map(address, size)
    for address, data in segments:
        uc.mem_write(address, data)
    row = bytearray([0x5a] * 0x40)
    row[0x2f], row[0x30] = state2f, state30
    uc.mem_write(ROW, bytes(row))
    uc.reg_write(UC_ARM_REG_R0, ROW)
    uc.reg_write(UC_ARM_REG_SP, 0x200ff000)
    uc.reg_write(UC_ARM_REG_LR, STOP | 1)
    calls, writes = [], []
    targets = {address: name for name, address in CHILDREN.items()}

    def code_hook(cpu, address, size, _):
        if address == STOP:
            cpu.emu_stop()
        elif address in targets:
            calls.append((targets[address], cpu.reg_read(UC_ARM_REG_R0)))
            cpu.reg_write(UC_ARM_REG_PC, cpu.reg_read(UC_ARM_REG_LR))

    def write_hook(cpu, access, address, size, value, _):
        if ROW <= address < ROW + 0x40:
            writes.append((address - ROW, size, value & ((1 << (size * 8)) - 1)))

    uc.hook_add(UC_HOOK_CODE, code_hook)
    uc.hook_add(UC_HOOK_MEM_WRITE, write_hook)
    uc.emu_start(entry | 1, STOP + 2, count=500)
    return calls, writes, bytes(uc.mem_read(ROW, 0x40))


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "close_chain.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m55", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2",
                    "-Wall", "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    if names(obj, "-g", "--defined-only") != set(ENTRIES):
        raise RuntimeError("close-chain C definitions changed")
    with tempfile.TemporaryDirectory() as directory:
        trial = Path(directory) / "close.elf"
        subprocess.run(["arm-none-eabi-ld", "-Ttext=0x110000", "-e",
                        "audio_ble_master_child_47a5c0",
                        *(f"--defsym={name}={address | 1}" for name, address in CHILDREN.items()),
                        str(obj), "-o", str(trial)], check=True, capture_output=True)
        native_segments, _ = image(NATIVE)
        source_segments, symbols = image(trial)
        cases = [(name, state2f, state30) for name in ENTRIES
                 for state2f in (0, 1, 0xff) for state30 in (0, 1, 0xff)]
        for name, state2f, state30 in cases:
            native = run(native_segments, ENTRIES[name], state2f, state30)
            compiled = run(native_segments + source_segments, symbols[name], state2f, state30)
            if native != compiled:
                raise RuntimeError(f"close-chain differs: {(name, state2f, state30)} {native[:2]} {compiled[:2]}")
    before = names(BASE, "-u")
    if "audio_ble_master_child_47a5c0" not in before:
        raise RuntimeError("Main close-chain import absent")
    linked = OUT / "apollo-main-master-close-chain.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), "-o", str(linked)], check=True)
    after = names(linked, "-u")
    if len(before) != 485 or len(after) != 486 or \
       before - after != {"audio_ble_master_child_47a5c0"} or \
       after - before != set(CHILDREN):
        raise RuntimeError("unexpected Main close-chain import delta")
    receipt = {
        "status": "PASS_EXPERIMENTAL_MAIN_MASTER_CLOSE_CHAIN_C",
        "native_elf": str(NATIVE.relative_to(ROOT)), "native_elf_sha256": sha(NATIVE),
        "native_entries": {name: hex(address) for name, address in ENTRIES.items()},
        "child_contracts": {name: hex(address) for name, address in CHILDREN.items()},
        "source": str(SOURCE.relative_to(ROOT)), "source_sha256": sha(SOURCE),
        "object": str(obj.relative_to(ROOT)), "object_sha256": sha(obj),
        "base_object": str(BASE.relative_to(ROOT)), "base_sha256": sha(BASE),
        "linked_object": str(linked.relative_to(ROOT)), "linked_object_sha256": sha(linked),
        "bounded_native_c_cases": len(cases), "unresolved_before": len(before),
        "unresolved_after": len(after), "imports_resolved": sorted(before - after),
        "imports_added": sorted(after - before), "source_complete": False,
        "full_payload_linked": False,
        "limits": ["Two close-chain C bodies are verified with lower callees cut at their entries.",
                   "The two lower cleanup bodies and live BLE storage remain open."],
    }
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(cases), len(before), len(after), sha(path))


if __name__ == "__main__":
    main()
