# SPDX-License-Identifier: MIT
"""Decode upstream/stock cache disable and check ordered barriers/MMIO/ABI."""
import json,re,subprocess,random
from build_gx8002_dcache_disable_upstream_candidate import build,ROOT,IMAGE,IMAGE_SHA,sha
from build_transparent_image import Elf32
from verify_gx8002_memcpy_source import decode

def execute(code,entry,value,seed):
    r={f'r{i}':(seed+i*0x1020304)&0xffffffff for i in range(32)};initial=r.copy();trace=[];pc=entry
    for _ in range(32):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')]
        if op=='sync':trace.append(['sync'])
        elif op in ('lrw','movi'):r[p[0]]=int(p[1],0)
        elif op=='bclri':r[p[0]]&=~(1<<int(p[1],0))
        elif op=='andni':r[p[0]]=r[p[1]]&~int(p[2],0)
        elif op in ('ld.w','st.w'):
            m=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args)
            if not m:raise ValueError('memory operand')
            reg,base,offset=m.groups();address=r[base]+int(offset,0)
            if op=='ld.w':
                assert address==0xe000f000;r[reg]=value;trace.append(['read',address,value])
            else:trace.append(['write',address,r[reg]])
        elif op=='rts':
            assert all(r[f'r{i}']==initial[f'r{i}'] for i in (*range(4,12),*range(14,18)))
            return trace
        else:raise ValueError(('unknown instruction',op))
        pc+=width
    raise ValueError('execution bound')

def verify():
    candidate=build();assert candidate['fits'] and sha(IMAGE.read_bytes())==IMAGE_SHA
    stock=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(stock.read_bytes(),'stock')
    assert sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))==IMAGE_SHA
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    old=decode(subprocess.check_output([pre,'-D','--start-address=0x175f8','--stop-address=0x1761c',str(stock)],text=True))
    new=decode(subprocess.check_output([pre,'-d',str(ROOT/'build/gx8002-board/dcache-disable-upstream-candidate.elf')],text=True))
    randomizer=random.Random(0x175f8);values=[0,1,0xffffffff,0xfffffffe,*[1<<i for i in range(32)],*[randomizer.getrandbits(32) for _ in range(4096)]]
    for value in values:
        expected=[['sync'],['sync'],['read',0xe000f000,value],['write',0xe000f000,value&0xfffffffe],['write',0xe000f004,1],['sync'],['sync']]
        for code,entry in ((old,0x175f8),(new,0x100255e4)):
            assert execute(code,entry,value,value^0x98765432)==expected
    return {'candidate':candidate,'cases':len(values),'source_admitted':False,'limits':['Ordered decoded barriers/register accesses and leaf ABI checked. No physical cache-coherence or timing qualification; caller integration remains pending.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-dcache-disable-upstream-verification.json').write_text(json.dumps(r,indent=2)+'\n');print(r['cases'])
