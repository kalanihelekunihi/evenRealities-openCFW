# SPDX-License-Identifier: MIT
"""Prove the no-store path for the entire nonpositive signed-size interval."""
import json
from verify_gx8002_dcache_invalid_tail import verify as qualify
from verify_gx8002_dcache_invalid_loop import add,const,expression
from verify_gx8002_dcache_invalid_range import programs,ROOT

def nonpositive(code,guard,command_register,port_register):
    r={f'r{i}':expression(f'initial_r{i}') for i in range(32)}
    r['r1']=expression('size');r[command_register]=expression('command');r[port_register]=const(0xe000f000)
    initial={k:v.copy() for k,v in r.items()};pc=guard;condition=None;steps=0
    interval=(-2147483648,0)
    for _ in range(12):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];steps+=1;nxt=pc+width
        if op=='cmplti':
            assert p[0]=='r1' and r['r1']==expression('size') and int(p[1],0)==128
            assert interval[1]<128;condition=True
        elif op=='bf':
            assert condition is True
        elif op=='addu':r[p[0]]=add(r[p[0]],r[p[1]])
        elif op=='subu':r[p[0]]=add(r[p[1]],{k:(-v)&0xffffffff for k,v in r[p[2]].items()})
        elif op=='lrw':r[p[0]]=const(int(p[1],0))
        elif op=='bhz':
            assert p[0]=='r1' and r['r1']==expression('size') and interval[1]<=0
        elif op=='rts':
            assert all(r[f'r{i}']==initial[f'r{i}'] for i in (*range(4,12),*range(14,18)))
            return {'signed_interval':list(interval),'decoded_instructions':steps,'memory_accesses':0,'returns':True}
        else:raise ValueError(('unexpected nonpositive path',op,args))
        pc=nxt
    raise ValueError('nonpositive path bound')

def verify():
    evidence=qualify();old,new=programs()
    stock=nonpositive(old,0x17628,'r0','r3');source=nonpositive(new,0x10025612,'r3','r2')
    return {'positive_and_entry_evidence':evidence,'stock_nonpositive':stock,'source_nonpositive':source,'source_admitted':False,'limits':['Entire nonpositive signed-size interval follows a checked register-only return path. Positive bulk and all residual paths are qualified separately with symbolic command expressions. Architectural instruction semantics assumed; no physical coherence or timing qualification.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-dcache-invalid-signed.json').write_text(json.dumps(r,indent=2)+'\n');print('Entire signed nonpositive interval proved no-store and ABI preserving')
