#!/usr/bin/env python3
"""Check semantic 256-byte division lookup against authenticated XIP bytes."""
import hashlib
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
SOURCE = ROOT / ('g2/components/gx8002/app_callback_candidate/'
                 'resident_xip_udiv_bitlength_data.c')
IMAGE = ROOT / ('g2/build/pseudocode-first/20260930T190500Z/reviews/'
                'codec-canonical-images-003/images/binh_a_stage2_xip.bin')
body = SOURCE.read_text().split('= {', 1)[1].split('};', 1)[0]
values = bytes(map(int, re.findall(r'\b([0-9]+)u\b', body)))
stock = IMAGE.read_bytes()[0x1020bd1c - 0x10203004:0x1020be1c - 0x10203004]
assert len(values) == len(stock) == 256
assert values == bytes(index.bit_length() for index in range(256))
assert values == stock
receipt = {
    'source': str(SOURCE.relative_to(ROOT)),
    'stock_address': '0x1020bd1c',
    'bytes': len(values),
    'stock_and_semantic_sha256': hashlib.sha256(values).hexdigest(),
    'result': 'PASS',
    'limit': 'Initializer bytes only; final address placement and native lookup ABI unqualified',
}
(HERE / 'udiv-bitlength-data-receipt.json').write_text(
    json.dumps(receipt, indent=2) + '\n')
print(json.dumps(receipt))
