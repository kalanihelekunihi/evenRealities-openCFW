#!/usr/bin/env python3
"""Compare native RGB888 and style-color call contracts (lower 24 bits)."""
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path

from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB, UC_HOOK_CODE
from unicorn import arm_const as A

ROOT = Path(__file__).resolve().parents[4]
G2 = ROOT / "g2"
SOURCE = G2 / "components/audio/uart_thread_source_candidate/display_lv_color_setters_44104c.c"
IMAGE = (G2 / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
IMAGE_SHA = "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
assert hashlib.sha256(IMAGE).hexdigest() == IMAGE_SHA
FUNCTIONS = {
    "audio_uart_page_44104c": (0x44104c, 0x441068, None),
    "audio_uart_page_44127e": (0x44127e, 0x44129e, 0x1c),
    "audio_uart_page_4412ec": (0x4412ec, 0x44130c, 0x31),
    "audio_uart_page_44140e": (0x44140e, 0x44142e, 0x58),
}
OUT = G2 / "build/c-firmware/20261015/main-lv-color-setters-44104c"
OUT.mkdir(parents=True, exist_ok=True)

with tempfile.TemporaryDirectory() as temp:
    shim = Path(temp) / "shim.c"
    shim.write_text('''#include <stdint.h>
__attribute__((naked)) void audio_uart_page_style_apply_44be4c(void*a,uint32_t b,uint32_t c,uint32_t d){__asm volatile("bx lr");}
''')
    elf = Path(temp) / "candidate.elf"
    subprocess.run(["clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-std=c11", "-ffreestanding", "-fno-builtin", "-O2",
                    "-Wall", "-Wextra", "-Werror", "-nostdlib",
                    "-Wl,-Ttext=0x100000", "-Wl,-e,audio_uart_page_44104c",
                    str(SOURCE), str(shim), "-o", str(elf)], check=True)
    with elf.open("rb") as handle:
        parsed = ELFFile(handle)
        segments = [(s["p_vaddr"], s.data()) for s in parsed.iter_segments()
                    if s["p_type"] == "PT_LOAD"]
        symbols = {s.name: s["st_value"] for s in
                   parsed.get_section_by_name(".symtab").iter_symbols()}

    def run(compiled, name, color, selector, stack_fill):
        uc = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        uc.mem_map(0x400000, 0x400000)
        uc.mem_write(0x438000, IMAGE)
        uc.mem_map(0x100000, 0x100000)
        for address, data in segments: uc.mem_write(address, data)
        uc.mem_map(0x20000000, 0x100000)
        uc.mem_write(0x200fe000, bytes([stack_fill]) * 0x1000)
        uc.reg_write(A.UC_ARM_REG_SP, 0x200ff000)
        uc.reg_write(A.UC_ARM_REG_LR, 0x600001)
        uc.reg_write(A.UC_ARM_REG_R0, color if name == "audio_uart_page_44104c" else 0x20001000)
        uc.reg_write(A.UC_ARM_REG_R1, color)
        uc.reg_write(A.UC_ARM_REG_R2, selector)
        hook_at = (symbols["audio_uart_page_style_apply_44be4c"] & ~1
                   if compiled else 0x44be4c)
        seen = []

        def observe(cpu, address, size, _):
            if address != hook_at: return
            seen.append((cpu.reg_read(A.UC_ARM_REG_R0),
                         cpu.reg_read(A.UC_ARM_REG_R1),
                         cpu.reg_read(A.UC_ARM_REG_R2) & 0x00ffffff,
                         cpu.reg_read(A.UC_ARM_REG_R3)))
            cpu.reg_write(A.UC_ARM_REG_PC, cpu.reg_read(A.UC_ARM_REG_LR))

        uc.hook_add(UC_HOOK_CODE, observe)
        start = symbols[name] if compiled else FUNCTIONS[name][0]
        uc.emu_start(start | 1, 0x600000, count=1500)
        return seen, uc.reg_read(A.UC_ARM_REG_R0) & 0x00ffffff

    cases = 0
    for name, (_, _, property_id) in FUNCTIONS.items():
        for color in (0, 1, 0x112233, 0xff000000, 0xaabbccdd, 0xffffffff):
            for selector in (0, 0x10000, 0x12345678):
                for stack_fill in (0, 0x5a):
                    native = run(False, name, color, selector, stack_fill)
                    candidate = run(True, name, color, selector, stack_fill)
                    if name == "audio_uart_page_44104c":
                        if native[1] != candidate[1]:
                            raise AssertionError((name, color, native, candidate))
                    elif native[0] != candidate[0] or \
                            native[0] != [(0x20001000, property_id,
                                           color & 0x00ffffff, selector)]:
                        raise AssertionError((name, color, selector, native, candidate))
                    cases += 1

    receipt = {"status": "PASS_NATIVE_MAIN_LV_COLOR_SETTERS_44104C",
               "source": str(SOURCE.relative_to(ROOT)),
               "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
               "official_payload_sha256": IMAGE_SHA,
               "native_body_sha256": {name: hashlib.sha256(
                   IMAGE[start-0x438000:end-0x438000]).hexdigest()
                   for name, (start, end, _) in FUNCTIONS.items()},
               "source_owned_symbols": sorted(FUNCTIONS), "cases": cases,
               "limits": ["Native wrappers leave the upper color stack byte unspecified; only the 24-bit RGB value and style-call contract were compared.",
                          "Final placement and hardware behavior remain unverified."]}
    path = OUT / "oracle-receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(receipt["status"], cases, hashlib.sha256(path.read_bytes()).hexdigest())
