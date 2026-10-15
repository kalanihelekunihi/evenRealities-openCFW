#!/usr/bin/env python3
"""Compare Apollo GPU mode cache and two wrappers against native bytes."""
import hashlib
import itertools
import json
import subprocess
import tempfile
from pathlib import Path

from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS, UC_HOOK_CODE
from unicorn.arm_const import (UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2,
                               UC_ARM_REG_R3, UC_ARM_REG_SP, UC_ARM_REG_LR,
                               UC_ARM_REG_PC)

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/main/ambiq_gpu_mode_candidate_20261014/gpu_mode.c"
STOCK = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
RECEIPT = Path(__file__).with_name("ambiq-gpu-mode-native-results.json")
PAYLOAD = STOCK.read_bytes()[32:]
assert hashlib.sha256(STOCK.read_bytes()).hexdigest() == "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863"
ENTRIES = {
    "display_driver_gpu_mode_lower_4b06c0": (0x4b06c0, 0x4b072f),
    "display_driver_gpu_mode_4b0730": (0x4b0730, 0x4b0747),
    "display_driver_gpu_enable_4b0748": (0x4b0748, 0x4b075d),
}

with tempfile.TemporaryDirectory(prefix="g2-gpu-mode-") as folder:
    folder = Path(folder)
    stubs = folder / "stubs.s"
    stubs.write_text(".syntax unified\n.thumb\n.text\n" + "".join(
        f".global {name}\n.thumb_func\n{name}:\n bx lr\n" for name in
        ("audio_uart_ambiq_default_unit_4c791a", "display_driver_nema_mode_513924")))
    image = folder / "candidate.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-O2", "-ffreestanding", "-fno-builtin", "-Wall", "-Wextra", "-Werror",
                    "-nostdlib", "-Wl,-Ttext=0x100000", str(SOURCE), str(stubs),
                    "-o", str(image)], cwd=ROOT, check=True, capture_output=True)
    with image.open("rb") as stream:
        elf = ELFFile(stream)
        segments = [(s["p_vaddr"], s.data()) for s in elf.iter_segments() if s["p_type"] == "PT_LOAD"]
        symbols = {s.name: s["st_value"] for s in elf.get_section_by_name(".symtab").iter_symbols()}

    def run(name, native, args, cached):
        cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
        cpu.mem_map(0x400000, 0x400000)
        cpu.mem_write(0x438000, PAYLOAD)
        cpu.mem_map(0x100000, 0x200000)
        cpu.mem_map(0x20000000, 0x100000)
        if not native:
            for address, data in segments:
                cpu.mem_write(address, data)
        for base in (0x20080000, 0x20081000):
            cpu.mem_write(base + 0x50, cached[0].to_bytes(4, "little") +
                          bytes(cached[1:]) + b"\xaa")
        cpu.reg_write(UC_ARM_REG_SP, 0x200ff000)
        cpu.reg_write(UC_ARM_REG_LR, 0x600001)
        for reg, value in zip((UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_R3), args):
            cpu.reg_write(reg, value)
        cpu.mem_write(0x200ff000, args[4].to_bytes(4, "little") + args[5].to_bytes(4, "little"))
        default = 0x4c791a if native else symbols["audio_uart_ambiq_default_unit_4c791a"] & ~1
        child = 0x513924 if native else symbols["display_driver_nema_mode_513924"] & ~1
        events = []
        done = [False]

        def hook(uc, address, _size, _user):
            if address == 0x600000:
                done[0] = True
                uc.emu_stop()
            elif address == default:
                events.append(("default",))
                uc.reg_write(UC_ARM_REG_R0, 0x20080000)
                uc.reg_write(UC_ARM_REG_PC, uc.reg_read(UC_ARM_REG_LR))
            elif address == child:
                events.append(("mode", *(uc.reg_read(r) for r in
                                          (UC_ARM_REG_R0, UC_ARM_REG_R1,
                                           UC_ARM_REG_R2, UC_ARM_REG_R3))))
                uc.reg_write(UC_ARM_REG_PC, uc.reg_read(UC_ARM_REG_LR))

        cpu.hook_add(UC_HOOK_CODE, hook)
        entry = ENTRIES[name][0] if native else symbols[name]
        cpu.emu_start(entry | 1, 0, count=150)
        assert done[0], (name, native, args, events)
        return events, tuple(bytes(cpu.mem_read(base + 0x50, 8)) for base in
                             (0x20080000, 0x20081000))

    cases = []
    for unit, mode, a, b, c, force, cached in itertools.product(
        (0, 0x20081000), (0, 1, 0x504, 0x8000504),
        (0, 0x100), (0xffffffff, 1), (0xffffffff, 0x80),
        (0, 1, 0x100), ((0, 0, 0, 0), (0x504, 0, 0xff, 0xff))):
        if len(cases) >= 384:
            break
        cases.append(("display_driver_gpu_mode_lower_4b06c0",
                      (unit, mode, a, b, c, force), cached))
    for name in ("display_driver_gpu_mode_4b0730", "display_driver_gpu_enable_4b0748"):
        for unit, mode, cached in itertools.product(
            (0, 0x20081000), (0, 0x504, 0x8000504),
            ((0, 0, 0, 0), (0x504, 0, 0xff, 0xff))):
            cases.append((name, (unit, mode, 0, 0, 0, 0), cached))
    for name, args, cached in cases:
        actual = run(name, True, args, cached)
        candidate = run(name, False, args, cached)
        assert actual == candidate, (name, args, cached, actual, candidate)

receipt = {
    "status": "PASS_AMBIQ_GPU_MODE_NATIVE",
    "cases": len(cases),
    "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
    "stock_sha256": hashlib.sha256(STOCK.read_bytes()).hexdigest(),
    "native_bodies": {name: {"start": hex(start), "end_inclusive": hex(end),
                             "sha256": hashlib.sha256(PAYLOAD[start-0x438000:end+1-0x438000]).hexdigest()}
                      for name, (start, end) in ENTRIES.items()},
    "limits": ["Default-unit and Nema-mode children are entry-cut; cache bytes and ordered ABI calls compare",
               "Wrapper return registers are unspecified by their C callers and excluded",
               "Synthetic state excludes concurrency and hardware GPU behavior"],
}
RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n")
print(receipt["status"], receipt["cases"])
