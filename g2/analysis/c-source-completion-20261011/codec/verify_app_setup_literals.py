#!/usr/bin/env python3
"""Authenticate application UART setup and command descriptor strings."""
import hashlib
import json
import struct
from pathlib import Path

root = Path(__file__).resolve().parents[4]
image = root / ('g2/build/pseudocode-first/20260930T190500Z/reviews/'
                'codec-canonical-images-003/images/binh_a_stage2_xip.bin')
data = image.read_bytes()
base = 0x10203004
def cstring(address):
    offset = address - base
    return data[offset:data.index(0, offset) + 1]

settings = data[0x1020b688-base:0x1020b698-base]
assert struct.unpack('<4I', settings) == (0, 115200, 0x58585542, 1)
names = {
    0x1020b698: 'mic status',
    0x1020b6a3: 'gsensor status',
    0x1020b6b2: 'version',
    0x1020b6ba: 'switch bf cmd',
    0x1020b6c8: 'open vad reporting',
    0x1020b6db: 'close vad reporting',
    0x1020b6ef: 'set pga gain',
    0x1020b6fc: 'start Dmic cmd',
    0x1020b70b: 'close Dmic cmd',
    0x1020b71a: 'pdm ch delay',
    0x1020b727: 'i2s set state',
}
source = (root / 'g2/components/gx8002/app_callback_candidate/'
          'resident_xip_app_commands.c').read_text()
for address, value in names.items():
    assert cstring(address) == value.encode() + b'\x00'
    assert f'"{value}"' in source
receipt = {
    'native_image_sha256': hashlib.sha256(data).hexdigest(),
    'uart_settings_address': '0x1020b688',
    'uart_settings_sha256': hashlib.sha256(settings).hexdigest(),
    'command_names': {hex(k): v for k, v in names.items()},
    'scope': 'stock literal identities; callback execution and final XIP placement open',
}
Path(__file__).with_name('app-setup-literals-receipt.json').write_text(
    json.dumps(receipt, indent=2) + '\n')
print(json.dumps({'uart_settings_bytes': len(settings),
                  'command_names': len(names)}))
