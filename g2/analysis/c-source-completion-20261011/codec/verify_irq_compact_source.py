#!/usr/bin/env python3
"""Compare named-instruction CK804EF IRQ object with stock native bytes."""
import hashlib
import json
from pathlib import Path

root = Path(__file__).resolve().parents[4]
here = Path(__file__).resolve().parent
compiled = (here / 'resident_irq_compact_corrected.bin').read_bytes()
native_image = (root / ('g2/build/pseudocode-first/20260930T190500Z/'
                        'reviews/codec-canonical-images-003/images/'
                        'binh_a_stage2_sram.bin')).read_bytes()
start, end, base = 0x10025574, 0x100255c4, 0x10023400
native = native_image[start-base:end-base]
assert len(compiled) == len(native) == 80
assert compiled == native
receipt = {
    'native_image_sha256': hashlib.sha256(native_image).hexdigest(),
    'native_range': '0x10025574..0x100255c3',
    'source': 'g2/components/gx8002/app_callback_candidate/resident_irq_compact_unqualified.S',
    'target_cpu': 'ck804ef',
    'bytes': len(native),
    'native_sha256': hashlib.sha256(native).hexdigest(),
    'compiled_sha256': hashlib.sha256(compiled).hexdigest(),
    'exact_equal': True,
    'fpu_registers': 'fr0-fr7; stock opcode pair f4ee3400/f4ee3000',
    'scope': 'full isolated source/stock bytes including literal pool; selected graph and runtime qualification separate',
}
(here / 'irq-compact-source-receipt.json').write_text(
    json.dumps(receipt, indent=2) + '\n')
print(json.dumps({'bytes': len(native), 'equal': True,
                  'sha256': receipt['native_sha256']}))
