#!/usr/bin/env python3
"""Verify stock XIP CRC table against the pinned SDK's CRC-32 polynomial."""
import hashlib
import json
import struct
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
IMAGE = ROOT / ('g2/build/pseudocode-first/20260930T190500Z/reviews/'
                'codec-canonical-images-003/images/binh_a_stage2_xip.bin')
SDK = ROOT / 'third-party/upstream/nationalchip-lvp-kws/base/src/crc32.c'
assert SDK.is_file()
source = SDK.read_text()
assert '0xedb88320' in source.lower() or '0x77073096' in source.lower()
values = []
for index in range(256):
    crc = index
    for _ in range(8):
        crc = (crc >> 1) ^ (0xedb88320 if crc & 1 else 0)
    values.append(crc)
expected = struct.pack('<256I', *values)
stock = IMAGE.read_bytes()[0x1020b908 - 0x10203004:
                           0x1020bd08 - 0x10203004]
assert len(stock) == 1024 and stock == expected
receipt = {
    'stock_address': '0x1020b908',
    'bytes': len(stock),
    'sha256': hashlib.sha256(stock).hexdigest(),
    'pinned_source': str(SDK.relative_to(ROOT)),
    'result': 'PASS',
    'limit': 'Initializer bytes/algorithm only; final address placement unqualified',
}
(HERE / 'crc-table-data-receipt.json').write_text(
    json.dumps(receipt, indent=2) + '\n')
print(json.dumps(receipt))
