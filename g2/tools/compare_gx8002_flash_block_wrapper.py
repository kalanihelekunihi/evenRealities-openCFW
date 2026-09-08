#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Decoded wrapper ABI/call qualification with adversarial helper returns."""
import json,re,subprocess
from compare_gx8002_flash_block_bounds import ROOT,decode,MASK
SP=0x30001000

def execute(code,pc,delta,address,length,start,end,returns):
    r={f'r{i}':0x12340000+i for i in range(32)}
    r.update(r0=address,r1=length,r2=start,r3=end,r14=SP)
    initial=r.copy();stack={};calls=[];low=SP
    for _ in range(80):
        op,args,width=code[pc];p=[v.strip() for v in args.split(',')];n=pc+width
        if op in ('push','pop'):
            regs=[]
            for item in p:
                if '-' in item:
                    a,b=item.split('-');regs.extend(f'r{i}' for i in range(int(a[1:]),int(b[1:])+1))
                else:regs.append(item)
            if op=='push':
                r['r14']-=4*len(regs);low=min(low,r['r14'])
                for i,reg in enumerate(regs):stack[r['r14']+4*i]=r[reg]
            else:
                for i,reg in enumerate(regs):r[reg]=stack[r['r14']+4*i]
                r['r14']+=4*len(regs)
                if 'r15' in regs:
                    if r['r14']!=SP or any(r[f'r{i}']!=initial[f'r{i}'] for i in range(4,12)) or r['r15']!=initial['r15']:
                        raise ValueError('return ABI mismatch')
                    if SP-low!=20:raise ValueError('frame mismatch')
                    return r['r0'],calls
        elif op=='mov':r[p[0]]=r[p[1]]
        elif op in ('addi','subi','addu'):
            a=r[p[1]] if len(p)==3 else r[p[0]]
            b=r[p[-1]] if op=='addu' else int(p[-1],0)
            r[p[0]]=(a-b if op=='subi' else a+b)&MASK
            low=min(low,r['r14'])
        elif op=='bnez':
            if r[p[0]]:n=int(p[1],0)
        elif op=='bsr':
            if int(p[0],0)+delta!=0x100238a4:raise ValueError('wrong helper')
            if r['r14']!=SP-20:raise ValueError('frame mismatch')
            count=len(calls)
            if count>=len(returns):raise ValueError('extra call')
            if count==0:
                expected=[address,start,SP-20]
            else:expected=[(address+length-1)&MASK,SP-20,end]
            args_now=[r[f'r{i}'] for i in range(3)]
            if args_now!=expected:raise ValueError('call arguments mismatch')
            calls.append(args_now)
            stack[SP-20]=0xaabbccdd
            for i in (0,1,2,3,12,13,15):r[f'r{i}']=(0xcafe0000+i+count)&MASK
            r['r0']=returns[count]&MASK
        else:raise ValueError('unknown wrapper instruction '+op)
        pc=n
    raise ValueError('execution bound')

def verify():
    out=ROOT/'build/gx8002-board';pre=ROOT/'build/csky-macos/install/bin/csky-unknown-elf-'
    old=decode(subprocess.check_output([str(pre)+'objdump','-D','--start-address=0x15aa4','--stop-address=0x15acc',str(out/'block-range-stock.elf')],text=True))
    new=decode((out/'block-range-linked.disassembly.txt').read_text());cases=0
    for address in (0,1,4095,4096,0x7fffffff,0xffffffff):
      for length in (0,1,4096,0xffffffff):
       for returns in ((-1,),(7,),(0,0),(0,-1),(0,7)):
        for start,end in ((0x20028000,0x20028004),(0x20028000,0x20028000)):
         a=execute(old,0x15aa4,0x1000dfec,address,length,start,end,returns)
         b=execute(new,0x10023a90,0,address,length,start,end,returns)
         if a!=b or a[0]!=(returns[-1]&MASK) or len(a[1])!=len(returns):raise ValueError('wrapper result mismatch')
         cases+=1
    report={'decoded_wrapper_cases':cases,'frame_bytes':20,'helper_clobbers':[0,1,2,3,12,13,15],
            'limits':['Helper behavior qualified separately; no hardware qualification.']}
    (ROOT/'docs/research/gx8002-flash-block-wrapper-comparison.json').write_text(json.dumps(report,indent=2)+'\n')
    print(report);return report
if __name__=='__main__':verify()
