#!/usr/bin/env python3
"""Bind source-derived HCI tables after checking every represented ROM byte."""
from pathlib import Path
import hashlib
import json
import subprocess

from elftools.elf.elffile import ELFFile

root = Path(__file__).resolve().parents[3]
out = root / 'build/c-firmware/hci-rom-tables-round1037'
out.mkdir(parents=True, exist_ok=True)
base = root / 'build/c-firmware/radio-rom-literals-round1036/apollo-main-radio-rom-literals.o'
linked = out / 'apollo-main-hci-rom-tables.o'
blob = (root / 'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(blob).hexdigest() == '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
tables = [
    ('root-hci-event-sizes-round427/event_sizes.c', 'audio_ble_hci_event_sizes_6e3720', 0x6e3720, 86),
    ('root-dm-hci-route-table-round429/dm_hci_route_table.c', 'audio_ble_dm_hci_event_class_map_6e006c', 0x6e006c, 90),
]
objects = []
sources = []
for relative, name, address, size in tables:
    source = root / 'analysis/c-source-completion-20261011/peripherals' / relative
    obj = out / (source.stem + '.o')
    subprocess.run([
        'clang', '--target=arm-none-eabi', '-mcpu=cortex-m55', '-mthumb',
        '-fshort-enums', '-std=c11', '-ffreestanding', '-fno-builtin', '-O2',
        '-Wall', '-Wextra', '-Werror', '-c', str(source), '-o', str(obj)
    ], check=True)
    with obj.open('rb') as stream:
        elf = ELFFile(stream)
        symbol = next(s for s in elf.get_section_by_name('.symtab').iter_symbols() if s.name == name)
        assert symbol['st_size'] == size, (name, symbol['st_size'], size)
        section = elf.get_section(symbol['st_shndx'])
        assert section.name == '.rodata', (name, section.name)
        actual = section.data()[symbol['st_value']:symbol['st_value'] + size]
        native = blob[address - 0x438000:address - 0x438000 + size]
        assert len(actual) == size and actual == native, name
    objects.append(obj)
    sources.append(source)

def imports(path):
    return {line.split()[-1] for line in subprocess.check_output(
        ['arm-none-eabi-nm', '-u', str(path)], text=True).splitlines()}

before = imports(base)
names = {name for _, name, _, _ in tables}
assert names <= before, sorted(names - before)
subprocess.run(['arm-none-eabi-ld', '-r', str(base), *map(str, objects), '-o', str(linked)], check=True)
after = imports(linked)
assert before - after == names and not after - before, (sorted(before - after), sorted(after - before))
receipt = {
    'round': 1037,
    'status': 'PASS_HCI_ROM_TABLES_BINDING',
    'component': 'Apollo HCI event sizes and DM event class map',
    'sources': [{'path': str(s.relative_to(root)), 'sha256': hashlib.sha256(s.read_bytes()).hexdigest()} for s in sources],
    'official_image_sha256': hashlib.sha256(blob).hexdigest(),
    'byte_counts': {name: size for _, name, _, size in tables},
    'linked_object': str(linked.relative_to(root)),
    'linked_sha256': hashlib.sha256(linked.read_bytes()).hexdigest(),
    'unresolved_before': len(before),
    'unresolved_after': len(after),
    'whole_image_complete': False,
    'hardware_proof': False,
    'gates': ['The 86th HCI size byte matches ROM but its original allocation extent remains unproved',
              'Exact original ROM placement and full image link remain open'],
}
(out / 'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
print(receipt['status'], len(before), len(after), receipt['linked_sha256'])
