#!/usr/bin/env python3
"""Compare vector pointer identities with stock and target relocations."""
import json
import re
import struct
import subprocess
from collections import Counter
from pathlib import Path

root = Path(__file__).resolve().parents[4]
image = root / 'g2/build/pseudocode-first/20260930T190500Z/reviews/codec-canonical-images-003/images/binh_a_stage2_sram.bin'
obj = root / 'g2/build/c-firmware/20261011/codec-resident-startup-ambient-round/codec/resident_vectors_candidate.o'
readelf = root / 'g2/build/pseudocode-first/20260930T190500Z/tools/csky-binutils-001/install/bin/csky-elfabiv2-readelf'
stock = struct.unpack_from('<64I', image.read_bytes())
expected_words = [0x10023500] + [0x10023640] * 31 + [0x10025574] * 32
output = subprocess.run([str(readelf), '-rW', str(obj)], capture_output=True, text=True, check=True).stdout
entries = []
for line in output.splitlines():
    match = re.match(r'^([0-9a-fA-F]{8})\s+\S+\s+R_CKCORE_ADDR32\s+\S+\s+(\S+)\s+\+\s+0$', line)
    if match: entries.append((int(match.group(1), 16), match.group(2)))
expected_symbols = (['gx8002_resident_reset_entry_23500'] +
                    ['gx8002_resident_exception_bridge_23640'] * 31 +
                    ['gx8002_resident_irq_compact_entry_25574'] * 32)
exact = list(stock) == expected_words and entries == list(zip(range(0, 256, 4), expected_symbols))
result = {'stock_words': len(stock), 'relocations': len(entries), 'stock_address_counts': dict(Counter(hex(x) for x in stock)),
          'relocation_symbol_counts': dict(Counter(name for _, name in entries)), 'identity_and_order_exact': exact,
          'scope': 'vector pointer identity and relocation order; final linked addresses and runtime alias unqualified'}
Path(__file__).with_name('resident-vector-relocation-receipt.json').write_text(json.dumps(result, indent=2)+'\n')
print(json.dumps(result))
raise SystemExit(not exact)
