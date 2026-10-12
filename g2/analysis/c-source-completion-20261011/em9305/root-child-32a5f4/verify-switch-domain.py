#!/usr/bin/env python3
from pathlib import Path
import json,hashlib
P=Path(__file__).resolve().parent;R=P.parents[4]
b=(R/'g2/build/c-firmware/20261011/em-activation-round/em-inspection.bin').read_bytes()
assert hashlib.sha256(b).hexdigest()=='0de6e945a56ec886a92e44d4eaefe02fbca6db11f8747876e30bffb45cffce03'
t=b[0x3344b7-0x302400:0x3344b7-0x302400+9];assert t==(P/'slave-switch-table.bin').read_bytes()
# Unsigned BRHS excludes underflow and indices >=9; the delayed SEXB cannot
# introduce a negative index on the fallthrough domain 0..8.
rows=[]
for value in range(256):
 index=(value-3)&0xffffffff
 if index<9 and (393 & (1<<index)):
  assert index<128
  rows.append({'input_byte':value,'index':index,'output_event':t[index]})
r=json.loads((P/'switch-index-domain.json').read_text())
assert r['input_cases']==256 and rows==r['accepted_rows']
assert [x['index'] for x in rows]==[0,3,7,8]
print('PASS: all 256 native input values, four accepted indices, nine SDK/stock bytes')
