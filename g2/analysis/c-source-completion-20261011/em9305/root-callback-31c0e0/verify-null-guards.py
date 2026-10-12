#!/usr/bin/env python3
from pathlib import Path
import json,re,struct,hashlib
P=Path(__file__).resolve().parent;R=P.parents[4];b=(R/'g2/build/c-firmware/20261011/em-activation-round/em-inspection.bin').read_bytes();assert hashlib.sha256(b).hexdigest()=='0de6e945a56ec886a92e44d4eaefe02fbca6db11f8747876e30bffb45cffce03'
ptr=struct.unpack('<10I',b[0x335300-0x302400:0x335328-0x302400]);n={}
for l in (P/'native.txt').read_text().splitlines():
 v=l.split('\t')
 if len(v)>=4 and re.fullmatch(r'\s*[0-9a-f]+:',v[0]):n[int(v[0].strip()[:-1],16)]=(v[2].strip(),v[3].strip(),l)
checks=[(0x31c298,0x31c2a0,0x31c212,0),(0x31c2b4,0x31c2c0,0x31c2cc,0),(0x31c2e0,0x31c2e8,0x31c2f4,4),(0x31c38a,0x31c394,0x31c39a,16),(0x31c3ea,0x31c3f4,0x31c3fa,16)]
for guard,load,skip,field in checks:
 m,o,line=n[guard];assert m.startswith('breq') and o.startswith('r13,0x1b,') and ';0x'+format(skip,'x') in line
 assert n[load][0].startswith('ld') and ptr[5+field//4]!=0
 # No explicit branch can bypass the guard by entering its load sequence.
 for addr,(_,_,line) in n.items():
  d=re.search(r';0x([0-9a-f]+)',line)
  if d and guard<int(d[1],16)<=load:assert guard<=addr<=load,(hex(addr),line)
assert all(ptr[row*5+field//4] for row in range(2) for field in [8,12])
r={'status':'PASS_FIVE_LOCAL_NULL_SLOT_GUARDS','zero_slot_offsets':[0,4,16],'guarded_loads':[{'guard':hex(a),'load':hex(c),'state27_skip':hex(s),'field':f} for a,c,s,f in checks],'nonzero_both_rows_fields':[8,12],'limits':['Local native guards and explicit branch ingress verified.','Whole register dataflow, external callback clobbers, startup writes and hardware remain separate.']};(P/'null-guard-receipt.json').write_text(json.dumps(r,indent=2)+'\n');print(r)
