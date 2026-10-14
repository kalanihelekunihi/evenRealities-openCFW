#!/usr/bin/env python3
"""Check pinned CapSense v5 LP field layout against authenticated G2 ROM."""
import hashlib
import json
import re
import struct
import subprocess
from pathlib import Path

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[4]
FIRMWARE = ROOT / 'g2/blobs/official/g2-2.2.6.10/firmware_touch.bin'
SOURCE = OUT / 'v5_0_0_f0_lp1.c'
image = FIRMWARE.read_bytes()
assert hashlib.sha256(image).hexdigest() == '0d13d8bb1337bf22989dc16143e3d5eca29a31cc1ed753ff624668750ea9470d'
offset = 32 + 0xb0f8 - 0x3300
records = image[offset:offset + 3 * 144]
assert hashlib.sha256(records).hexdigest() == '27ef6582ee031179cdfb25d6e091b0be3f869c1ac1e73eb7f58ebaf2ef8022ce'
probe = subprocess.run(['clang', '-target', 'armv6m-none-eabi', '-mcpu=cortex-m0plus',
                        '-mthumb', '-std=c11', '-ffreestanding', '-Xclang',
                        '-fdump-record-layouts', '-fsyntax-only', str(SOURCE)],
                       text=True, capture_output=True, check=True)
layout = probe.stdout + probe.stderr
block = layout.split('*** Dumping AST Record Layout')[-1]
fields = {}
for line in block.splitlines():
    match = re.match(r'\s*(\d+)\s*\|\s+\S.*?\s+(\w+)\s*$', line)
    if match:
        fields[match.group(2)] = int(match.group(1))
assert '[sizeof=144, align=4]' in block
assert {k: fields[k] for k in ('ptrWdContext', 'ptrSnsContext', 'ptrEltdConfig',
                               'ptrRawFilterHistory', 'ptrRawFilterHistoryLow',
                               'ptrDebounceArr', 'ptrPosFilterHistory',
                               'numSns', 'senseMethod', 'wdType', 'ptrMpTable',
                               'iirCoeffHw', 'cdacConfig')} == {
    'ptrWdContext': 0, 'ptrSnsContext': 4, 'ptrEltdConfig': 8,
    'ptrRawFilterHistory': 28, 'ptrRawFilterHistoryLow': 32,
    'ptrDebounceArr': 40, 'ptrPosFilterHistory': 60, 'numSns': 56,
    'senseMethod': 122, 'wdType': 123, 'ptrMpTable': 124,
    'iirCoeffHw': 140, 'cdacConfig': 142}
rows = []
for i in range(3):
    rec = records[i * 144:(i + 1) * 144]
    u32 = lambda name: struct.unpack_from('<I', rec, fields[name])[0]
    u16 = lambda name: struct.unpack_from('<H', rec, fields[name])[0]
    u8 = lambda name: rec[fields[name]]
    row = {'index': i, 'rom_address': hex(0xb0f8 + i * 144),
           'sha256': hashlib.sha256(rec).hexdigest(),
           'widget_context': hex(u32('ptrWdContext')),
           'sensor_context': hex(u32('ptrSnsContext')),
           'electrode_config': hex(u32('ptrEltdConfig')),
           'num_sensors': u16('numSns'), 'num_cols': u8('numCols'),
           'num_rows': u8('numRows'), 'sense_method': u8('senseMethod'),
           'widget_type': u8('wdType'), 'num_slots': u16('numSlots'),
           'raw_history': hex(u32('ptrRawFilterHistory')),
           'raw_history_low': hex(u32('ptrRawFilterHistoryLow')),
           'debounce_array': hex(u32('ptrDebounceArr')),
           'position_history': hex(u32('ptrPosFilterHistory')),
           'mp_table': hex(u32('ptrMpTable')),
           'iir_coeff_hw': u8('iirCoeffHw'),
           'cdac_config': hex(u16('cdacConfig'))}
    assert 0x20000000 <= u32('ptrWdContext') < 0x20010000
    assert 0x20000000 <= u32('ptrSnsContext') < 0x20010000
    assert 0xb2a8 <= u32('ptrEltdConfig') < 0xb32c
    assert row['num_sensors'] > 0 and row['num_slots'] > 0
    rows.append(row)
result = {'status': 'PASS_BOUNDED_V5_LP_LAYOUT_AND_ROM_FIELD_COHERENCE',
          'source_commit': 'a4aa9306f7e4323994902f0baf5b1570ffbbfe59',
          'firmware_sha256': hashlib.sha256(image).hexdigest(),
          'records_sha256': hashlib.sha256(records).hexdigest(),
          'source_sha256': hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
          'sizeof_widget': 144, 'field_offsets': fields, 'records': rows,
          'limits': ['Field coherence and stride support the v5 LP ABI hypothesis; they do not prove exact middleware revision or generated initializer provenance.',
                     'No product-generated source, complete allocation extents, final placement, or hardware behavior is established.']}
(OUT / 'v5-native-widget-audit.json').write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
print(result['status'])
