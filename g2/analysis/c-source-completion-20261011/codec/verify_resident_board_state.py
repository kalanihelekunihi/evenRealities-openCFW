#!/usr/bin/env python3
"""Check partially attributed board state object's exact source bytes."""
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path

root = Path(__file__).resolve().parents[4]
image = root / 'g2/build/pseudocode-first/20260930T190500Z/reviews/codec-canonical-images-003/images/binh_a_stage2_sram.bin'
obj = root / 'g2/build/c-firmware/20261011/codec-resident-vic-boardstate-round/codec/resident_board_product_state.o'
objcopy = root / 'g2/build/pseudocode-first/20260930T190500Z/tools/csky-binutils-001/install/bin/csky-elfabiv2-objcopy'
with tempfile.TemporaryDirectory() as tmp:
    out = Path(tmp) / 'section.bin'
    subprocess.run([str(objcopy), '--dump-section', f'.gx8002.board_state.269a4={out}', str(obj)], check=True, capture_output=True)
    actual = out.read_bytes()
stock = image.read_bytes()[0x100269a4-0x10023400:0x100269cc-0x10023400]
result = {'source_address': '0x100269a4', 'bytes': len(actual), 'exact': actual == stock and len(actual) == 40,
          'stock_sha256': hashlib.sha256(stock).hexdigest(), 'object_sha256': hashlib.sha256(actual).hexdigest(),
          'known_consumer': 'XIP 0x10203004 returns runtime 0x200269a4; XIP 0x1020302e reads halfword +0x20',
          'scope': 'target object bytes; field semantics and runtime alias/linker placement remain incomplete'}
Path(__file__).with_name('resident-board-state-receipt.json').write_text(json.dumps(result, indent=2)+'\n')
print(json.dumps(result))
raise SystemExit(not result['exact'])
