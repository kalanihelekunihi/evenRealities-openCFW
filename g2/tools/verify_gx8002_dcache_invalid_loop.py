# SPDX-License-Identifier: MIT
"""Symbolic affine effects of every decoded cache bulk-loop instruction.

Expressions are normalized linear polynomials modulo 2**32. This proves the
bulk transition for arbitrary register words, not physical cache behavior.
"""
import json
from verify_gx8002_dcache_invalid_range import verify as qualify,programs,ROOT
MASK=0xffffffff

def add(a,b):
    keys=set(a)|set(b)
    return {k:(a.get(k,0)+b.get(k,0))&MASK for k in keys if (a.get(k,0)+b.get(k,0))&MASK}
def const(n):return {'constant':n&MASK} if n&MASK else {}
def expression(name):return {name:1}

def block(code,start,end,command_register,port_register,guard):
    r={f'r{i}':expression(f'initial_r{i}') for i in range(32)}
    r[command_register]=expression('command');r['r1']=expression('size');r[port_register]=const(0xe000f000)
    initial={k:v.copy() for k,v in r.items()};writes=[];pc=start;instructions=0;back_edges=0
    import re
    while pc<end:
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];instructions+=1
        if op in ('addi','subi'):
            source=p[1] if len(p)==3 else p[0]
            n=int(p[-1],0)*(1 if op=='addi' else -1)
            r[p[0]]=add(r[source],const(n))
        elif op=='st.w':
            m=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args)
            assert m
            reg,base,offset=m.groups();assert add(r[base],const(int(offset,0)))==const(0xe000f004)
            writes.append(r[reg].copy())
        elif op=='br':
            assert pc+width==end and int(args,0)==guard
            back_edges+=1
        else:raise ValueError(('unexpected bulk instruction',op,args))
        pc+=width
    assert pc==end and back_edges==1
    assert writes==[add(expression('command'),const(16*i)) for i in range(8)]
    assert r[command_register]==add(expression('command'),const(128))
    assert r['r1']==add(expression('size'),const(-128))
    assert r[port_register]==initial[port_register]
    assert all(r[f'r{i}']==initial[f'r{i}'] for i in (*range(4,12),*range(14,18)))
    op,args,width=code[guard];assert op=='cmplti' and args=='r1, 128'
    branch=code[guard+width];assert branch[0]=='bf' and int(branch[1],0)==start
    return {'instructions':instructions,'writes_per_iteration':8,'command_increment':128,'size_decrement':128,'preserved_cache_port':0xe000f004}

def verify():
    evidence=qualify();old,new=programs()
    stock=block(old,0x1763a,0x1766c,'r0','r3',0x17628)
    source=block(new,0x10025624,0x10025656,'r3','r2',0x10025612)
    # Positive signed inputs strictly decrease by 128 without signed overflow.
    # The modulo address transition permits wraparound without changing order.
    bounds=[]
    for size in (128,129,255,256,0x10000001,0x40000000,0x7fffffff):
        iterations,remainder=divmod(size,128)
        assert 0<=remainder<128 and iterations*128+remainder==size
        bounds.append({'size':size,'bulk_iterations':iterations,'bulk_writes':8*iterations,'tail_remainder':remainder})
    return {'evidence':evidence,'stock_bulk':stock,'source_bulk':source,'large_input_decomposition':bounds,'source_admitted':False,'limits':['Normalized modulo-32 affine interpretation proves every bulk iteration for all command/size words. Signed guard and decreasing positive size justify finite repetition. Residual path remains covered by finite decoded tests; complete entry-to-return symbolic proof is not yet supplied. No hardware coherence or timing qualification.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-dcache-invalid-loop.json').write_text(json.dumps(r,indent=2)+'\n');print('Stock/source bulk transitions proved with symbolic modulo-32 expressions')
