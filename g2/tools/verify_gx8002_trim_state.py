# SPDX-License-Identifier: MIT
"""Decoded trim query/wrapper ordering, return masking and integer ABI."""
import json,random
from build_gx8002_trim_state_candidate import build,ROOT,IMAGE
from build_gx8002_trim_clock_enable_candidate import build as build_gate
from verify_gx8002_memcpy_source import decode
from build_transparent_image import Elf32


def verify(gate_runner=None):
    candidate=build();gate=build_gate();codes={}
    for name,offset in (('trim-state',0x16a30),('trim-clock-enable',0x16a24)):
        p=ROOT/f'build/gx8002-board/{name}-candidate.elf';e=Elf32(p.read_bytes(),name);data=e.contents(next(s for s in e.sections if s['name']=='.text'));assert data==IMAGE.read_bytes()[offset:offset+len(data)]
        codes[name]=decode((ROOT/f'build/gx8002-board/{name}-candidate.disassembly.txt').read_text())
    rng=random.Random(123);cases=0
    for value in [0,1,2,0xffffffff]+[rng.getrandbits(32) for _ in range(256)]:
        trace=[]
        def run(name,entry):
            r={f'r{i}':0x12340000+i for i in range(32)};r['r14']=0x20070000;initial=dict(r);pc=entry
            for _ in range(16):
                op,args,width=codes[name][pc];p=[v.strip() for v in args.split(',')]
                if op=='push':assert args=='r15';saved=r['r15'];r['r14']-=4
                elif op=='pop':
                    assert args=='r15';r['r15']=saved;r['r14']+=4;assert all(r[f'r{i}']==initial[f'r{i}'] for i in (*range(4,12),14,15,16,17));return r['r0']
                elif op in ('movi','movih'):r[p[0]]=int(p[1],0)<<(16 if op=='movih' else 0)
                elif op=='andi':r[p[0]]=r[p[1]]&int(p[2],0)
                elif op=='ld.w':assert args=='r0, (r3, 0x30)' and r['r3']==0xa0010000;r['r0']=value;trace.append(('read',0xa0010030,value))
                elif op=='bsr':
                    target=int(args,0)
                    if target==0x10024a10:run('trim-clock-enable',target)
                    else:
                        assert target==0x10025080;trace.append(('gate',r['r0'],r['r1']))
                        if gate_runner:gate_runner(r['r0'],r['r1'],value)
                    for i in (0,1,2,3,12,13,15,*range(18,32)):r[f'r{i}']=0xdead0000+i
                else:raise ValueError((op,args))
                pc+=width
            raise AssertionError('Execution bound')
        assert run('trim-state',0x10024a1c)==value&1
        assert trace==[('gate',9,1),('read',0xa0010030,value)];cases+=1
    return {'candidate':candidate,'gate':gate,'cases':cases,'source_admitted':False,'limits':['Both compiled bodies byte-exact to stock executable prefixes; decoded nested wrapper, gate arguments, read order, result and integer ABI checked. Actual gate programming remains modeled; hardware timing unqualified.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-trim-state.json').write_text(json.dumps(r,indent=2)+'\n');print(r['cases'])
