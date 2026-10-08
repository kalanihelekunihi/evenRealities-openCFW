#!/usr/bin/env python3
"""Reject odd Thumb instruction placement, including unaligned assembly inputs.

STT_FUNC Thumb values normally have bit zero set. ARM ELF mapping symbols
($t) instead identify the actual instruction address without that tag.
"""
import argparse
import hashlib
import json
from pathlib import Path
from elftools.elf.elffile import ELFFile


def inspect(path):
    checked = []
    with path.open('rb') as stream:
        elf = ELFFile(stream)
        executable = {index: section.name for index, section in enumerate(elf.iter_sections())
                      if section['sh_flags'] & 4 and section['sh_size']}
        mapped = set()
        for symbol in elf.get_section_by_name('.symtab').iter_symbols():
            index = symbol['st_shndx']
            if not isinstance(index, int):
                continue
            section = elf.get_section(index)
            if not section['sh_flags'] & 4:
                continue
            value = symbol['st_value']
            if symbol.name == '$t' or symbol.name.startswith('$t.'):
                assert value % 2 == 0, f'odd Thumb code mapping {symbol.name} at {value:#x} in {section.name}'
                mapped.add(index)
                checked.append(dict(symbol=symbol.name, address=hex(value), section=section.name))
            elif symbol['st_info']['type'] == 'STT_FUNC':
                assert value & 1, f'missing Thumb function tag: {symbol.name} at {value:#x}'
        assert checked, 'no Thumb mapping symbols available; alignment cannot be checked'
        assert not executable.keys() - mapped, f'executable sections without Thumb mappings: {[executable[i] for i in executable.keys() - mapped]}'
    return dict(status='PASS', elf_sha256=hashlib.sha256(path.read_bytes()).hexdigest(), thumb_mappings=checked)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--elf', type=Path, required=True)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    result = inspect(args.elf)
    if args.output:
        args.output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(dict(status=result['status'], elf_sha256=result['elf_sha256'], mappings=len(result['thumb_mappings']))))
