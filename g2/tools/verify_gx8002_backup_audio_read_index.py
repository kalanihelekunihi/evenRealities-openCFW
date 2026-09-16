# SPDX-License-Identifier: MIT
"""Decoded unsigned read-index arithmetic, writes and return contract."""
import json,re
from itertools import product
from build_gx8002_backup_audio_read_index import build,ROOT
from verify_gx8002_memcpy_source import decode
MASK=0xffffffff

def execute(code,read,write,offset):
    r={f'r{i}':0xabc00000+i for i in range(32)};r['r0']=offset;initial=r.copy();memory={0x2002d75c:read,0x2002d760:write};pc=0x1000a3fc;condition=False;trace=[]
    for _ in range(25):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];nxt=pc+width
        if op in ('lrw','movi'):r[p[0]]=int(p[1],0)
        elif op=='addu':r[p[0]]=(r[p[0]]+r[p[1]])&MASK
        elif op=='subi':r[p[0]]=(r[p[0]]-int(p[1],0))&MASK
        elif op=='cmphs':condition=r[p[0]]>=r[p[1]]
        elif op in ('br','bf'):
            if op=='br' or not condition:nxt=int(p[0],0)
        elif op in ('ld.w','st.w'):
            reg,base,off=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args).groups();address=r[base]+int(off,0)
            if op=='ld.w':r[reg]=memory[address];trace.append(('read',address,r[reg]))
            else:memory[address]=r[reg];trace.append(('write',address,r[reg]))
        elif op=='rts':
            assert all(r[f'r{i}']==initial[f'r{i}'] for i in (*range(4,12),14,15,16,17));return r['r0'],memory,trace
        else:raise AssertionError((op,args))
        pc=nxt
    raise AssertionError('bound')

def verify():
    evidence=build();assert evidence['exact_stock'];code=decode((ROOT/'build/gx8002-backup-audio-read-index/index.disassembly.txt').read_text());cases=0
    values=(0,1,2,3,4,127,128,255,256,0x7fffffff,0x80000000,0xfffffffe,MASK)
    for read,write,offset in product(values,repeat=3):
        next_index=(read+offset)&MASK;ok=next_index<=write
        expected_trace=[('read',0x2002d75c,read),('read',0x2002d760,write)]+([('write',0x2002d75c,next_index)] if ok else [])
        assert execute(code,read,write,offset)==(0 if ok else MASK,{0x2002d75c:next_index if ok else read,0x2002d760:write},expected_trace);cases+=1
    report={'build':evidence,'cases':cases,'source_admitted':False,'limits':['Compiled bytes equal stock at the same runtime entry; modeled unsigned arithmetic and ordered state accesses verified.', 'Concurrent audio/DMA updates and hardware behavior unqualified; storage remains unowned.']}
    (ROOT/'docs/research/gx8002-backup-audio-read-index-verification.json').write_text(json.dumps(report,indent=2)+'\n');return report
if __name__=='__main__':print(verify()['cases'])
