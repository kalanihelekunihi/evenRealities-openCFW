#!/usr/bin/env python3
"""Bind and place the minimum stock-observed Apollo appMaster state span."""
from pathlib import Path
import hashlib
import json
import subprocess

from elftools.elf.elffile import ELFFile

root = Path(__file__).resolve().parents[3]
out = root / 'build/c-firmware/ble-subsystem-state-round1043'
out.mkdir(parents=True, exist_ok=True)
source_dir = root / 'components/audio/uart_thread_source_candidate'
source = source_dir / 'display_ble_subsystem_state.c'
linker = source_dir / 'display_ble_subsystem_state.ld'
base = root / 'build/c-firmware/ble-subsystem-secondary-round1042/apollo-main-ble-subsystem-secondary.o'
obj = out / 'display_ble_subsystem_state.o'
linked = out / 'apollo-main-ble-subsystem-state.o'
probe = out / 'ble-subsystem-state-placement.elf'
blob = (root / 'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(blob).hexdigest() == '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
def word(address):
    return int.from_bytes(blob[address - 0x438000:address - 0x438000 + 4], 'little')
assert word(0x5040bc) == 0x20071670
assert 10 * 15 == 0x96 and 0x9d + 1 == 0x9e
subprocess.run([
    'clang', '--target=arm-none-eabi', '-mcpu=cortex-m55', '-mthumb',
    '-fshort-enums', '-std=c11', '-ffreestanding', '-fno-builtin', '-O2',
    '-Wall', '-Wextra', '-Werror', '-c', str(source), '-o', str(obj)
], check=True)
name = 'audio_ble_subsystem_state_20071670'
with obj.open('rb') as stream:
    elf = ELFFile(stream)
    symbol = next(s for s in elf.get_section_by_name('.symtab').iter_symbols() if s.name == name)
    assert symbol['st_size'] == 0x9e
    section = elf.get_section(symbol['st_shndx'])
    assert section['sh_type'] == 'SHT_NOBITS'
subprocess.run(['arm-none-eabi-ld', '-T', str(linker), str(obj), '-o', str(probe)], check=True)
with probe.open('rb') as stream:
    elf = ELFFile(stream)
    symbol = next(s for s in elf.get_section_by_name('.symtab').iter_symbols() if s.name == name)
    assert symbol['st_value'] == 0x20071670 and symbol['st_size'] == 0x9e
    section = elf.get_section(symbol['st_shndx'])
    assert section['sh_type'] == 'SHT_NOBITS'
assert 0x20071670 + 0x9e <= 0x200717b0
prior = json.loads((root / 'build/c-firmware/terminal-ram-placement-round1002/receipt.json').read_text())
spans = [(int(value['address'], 16), int(value['address'], 16) + value['size'], name)
         for name, value in prior['symbols'].items()]
spans += [(0x20071670, 0x2007170e, name),
          (0x200740fc, 0x20074100, 'ble_primary_callback_slot'),
          (0x20074100, 0x20074104, 'ble_callback_slot')]
spans.sort()
assert len(spans) == 27 and all(a[1] <= b[0] for a, b in zip(spans, spans[1:])), spans
def imports(path):
    return {line.split()[-1] for line in subprocess.check_output(
        ['arm-none-eabi-nm', '-u', str(path)], text=True).splitlines()}
before = imports(base)
assert name in before
subprocess.run(['arm-none-eabi-ld', '-r', str(base), str(obj), '-o', str(linked)], check=True)
after = imports(linked)
assert before - after == {name} and not after - before
receipt = {
    'round': 1043,
    'status': 'PASS_BLE_SUBSYSTEM_STATE_MINIMUM_PLACEMENT',
    'component': 'Apollo appMaster ten-row state and live flags',
    'source': str(source.relative_to(root)),
    'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
    'linker': str(linker.relative_to(root)),
    'linker_sha256': hashlib.sha256(linker.read_bytes()).hexdigest(),
    'official_image_sha256': hashlib.sha256(blob).hexdigest(),
    'address': '0x20071670',
    'minimum_span_bytes': 0x9e,
    'nonoverlap_minimum_spans_checked': len(spans),
    'probe_elf': str(probe.relative_to(root)),
    'probe_sha256': hashlib.sha256(probe.read_bytes()).hexdigest(),
    'linked_object': str(linked.relative_to(root)),
    'linked_sha256': hashlib.sha256(linked.read_bytes()).hexdigest(),
    'unresolved_before': len(before),
    'unresolved_after': len(after),
    'whole_image_complete': False,
    'hardware_proof': False,
    'gates': ['The 0x9e-byte span is a minimum from observed accesses, not proven original allocation extent',
              'Full RAM overlap, boot initialization and hardware execution remain open'],
}
(out / 'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
print(receipt['status'], len(before), len(after), receipt['linked_sha256'])
