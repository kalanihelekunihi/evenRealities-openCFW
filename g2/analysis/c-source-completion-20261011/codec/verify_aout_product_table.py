#!/usr/bin/env python3
"""Check the 21-word native AOUT table against source provider identities.

This proves the stock initializer words, not final C linker placement.
"""
import hashlib
import json
import struct
from pathlib import Path

root = Path(__file__).resolve().parents[4]
image = root / ('g2/build/pseudocode-first/20260930T190500Z/reviews/'
                'codec-canonical-images-003/images/binh_a_stage2_sram.bin')
data = image.read_bytes()
base = 0x10023400
address = 0x10026bc8
table = data[address-base:address-base+84]
words = struct.unpack('<21I', table)
expected = [
    0x10205254, 0x10204f18, 0x10205344, 0x10204ec0,
    0x1020521c, 0x102052e0, 0x10204e6c, 0x10204d38,
    0x10204c64, 0x10204c90, 0x10205318, 0x102051a8,
    0, 0x10204d04, 0x10204f90, 0x10204ff0,
    0x1020508c, 0x10204cd4, 0x1020502c, 0x10204cdc,
    0x10204cfc,
]
assert list(words) == expected
source = (root / 'g2/components/gx8002/app_callback_candidate/'
          'resident_xip_aout_product_table.c').read_text()
names = [
    'alloc_playback', 'hw_initialize', 'exit', 'suspend', 'resume',
    'free', 'config_buffer', 'config_pcm', 'config_i2s', 'config_dac',
    'config_cb', 'push_frame', None, 'drain_frame', 'set_db',
    'get_db', 'set_mute', 'get_mute', 'set_channel', 'set_fixed_src',
    'get_sdc_addr',
]
for name, value in zip(names, words):
    if name is not None:
        assert f'gx8002_xip_aout_{name}_{value:08x}' in source
assert '.reserved_zero = 0u' in source
receipt = {
    'native_image_sha256': hashlib.sha256(data).hexdigest(),
    'native_table_address': hex(address),
    'runtime_alias_in_xip_calls': '0x20026bc8',
    'native_table_sha256': hashlib.sha256(table).hexdigest(),
    'words': [hex(value) for value in words],
    'source_relocation_identities_match': True,
    'scope': 'native word/provider identity; final section placement and alias/copy remain open',
}
Path(__file__).with_name('aout-product-table-receipt.json').write_text(
    json.dumps(receipt, indent=2) + '\n')
print(json.dumps({'words': len(words),
                  'table_sha256': receipt['native_table_sha256'],
                  'identities_match': True}))
