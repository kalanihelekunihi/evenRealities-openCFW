# SPDX-License-Identifier: MIT
"""Symbolic command values through all finite residual cache-loop lengths."""
import json,re
from verify_gx8002_dcache_invalid_loop import verify as qualify,add,const,expression,ROOT
from verify_gx8002_dcache_invalid_range import programs,signed

def tail(code,start,command_register,port_register,remaining):
    r={f'r{i}':expression(f'initial_r{i}') for i in range(32)}
    r[command_register]=expression('command');r[port_register]=const(0xe000f000);r['r1']=const(remaining)
    initial={k:v.copy() for k,v in r.items()};pc=start;writes=[]
    for _ in range(64):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];nxt=pc+width
        if op=='addu':r[p[0]]=add(r[p[0]],r[p[1]])
        elif op=='subu':r[p[0]]=add(r[p[1]],{k:(-v)&0xffffffff for k,v in r[p[2]].items()})
        elif op=='subi':r[p[0]]=add(r[p[0]],const(-int(p[1],0)))
        elif op=='lrw':r[p[0]]=const(int(p[1],0))
        elif op=='bhz':
            assert set(r[p[0]])<={'constant'}
            if signed(r[p[0]].get('constant',0))>0:nxt=int(p[1],0)
        elif op=='br':nxt=int(args,0)
        elif op=='st.w':
            m=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args);assert m
            reg,base,off=m.groups();assert add(r[base],const(int(off,0)))==const(0xe000f004)
            writes.append(r[reg].copy())
        elif op=='rts':
            assert all(r[f'r{i}']==initial[f'r{i}'] for i in (*range(4,12),*range(14,18)))
            count=(remaining+15)//16 if remaining>0 else 0
            assert writes==[add(expression('command'),const(16*i)) for i in range(count)]
            return count
        else:raise ValueError(('unexpected tail instruction',op,args))
        pc=nxt
    raise ValueError('tail bound')

def sequence(code,start,stop):
    rows=[];pc=start
    while pc<stop:
        op,args,width=code[pc];rows.append((op,args));pc+=width
    assert pc==stop
    return rows

def verify():
    evidence=qualify();old,new=programs()
    # Exact decoded setup establishes command=(pointer & ~15)|2 and leaves
    # signed size unchanged. All operations here are register-only.
    assert sequence(old,0x1761c,0x17628)==[('movi','r3, 0'),('subi','r3, 16'),('and','r0, r3'),('ori','r0, r0, 2'),('lrw','r3, 0xe000f000')]
    assert sequence(new,0x10025608,0x10025612)==[('andni','r0, r0, 15'),('ori','r3, r0, 2'),('lrw','r2, 0xe000f000')]
    for remaining in range(128):
        assert tail(old,0x1762e,'r0','r3',remaining)==tail(new,0x10025618,'r3','r2',remaining)
    for remaining in (-1,-128,-2147483648):
        assert tail(old,0x1762e,'r0','r3',remaining)==tail(new,0x10025618,'r3','r2',remaining)==0
    return {'bulk_evidence':evidence,'symbolic_residual_lengths':128,'negative_boundary_cases':3,'source_admitted':False,'limits':['Symbolic arbitrary command values cover all 128 positive-path residuals. Entry setup checked instruction-by-instruction. Bulk guard/decrease proof supplies positive-length termination. Negative sizes follow a no-store branch; tested boundary representatives are not an exhaustive symbolic signed-predicate proof. No hardware coherence/timing qualification.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-dcache-invalid-tail.json').write_text(json.dumps(r,indent=2)+'\n');print('All 128 residual lengths passed with symbolic command addresses')
