#!/usr/bin/env python3
"""Check clock boot source records and mode adjustments against stock."""
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path

root = Path(__file__).resolve().parents[4]
image = root / 'g2/build/pseudocode-first/20260930T190500Z/reviews/codec-canonical-images-003/images/binh_a_stage2_sram.bin'
obj = root / 'g2/build/c-firmware/20261011/codec-resident-clock-boot-table-round/codec/resident_clock_boot_literals.o'
objcopy = root / 'g2/build/pseudocode-first/20260930T190500Z/tools/csky-binutils-001/install/bin/csky-elfabiv2-objcopy'
stock = image.read_bytes()
checks = []
for addr, size in [(0x10025cd0, 16), (0x10025ce0, 20)]:
    section = f'.gx8002.clock_boot.{addr & 0xfffff:x}'
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / 'section.bin'
        subprocess.run([str(objcopy), '--dump-section', f'{section}={out}', str(obj)], check=True, capture_output=True)
        actual = out.read_bytes()
    expected = stock[addr-0x10023400:addr-0x10023400+size]
    checks.append({'address': hex(addr), 'bytes': len(actual), 'exact': actual == expected and len(actual) == size,
                   'stock_sha256': hashlib.sha256(expected).hexdigest(), 'object_sha256': hashlib.sha256(actual).hexdigest()})
result = {'checks': checks, 'all_exact': all(c['exact'] for c in checks),
          'scope': 'target object bytes only; startup source selection and linker placement unqualified'}
Path(__file__).with_name('resident-clock-boot-literals-receipt.json').write_text(json.dumps(result, indent=2)+'\n')
print(json.dumps({'checks': len(checks), 'bytes': sum(c['bytes'] for c in checks), 'all_exact': result['all_exact']}))
raise SystemExit(not result['all_exact'])
