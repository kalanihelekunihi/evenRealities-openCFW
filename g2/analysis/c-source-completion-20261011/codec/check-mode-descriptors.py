#!/usr/bin/env python3
"""Check native XIP descriptor identities; linked placement is separate."""
from pathlib import Path
import hashlib
import json
import struct

root = Path(__file__).resolve().parents[4]
path = root/'g2/build/pseudocode-first/20260930T190500Z/reviews/codec-canonical-images-003/images/binh_a_stage2_xip.bin'
source = root/'g2/components/gx8002/app_callback_candidate/resident_xip_mode_initialize.c'
blob = path.read_bytes()
base = 0x10203004
def words(address, count):
    return list(struct.unpack_from('<'+'I'*count,blob,address-base))
assert words(0x1020b1bc,2) == [0x1020b1c4,0x1020b204]
idle = words(0x1020b1c4,5)
tws = words(0x1020b204,5)
assert idle == [0,0x10208634,0x10208624,0x1020861c,0x10208620]
assert tws == [1,0x10208670,0x1020864c,0x10026358,0x10208644]
result = {
    'status':'PASS', 'scope':'native descriptor words and source-owned typed relocation identities; no linked-layout proof',
    'native_xip_sha256':hashlib.sha256(blob).hexdigest(),
    'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
    'selector':[hex(x) for x in words(0x1020b1bc,2)],
    'idle':[hex(x) for x in idle], 'tws':[hex(x) for x in tws],
}
Path(__file__).with_suffix('.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'status':'PASS','descriptor_words':len(idle)+len(tws),'selector_words':2}))
