#!/usr/bin/env python3
"""Audit current source-coherent Apollo BLE callbacks and RAM sections."""
from pathlib import Path
import hashlib
import json
import subprocess

from elftools.elf.elffile import ELFFile

root = Path(__file__).resolve().parents[3]
out = root / 'build/c-firmware/ble-source-aggregate-round1045'
out.mkdir(parents=True, exist_ok=True)
audio_receipt = root / 'build/c-firmware/audio-source-coherence-round855/receipt.json'
audio_collisions = root / 'build/c-firmware/audio-source-coherence-round855/provider-collisions.json'
main_receipt = root / 'build/c-firmware/main-source-audit-round857/link-receipt.json'
foundation_receipt = root / 'build/c-firmware/foundation-integration-round858/link-receipt.json'
audio = json.loads(audio_receipt.read_text())
collisions = json.loads(audio_collisions.read_text())
main = json.loads(main_receipt.read_text())
foundation = json.loads(foundation_receipt.read_text())
assert audio['total_sources'] == audio['compiled'] and audio['compiled'] >= 1089 and audio['failed'] == 0
assert collisions['strong_collisions'] == 0
assert main['strong_provider_collisions'] == 0
assert foundation['status'] == 'PASS_RELOCATABLE_ONLY'
linked = root / foundation['linked_object']
assert hashlib.sha256(linked.read_bytes()).hexdigest() == foundation['linked_sha256']
expected = {
    'audio_ble_subsystem_primary_callback_slot': ('.bss.g2.ram.ble_subsystem_primary_callback_slot', 4),
    'audio_ble_subsystem_callback_slot': ('.bss.g2.ram.ble_subsystem_callback_slot', 4),
    'audio_ble_subsystem_state_20071670': ('.bss.g2.ram.ble_subsystem_state', 0x9e),
    'audio_ble_subsystem_link_state_200719c8': ('.bss.g2.ram.ble_subsystem_link_state', 0x80),
    'audio_ble_subsystem_rows_200733fc': ('.bss.g2.ram.ble_subsystem_rows', 0x30),
}
with linked.open('rb') as stream:
    elf = ELFFile(stream)
    symbols = {symbol.name: symbol for symbol in elf.get_section_by_name('.symtab').iter_symbols()}
    for name, (section_name, size) in expected.items():
        symbol = symbols[name]
        assert symbol['st_size'] == size, (name, symbol['st_size'], size)
        section = elf.get_section(symbol['st_shndx'])
        assert section.name == section_name and section['sh_type'] == 'SHT_NOBITS', name
    for name in ('audio_ble_subsystem_primary_handler_4b3bec', 'audio_ble_subsystem_handler_503936'):
        assert symbols[name]['st_shndx'] != 'SHN_UNDEF', name
imports = {line.split()[-1] for line in subprocess.check_output(
    ['arm-none-eabi-nm', '-u', str(linked)], text=True).splitlines()}
assert not (set(expected) | {'audio_ble_subsystem_primary_handler_4b3bec',
                             'audio_ble_subsystem_handler_503936'}) & imports
assert len(imports) == foundation['unresolved_count']
receipt = {
    'round': 1045,
    'status': 'PASS_BLE_SOURCE_COHERENT_AGGREGATE',
    'component': 'Apollo current audio, Main and selected foundation C source set',
    'audio_sources_compiled': audio['compiled'],
    'audio_strong_collisions': collisions['strong_collisions'],
    'main_source_units': main['new_source_units'],
    'foundation_source_units': foundation['new_source_units'],
    'ble_ram_sections': {name: {'section': section, 'size': size}
                         for name, (section, size) in expected.items()},
    'linked_object': foundation['linked_object'],
    'linked_sha256': foundation['linked_sha256'],
    'unresolved_after': len(imports),
    'whole_image_complete': False,
    'hardware_proof': False,
    'gates': ['This fresh source-coherent aggregate is not the older incremental selected chain',
              f'{len(imports)} cross-component and dependency imports remain in this aggregate',
              'Full linker placement, startup, binary equality and hardware operation remain open'],
}
(out / 'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
print(receipt['status'], len(expected), len(imports), receipt['linked_sha256'])
