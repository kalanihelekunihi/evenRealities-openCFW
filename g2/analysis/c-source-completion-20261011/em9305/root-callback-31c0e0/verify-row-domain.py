#!/usr/bin/env python3
from pathlib import Path
import re,json,hashlib
P=Path(__file__).resolve().parent;n={}
for l in (P/'native.txt').read_text().splitlines():
 v=l.split('\t')
 if len(v)>=4 and re.fullmatch(r'\s*[0-9a-f]+:',v[0]):n[int(v[0].strip()[:-1],16)]=(v[2].strip(),v[3].strip(),l)
expected={0x31c1f6:('cmp','r13,255'),0x31c1fc:('seteq','r0,r13,0x1c'),0x31c200:('asl_s','r0,r0'),0x31c202:('cmp_s','r13,0x1b'),0x31c204:('add_s','r0,r0,-1'),0x31c206:('mov.eq','r0,0'),0x31c20a:('brlo.d.nt','r0,0x2,14'),0x31c20e:('extb_s','r15,r0')}
for a,v in expected.items():assert n[a][:2]==v,(hex(a),n[a][:2])
assert ';0x31c216' in n[0x31c20a][2]
accepted=[]
for state in range(65536):
 row=((2 if state==28 else 0)-1)&0xffffffff
 if state==27:row=0
 if state!=255 and row<2:accepted.append((state,row))
assert accepted==[(27,0),(28,1)]
# For all remaining uint32 values seteq is zero and cmp.eq is false,
# leaving row=UINT32_MAX; the unsigned admission fails.
fields=[0,4,8,12,16];assert all(0<=row*20+field<=36 for _,row in accepted for field in fields)
r={'status':'PASS_NATIVE_ROW_ADMISSION_DOMAIN','enumerated_states':65536,'accepted_state_rows':accepted,'remaining_uint32_domain_argument':'All states above 65535 differ from27/28, producing UINT32_MAX, rejected by unsigned row<2.','row_stride_bytes':20,'field_offsets':fields,'max_word_offset':36,'extent_bytes':40,'native_disassembly_sha256':hashlib.sha256((P/'native.txt').read_bytes()).hexdigest(),'limits':['Proves the row admission block and arithmetic domain.','Complete dataflow through all call clobbers and table consumers, null avoidance and relocated dispatcher remain open.']};(P/'row-domain-receipt.json').write_text(json.dumps(r,indent=2)+'\n');print(r)
