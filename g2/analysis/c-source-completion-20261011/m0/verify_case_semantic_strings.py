#!/usr/bin/env python3
"""Verify all named CASE semantic strings in an independently linked C ELF."""
from pathlib import Path
import argparse, hashlib, json, re
from elftools.elf.elffile import ELFFile

H = Path(__file__).resolve().parent
R = H.parents[3]
rows = json.loads((H / 'case-semantic-strings.json').read_text())['rows']
parser = argparse.ArgumentParser()
parser.add_argument('elf', type=Path)
parser.add_argument('--allow-gc', action='store_true')
args = parser.parse_args()
with args.elf.open('rb') as fp:
    elf = ELFFile(fp)
    symbols = {s.name: s['st_value'] for s in elf.get_section_by_name('.symtab').iter_symbols()}
    segments = [(p['p_vaddr'], p.data()) for p in elf.iter_segments() if p['p_type'] == 'PT_LOAD']
def at(address, size):
    for base, data in segments:
        if base <= address and address + size <= base + len(data):
            return data[address - base:address - base + size]
    raise AssertionError(hex(address))
verified = 0
for row in rows:
    suffix = row['native_address'][2:]
    symbol = 'case_string_' + suffix
    if symbol not in symbols and args.allow_gc:
        continue
    assert symbol in symbols, symbol
    data = at(symbols[symbol], row['length_with_nul'])
    assert data == row['semantic_text'].encode('ascii') + b'\0', symbol
    assert hashlib.sha256(data).hexdigest() == row['sha256_with_nul'], symbol
    verified += 1
component = R / 'g2/components/case'
remaining = set()
for source in component.rglob('*.c'):
    if 'semantic_strings_candidate_20261011' in source.parts:
        continue
    remaining |= {int(x[:-1], 16) for x in re.findall(r'0x0800[0-9A-Fa-f]{4}u', source.read_text())}
assert not remaining.intersection(int(r['native_address'], 16) for r in rows)
print('PASS_CASE_SEMANTIC_STRINGS', verified, 'of', len(rows),
      'remaining_nonstring_absolute_addresses', len(remaining))
