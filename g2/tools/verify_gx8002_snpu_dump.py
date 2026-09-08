#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Compare dump reads and printf calls under helper clobbers/changing memory."""
import json,re,struct,subprocess
from build_gx8002_snpu_overtime_candidate import ROOT,IMAGE,build
from verify_gx8002_memcpy_source import decode
MASK=0xffffffff
ADDRESS=0x10205ad8
OFFSET=0xf064
DELTA=0x101f6a74
FORMAT=0x1020ac0e
NEWLINE=0x1020b7c2

def read_value(seed,index,calls,changing):return (seed^(index*0x1020304)^(calls*0x9e3779b9 if changing else 0))&MASK

def expected(base,seed,changing):
    trace=[];calls=0
    for index in range(32):
        value=read_value(seed,index,calls,changing);trace.extend([['read',base+index*4,value],['printf',FORMAT,value]]);calls+=1
        if (index+1)%10==0:trace.append(['printf',NEWLINE]);calls+=1
    trace.append(['printf',NEWLINE]);calls+=1
    return trace,(seed^calls^0xcafe0000)&MASK

def execute(code,pc,delta,base,seed,changing,read_word=None,print_call=None,stack_top=0x2002f7fc):
    r={f'r{i}':(seed+i*0x1020304)&MASK for i in range(32)};r['r0']=base;r['r14']=stack_top;initial=r.copy();saved=None;condition=False;trace=[];calls=0
    for _ in range(1000):
        op,args,width=code[pc];p=[v.strip() for v in args.split(',')];nxt=pc+width
        if op=='push':
            if saved is not None or args!='r4-r8, r15':raise ValueError('dump frame')
            saved={f'r{i}':r[f'r{i}'] for i in (*range(4,9),15)};r['r14']-=24
        elif op in ('lrw','movi'):r[p[0]]=int(p[1],0)
        elif op=='mov':r[p[0]]=r[p[1]]
        elif op in ('addi','subi'):
            value=r[p[0]] if len(p)==2 else r[p[1]];amount=int(p[-1],0);r[p[0]]=(value+(amount if op=='addi' else -amount))&MASK
        elif op in ('subu','mult'):
            left=r[p[0]] if len(p)==2 else r[p[1]];right=r[p[-1]];r[p[0]]=(left-right if op=='subu' else left*right)&MASK
        elif op=='divs':
            a=r[p[1]];a=a if a<0x80000000 else a-0x100000000;b=r[p[2]];b=b if b<0x80000000 else b-0x100000000
            if not b:raise ValueError('dump divide zero')
            r[p[0]]=((abs(a)//abs(b))*(-1 if (a<0)!=(b<0) else 1))&MASK
        elif op=='ld.w':
            match=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args)
            if not match:raise ValueError('dump load operand')
            reg,pointer,offset=match.groups();address=(r[pointer]+int(offset,0))&MASK
            if address&3 or not base<=address<base+128:raise ValueError('dump read bounds')
            value=read_word(address) if read_word else read_value(seed,(address-base)//4,calls,changing);r[reg]=value;trace.append(['read',address,value])
        elif op=='cmpne':condition=r[p[0]]!=r[p[1]]
        elif op=='cmpnei':condition=r[p[0]]!=int(p[1],0)
        elif op in ('bt','bf'):
            if condition==(op=='bt'):nxt=int(args,0)
        elif op in ('bez','bnez'):
            if (r[p[0]]==0)==(op=='bez'):nxt=int(p[1],0)
        elif op=='br':nxt=int(args,0)
        elif op=='bsr':
            if ((int(args,0)+delta)&MASK)!=0x10206c24:raise ValueError('dump helper target')
            if saved is None or r['r14']!=initial['r14']-24:raise ValueError('dump call frame')
            if r['r0']==FORMAT:trace.append(['printf',FORMAT,r['r1']])
            elif r['r0']==NEWLINE:trace.append(['printf',NEWLINE])
            else:raise ValueError('dump format pointer')
            returned=print_call(r['r0'],r['r1']) if print_call else None
            calls+=1
            for i in (0,1,2,3,12,13,15,*range(18,32)):r[f'r{i}']=(seed^0xbeef0000^calls^i)&MASK
            r['r0']=returned if print_call else (seed^calls^0xcafe0000)&MASK
        elif op=='pop':
            if saved is None or args!='r4-r8, r15' or r['r14']!=initial['r14']-24:raise ValueError('dump return frame')
            r.update(saved);r['r14']+=24
            if any(r[f'r{i}']!=initial[f'r{i}'] for i in (*range(4,12),14,15,16,17)):raise ValueError('dump ABI')
            return trace,r['r0']
        else:raise ValueError('dump unknown instruction '+op)
        pc=nxt
    raise ValueError('dump execution bound')

def verify():
    evidence=build();out=ROOT/'build/gx8002-board';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');w=out/'snpu-dump-stock.elf'
    subprocess.run([pre+'objcopy','-I','binary','-O','elf32-csky-little','-B','csky',str(IMAGE),str(w)],check=True);b=bytearray(w.read_bytes());struct.pack_into('<I',b,36,0x21006009);w.write_bytes(b)
    old=decode(subprocess.check_output([pre+'objdump','-D','--start-address=0xf064','--stop-address=0xf0a8',str(w)],text=True));new=decode((out/'snpu-overtime-candidate.disassembly.txt').read_text());cases=0
    for base in (0x20030000,0x21000080,0x22001000):
        for seed in (0,MASK,0x12345678,*[1<<i for i in range(32)],*[MASK^(1<<i) for i in range(32)]):
            for changing in (False,True):
                wanted=expected(base,seed,changing)
                if execute(old,OFFSET,DELTA,base,seed,changing)!=wanted or execute(new,ADDRESS,0,base,seed,changing)!=wanted:raise ValueError('dump read/printf/return mismatch')
                cases+=1
    return {'evidence':evidence,'cases':cases,'frame_bytes':24,'source_admitted':False,'dump_qualified':True,'limits':['Dump-only qualification. Overtime reset remains unqualified; combined ELF must not yet be admitted. Exactly32 aligned readable words, changing read values at printf boundaries, helper clobbers and observed final printf r0 checked. Pointer validity outside modeled memory and physical timing unqualified.']}
if __name__=='__main__':(ROOT/'docs/research/gx8002-snpu-dump-verification.json').write_text(json.dumps(verify(),indent=2)+'\n')
