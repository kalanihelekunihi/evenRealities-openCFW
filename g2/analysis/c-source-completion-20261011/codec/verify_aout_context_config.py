#!/usr/bin/env python3
"""Check exact stock AOUT context/config initialization words.

ELF relocation and section-size checks belong to the target build.
"""
import hashlib
import json
import struct
from pathlib import Path

root = Path(__file__).resolve().parents[4]
base = root / ('g2/build/pseudocode-first/20260930T190500Z/reviews/'
               'codec-canonical-images-003/images')
sram = (base / 'binh_a_stage2_sram.bin').read_bytes()
xip = (base / 'binh_a_stage2_xip.bin').read_bytes()
context = sram[0x10026b94 - 0x10023400:0x10026bc8 - 0x10023400]
config = sram[0x10026c1c - 0x10023400:0x10026c74 - 0x10023400]
route = xip[0x1020aa26 - 0x10203004:0x1020aa33 - 0x10203004]
assert route == b'0 route play\x00'
assert struct.unpack('<13I', context) == (0x1020aa26,) + (0,) * 12
words = struct.unpack('<22I', config)
nonzero = {i * 4: value for i, value in enumerate(words) if value}
assert nonzero == {
    0x04: 1, 0x1c: 1, 0x34: 0xff0f0003, 0x38: 3,
    0x40: 0xfff00003, 0x44: 3, 0x4c: 4, 0x54: 1,
}
receipt = {
    'native_sram_sha256': hashlib.sha256(sram).hexdigest(),
    'context_address': '0x10026b94',
    'context_sha256': hashlib.sha256(context).hexdigest(),
    'route_xip_address': '0x1020aa26',
    'route_literal': route.decode('ascii').rstrip('\x00'),
    'config_address': '0x10026c1c',
    'config_sha256': hashlib.sha256(config).hexdigest(),
    'nonzero_config_words': {hex(k): hex(v) for k, v in nonzero.items()},
    'scope': 'stock initializer evidence; C relocation identity and final alias/copy are separate',
}
Path(__file__).with_name('aout-context-config-receipt.json').write_text(
    json.dumps(receipt, indent=2) + '\n')
print(json.dumps({'context_bytes': len(context), 'config_bytes': len(config),
                  'nonzero_config_words': len(nonzero)}))
