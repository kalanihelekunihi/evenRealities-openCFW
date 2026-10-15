#!/usr/bin/env python3
"""Verify native placement sections for existing BLE subsystem arrays."""
from pathlib import Path
import hashlib
import json
import subprocess

from elftools.elf.elffile import ELFFile

root = Path(__file__).resolve().parents[3]
out = root / 'build/c-firmware/ble-subsystem-storage-round1044'
out.mkdir(parents=True, exist_ok=True)
source_dir = root / 'components/audio/uart_thread_source_candidate'
source = source_dir / 'display_ble_subsystem_storage.c'
linker = source_dir / 'display_ble_subsystem_storage.ld'
selected = root / 'build/c-firmware/ble-subsystem-state-round1043/apollo-main-ble-subsystem-state.o'
obj = out / 'display_ble_subsystem_storage.o'
probe = out / 'ble-subsystem-storage-placement.elf'
blob = (root / 'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(blob).hexdigest() == '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
def word(address):
    return int.from_bytes(blob[address - 0x438000:address - 0x438000 + 4], 'little')
expected = {
    'audio_ble_subsystem_link_state_200719c8': (0x200719c8, 0x80),
    'audio_ble_subsystem_rows_200733fc': (0x200733fc, 0x30),
}
assert word(0x4b3c8c) == expected['audio_ble_subsystem_link_state_200719c8'][0]
assert word(0x53345c) == expected['audio_ble_subsystem_rows_200733fc'][0]
subprocess.run([
    'clang', '--target=arm-none-eabi', '-mcpu=cortex-m55', '-mthumb',
    '-fshort-enums', '-std=c11', '-ffreestanding', '-fno-builtin', '-O2',
    '-Wall', '-Wextra', '-Werror', '-c', str(source), '-o', str(obj)
], check=True)
with obj.open('rb') as stream:
    elf = ELFFile(stream)
    symbols = {symbol.name: symbol for symbol in elf.get_section_by_name('.symtab').iter_symbols()}
    for name, (_, size) in expected.items():
        symbol = symbols[name]
        assert symbol['st_size'] == size
        section = elf.get_section(symbol['st_shndx'])
        assert section['sh_type'] == 'SHT_NOBITS' and '.bss.g2.ram.' in section.name
subprocess.run(['arm-none-eabi-ld', '-T', str(linker), str(obj), '-o', str(probe)], check=True)
with probe.open('rb') as stream:
    elf = ELFFile(stream)
    symbols = {symbol.name: symbol for symbol in elf.get_section_by_name('.symtab').iter_symbols()}
    for name, (address, size) in expected.items():
        symbol = symbols[name]
        assert symbol['st_value'] == address and symbol['st_size'] == size
        section = elf.get_section(symbol['st_shndx'])
        assert section['sh_type'] == 'SHT_NOBITS'

prior = json.loads((root / 'build/c-firmware/terminal-ram-placement-round1002/receipt.json').read_text())
spans = [(int(value['address'], 16), int(value['address'], 16) + value['size'], name)
         for name, value in prior['symbols'].items()]
spans += [(0x20071670, 0x2007170e, 'ble_subsystem_state_min'),
          (0x200740fc, 0x20074100, 'ble_primary_callback_slot'),
          (0x20074100, 0x20074104, 'ble_callback_slot')]
spans += [(address, address + size, name) for name, (address, size) in expected.items()]
spans.sort()
assert len(spans) == 29 and all(a[1] <= b[0] for a, b in zip(spans, spans[1:])), spans

with selected.open('rb') as stream:
    elf = ELFFile(stream)
    symbols = {symbol.name: symbol for symbol in elf.get_section_by_name('.symtab').iter_symbols()}
    selected_sections = {name: elf.get_section(symbols[name]['st_shndx']).name for name in expected}
assert all(not name.startswith('.bss.g2.ram.') for name in selected_sections.values())
receipt = {
    'round': 1044,
    'status': 'PASS_BLE_SUBSYSTEM_STORAGE_SOURCE_PLACEMENT',
    'component': 'Apollo BLE subsystem link state and discovery rows',
    'source': str(source.relative_to(root)),
    'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
    'linker': str(linker.relative_to(root)),
    'linker_sha256': hashlib.sha256(linker.read_bytes()).hexdigest(),
    'official_image_sha256': hashlib.sha256(blob).hexdigest(),
    'addresses': {name: {'address': hex(address), 'size': size} for name, (address, size) in expected.items()},
    'nonoverlap_minimum_spans_checked': len(spans),
    'probe_elf': str(probe.relative_to(root)),
    'probe_sha256': hashlib.sha256(probe.read_bytes()).hexdigest(),
    'selected_linked_object': str(selected.relative_to(root)),
    'selected_linked_sha256': hashlib.sha256(selected.read_bytes()).hexdigest(),
    'selected_sections': selected_sections,
    'whole_image_complete': False,
    'hardware_proof': False,
    'gates': ['Selected aggregate still has the historical generic BSS owner; rebuild upstream object to propagate new sections',
              'Full RAM overlap, boot initialization and hardware execution remain open'],
}
(out / 'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
print(receipt['status'], len(spans), selected_sections)
