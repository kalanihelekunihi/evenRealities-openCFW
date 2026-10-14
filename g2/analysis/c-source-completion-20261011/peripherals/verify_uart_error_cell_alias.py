#!/usr/bin/env python3
"""Compare native/C locale range error writes and check one shared C cell."""
from pathlib import Path
import struct
import subprocess
import tempfile

from elftools.elf.elffile import ELFFile
from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB
from unicorn.arm_const import UC_ARM_REG_LR, UC_ARM_REG_SP

ROOT = Path(__file__).resolve().parents[3]
BLOB = (ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin").read_bytes()[32:]
HERE = ROOT / "components/audio/uart_thread_source_candidate"
with tempfile.TemporaryDirectory() as directory:
    shim = Path(directory) / "shim.c"
    shim.write_text("#include <stdint.h>\nuint8_t audio_uart_ring_locale_dispatch_200044c0[0x30];\n")
    elf_path = Path(directory) / "candidate.elf"
    subprocess.run(["/usr/bin/clang", "--target=arm-none-eabi", "-mcpu=cortex-m4", "-mthumb",
                    "-O2", "-nostdlib", "-Wl,-Ttext=0x100000",
                    "-Wl,-e,audio_uart_ring_errno_range_set_439cb2",
                    str(HERE / "display_ring_locale_dispatch.c"),
                    str(HERE / "display_uart_error_cell.c"), str(shim),
                    "-o", str(elf_path)], check=True)
    with elf_path.open("rb") as stream:
        elf = ELFFile(stream)
        symbols = {s.name: s["st_value"] for s in elf.get_section_by_name(".symtab").iter_symbols()}
        segments = [(s["p_vaddr"], s.data()) for s in elf.iter_segments() if s["p_type"] == "PT_LOAD"]
    assert symbols["audio_uart_float_math_error_cell_20074f14"] == \
           symbols["audio_uart_ring_errno_20074f14"]
    observed = []
    for compiled in (False, True):
        uc = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
        uc.mem_map(0x400000, 0x400000)
        uc.mem_write(0x438000, BLOB)
        uc.mem_map(0x100000, 0x100000)
        uc.mem_map(0x20000000, 0x100000)
        for address, data in segments:
            uc.mem_write(address, data)
        cell = symbols["audio_uart_ring_errno_20074f14"] if compiled else 0x20074f14
        uc.mem_write(cell, struct.pack("<I", 0x12345678))
        uc.reg_write(UC_ARM_REG_SP, 0x200ff000)
        uc.reg_write(UC_ARM_REG_LR, 0x600001)
        entry = symbols["audio_uart_ring_errno_range_set_439cb2"] if compiled else 0x439cb2
        uc.emu_start(entry | 1, 0x600000, count=100)
        observed.append(bytes(uc.mem_read(cell, 4)))
    assert observed == [struct.pack("<I", 0x22)] * 2, observed
print("PASS_UART_ERROR_CELL_ALIAS", observed[0].hex())
