#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Qualify SNPU initialization's ordered writes, calls, mutations and ABI."""
import json,re,shutil,struct,subprocess
from build_gx8002_snpu_initialize_candidate import ROOT,IMAGE,build
from verify_gx8002_memcpy_source import decode
from verify_gx8002_logging import check_paths
MASK=0xffffffff
DELTA=0x101f6a74
ADDRESS=0x10205cf4
OFFSET=0xf280
STATE=0x20027350
WRITES=((0x5c4,0xa0c00000),(0x5c8,0xa0300000),(0x5cc,0xa0c00190),(0x5b4,0),(0x5b0,0))
class Model:
    def __init__(self,seed,mutation):
        self.seed=seed;self.mutation=mutation;self.trace=[];self.calls=0
        self.memory={STATE+offset:(seed^offset)&MASK for offset in (0,*(o for o,v in WRITES))}
    def write(self,address,value):
        if address not in self.memory:raise ValueError('SNPU initialization write address')
        self.trace.append(['write',address,value]);self.memory[address]=value
    def call(self,target,arg0,arg1):
        if target==0x102055a8:self.trace.append(['device_init',arg0])
        elif target==0x102058d4:self.trace.append(['tcb_init'])
        elif target==0x102055b0:self.trace.append(['request_irq',arg0,arg1])
        else:raise ValueError('SNPU initialization helper')
        self.calls+=1
        if self.mutation=='all' or self.mutation=='last' and self.calls==3:
            for address in self.memory:
                self.memory[address]=(self.seed^address^self.calls)&MASK
                self.trace.append(['helper_write',address,self.memory[address]])
        elif self.mutation not in ('none','last'):raise ValueError('SNPU initialization mutation')

def expected(seed,mutation):
    m=Model(seed,mutation);m.call(0x102055a8,0xa0c00000,0)
    for offset,value in WRITES:m.write(STATE+offset,value)
    m.call(0x102058d4,0,0);m.call(0x102055b0,0x10205ce0,0);m.write(STATE,2)
    return m.trace,m.memory,0

def execute(code,pc,delta,seed,mutation):
    m=Model(seed,mutation);r={f'r{i}':(seed+i*0x1020304)&MASK for i in range(32)};r['r14']=0x2002f7fc;initial=r.copy();saved=None
    for _ in range(40):
        op,args,width=code[pc];p=[s.strip() for s in args.split(',')]
        if op=='push':
            if saved is not None or args!='r4-r5, r15':raise ValueError('SNPU initialization frame')
            saved={k:r[k] for k in ('r4','r5','r15')};r['r14']-=12
        elif op in ('movi','lrw'):r[p[0]]=int(p[1],0)
        elif op=='movih':r[p[0]]=(int(p[1],0)<<16)&MASK
        elif op=='mov':r[p[0]]=r[p[1]]
        elif op=='st.w':
            match=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args)
            if not match:raise ValueError('SNPU initialization store operand')
            reg,base,offset=match.groups();m.write((r[base]+int(offset,0))&MASK,r[reg])
        elif op=='bsr':
            if saved is None or r['r14']!=initial['r14']-12:raise ValueError('SNPU initialization call frame')
            m.call((int(args,0)+delta)&MASK,r['r0'],r['r1'])
            for i in (0,1,2,3,12,13,15,*range(18,32)):r[f'r{i}']=(seed^0xcafe0000^m.calls^i)&MASK
        elif op=='pop':
            if saved is None or args!='r4-r5, r15' or r['r14']!=initial['r14']-12:raise ValueError('SNPU initialization return frame')
            r.update(saved);r['r14']+=12
            if any(r[f'r{i}']!=initial[f'r{i}'] for i in (*range(4,12),14,15,16,17)):raise ValueError('SNPU initialization ABI')
            return m.trace,m.memory,r['r0']
        else:raise ValueError('SNPU initialization unknown instruction '+op)
        pc+=width
    raise ValueError('SNPU initialization execution bound')

def verify(prefix=None,sdk=None,output=None):
    check_paths(prefix,sdk);evidence=build();out=ROOT/'build/gx8002-board';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');w=out/'snpu-initialize-stock.elf'
    subprocess.run([pre+'objcopy','-I','binary','-O','elf32-csky-little','-B','csky',str(IMAGE),str(w)],check=True);b=bytearray(w.read_bytes());struct.pack_into('<I',b,36,0x21006009);w.write_bytes(b)
    old=decode(subprocess.check_output([pre+'objdump','-D','--start-address=0xf280','--stop-address=0xf2cc',str(w)],text=True));new=decode((out/'snpu-initialize-candidate.disassembly.txt').read_text());cases=0
    for seed in (0,MASK,0x12345678,*[1<<i for i in range(32)],*[MASK^(1<<i) for i in range(32)]):
        for mutation in ('none','all','last'):
            wanted=expected(seed,mutation)
            if execute(old,OFFSET,DELTA,seed,mutation)!=wanted or execute(new,ADDRESS,0,seed,mutation)!=wanted:raise ValueError('SNPU initialization trace/state/return mismatch')
            cases+=1
    if not evidence['fits']:raise ValueError('SNPU initialization envelope')
    row={k:evidence[k] for k in ('symbol','section_name','compiled_bytes','compiled_sha256')};row['stock_occurrences']=[{'symbol':evidence['symbol'],'package_offset':OFFSET,'bytes':76,'sha256':evidence['stock_sha256'],'region':'image_a_xip_text'}]
    if output:
        output.mkdir(parents=True,exist_ok=True);shutil.copyfile(out/'snpu-initialize-candidate.elf',output/'snpu-initialize.elf')
    return {'functions':[row],'evidence':evidence,'cases':cases,'source_admitted':True,'hardware_qualified':False,'limits':['Caller qualification only: ordered writes, exact helper/ISR arguments, helper mutations, caller clobbers and twelve-byte frame. TCB and ISR implementations remain separate recovery work. Offset-only state view does not own or fully describe driver state; no hardware qualification.']}
if __name__=='__main__':(ROOT/'docs/research/gx8002-snpu-initialize-verification.json').write_text(json.dumps(verify(),indent=2)+'\n')
