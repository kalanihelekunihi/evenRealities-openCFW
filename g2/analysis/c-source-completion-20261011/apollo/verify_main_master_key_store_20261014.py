#!/usr/bin/env python3
"""Compare AppDbSetKey state and provider calls with native 0x47aed4."""
import json
import re
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
SOURCE = G2 / "components/audio/master_dispatch_candidate_20261014/key_store.c"
NATIVE = G2 / "analysis/shortcut-arm-tools-20261009-agent3/main-analysis-only.elf"
BASE = G2 / "build/c-firmware/20261014/main-master-close-provider-aliases/apollo-main-master-close-provider-aliases.o"
OUT = G2 / "build/c-firmware/20261014/main-master-key-store"
ENTRY, RECORD, MESSAGE, STOP = 0x47aed4, 0x20043000, 0x20044000, 0x10010000
FLAGS = 0x43d0ce
EXTENDED, COMPRESSED = 0x43d574, 0x43ce9e
PROVIDERS = {"audio_queue_copy_bytes": 0x439be4,
             "audio_ble_copy_address6_4d293c": 0x4d293c,
             "audio_ble_privacy_rewrite_record": 0x479b74,
             "audio_ble_pair_record_validate": 0x47b730}


def run(segments, entry, key_type, valid, mask, flags):
    uc = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
    for address, size in ((0x100000, 0x100000), (0x400000, 0x400000),
                          (0x10000000, 0x20000), (0x20000000, 0x100000)):
        uc.mem_map(address, size)
    for address, data in segments:
        uc.mem_write(address, data)
    row = bytearray([0x5a] * 0x100)
    row[0x2e], row[0x30] = mask, valid
    message = bytearray((i * 7 + 3) & 0xff for i in range(0x40))
    message[0x1e], message[0x1f] = key_type, 3
    uc.mem_write(RECORD, bytes(row))
    uc.mem_write(MESSAGE, bytes(message))
    uc.reg_write(UC_ARM_REG_R0, RECORD)
    uc.reg_write(UC_ARM_REG_R1, MESSAGE)
    uc.reg_write(UC_ARM_REG_SP, 0x200ff000)
    uc.reg_write(UC_ARM_REG_LR, STOP | 1)
    calls = []
    targets = {address: name for name, address in PROVIDERS.items()}

    def string(cpu, address):
        return bytes(cpu.mem_read(address, 256)).split(b"\0", 1)[0].decode("ascii")

    def arity(fmt):
        return len(re.findall(r"%(?!%)(?:0?\d*)[A-Za-z]", fmt))

    def code_hook(cpu, address, size, _):
        if address == STOP:
            cpu.emu_stop()
            return
        if address == FLAGS:
            cpu.reg_write(UC_ARM_REG_R0, flags)
            cpu.reg_write(UC_ARM_REG_PC, cpu.reg_read(UC_ARM_REG_LR))
            return
        if address == EXTENDED:
            sp = cpu.reg_read(UC_ARM_REG_SP)
            r0, r1, r2, r3 = (cpu.reg_read(reg) for reg in
                              (UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_R3))
            line, fmt = (int.from_bytes(cpu.mem_read(sp + i, 4), "little") for i in (0, 4))
            text = string(cpu, fmt)
            args = tuple(int.from_bytes(cpu.mem_read(sp + 8 + i * 4, 4), "little")
                         for i in range(arity(text)))
            calls.append(("extended", r0, string(cpu, r1), string(cpu, r2),
                          string(cpu, r3), line, text, args))
            cpu.reg_write(UC_ARM_REG_PC, cpu.reg_read(UC_ARM_REG_LR))
            return
        if address == COMPRESSED:
            sp = cpu.reg_read(UC_ARM_REG_SP)
            r0, r1, r2, r3 = (cpu.reg_read(reg) for reg in
                              (UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_R3))
            text = string(cpu, r1)
            args = (r3,) + tuple(int.from_bytes(cpu.mem_read(sp + i * 4, 4), "little")
                                 for i in range(max(arity(text) - 1, 0)))
            calls.append(("compressed", r0, text, string(cpu, r2),
                          args[:arity(text)]))
            cpu.reg_write(UC_ARM_REG_PC, cpu.reg_read(UC_ARM_REG_LR))
            return
        if address not in targets:
            return
        name = targets[address]
        r0, r1, r2 = (cpu.reg_read(reg) for reg in
                      (UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2))
        if address in (0x439be4, 0x4d293c):
            length = r2 if address == 0x439be4 else 6
            calls.append((name, r0, r1, length))
            cpu.mem_write(r0, bytes(cpu.mem_read(r1, length)))
        else:
            calls.append((name, r0))
        cpu.reg_write(UC_ARM_REG_R0, 0)
        cpu.reg_write(UC_ARM_REG_PC, cpu.reg_read(UC_ARM_REG_LR))

    uc.hook_add(UC_HOOK_CODE, code_hook)
    uc.emu_start(entry | 1, STOP + 2, count=10000)
    return calls, bytes(uc.mem_read(RECORD, 0x100))


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "key_store.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m55", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                    "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    if names(obj, "-g", "--defined-only") != {"audio_ble_master_child_47aed4"}:
        raise RuntimeError("AppDbSetKey C definition changed")
    with tempfile.TemporaryDirectory() as directory:
        trial = Path(directory) / "key_store.elf"
        subprocess.run(["arm-none-eabi-ld", "-Ttext=0x110000", "-e",
                        "audio_ble_master_child_47aed4",
                        *(f"--defsym={name}={address | 1}" for name, address in PROVIDERS.items()),
                        f"--defsym=audio_log_flags={FLAGS | 1}",
                        f"--defsym=audio_log_extended={EXTENDED | 1}",
                        f"--defsym=compressed_log_output={COMPRESSED | 1}",
                        str(obj), "-o", str(trial)], check=True, capture_output=True)
        native_segments, _ = image(NATIVE)
        source_segments, symbols = image(trial)
        cases = [(key_type, valid, mask, flags)
                 for key_type in (0, 1, 2, 3, 4, 8, 0xff)
                 for valid in (0, 1, 2) for mask in (0, 2, 0xff)
                 for flags in (0, 1, 2, 4, 7)]
        for args in cases:
            native = run(native_segments, ENTRY, *args)
            compiled = run(native_segments + source_segments,
                           symbols["audio_ble_master_child_47aed4"], *args)
            if native != compiled:
                raise RuntimeError(f"AppDbSetKey differs: {args} {native[0]} {compiled[0]}")
    before = names(BASE, "-u")
    if "audio_ble_master_child_47aed4" not in before:
        raise RuntimeError("Main AppDbSetKey import absent")
    linked = OUT / "apollo-main-master-key-store.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), "-o", str(linked)], check=True)
    after = names(linked, "-u")
    if len(before) != 481 or len(after) != 480 or \
       before - after != {"audio_ble_master_child_47aed4"} or after - before:
        raise RuntimeError("unexpected Main key-store import delta")
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_MASTER_KEY_STORE_C",
               "native_elf": str(NATIVE.relative_to(ROOT)), "native_elf_sha256": sha(NATIVE),
               "native_entry": hex(ENTRY), "source": str(SOURCE.relative_to(ROOT)),
               "source_sha256": sha(SOURCE), "object": str(obj.relative_to(ROOT)),
               "object_sha256": sha(obj), "base_object": str(BASE.relative_to(ROOT)),
               "base_sha256": sha(BASE), "linked_object": str(linked.relative_to(ROOT)),
               "linked_object_sha256": sha(linked), "bounded_native_c_cases": len(cases),
               "unresolved_before": len(before), "unresolved_after": len(after),
               "imports_resolved": sorted(before - after), "source_complete": False,
               "full_payload_linked": False,
               "limits": ["Diagnostic branches are compared at provider ABI, including varargs; output formatting itself remains separate.",
                          "Copy, MRAM rewrite, and validation calls are intercepted at provider entries.",
                          "Whole-image layout and physical pairing remain open."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(cases), len(before), len(after), sha(path))


if __name__ == "__main__":
    main()
