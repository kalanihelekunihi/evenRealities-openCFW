#!/usr/bin/env python3
"""Target-compile the pinned TLSF semantics for the six stock tail words."""
from pathlib import Path
import hashlib
import json
import struct
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
STOCK = ROOT / 'g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin'
INVENTORY = HERE / 'boot-coplacement-gpio-mode-data-round/objects/inventory.json'
PROBE = HERE / 'boot_tlsf_tail_target_abi.c'
inventory = json.loads(INVENTORY.read_text())
unit = next(item for item in inventory['units']
            if item['status'] == 'selected' and
            item['source'] == 'g2/components/bootloader/allocator/upstream/tlsf.c')
source = ROOT / unit['source']
code = source.read_text()
for name in ('block_header_free_bit', 'block_header_prev_free_bit',
             'block_header_overhead', 'block_start_offset', 'block_size_min',
             'block_size_max'):
    assert 'static const size_t ' + name in code

blob = STOCK.read_bytes()
assert hashlib.sha256(blob).hexdigest() == 'f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5'
words = struct.unpack_from('<6I', blob, 0x4341a8-0x410000)
assert words == (1, 2, 4, 8, 12, 0x40000000)
command = unit['compiler'][:-4] + ['-fsyntax-only', str(PROBE)]
run = subprocess.run(command, capture_output=True, text=True)
assert run.returncode == 0, run.stderr

receipt = {
    'status': 'PASS_TLSF_TAIL_TARGET_ABI',
    'stock_range': ['0x4341a8', '0x4341c0'],
    'stock_words': [hex(word) for word in words],
    'pinned_selected_source': unit['source'],
    'pinned_source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
    'target_probe_sha256': hashlib.sha256(PROBE.read_bytes()).hexdigest(),
    'target_compile_command': command,
    'limits': [
        'The selected source defines all six named static const size_t values; the probe checks their target ABI formulas and locked words.',
        'The compiler may fold constants and omit a standalone 24-byte table. This is semantic source ownership, not fixed-byte linker placement or allocator runtime equality.',
    ],
}
(HERE / 'boot-tlsf-tail-source-receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
print(json.dumps({'status': receipt['status'], 'stock_words': receipt['stock_words']}))
