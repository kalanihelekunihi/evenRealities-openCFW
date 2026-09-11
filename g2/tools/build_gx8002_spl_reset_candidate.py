#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Compile and link the image-A SPL boot header/vectors and reset chain.

Two independent translation units are linked into one small standalone ELF:
the generated BINH header + 64-word vector table (data, no instructions) and
the reset entry / default trap handler / unreachable clear_bss stub (C-SKY
assembly derived from the public NationalChip lvp_kws spl_start.S). Both are
placed at their real package/runtime addresses so the vector table's two
targets resolve to this build's own function addresses with no leftover
relocations, and so the compiled bytes can be compared directly against the
authenticated stock image.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

from build_transparent_image import Elf32

ROOT = Path(__file__).resolve().parents[1]
COMPONENT = ROOT / 'components/shared/gx8002'
HEADER_SOURCE = COMPONENT / 'runtime_gx8002_image_a_stage1_header.c'
ENTRY_SOURCE = COMPONENT / 'runtime_gx8002_spl_reset_entry.S'
IMAGE = ROOT / 'blobs/official/g2-2.2.6.10/firmware_codec.bin'
IMAGE_SHA = 'b06dfef7faa2f1e52d2aacd07958d4b96ffc36dca5077ac9149e48f19fc9c4d0'

# Package/runtime placement (see docs/research/gx8002-spl-stage1-reset-source.md).
HEADER_PACKAGE_OFFSET = 0x0000958C
HEADER_SIZE = 280
ENTRY_PACKAGE_OFFSET = 0x000096A4
ENTRY_SIZE = 54
IRAM_BASE = 0x10000000
ENTRY_ADDRESS = IRAM_BASE + 0x100          # open_cfw_gx8002_spl_reset_entry
DEFAULT_HANDLER_ADDRESS = IRAM_BASE + 0x130
SPL_BOARD_INIT_R_ADDRESS = IRAM_BASE + 0xACC  # retained; external call boundary
STAGE2_RESET_ENTRY_ADDRESS = 0x10023500       # open_cfw_gx8002_reset_entry (already source-owned)
SPL_INITIAL_STACK = 0x20002FFC                # CONFIG_STAGE1_STACK (public SDK name)

C_FLAGS = ['-O2', '-mcpu=ck804ef', '-mhard-float', '-ffreestanding', '-fno-builtin',
           '-ffunction-sections', '-fdata-sections', '-Wall', '-Wextra', '-Werror']
ASM_FLAGS = ['-mcpu=ck804ef', '-mhard-float']

LINKER_SCRIPT = '''SECTIONS {{
  .rodata.header {header:#x} : {{ *(.rodata.open_cfw_gx8002_image_a_stage1_header) }}
  .text {entry:#x} : {{
    *(.text.open_cfw_gx8002_spl_reset_entry)
    *(.text.open_cfw_gx8002_spl_default_handler)
    *(.text.open_cfw_gx8002_spl_clear_bss)
  }}
}}
open_cfw_gx8002_spl_vectors = {vectors:#x};
open_cfw_gx8002_spl_initial_stack = {stack:#x};
open_cfw_gx8002_spl_board_init_r = {board_init:#x};
open_cfw_gx8002_reset_entry = {stage2_entry:#x};
'''


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def build(prefix: Path | None = None, output: Path | None = None) -> dict:
    prefix = prefix or ROOT / 'build/csky-macos/install/bin'
    output = output or ROOT / 'build/continue-analysis/CD-008'
    output.mkdir(parents=True, exist_ok=True)
    gcc, ld = str(prefix / 'csky-unknown-elf-gcc'), str(prefix / 'csky-unknown-elf-ld')

    header_obj = output / 'spl-header.o'
    subprocess.run([gcc, *C_FLAGS, '-I', str(COMPONENT), '-c', str(HEADER_SOURCE),
                     '-o', str(header_obj)], check=True, capture_output=True, text=True)
    entry_obj = output / 'spl-entry.o'
    subprocess.run([gcc, *ASM_FLAGS, '-c', str(ENTRY_SOURCE), '-o', str(entry_obj)],
                    check=True, capture_output=True, text=True)

    script = output / 'spl-reset.ld'
    script.write_text(LINKER_SCRIPT.format(
        header=HEADER_PACKAGE_OFFSET, entry=ENTRY_ADDRESS, vectors=IRAM_BASE,
        stack=SPL_INITIAL_STACK, board_init=SPL_BOARD_INIT_R_ADDRESS,
        stage2_entry=STAGE2_RESET_ENTRY_ADDRESS))
    elf_path = output / 'spl-reset.elf'
    subprocess.run([ld, '-T', str(script), str(entry_obj), str(header_obj), '-o', str(elf_path)],
                    check=True, capture_output=True, text=True)

    elf = Elf32(elf_path.read_bytes(), str(elf_path))
    header_section = next(s for s in elf.sections if s['name'] == '.rodata.header')
    text_section = next(s for s in elf.sections if s['name'] == '.text')
    if elf.relocations(header_section['index']) or elf.relocations(text_section['index']):
        raise ValueError('unresolved relocation in linked SPL reset candidate')
    if any(sym['name'] and sym['section'] == 0 for sym in elf.symbols()):
        raise ValueError('undefined target symbol in linked SPL reset candidate')
    header_bytes, entry_bytes = elf.contents(header_section), elf.contents(text_section)
    if len(header_bytes) != HEADER_SIZE or len(entry_bytes) != ENTRY_SIZE:
        raise ValueError('SPL reset candidate envelope changed')

    stock = IMAGE.read_bytes()
    if sha(stock) != IMAGE_SHA:
        raise ValueError('codec baseline changed')
    stock_header = stock[HEADER_PACKAGE_OFFSET:HEADER_PACKAGE_OFFSET + HEADER_SIZE]
    stock_entry = stock[ENTRY_PACKAGE_OFFSET:ENTRY_PACKAGE_OFFSET + ENTRY_SIZE]

    (output / 'spl-reset.disassembly.txt').write_text(
        subprocess.check_output([str(prefix / 'csky-unknown-elf-objdump'), '-dr', str(elf_path)],
                                 text=True))

    return {
        'header_bytes': header_bytes, 'entry_bytes': entry_bytes,
        'header_byte_exact': header_bytes == stock_header,
        'entry_byte_exact': entry_bytes == stock_entry,
        'header_sha256': sha(header_bytes), 'entry_sha256': sha(entry_bytes),
        'elf_path': str(elf_path), 'disassembly_path': str(output / 'spl-reset.disassembly.txt'),
    }


if __name__ == '__main__':
    result = build()
    print(json.dumps({k: v for k, v in result.items() if not k.endswith('_bytes')}, indent=2))
    if not (result['header_byte_exact'] and result['entry_byte_exact']):
        raise SystemExit('SPL reset candidate is not byte-exact against stock')
