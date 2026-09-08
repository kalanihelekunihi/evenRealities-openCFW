#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Qualify live SNPU suspend state, helper order and bounded polling prefixes."""
import json,re,shutil,struct,subprocess
from build_gx8002_snpu_suspend_candidate import ROOT,IMAGE,build
from verify_gx8002_memcpy_source import decode
from verify_gx8002_logging import check_paths
MASK=0xffffffff
DELTA=0x101f6a74
ADDRESS=0x10205a90
OFFSET=0xf01c
STATE=0x20027350
POINTER=STATE+0x5c4
PTRS=(0xa0b00000,0x21000000)
class PrefixReached(Exception):pass
class Model:
    def __init__(self,seed,state,pointer,enabled,delay,mutation,prefix):
        self.seed=seed;self.memory={STATE:state,POINTER:pointer};self.enabled=enabled;self.delay=delay;self.mutation=mutation;self.prefix=prefix;self.polls=0;self.calls=0;self.trace=[]
    def read(self,address):
        if address not in self.memory:raise ValueError('SNPU suspend invalid state read')
        value=self.memory[address];self.trace.append(['read',address,value]);return value
    def write(self,address,value):
        if address!=STATE:raise ValueError('SNPU suspend invalid state write')
        self.memory[address]=value;self.trace.append(['write',address,value])
    def call(self,target,arg):
        names={0x1020560c:'is_enabled',0x10205600:'disable',0x102056e4:'all_idle',0x100251ec:'clock'}
        if target not in names:raise ValueError('SNPU suspend unknown helper')
        name=names[target];self.trace.append([name,arg]);self.calls+=1
        result=(self.seed^0xcafe0000^self.calls)&MASK
        if name=='is_enabled':result=self.enabled
        if name=='all_idle':
            result=(self.seed|1) if self.delay is not None and self.polls>=self.delay else 0;self.polls+=1
        # Changes are explicit helper-boundary scenarios, not asynchronous proof.
        if self.mutation=='alternate':
            self.memory[POINTER]=PTRS[self.calls%2];self.trace.append(['helper_write',POINTER,self.memory[POINTER]])
            self.memory[STATE]=(self.seed^self.calls)&MASK;self.trace.append(['helper_write',STATE,self.memory[STATE]])
        elif self.mutation=='clock_state' and name=='clock':
            self.memory[STATE]=MASK;self.trace.append(['helper_write',STATE,MASK])
        elif self.mutation not in ('none','clock_state'):raise ValueError('SNPU mutation mode')
        if self.prefix is not None and self.polls>=self.prefix:raise PrefixReached
        return result

def expected(seed,state,pointer,enabled,delay,mutation,prefix=None):
    m=Model(seed,state,pointer,enabled,delay,mutation,prefix)
    try:
        p=m.read(POINTER)
        if p==0:return m.trace,m.memory,MASK,'return'
        if m.read(STATE)==2:return m.trace,m.memory,0,'return'
        if m.call(0x1020560c,p)!=0:
            m.call(0x10205600,m.read(POINTER))
            while m.call(0x102056e4,m.read(POINTER))==0:pass
        m.call(0x100251ec,0);m.write(STATE,2)
        return m.trace,m.memory,0,'return'
    except PrefixReached:return m.trace,m.memory,None,'poll_prefix'

