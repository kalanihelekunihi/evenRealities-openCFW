#!/usr/bin/env python3
"""Check source-owned RingDataRelay buffers and selected Apollo link."""
from pathlib import Path
import hashlib
import json
import subprocess

from elftools.elf.elffile import ELFFile

root = Path(__file__).resolve().parents[3]
out = root / 'build/c-firmware/ring-buffers-round901'
out.mkdir(parents=True, exist_ok=True)
src = root / 'components/audio/uart_thread_source_candidate/ring_buffers.c'
header = src.with_suffix('.h')
obj = out / 'ring_buffers.o'
linked = out / 'apollo-main-ring-buffers.o'
base = root / 'build/c-firmware/ring-pb-tx-ble-round900/apollo-main-ring-pb-tx-ble.o'
subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m55', '-mthumb',
                '-fshort-enums', '-std=c11', '-ffreestanding', '-fno-builtin', '-O2',
                '-Wall', '-Wextra', '-Werror', '-c', str(src), '-o', str(obj)], check=True)
with obj.open('rb') as f:
    elf = ELFFile(f)
    symbols = {s.name: s for s in elf.get_section_by_name('.symtab').iter_symbols()}
    for name, size in [('audio_ring_buffers', 128), ('audio_ring_tx_buffer', 256)]:
        sym = symbols[name]
        assert sym['st_size'] == size and sym['st_info']['bind'] == 'STB_GLOBAL'
        assert elf.get_section(sym['st_shndx'])['sh_type'] == 'SHT_NOBITS'
blob = (root / 'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()[32:]
assert hashlib.sha256(blob).hexdigest() == '19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701'
literals = [(0x5ce74c, 0x200f86bc), (0x5ce79c, 0x200f86fc), (0x5ce798, 0x2037c8a0)]
for address, value in literals:
    assert int.from_bytes(blob[address-0x438000:address-0x438000+4], 'little') == value
assert literals[1][1] - literals[0][1] == 64
subprocess.run(['arm-none-eabi-ld', '-r', str(base), str(obj), '-o', str(linked)], check=True)
def imports(path):
    return {x.split()[-1] for x in subprocess.check_output(['arm-none-eabi-nm', '-u', str(path)], text=True).splitlines()}
before, after = imports(base), imports(linked)
assert before - after == {'audio_ring_buffers', 'audio_ring_tx_buffer'} and not after - before
receipt = {
    'round': 901, 'status': 'PASS_RING_BUFFER_SOURCE_OWNERSHIP',
    'component': 'Apollo RingDataRelay decode, encode, and BLE transmit buffers',
    'sources': {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest() for p in [src, header]},
    'official_image_sha256': hashlib.sha256(blob).hexdigest(),
    'native_literals': [{'address': hex(a), 'value': hex(v)} for a, v in literals],
    'layout': {'decode_bytes': 64, 'encode_bytes': 64, 'encode_offset': 64, 'tx_bytes': 256},
    'linked_object': str(linked.relative_to(root)),
    'linked_sha256': hashlib.sha256(linked.read_bytes()).hexdigest(),
    'unresolved_before': len(before), 'unresolved_after': len(after),
    'whole_image_complete': False, 'hardware_proof': False,
    'gates': ['Final RAM/PSRAM addresses and startup ownership are not established',
              'Ring protobuf descriptor, fault handler, 51 registry callback bodies, and hardware execution remain open'],
}
(out / 'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
print(receipt['status'], len(before), len(after))
