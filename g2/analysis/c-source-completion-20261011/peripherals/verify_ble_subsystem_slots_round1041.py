#!/usr/bin/env python3
"""Place both source-owned Apollo BLE callback cells at native RAM addresses."""
from pathlib import Path
import hashlib
import json
import subprocess

from elftools.elf.elffile import ELFFile

root = Path(__file__).resolve().parents[3]
out = root / 'build/c-firmware/ble-subsystem-slots-round1041'
out.mkdir(parents=True, exist_ok=True)
source_dir = root / 'components/audio/uart_thread_source_candidate'
source = source_dir / 'display_ble_subsystem_callback_slots.c'
linker = source_dir / 'display_ble_subsystem_callback_slots.ld'
base = root / 'build/c-firmware/ble-subsystem-primary-round1040/apollo-main-ble-subsystem-primary.o'
obj = out / 'display_ble_subsystem_callback_slots.o'
linked = out / 'apollo-main-ble-subsystem-slots.o'
probe = out / 'ble-subsystem-slots-placement.elf'
blob = (root / 'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(blob).hexdigest() == '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
def word(address):
    return int.from_bytes(blob[address - 0x438000:address - 0x438000 + 4], 'little')
assert word(0x504118) == word(0x4b46ec) == 0x200740fc
subprocess.run([
    'clang', '--target=arm-none-eabi', '-mcpu=cortex-m55', '-mthumb',
    '-fshort-enums', '-std=c11', '-ffreestanding', '-fno-builtin', '-O2',
    '-Wall', '-Wextra', '-Werror', '-c', str(source), '-o', str(obj)
], check=True)
with obj.open('rb') as stream:
    elf = ELFFile(stream)
    symbols = {symbol.name: symbol for symbol in elf.get_section_by_name('.symtab').iter_symbols()}
    for name in ('audio_ble_subsystem_primary_callback_slot', 'audio_ble_subsystem_callback_slot'):
        symbol = symbols[name]
        assert symbol['st_size'] == 4, (name, symbol['st_size'])
        section = elf.get_section(symbol['st_shndx'])
        assert section['sh_type'] == 'SHT_NOBITS', (name, section['sh_type'])
subprocess.run(['arm-none-eabi-ld', '-T', str(linker), str(obj), '-o', str(probe)], check=True)
with probe.open('rb') as stream:
    elf = ELFFile(stream)
    symbols = {symbol.name: symbol for symbol in elf.get_section_by_name('.symtab').iter_symbols()}
    expected = {'audio_ble_subsystem_primary_callback_slot': 0x200740fc,
                'audio_ble_subsystem_callback_slot': 0x20074100}
    for name, address in expected.items():
        symbol = symbols[name]
        assert symbol['st_value'] == address and symbol['st_size'] == 4, (name, symbol['st_value'])
        section = elf.get_section(symbol['st_shndx'])
        assert section['sh_type'] == 'SHT_NOBITS', (name, section['sh_type'])
    assert expected['audio_ble_subsystem_primary_callback_slot'] + 4 == expected['audio_ble_subsystem_callback_slot']

def imports(path):
    return {line.split()[-1] for line in subprocess.check_output(
        ['arm-none-eabi-nm', '-u', str(path)], text=True).splitlines()}

before = imports(base)
assert set(expected) <= before
subprocess.run(['arm-none-eabi-ld', '-r', str(base), str(obj), '-o', str(linked)], check=True)
after = imports(linked)
assert before - after == set(expected) and not after - before
receipt = {
    'round': 1041,
    'status': 'PASS_BLE_SUBSYSTEM_CALLBACK_SLOTS_PLACEMENT',
    'component': 'Apollo BLE primary and secondary callback RAM slots',
    'source': str(source.relative_to(root)),
    'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
    'linker': str(linker.relative_to(root)),
    'linker_sha256': hashlib.sha256(linker.read_bytes()).hexdigest(),
    'official_image_sha256': hashlib.sha256(blob).hexdigest(),
    'addresses': {name: hex(address) for name, address in expected.items()},
    'probe_elf': str(probe.relative_to(root)),
    'probe_sha256': hashlib.sha256(probe.read_bytes()).hexdigest(),
    'linked_object': str(linked.relative_to(root)),
    'linked_sha256': hashlib.sha256(linked.read_bytes()).hexdigest(),
    'unresolved_before': len(before),
    'unresolved_after': len(after),
    'whole_image_complete': False,
    'hardware_proof': False,
    'gates': ['Isolated placement does not prove full RAM overlap or boot initialization',
              'Secondary callback body, complete BLE service and hardware execution remain open'],
}
(out / 'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
print(receipt['status'], len(before), len(after), receipt['linked_sha256'])
