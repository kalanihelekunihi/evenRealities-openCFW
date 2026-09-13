# SPDX-License-Identifier: MIT
"""Exact upstream audio divider wrapper and decoded helper argument qualification."""
import json
from build_gx8002_audio_lowpower_divider_candidate import build,ROOT
from verify_gx8002_memcpy_source import decode

def verify(divider_runner=None, candidate=None):
    candidate=build() if candidate is None else candidate;assert candidate['compiled_bytes']==20 and candidate['compiled_sha256']==candidate['stock_sha256']
    code=decode((ROOT/'build/gx8002-board/audio-lowpower-divider-candidate.disassembly.txt').read_text());cases=0
    for poison in (0,1,0xffffffff,0xdead0000):
        r={f'r{i}':0x12340000+i for i in range(32)};r['r14']=0x20070000;initial=r.copy();pc=0x10025a00;calls=[]
        for _ in range(12):
            op,args,width=code[pc];p=[s.strip() for s in args.split(',')]
            if op=='push':assert args=='r15';saved=r['r15'];r['r14']-=4
            elif op=='pop':
                r['r15']=saved;r['r14']+=4;assert all(r[f'r{i}']==initial[f'r{i}'] for i in (*range(4,12),14,15,16,17));break
            elif op=='movi':r[p[0]]=int(p[1],0)
            elif op=='bsr':
                assert int(args,0)==0x10024df8;calls.append((r['r0'],r['r1']))
                if divider_runner is not None:divider_runner(r['r0'],r['r1'])
                for i in (0,1,2,3,12,13,15,*range(18,32)):r[f'r{i}']=(poison+i)&0xffffffff
            else:raise ValueError((op,args))
            pc+=width
        else:raise AssertionError('Execution bound')
        assert calls==[(7,0),(8,0)];cases+=1
    return {'candidate':candidate,'cases':cases,'source_admitted':False,'limits':['Authenticated upstream compiled wrapper is byte-exact; decoded call order, arguments and integer ABI checked under caller clobber patterns. Full decoded divider integration remains outstanding; physical timing unqualified.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-audio-lowpower-divider.json').write_text(json.dumps(r,indent=2)+'\n');print(r['cases'])