def execute(code,pc,delta,seed,state,pointer,enabled,delay,mutation,prefix=None):
    m=Model(seed,state,pointer,enabled,delay,mutation,prefix);r={f'r{i}':(seed+i*0x1020304)&MASK for i in range(32)};r['r14']=0x2002f7fc;initial=r.copy();saved=None;condition=False
    try:
        for _ in range(10000):
            op,args,width=code[pc];p=[v.strip() for v in args.split(',')];nxt=pc+width
            if op=='push':
                if saved is not None or args!='r4, r15':raise ValueError('SNPU suspend frame')
                saved={'r4':r['r4'],'r15':r['r15']};r['r14']-=8
            elif op in ('movi','lrw'):r[p[0]]=int(p[1],0)
            elif op=='subi':r[p[0]]=(r[p[0]]-int(p[1],0))&MASK
            elif op in ('ld.w','st.w'):
                match=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args)
                if not match:raise ValueError('SNPU suspend memory operand')
                reg,base,off=match.groups();address=(r[base]+int(off,0))&MASK
                if op=='ld.w':r[reg]=m.read(address)
                else:m.write(address,r[reg])
            elif op=='cmpnei':condition=r[p[0]]!=int(p[1],0)
            elif op=='bf':
                if not condition:nxt=int(args,0)
            elif op in ('bez','bnez'):
                if (r[p[0]]==0)==(op=='bez'):nxt=int(p[1],0)
            elif op=='br':nxt=int(args,0)
            elif op=='bsr':
                if saved is None or r['r14']!=initial['r14']-8:raise ValueError('SNPU suspend call frame')
                result=m.call((int(args,0)+delta)&MASK,r['r0'])
                for i in (0,1,2,3,12,13,15,*range(18,32)):r[f'r{i}']=(seed^0xcafe0000^(m.calls*7919)^i)&MASK
                r['r0']=result
            elif op=='pop':
                if saved is None or args!='r4, r15' or r['r14']!=initial['r14']-8:raise ValueError('SNPU suspend return frame')
                r.update(saved);r['r14']+=8
                if any(r[f'r{i}']!=initial[f'r{i}'] for i in (*range(4,12),14,15,16,17)):raise ValueError('SNPU suspend ABI')
                return m.trace,m.memory,r['r0'],'return'
            else:raise ValueError('unknown SNPU suspend instruction '+op)
            pc=nxt
    except PrefixReached:
        if saved is None or r['r14']!=initial['r14']-8:raise ValueError('SNPU suspend prefix frame')
        return m.trace,m.memory,None,'poll_prefix'
    raise ValueError('SNPU suspend execution bound')

def verify(prefix=None,sdk=None,output=None):
    check_paths(prefix,sdk);evidence=build();out=ROOT/'build/gx8002-board';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');w=out/'snpu-suspend-stock.elf'
    subprocess.run([pre+'objcopy','-I','binary','-O','elf32-csky-little','-B','csky',str(IMAGE),str(w)],check=True)
    b=bytearray(w.read_bytes());struct.pack_into('<I',b,36,0x21006009);w.write_bytes(b)
    old=decode(subprocess.check_output([pre+'objdump','-D','--start-address=0xf01c','--stop-address=0xf064',str(w)],text=True));new=decode((out/'snpu-suspend-candidate.disassembly.txt').read_text());cases=prefixes=0
    for seed in (0,MASK,0x12345678):
      for pointer in (0,*PTRS):
       for state in (0,1,2,3,0x7fffffff,0x80000000,MASK):
        for enabled in (0,1,0x80000000,MASK):
         for delay in (0,1,7,63):
          for mutation in ('none','alternate','clock_state'):
           args=(seed,state,pointer,enabled,delay,mutation);wanted=expected(*args)
           for code,pc,delta in ((old,OFFSET,DELTA),(new,ADDRESS,0)):
            if execute(code,pc,delta,*args)!=wanted:raise ValueError('SNPU suspend trace/state/return mismatch')
           cases+=1
      for pointer in PTRS:
       for mutation in ('none','alternate','clock_state'):
        for limit in (1,2,32):
         args=(seed,1,pointer,1,None,mutation,limit);wanted=expected(*args)
         for code,pc,delta in ((old,OFFSET,DELTA),(new,ADDRESS,0)):
          if execute(code,pc,delta,*args)!=wanted:raise ValueError('SNPU suspend polling prefix mismatch')
         prefixes+=1
    if not evidence['fits']:raise ValueError('SNPU suspend envelope')
    row={k:evidence[k] for k in ('symbol','section_name','compiled_bytes','compiled_sha256')};row['stock_occurrences']=[{'symbol':evidence['symbol'],'package_offset':OFFSET,'bytes':72,'sha256':evidence['stock_sha256'],'region':'image_a_xip_text'}]
    if output:
        output.mkdir(parents=True,exist_ok=True);shutil.copyfile(out/'snpu-suspend-candidate.elf',output/'snpu-suspend.elf')
    return {'functions':[row],'evidence':evidence,'cases':cases,'noncompletion_prefix_cases':prefixes,'frame_bytes':8,'source_admitted':True,'hardware_qualified':False,'limits':['Helper boundary model uses synthetic nonnull register pointers after the initial null check. Helpers may change pointer/state; their implementation and physical timing remain separate. Never-ready loop checked through32 polling prefixes. Full SNPU state layout remains unmodeled and is not source-owned by this function.']}
if __name__=='__main__':(ROOT/'docs/research/gx8002-snpu-suspend-verification.json').write_text(json.dumps(verify(),indent=2)+'\n')
