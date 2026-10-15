#!/usr/bin/env python3
"""Bounded native/C comparison for Apollo Main pair-state writes at 0x47a49c."""
import json
import struct
import subprocess
import tempfile
from pathlib import Path

from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE, UC_HOOK_MEM_WRITE
from unicorn.arm_const import UC_ARM_REG_LR, UC_ARM_REG_PC, UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_R3, UC_ARM_REG_SP

from verify_main_master_dispatch_children_20261014 import image, names, sha

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/master_dispatch_candidate_20261014/pair_state.c"
NATIVE = G2 / "analysis/shortcut-arm-tools-20261009-agent3/main-analysis-only.elf"
BASE = G2 / "build/c-firmware/20261014/main-master-pair-child/apollo-main-master-pair-child.o"
OUT = G2 / "build/c-firmware/20261014/main-master-pair-state"
ENTRY, RECORD, COUNTER, STOP = 0x47a49c, 0x20043000, 0x20074344, 0x10010000
CALLEES = {"audio_ble_privacy_rewrite_record": 0x479b74,
           "audio_ble_pair_record_validate": 0x47b730}
FLAGS, EXTENDED, COMPRESSED = 0x43d0ce, 0x43d574, 0x43ce9e


def run(segments, entry, mode, initial, flags, saved):
    uc = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
    for address, size in ((0x100000, 0x100000), (0x400000, 0x400000),
                          (0x10000000, 0x20000), (0x20000000, 0x100000)):
        uc.mem_map(address, size)
    for address, data in segments:
        uc.mem_write(address, data)
    uc.mem_write(RECORD, bytes([0x5a] * 0x100))
    uc.mem_write(COUNTER, struct.pack("<I", initial))
    uc.reg_write(UC_ARM_REG_R0, RECORD)
    uc.reg_write(UC_ARM_REG_R1, mode)
    uc.reg_write(UC_ARM_REG_SP, 0x200ff000)
    uc.reg_write(UC_ARM_REG_LR, STOP | 1)
    calls, writes = [], []
    targets = {value: name for name, value in CALLEES.items()}

    def string(cpu, address):
        return bytes(cpu.mem_read(address, 180)).split(b"\0", 1)[0].decode("ascii")

    def code_hook(cpu, address, size, _):
        if address == STOP:
            cpu.emu_stop()
        elif address == FLAGS:
            cpu.reg_write(UC_ARM_REG_R0, flags)
            cpu.reg_write(UC_ARM_REG_PC, cpu.reg_read(UC_ARM_REG_LR))
        elif address == EXTENDED:
            sp = cpu.reg_read(UC_ARM_REG_SP)
            line, fmt, value = struct.unpack("<III", bytes(cpu.mem_read(sp, 12)))
            calls.append(("extended", cpu.reg_read(UC_ARM_REG_R0),
                          string(cpu, cpu.reg_read(UC_ARM_REG_R1)),
                          string(cpu, cpu.reg_read(UC_ARM_REG_R2)),
                          string(cpu, cpu.reg_read(UC_ARM_REG_R3)), line,
                          string(cpu, fmt), value if line != 0x2d3 else None))
            cpu.reg_write(UC_ARM_REG_PC, cpu.reg_read(UC_ARM_REG_LR))
        elif address == COMPRESSED:
            calls.append(("compressed", cpu.reg_read(UC_ARM_REG_R0),
                          string(cpu, cpu.reg_read(UC_ARM_REG_R1)),
                          string(cpu, cpu.reg_read(UC_ARM_REG_R2)),
                          cpu.reg_read(UC_ARM_REG_R3) if
                          cpu.reg_read(UC_ARM_REG_R0) == 0x10400000 else None))
            cpu.reg_write(UC_ARM_REG_PC, cpu.reg_read(UC_ARM_REG_LR))
        elif address in targets:
            calls.append((targets[address], cpu.reg_read(UC_ARM_REG_R0)))
            cpu.reg_write(UC_ARM_REG_R0, saved if address == 0x479b74 else 0)
            cpu.reg_write(UC_ARM_REG_PC, cpu.reg_read(UC_ARM_REG_LR))

    def write_hook(cpu, access, address, size, value, _):
        if RECORD <= address < RECORD + 0x100 or address == COUNTER:
            writes.append((address, size, value & ((1 << (size * 8)) - 1)))

    uc.hook_add(UC_HOOK_CODE, code_hook)
    uc.hook_add(UC_HOOK_MEM_WRITE, write_hook)
    uc.emu_start(entry | 1, STOP + 2, count=600)
    return calls, writes, bytes(uc.mem_read(RECORD, 0x100)), bytes(uc.mem_read(COUNTER, 4))


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    obj = OUT / "pair_state.o"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m55", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2", "-Wall",
                    "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(obj)], check=True)
    if names(obj, "-g", "--defined-only") != {"audio_ble_master_pair_state_47a49c"}:
        raise RuntimeError("pair-state C definition changed")
    with tempfile.TemporaryDirectory() as directory:
        trial = Path(directory) / "pair_state.elf"
        subprocess.run(["arm-none-eabi-ld", "-Ttext=0x110000", "-e",
                        "audio_ble_master_pair_state_47a49c",
                        *(f"--defsym={name}={address | 1}" for name, address in CALLEES.items()),
                        f"--defsym=audio_log_flags={FLAGS | 1}",
                        f"--defsym=audio_log_extended={EXTENDED | 1}",
                        f"--defsym=compressed_log_output={COMPRESSED | 1}",
                        f"--defsym=audio_ble_pair_timestamp_counter_20074344={COUNTER}",
                        str(obj), "-o", str(trial)], check=True, capture_output=True)
        native_segments, _ = image(NATIVE)
        source_segments, symbols = image(trial)
        cases = [(mode, count, flags, saved)
                 for mode in (0, 1, 4, 0xff)
                 for count in (0, 0xfffffffe)
                 for flags in (0, 1, 2, 4, 7)
                 for saved in (0, 1)]
        for args in cases:
            native = run(native_segments, ENTRY, *args)
            compiled = run(native_segments + source_segments,
                           symbols["audio_ble_master_pair_state_47a49c"], *args)
            if native != compiled:
                raise RuntimeError(f"pair-state differs: {args} {native[:2]} {compiled[:2]}")
    before = names(BASE, "-u")
    if "audio_ble_master_pair_state_47a49c" not in before:
        raise RuntimeError("Main pair-state import absent")
    linked = OUT / "apollo-main-master-pair-state.o"
    subprocess.run(["arm-none-eabi-ld", "-r", str(BASE), str(obj), "-o", str(linked)], check=True)
    after = names(linked, "-u")
    if before - after != {"audio_ble_master_pair_state_47a49c"} or after - before:
        raise RuntimeError("unexpected Main pair-state import delta")
    receipt = {"status": "PASS_EXPERIMENTAL_MAIN_MASTER_PAIR_STATE_C",
               "native_elf": str(NATIVE.relative_to(ROOT)), "native_elf_sha256": sha(NATIVE),
               "native_entry": hex(ENTRY), "source": str(SOURCE.relative_to(ROOT)),
               "source_sha256": sha(SOURCE), "object": str(obj.relative_to(ROOT)),
               "object_sha256": sha(obj), "base_object": str(BASE.relative_to(ROOT)),
               "base_sha256": sha(BASE), "linked_object": str(linked.relative_to(ROOT)),
               "linked_object_sha256": sha(linked), "bounded_native_c_cases": len(cases),
               "unresolved_before": len(before), "unresolved_after": len(after),
               "imports_resolved": sorted(before - after), "source_complete": False,
               "full_payload_linked": False,
               "limits": ["Provider calls are intercepted; their internals are separate contracts.",
                          "Diagnostic calls are compared at the provider ABI; pairing on hardware remains unqualified."]}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], len(cases), len(before), len(after), sha(path))


if __name__ == "__main__":
    main()
