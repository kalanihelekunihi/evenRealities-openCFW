#!/usr/bin/env python3
"""Compare native GPU blit stride, state, and command writes to C."""
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
SOURCE = G2 / "components/main/ambiq_gpu_blit_candidate_20261014/gpu_blit.c"
STOCK = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
RECEIPT = Path(__file__).with_name("ambiq-gpu-blit-native-results.json")
PAYLOAD = STOCK.read_bytes()[32:]
assert hashlib.sha256(STOCK.read_bytes()).hexdigest() == "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863"

with tempfile.TemporaryDirectory(prefix="g2-gpu-blit-") as folder:
    folder = Path(folder)
    stubs = folder / "stubs.s"
    stubs.write_text(".syntax unified\n.thumb\n.text\n"
                     ".global audio_uart_nema_cl_get_space_514aec\n.thumb_func\n"
                     "audio_uart_nema_cl_get_space_514aec:\n bx lr\n"
                     ".bss\n.global audio_uart_ambiq_unit_cell\n"
                     "audio_uart_ambiq_unit_cell: .space 4\n")
    image = folder / "candidate.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-O2", "-ffreestanding", "-fno-builtin", "-Wall", "-Wextra", "-Werror",
                    "-nostdlib", "-Wl,-Ttext=0x100000", str(SOURCE), str(stubs),
                    "-o", str(image)], cwd=ROOT, check=True, capture_output=True)
    with image.open("rb") as stream:
        elf = ELFFile(stream)
        segments = [(s["p_vaddr"], s.data()) for s in elf.iter_segments() if s["p_type"] == "PT_LOAD"]
        symbols = {s.name: s["st_value"] for s in elf.get_section_by_name(".symtab").iter_symbols()}

    def run(native, args, allocate):
        cpu = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
        cpu.mem_map(0x400000, 0x400000)
        cpu.mem_write(0x438000, PAYLOAD)
        cpu.mem_map(0x100000, 0x200000)
        cpu.mem_map(0x20000000, 0x100000)
        if not native:
            for address, data in segments:
                cpu.mem_write(address, data)
        cell = 0x20074efc if native else symbols["audio_uart_ambiq_unit_cell"]
        cpu.mem_write(cell, (0x20080000).to_bytes(4, "little"))
        cpu.mem_write(0x20080050, bytes([0xcc]) * 24)
        cpu.mem_write(0x20090000, bytes([0xdd]) * 24)
        cpu.reg_write(UC_ARM_REG_SP, 0x200ff000)
        cpu.reg_write(UC_ARM_REG_LR, 0x600001)
        for reg, value in zip((UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_R3), args):
            cpu.reg_write(reg, value)
        cpu.mem_write(0x200ff000, args[4].to_bytes(4, "little") + args[5].to_bytes(4, "little"))
        allocator = 0x514aec if native else symbols["audio_uart_nema_cl_get_space_514aec"] & ~1
        events = []
        done = [False]

        def hook(uc, address, _size, _user):
            if address == 0x600000:
                done[0] = True
                uc.emu_stop()
            elif address == allocator:
                events.append(("alloc", uc.reg_read(UC_ARM_REG_R0)))
                uc.reg_write(UC_ARM_REG_R0, 0x20090000 if allocate else 0)
                uc.reg_write(UC_ARM_REG_PC, uc.reg_read(UC_ARM_REG_LR))

        cpu.hook_add(UC_HOOK_CODE, hook)
        entry = 0x4b1608 if native else symbols["display_driver_gpu_blit_4b1608"]
        cpu.emu_start(entry | 1, 0, count=400)
        assert done[0], (native, args, events)
        return (events, bytes(cpu.mem_read(0x20080050, 24)),
                bytes(cpu.mem_read(0x20090000, 24)))

    cases = []
    for kind, width, flags, allocate in itertools.product(
        range(0x80), (0, 1, 3, 7, 0x7fffffff), (0, 0x10), (False, True)):
        cases.append(((0x20084000, width, 0x12345, kind | 0x100, 0xffffffff, flags), allocate))
    for kind, width, stride, allocate in itertools.product(
        range(0x80), (2, 640), (0, 17), (False, True)):
        cases.append(((0x20084000, width, 0x23456, kind, stride, 0x100), allocate))
    for width in (0x80000000, 0xffffffff, 0x12345678):
        for kind in (0x0b, 0x12, 0x16, 0x28, 0x29, 0x39, 0x4c, 0x4e, 0x7f):
            cases.append(((0, width, 0xffffffff, kind, 0xffffffff, 0x10), True))
    for args, allocate in cases:
        actual = run(True, args, allocate)
        candidate = run(False, args, allocate)
        assert actual == candidate, (args, allocate, actual, candidate)

RANGES = ((0x4b1608, 0x4b166f), (0x4b16b4, 0x4b16f1), (0x4b173e, 0x4b178b))
receipt = {
    "status": "PASS_AMBIQ_GPU_BLIT_NATIVE",
    "cases": len(cases),
    "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
    "stock_sha256": hashlib.sha256(STOCK.read_bytes()).hexdigest(),
    "native_body_ranges": [[hex(a), hex(b)] for a, b in RANGES],
    "native_body_sha256": hashlib.sha256(b"".join(PAYLOAD[a-0x438000:b+1-0x438000] for a, b in RANGES)).hexdigest(),
    "limits": ["Allocator is entry-cut; state and command bytes compare against native execution",
               "Synthetic format, width, stride and allocation cases include all low-seven-bit format values",
               "Live GPU ownership, concurrent state changes, final placement and hardware remain unqualified"],
}
RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n")
print(receipt["status"], receipt["cases"])
