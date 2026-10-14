#!/usr/bin/env python3
"""Validate the current exploratory Bootloader link and all vector slots."""
import argparse
import hashlib
import json
import re
import struct
import subprocess
from pathlib import Path
from elftools.elf.elffile import ELFFile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
parser = argparse.ArgumentParser()
parser.add_argument('--elf', type=Path, required=True)
parser.add_argument('--output', type=Path, required=True)
parser.add_argument('--build-receipt', type=Path, required=True)
args = parser.parse_args()
build = json.loads(args.build_receipt.read_text())['images']['apollo_bootloader']
selected_symbols = set(build['relocatable_link']['defined_symbols'])
nm = subprocess.check_output(['arm-none-eabi-nm', '-g', '--defined-only', str(args.elf)], text=True)
linked_symbols = {line.split()[-1] for line in nm.splitlines() if line.split()}
unretained_symbols = sorted(selected_symbols - linked_symbols)
stock = (ROOT / 'g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin').read_bytes()
assert hashlib.sha256(stock).hexdigest() == 'f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5'
vector_source = ROOT / 'g2/components/bootloader/startup/vectors.S'
entries = []
for line in vector_source.read_text().splitlines():
    match = re.match(r'\s*\.word\s+(\S+)\s+/\* vector (\d+) \*/', line)
    if match:
        assert int(match.group(2)) == len(entries)
        entries.append(match.group(1))
assert len(entries) == 256
with args.elf.open('rb') as stream:
    elf = ELFFile(stream)
    assert elf.elfclass == 32 and elf.little_endian and elf['e_machine'] == 'EM_ARM'
    symtab = elf.get_section_by_name('.symtab')
    symbols = {s.name: s['st_value'] for s in symtab.iter_symbols() if s.name}
    flash = [p for p in elf.iter_segments() if p['p_type'] == 'PT_LOAD' and p['p_vaddr'] == 0x410000]
    assert len(flash) == 1
    segment = flash[0]
    assert segment['p_paddr'] == 0x410000 and segment['p_filesz'] == segment['p_memsz']
    end = segment['p_vaddr'] + segment['p_memsz']
    assert end <= 0x437fe0
    linked = segment.data()[:1024]
    assert len(linked) == 1024
    assert symbols['opencfw_boot_vectors'] == 0x410000
    assert symbols['opencfw_boot_reset_entry'] == elf['e_entry']
    source_words = struct.unpack('<256I', linked)
    stock_words = struct.unpack('<256I', stock[:1024])
    assert source_words[0] == stock_words[0] == 0x2007fb00
    names = set()
    zero_slots = []
    for index, (declaration, current, native) in enumerate(zip(entries, source_words, stock_words)):
        if index == 0:
            continue
        if declaration == '0':
            assert current == native == 0, index
            zero_slots.append(index)
        else:
            assert declaration in symbols, (index, declaration)
            assert current == symbols[declaration], (index, declaration, hex(current), hex(symbols[declaration]))
            assert current & 1 and native & 1, index
            assert 0x410000 <= (current & ~1) < end, (index, hex(current))
            names.add(declaration)
    assert source_words[1] == elf['e_entry']
    report = {'status': 'PASS_CURRENT_EXPLORATORY_BOOT_VECTOR_AND_FLASH_FIT',
              'stock_sha256': hashlib.sha256(stock).hexdigest(),
              'linked_elf_sha256': hashlib.sha256(args.elf.read_bytes()).hexdigest(),
              'vector_source_sha256': hashlib.sha256(vector_source.read_bytes()).hexdigest(),
              'flash_start': hex(segment['p_vaddr']), 'flash_end_exclusive': hex(end),
              'preamble_start': '0x437fe0', 'remaining_bytes_before_preamble': 0x437fe0 - end,
              'flash_load_bytes': segment['p_filesz'],
              'vector_words': 256, 'zero_vector_slots': zero_slots,
              'named_handler_count': len(names), 'named_handlers': sorted(names),
              'linked_reset_entry': hex(elf['e_entry']),
              'selected_relocatable_definitions': len(selected_symbols),
              'retained_selected_global_symbols': len(selected_symbols & linked_symbols),
              'unretained_selected_global_symbols': unretained_symbols,
              'limits': ['The stock and source handler addresses differ by design; this verifies structure and linked symbol ownership, not byte identity.',
                         'Garbage collection discards selected providers without a live root; the unretained list is not itself proof those bodies are missing or unnecessary.',
                         'The linker script is exploratory and does not prove all load/run scatter destinations or nonvector code/data coverage.',
                         'Resident ROM timing, startup execution and hardware behavior remain unverified.']}
args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
print(report['status'], report['flash_load_bytes'], report['remaining_bytes_before_preamble'])
