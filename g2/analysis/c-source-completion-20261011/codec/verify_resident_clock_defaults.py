#!/usr/bin/env python3
"""Check source-owned 60-byte clock default object against stock image A."""
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path

root = Path(__file__).resolve().parents[4]
image = root / 'g2/build/pseudocode-first/20260930T190500Z/reviews/codec-canonical-images-003/images/binh_a_stage2_sram.bin'
obj = root / 'g2/build/c-firmware/20261011/codec-resident-snpu-clockdefaults-round/codec/resident_clock_runtime_defaults.o'
objcopy = root / 'g2/build/pseudocode-first/20260930T190500Z/tools/csky-binutils-001/install/bin/csky-elfabiv2-objcopy'
with tempfile.TemporaryDirectory() as tmp:
    out = Path(tmp) / 'section.bin'
    subprocess.run([str(objcopy), '--dump-section', f'.gx8002.clock_defaults.268c8={out}', str(obj)], check=True, capture_output=True)
    actual = out.read_bytes()
stock = image.read_bytes()[0x100268c8-0x10023400:0x10026904-0x10023400]
result = {'source_address': '0x100268c8', 'bytes': len(actual), 'exact': actual == stock and len(actual) == 60,
          'stock_sha256': hashlib.sha256(stock).hexdigest(), 'object_sha256': hashlib.sha256(actual).hexdigest(),
          'scope': 'target object bytes; final runtime alias and linker placement unqualified'}
Path(__file__).with_name('resident-clock-defaults-receipt.json').write_text(json.dumps(result, indent=2)+'\n')
print(json.dumps(result))
raise SystemExit(not result['exact'])
