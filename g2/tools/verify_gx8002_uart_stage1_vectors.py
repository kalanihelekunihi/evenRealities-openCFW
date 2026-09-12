#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Decoded-target check for the UART boot stage-1 vectors/traps (CD-001).

Assembles components/shared/gx8002/runtime_gx8002_uart_stage1_vectors.S
(clean-room table + trap entries, no upstream text), links the vector
table at its real runtime address 0x10000000 and the traps at
0x10000130, and checks three claims:

1. The linked 256-byte table is byte-exact against the stock envelope
   at package 0x50..0x150, and the linked 8-byte traps are byte-exact
   against the stock envelope at package 0x180..0x188.
2. Structure, read back from the linked image rather than assumed: the
   table is word0 == reset-entry symbol address, words 1..31 == the
   exception-trap symbol address, words 32..63 == the IRQ-trap symbol
   address, where those addresses are the linker's own symbol values.
3. Each trap cell decodes as a branch-to-self (`br` whose target is its
   own address) followed by a zero pad halfword, and single-stepping
   the decoded `br` twice returns to the same PC (infinite wait loop).

The reset-entry address itself (0x10000100) remains a linker-supplied
absolute: its contents are reconstructed by the reset tranche, not here.
"""
import json
import struct
import subprocess
from pathlib import Path

from analyze_gx8002_upstream_objects import (
    IMAGE,
    IMAGE_SHA,
    sha,
)
from build_transparent_image import Elf32
from verify_gx8002_memcpy_source import decode

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'components/shared/gx8002/runtime_gx8002_uart_stage1_vectors.S'
NOTICE = ROOT / 'components/shared/gx8002/NATIONALCHIP-UART-BOOT-STAGE1-VECTORS-NOTICE.txt'
ASM_FLAGS = ['-mcpu=ck804ef', '-mhard-float']

VECTORS_ADDRESS = 0x10000000
VECTORS_OFFSET = 0x50
VECTORS_SIZE = 256
TRAPS_ADDRESS = 0x10000130
TRAPS_OFFSET = 0x180
TRAPS_SIZE = 8
RESET_ENTRY = 0x10000100

LINKER_SCRIPT = '''SECTIONS {{
  .rodata.open_cfw_gx8002_uart_stage1_vectors {vectors:#x} : {{ *(.rodata.open_cfw_gx8002_uart_stage1_vectors) }}
  .text.open_cfw_gx8002_uart_stage1_traps {traps:#x} : {{ *(.text.open_cfw_gx8002_uart_stage1_traps) }}
}}
open_cfw_gx8002_uart_stage1_reset_entry = {reset:#x};
'''

# (symbol, section, runtime address, package offset, stock bytes, ownership).
SPECS = [
    ('open_cfw_gx8002_uart_stage1_vectors',
     '.rodata.open_cfw_gx8002_uart_stage1_vectors',
     VECTORS_ADDRESS, VECTORS_OFFSET, VECTORS_SIZE, 'generated_source_data'),
    ('open_cfw_gx8002_uart_stage1_traps',
     '.text.open_cfw_gx8002_uart_stage1_traps',
     TRAPS_ADDRESS, TRAPS_OFFSET, TRAPS_SIZE, 'compiled_assembly'),
]


def symbol_addresses(elf):
    values = {}
    for entry in elf.symbols():
        if entry['name'] in ('open_cfw_gx8002_uart_stage1_reset_entry',
                             'open_cfw_gx8002_uart_stage1_exc_trap',
                             'open_cfw_gx8002_uart_stage1_irq_trap'):
            values[entry['name']] = entry['value']
    return values


def verify(prefix=None, sdk=None, output=None):
    output = output or ROOT / 'build/gx8002-uart-stage1-vectors'
    output.mkdir(parents=True, exist_ok=True)
    prefix = prefix or ROOT / 'build/csky-macos/install/bin'
    obj = output / 'vectors.o'
    subprocess.run([str(prefix / 'csky-unknown-elf-as'), *ASM_FLAGS,
                    str(SOURCE), '-o', str(obj)], check=True)
    script = output / 'vectors.ld'
    script.write_text(LINKER_SCRIPT.format(vectors=VECTORS_ADDRESS,
                                           traps=TRAPS_ADDRESS,
                                           reset=RESET_ENTRY))
    elf_path = output / 'vectors.elf'
    subprocess.run([str(prefix / 'csky-unknown-elf-ld'), '-T', str(script),
                    str(obj), '-o', str(elf_path)], check=True)
    elf = Elf32(elf_path.read_bytes(), str(elf_path))
    if any(s['name'] and s['section'] == 0 for s in elf.symbols()):
        raise ValueError('undefined target symbol')
    stock = IMAGE.read_bytes()
    if sha(stock) != IMAGE_SHA:
        raise ValueError('stock identity changed')
    addresses = symbol_addresses(elf)
    if (addresses.get('open_cfw_gx8002_uart_stage1_reset_entry') != RESET_ENTRY
            or addresses.get('open_cfw_gx8002_uart_stage1_exc_trap') != TRAPS_ADDRESS
            or addresses.get('open_cfw_gx8002_uart_stage1_irq_trap') != TRAPS_ADDRESS + 4):
        raise ValueError('trap symbols not at their linked envelope: %r' % (addresses,))
    disassembly = subprocess.check_output(
        [str(prefix / 'csky-unknown-elf-objdump'), '-d', str(elf_path)], text=True)
    (output / 'vectors.disassembly.txt').write_text(disassembly)
    functions = []
    cases = 0
    for symbol, section_name, entry, offset, size, ownership in SPECS:
        section = next(s for s in elf.sections if s['name'] == section_name)
        payload = elf.contents(section)
        if len(payload) != size:
            raise ValueError('candidate size changed the envelope: ' + symbol)
        if offset % section['align']:
            raise ValueError('candidate misaligned for placement: ' + symbol)
        if elf.relocations(section['index']):
            raise ValueError('unexpected relocation: ' + symbol)
        if payload != stock[offset:offset + size]:
            raise ValueError('linked bytes are not byte-exact stock: ' + symbol)
        cases += 1
    # Structural claim 2: the table words are the linker's own symbol values.
    vectors = next(s for s in elf.sections
                   if s['name'] == '.rodata.open_cfw_gx8002_uart_stage1_vectors')
    words = struct.unpack('<64I', elf.contents(vectors))
    if words[0] != RESET_ENTRY:
        raise ValueError('table word 0 is not the reset entry')
    if any(word != TRAPS_ADDRESS for word in words[1:32]):
        raise ValueError('table words 1..31 are not the exception trap')
    if any(word != TRAPS_ADDRESS + 4 for word in words[32:64]):
        raise ValueError('table words 32..63 are not the IRQ trap')
    cases += 1
    # Structural claim 3: each trap cell is br-to-self plus a zero pad,
    # and stepping the decoded branch twice returns to the same PC.
    traps = next(s for s in elf.sections
                 if s['name'] == '.text.open_cfw_gx8002_uart_stage1_traps')
    raw = elf.contents(traps)
    decoded = decode(subprocess.check_output(
        [str(prefix / 'csky-unknown-elf-objdump'), '-d',
         '--start-address=%#x' % TRAPS_ADDRESS,
         '--stop-address=%#x' % (TRAPS_ADDRESS + TRAPS_SIZE),
         str(elf_path)], text=True))
    for cell in (TRAPS_ADDRESS, TRAPS_ADDRESS + 4):
        op, operand, width = decoded[cell]
        if op != 'br' or int(operand, 0) != cell or width != 2:
            raise ValueError('trap cell is not br-to-self at %#x' % cell)
        pad = struct.unpack_from('<H', raw, cell - TRAPS_ADDRESS + 2)[0]
        if pad != 0:
            raise ValueError('trap pad is not zero fill at %#x' % cell)
        pc = cell
        for _ in range(2):
            op, operand, _ = decoded[pc]
            pc = int(operand, 0)
        if pc != cell:
            raise ValueError('trap does not loop at %#x' % cell)
        cases += 1
    for symbol, section_name, entry, offset, size, ownership in SPECS:
        section = next(s for s in elf.sections if s['name'] == section_name)
        payload = elf.contents(section)
        functions.append({'symbol': symbol, 'compiled_bytes': len(payload),
                          'compiled_sha256': sha(payload),
                          'section_name': section_name,
                          'ownership_kind': ownership,
                          'stock_occurrences': [{'symbol': symbol, 'package_offset': offset,
                                                 'bytes': size,
                                                 'sha256': sha(stock[offset:offset + size]),
                                                 'region': 'uart_boot_stage1'}]})
    report = {'s_source_sha256': sha(SOURCE.read_bytes()),
              'notice_sha256': sha(NOTICE.read_bytes()),
              'assemble_flags': ASM_FLAGS,
              'link_addresses': {'vectors': VECTORS_ADDRESS, 'traps': TRAPS_ADDRESS,
                                 'reset_entry': RESET_ENTRY},
              'functions': functions, 'target_cases': cases, 'source_admitted': True,
              'admission_scope': 'experimental hybrid codec; UART boot stage-1 '
                                 'vector table and trap entries only',
              'stock_equivalence_proven': False,
              'limits': ['Byte-exact linked-image equivalence over the two '
                         'envelopes plus structural symbol checks; no processor '
                         'emulation beyond single-stepping the two decoded '
                         'self-branches. Hardware timing remains unqualified.']}
    (output / 'verification.json').write_text(json.dumps(report, indent=2) + '\n')
    print(cases)
    return report


if __name__ == '__main__':
    (ROOT / 'docs/research/gx8002-uart-stage1-vectors-verification.json').write_text(
        json.dumps(verify(), indent=2) + '\n')
    print(json.dumps(json.loads(
        (ROOT / 'docs/research/gx8002-uart-stage1-vectors-verification.json').read_text()),
        indent=2))
