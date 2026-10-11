#!/usr/bin/env python3
"""Bounded stock table/source constant check, not an execution oracle."""
from pathlib import Path
import hashlib
import json
import re
import struct

root = Path(__file__).resolve().parents[4]
binary = root / ('g2/build/pseudocode-first/20260930T190500Z/reviews/'
                 'codec-canonical-images-003/images/binh_a_stage2_sram.bin')
source = root / 'g2/components/gx8002/app_callback_candidate/resident_clock_frequency.c'
blob = binary.read_bytes()
code = source.read_text()
raw = [struct.unpack_from('<I', blob, 0x10025460 - 0x10023400 + 4*i)[0]
       for i in range(19)]
expected = [0x100253a8, 0x100253a8] + [0x1002522a]*8 + [
    0x10025228, 0x10025228, 0x1002522a,
    0x1002534a, 0x1002534a, 0x1002522a,
    0x10025342, 0x10025342, 0x10025346]
assert raw == expected
for literal in ('32000u', '1024000u', '2048000u', '12288000u',
                '24576000u', '61440000u', '73728000u', '86016000u',
                '98304000u', '0xfff83000', '0x000f9fff', '0xfffda800',
                '0x002c87ff'):
    assert literal in code, literal
assert re.search(r'case 2u: reference = 86016000u;', code)
assert re.search(r'case 3u: reference = 98304000u;', code)
assert re.search(r'case 1u: reference = 73728000u;', code)
print(json.dumps({
    'status': 'PASS', 'scope': 'native jump-table bytes and source constants only',
    'table_entries': len(raw), 'native_image_sha256': hashlib.sha256(blob).hexdigest(),
    'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
    'runtime_equivalence': 'not tested'
}, indent=2))
