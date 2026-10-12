#!/usr/bin/env python3
"""Check field-wise interpretation of image-A sample/KWS SRAM initializer.

The address words document native relocation identities. The eventual C
object must own these as relocations; this check alone does not place them.
"""
import hashlib
import json
import struct
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
IMAGE = ROOT / ('g2/build/pseudocode-first/20260930T190500Z/reviews/'
                'codec-canonical-images-003/images/binh_a_stage2_sram.bin')
BASE = 0x10023400
START, END = 0x10026c74, 0x10026d7c
raw = IMAGE.read_bytes()[START-BASE:END-BASE]

def keyword(phrase, threshold, code):
    name = phrase.encode('ascii')
    assert len(name) < 40
    return (name.ljust(40,b'\0') + struct.pack('<HH',54,54) +
            bytes(28) + struct.pack('<IIII',2,threshold,code,1))

expected = bytearray()
expected += struct.pack('<II',4,4)
expected += keyword('hey_even',0x237,100)
expected += keyword('hi_even',0x1cc,101)
expected += struct.pack('<I',1)
expected += struct.pack('<III',0xffffffff,1,0x20026d3c)
expected += struct.pack('<8I',0x1020b649,0x10208e4c,0x10208f04,
                        0x102091bc,0x10208dec,0x1020b654,
                        0x10208dcc,0x1020b665)
expected += struct.pack('<I',0x58585542) + bytes(28)
assert len(expected) == END-START == 264
assert expected == raw, [(hex(START+i),a,b) for i,(a,b)
                         in enumerate(zip(expected,raw)) if a!=b][:10]
receipt = {'stock_image_sha256':hashlib.sha256(IMAGE.read_bytes()).hexdigest(),
           'source_range':[hex(START),hex(END)],'bytes':len(expected),
           'range_sha256':hashlib.sha256(raw).hexdigest(),
           'fieldwise_exact':True,
           'segments':[
               {'address':'0x10026c74','bytes':8,'kind':'two receive config words'},
               {'address':'0x10026c7c','bytes':176,'kind':'two 88-byte keyword records'},
               {'address':'0x10026d2c','bytes':4,'kind':'sample state word'},
               {'address':'0x10026d30','bytes':44,'kind':'sample callback descriptor and eight relocations'},
               {'address':'0x10026d5c','bytes':32,'kind':'initialized BUXX request and reserved tail'}],
           'limit':'stock scalar/address identity; C relocation, final placement/copy, and native runtime remain unqualified'}
(HERE/'sample-app-tail-semantic-receipt.json').write_text(
    json.dumps(receipt,indent=2)+'\n')
print(json.dumps({'bytes':len(expected),'fieldwise_exact':True,
                  'sha256':receipt['range_sha256']}))
