#!/usr/bin/env python3
"""Compare native GPU position and Nema select ABI effects to C."""
import hashlib
import itertools
import json
import subprocess
import tempfile
from pathlib import Path

from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_MODE_MCLASS, UC_HOOK_CODE
from unicorn.arm_const import (UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2,
                               UC_ARM_REG_R3, UC_ARM_REG_S0, UC_ARM_REG_S1,
                               UC_ARM_REG_SP, UC_ARM_REG_LR, UC_ARM_REG_PC)

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
DIR = G2 / "components/main/ambiq_gpu_position_candidate_20261014"
SOURCES = (DIR / "position.c", DIR / "nema_select.c")
STOCK = G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
RECEIPT = Path(__file__).with_name("ambiq-gpu-position-native-results.json")
PAYLOAD = STOCK.read_bytes()[32:]
assert hashlib.sha256(STOCK.read_bytes()).hexdigest() == "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863"
ENTRIES = {
    "display_driver_gpu_position_4b1b48": (0x4b1b48, 0x4b1b83),
    "display_driver_nema_select_522a16": (0x522a16, 0x522a1f),
}

with tempfile.TemporaryDirectory(prefix="g2-gpu-position-") as folder:
    folder = Path(folder)
    stubs = folder / "stubs.s"
    stubs.write_text(".syntax unified\n.thumb\n.text\n" + "".join(
        f".global {name}\n.thumb_func\n{name}:\n bx lr\n" for name in
        ("display_driver_nema_float_translate_5228b0",
         "audio_uart_nema_mask_rectangle_522ae0",
         "audio_uart_nema_child_514846")) +
        ".bss\n.global audio_uart_ambiq_unit_cell\n"
        "audio_uart_ambiq_unit_cell: .space 4\n")
    image = folder / "candidate.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4",
                    "-mfpu=fpv4-sp-d16", "-mfloat-abi=softfp", "-mthumb",
                    "-O2", "-ffreestanding", "-fno-builtin", "-Wall", "-Wextra", "-Werror",
                    "-nostdlib", "-Wl,-Ttext=0x100000", *map(str, SOURCES),
                    str(stubs), "-o", str(image)], cwd=ROOT, check=True, capture_output=True)
    with image.open("rb") as stream:
        elf = ELFFile(stream)
        segments = [(s["p_vaddr"], s.data()) for s in elf.iter_segments() if s["p_type"] == "PT_LOAD"]
        symbols = {s.name: s["st_value"] for s in elf.get_section_by_name(".symtab").iter_symbols()}

    def run(name, native, arguments, dimensions):
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
        cpu.mem_write(0x20080054, dimensions[0].to_bytes(4, "little") +
                      dimensions[1].to_bytes(4, "little"))
        cpu.reg_write(UC_ARM_REG_SP, 0x200ff000)
        cpu.reg_write(UC_ARM_REG_LR, 0x600001)
        cpu.reg_write(UC_ARM_REG_R0, arguments[0])
        cpu.reg_write(UC_ARM_REG_R1, arguments[1])
        cuts = {
            0x5228b0 if native else symbols["display_driver_nema_float_translate_5228b0"] & ~1: "translate",
            0x522ae0 if native else symbols["audio_uart_nema_mask_rectangle_522ae0"] & ~1: "rectangle",
            0x514846 if native else symbols["audio_uart_nema_child_514846"] & ~1: "select",
        }
        events = []
        done = [False]

        def hook(uc, address, _size, _user):
            if address == 0x600000:
                done[0] = True
                uc.emu_stop()
            elif address in cuts:
                kind = cuts[address]
                if kind == "translate":
                    events.append((kind, uc.reg_read(UC_ARM_REG_S0), uc.reg_read(UC_ARM_REG_S1)))
                elif kind == "rectangle":
                    events.append((kind, *(uc.reg_read(r) for r in
                                           (UC_ARM_REG_R0, UC_ARM_REG_R1,
                                            UC_ARM_REG_R2, UC_ARM_REG_R3))))
                else:
                    events.append((kind, uc.reg_read(UC_ARM_REG_R0), uc.reg_read(UC_ARM_REG_R1)))
                uc.reg_write(UC_ARM_REG_PC, uc.reg_read(UC_ARM_REG_LR))

        cpu.hook_add(UC_HOOK_CODE, hook)
        entry = ENTRIES[name][0] if native else symbols[name]
        cpu.emu_start(entry | 1, 0, count=120)
        assert done[0], (name, native, arguments, events)
        return events, bytes(cpu.mem_read(0x20080054, 8))

    values = (0, 1, 0xffffffff, 0x01000000, 0xff000000,
              0x7fffffff, 0x80000000, 0x12345678)
    dimensions = ((0, 0), (1, 2), (0xffff, 0x80000000))
    cases = [("display_driver_gpu_position_4b1b48", (x, y), dims)
             for x, y, dims in itertools.product(values, values, dimensions)]
    cases += [("display_driver_nema_select_522a16", (color, 0), (0, 0))
              for color in (0, 1, 0xff, 0x80000000, 0xffffffff, 0x12345678)]
    for name, arguments, dims in cases:
        actual = run(name, True, arguments, dims)
        candidate = run(name, False, arguments, dims)
        assert actual == candidate, (name, arguments, dims, actual, candidate)

receipt = {
    "status": "PASS_AMBIQ_GPU_POSITION_NATIVE",
    "cases": len(cases),
    "source_sha256": {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in SOURCES},
    "stock_sha256": hashlib.sha256(STOCK.read_bytes()).hexdigest(),
    "native_bodies": {name: {"start": hex(start), "end_inclusive": hex(end),
                             "sha256": hashlib.sha256(PAYLOAD[start-0x438000:end+1-0x438000]).hexdigest()}
                      for name, (start, end) in ENTRIES.items()},
    "limits": ["Float translation, rectangle, and Nema register children are entry-cut",
               "Synthetic unit dimensions and integer coordinates cover conversion boundaries",
               "Product-state initialization, final placement, and hardware GPU behavior remain unqualified"],
}
RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n")
print(receipt["status"], receipt["cases"])
