#!/usr/bin/env python3
"""Bind the remaining two byte-exact Apollo radio ROM literals."""
from pathlib import Path
import hashlib
import json
import re
import subprocess

from elftools.elf.elffile import ELFFile

root = Path(__file__).resolve().parents[3]
out = root / 'build/c-firmware/radio-rom-tail-round1038'
out.mkdir(parents=True, exist_ok=True)
source = root / 'analysis/c-source-completion-20261011/peripherals/root-rom-radio-tail-round425/radio_tail.c'
base = root / 'build/c-firmware/hci-rom-tables-round1037/apollo-main-hci-rom-tables.o'
obj = out / 'radio_tail.o'
linked = out / 'apollo-main-radio-rom-tail.o'
blob = (root / 'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(blob).hexdigest() == '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
entries = re.findall(
    r'/\* Stock 0x([0-9a-f]+); (\d+) bytes including NUL\. \*/\s*'
    r'const uint8_t ([A-Za-z_][A-Za-z_0-9]*)\[\]', source.read_text()
)
assert len(entries) == 2, len(entries)
subprocess.run([
    'clang', '--target=arm-none-eabi', '-mcpu=cortex-m55', '-mthumb',
    '-fshort-enums', '-std=c11', '-ffreestanding', '-fno-builtin', '-O2',
    '-Wall', '-Wextra', '-Werror', '-c', str(source), '-o', str(obj)
], check=True)
with obj.open('rb') as stream:
    elf = ELFFile(stream)
    symbols = {s.name: s for s in elf.get_section_by_name('.symtab').iter_symbols()}
    for address_text, size_text, name in entries:
        address, size = int(address_text, 16), int(size_text)
        symbol = symbols[name]
        assert symbol['st_size'] == size, (name, symbol['st_size'], size)
        section = elf.get_section(symbol['st_shndx'])
        assert section.name == '.rodata', (name, section.name)
        actual = section.data()[symbol['st_value']:symbol['st_value'] + size]
        native = blob[address - 0x438000:address - 0x438000 + size]
        assert len(actual) == size and actual == native, name

def imports(path):
    return {line.split()[-1] for line in subprocess.check_output(
        ['arm-none-eabi-nm', '-u', str(path)], text=True).splitlines()}

before = imports(base)
names = {name for _, _, name in entries}
assert names <= before, sorted(names - before)
subprocess.run(['arm-none-eabi-ld', '-r', str(base), str(obj), '-o', str(linked)], check=True)
after = imports(linked)
assert before - after == names and not after - before, (sorted(before - after), sorted(after - before))
receipt = {
    'round': 1038,
    'status': 'PASS_EXACT_RADIO_ROM_TAIL_BINDING',
    'component': 'Apollo radio tail literals',
    'source': str(source.relative_to(root)),
    'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
    'official_image_sha256': hashlib.sha256(blob).hexdigest(),
    'literal_count': len(entries),
    'linked_object': str(linked.relative_to(root)),
    'linked_sha256': hashlib.sha256(linked.read_bytes()).hexdigest(),
    'unresolved_before': len(before),
    'unresolved_after': len(after),
    'whole_image_complete': False,
    'hardware_proof': False,
    'gates': ['Original ROM placement is not established by the relocatable object',
              'Full image layout and hardware operation remain open'],
}
(out / 'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
print(receipt['status'], len(before), len(after), receipt['linked_sha256'])
