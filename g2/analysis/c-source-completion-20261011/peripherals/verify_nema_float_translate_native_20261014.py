#!/usr/bin/env python3
"""Compare full native 0x5228b0 command effects to the C provider."""
import hashlib
import itertools
import json
import struct
import subprocess
import tempfile
from pathlib import Path

from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS, UC_HOOK_CODE
from unicorn.arm_const import (UC_ARM_REG_S0, UC_ARM_REG_S1, UC_ARM_REG_R0,
                               UC_ARM_REG_R1, UC_ARM_REG_SP, UC_ARM_REG_LR,
                               UC_ARM_REG_PC)

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/main/ambiq_buffer_handlers_candidate_20261014/nema_float_translate.c"
STOCK = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
RECEIPT = Path(__file__).with_name("nema-float-translate-native-results.json")
PAYLOAD = STOCK.read_bytes()[32:]
assert hashlib.sha256(STOCK.read_bytes()).hexdigest() == "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863"


def f32(value):
    return int.from_bytes(struct.pack("<f", value), "little")


with tempfile.TemporaryDirectory(prefix="g2-nema-float-") as folder:
    folder = Path(folder)
    stubs = folder / "stubs.s"
    stubs.write_text(".syntax unified\n.thumb\n.text\n" + "".join(
        f".global {name}\n.thumb_func\n{name}:\n bx lr\n" for name in
        ("audio_uart_nema_cl_get_space_514aec", "audio_uart_nema_child_514846")))
    elf_path = folder / "candidate.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4",
                    "-mfpu=fpv4-sp-d16", "-mfloat-abi=softfp", "-mthumb",
                    "-O2", "-ffreestanding", "-fno-builtin", "-Wall", "-Wextra", "-Werror",
                    "-nostdlib", "-Wl,-Ttext=0x100000", str(SOURCE), str(stubs),
                    "-o", str(elf_path)], cwd=ROOT, check=True)
    with elf_path.open("rb") as stream:
        elf = ELFFile(stream)
        segments = [(segment["p_vaddr"], segment.data()) for segment in elf.iter_segments()
                    if segment["p_type"] == "PT_LOAD"]
        symbols = {symbol.name: symbol["st_value"] for symbol in
                   elf.get_section_by_name(".symtab").iter_symbols()}

    values = [f32(x) for x in (-4096., -2049., -2048., -2047., -1., -0., 0.,
                               1., 2047., 2048., 2049., 4096.)]
    values += [0x7f800000, 0xff800000, 0x7fc00000, 0xffc00000]
    cases = list(itertools.product(values, values, (False, True)))

    def run(native, xb, yb, allocate):
        cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
        cpu.mem_map(0x400000, 0x400000)
        cpu.mem_write(0x438000, PAYLOAD)
        cpu.mem_map(0x100000, 0x200000)
        cpu.mem_map(0x20000000, 0x100000)
        if not native:
            for address, data in segments:
                cpu.mem_write(address, data)
        cpu.mem_write(0x20090000, bytes([0xcc]) * 16)
        cpu.reg_write(UC_ARM_REG_SP, 0x200ff000)
        cpu.reg_write(UC_ARM_REG_LR, 0x600001)
        cpu.reg_write(UC_ARM_REG_S0, xb)
        cpu.reg_write(UC_ARM_REG_S1, yb)
        alloc = 0x514aec if native else symbols["audio_uart_nema_cl_get_space_514aec"] & ~1
        child = 0x514846 if native else symbols["audio_uart_nema_child_514846"] & ~1
        events = []
        done = [False]

        def hook(uc, address, _size, _user):
            if address == 0x600000:
                done[0] = True
                uc.emu_stop()
            elif address == alloc:
                events.append(("alloc", uc.reg_read(UC_ARM_REG_R0)))
                uc.reg_write(UC_ARM_REG_R0, 0x20090000 if allocate else 0)
                uc.reg_write(UC_ARM_REG_PC, uc.reg_read(UC_ARM_REG_LR))
            elif address == child:
                events.append(("child", uc.reg_read(UC_ARM_REG_R0), uc.reg_read(UC_ARM_REG_R1)))
                uc.reg_write(UC_ARM_REG_PC, uc.reg_read(UC_ARM_REG_LR))

        cpu.hook_add(UC_HOOK_CODE, hook)
        entry = 0x5228b0 if native else symbols["display_driver_nema_float_translate_5228b0"]
        cpu.emu_start(entry | 1, 0, count=120)
        assert done[0], (native, hex(xb), hex(yb), allocate, events)
        return events, bytes(cpu.mem_read(0x20090000, 16))

    for xb, yb, allocate in cases:
        actual = run(True, xb, yb, allocate)
        candidate = run(False, xb, yb, allocate)
        assert actual == candidate, (hex(xb), hex(yb), allocate, actual, candidate)

receipt = {
    "status": "PASS_NEMA_FLOAT_TRANSLATE_NATIVE",
    "cases": len(cases),
    "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
    "stock_sha256": hashlib.sha256(STOCK.read_bytes()).hexdigest(),
    "native_body_start": "0x5228b0", "native_body_end_inclusive": "0x522915",
    "native_body_sha256": hashlib.sha256(PAYLOAD[0x5228b0-0x438000:0x522916-0x438000]).hexdigest(),
    "limits": ["Allocator and child call are cut at their entry; command bytes and ordered ABI events compare",
               "Synthetic float arguments include thresholds, infinities, and quiet NaNs",
               "Real Nema command-buffer ownership and hardware execution remain unqualified"],
}
RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n")
print(receipt["status"], receipt["cases"])
