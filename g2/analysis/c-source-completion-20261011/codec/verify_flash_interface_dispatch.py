#!/usr/bin/env python3
"""Compare native branch tree at 0x100244a8..0x10024538 with C classes.

This is a bounded static control-flow check, not C-SKY MMIO execution.
"""
import hashlib
import json
import random
from pathlib import Path

PAIR = {0x856013,0x856014,0x0b4014,0x0b4016,0x0b4017,0x854012,
        0xb36014,0xba6015,0xc84015,0xc84215,0xc86015,0xc86016,
        0xcd7015,0xef4015}
NONE = {0x1c3812,0x1c3813,0x1c7017}
SPECIAL = {0x684015:'both',0xc22017:'status'}

def native(x):
    if x <= 0x856014:
        if x >= 0x856013: return 'pair'
        if x <= 0x1c3813:
            if x >= 0x1c3812: return 'none'
            if x == 0x0b4014: return 'pair'
            if x < 0x0b4014: return 'single'
            return 'pair' if (x + 0xfff4bfea) & 0xffffffff < 2 else 'single'
        if x == 0x684015: return 'both'
        if x == 0x854012: return 'pair'
        if x == 0x1c7017: return 'none'
        return 'single'
    if x == 0xc84215: return 'pair'
    if x < 0xc84215:
        if x == 0xba6015: return 'pair'
        if x < 0xba6015: return 'pair' if x == 0xb36014 else 'single'
        if x == 0xc22017: return 'status'
        return 'pair' if x == 0xc84015 else 'single'
    if x == 0xcd7015: return 'pair'
    if x < 0xcd7015:
        return 'pair' if (x + 0xff379feb) & 0xffffffff < 2 else 'single'
    return 'pair' if x == 0xef4015 else 'single'

def candidate(x):
    if x in PAIR: return 'pair'
    if x in NONE: return 'none'
    if x in SPECIAL: return SPECIAL[x]
    return 'single'

literals = [0x856014,0x856013,0x1c3813,0x1c3812,0x0b4014,0x0b4016,
            0x0b4017,0x684015,0x854012,0x1c7017,0xc84215,0xba6015,
            0xb36014,0xc22017,0xc84015,0xcd7015,0xc86015,0xc86016,0xef4015]
values = {0,1,0xfffffffe,0xffffffff}
for x in literals:
    for d in range(-3,4): values.add((x+d)&0xffffffff)
rng=random.Random(0x2443c)
values.update(rng.getrandbits(32) for _ in range(100000))
errors=[(x,native(x),candidate(x)) for x in sorted(values) if native(x)!=candidate(x)]
p=Path(__file__).resolve().parents[4]/'g2/build/pseudocode-first/20260930T190500Z/reviews/codec-canonical-images-003/images/binh_a_stage2_sram.bin'
b=p.read_bytes(); base=0x10023400
receipt={'source_image_sha256':hashlib.sha256(b).hexdigest(),
         'native_branch_range':'0x100244a8..0x10024538',
         'literal_pool_sha256':hashlib.sha256(b[0x10024598-base:0x100245f0-base]).hexdigest(),
         'vectors':len(values),'mismatches':errors[:20],'mismatch_count':len(errors),
         'scope':'static branch model and C switch classes; not native execution'}
Path(__file__).with_name('flash-interface-dispatch-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps({'vectors':len(values),'mismatch_count':len(errors)}))
raise SystemExit(bool(errors))
