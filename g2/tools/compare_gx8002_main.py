#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Check main's startup, nonzero tick loop and zero-return shutdown sequence."""
import json,re,struct,subprocess
from build_gx8002_main_candidate import ROOT,IMAGE,BINDINGS,build
from verify_gx8002_memcpy_source import decode
MASK=0xffffffff

def execute(code,pc,delta,ticks,seed=0,prefix=False):
    r={f'r{i}':(seed+i*0x1020304)&MASK for i in range(32)};r['r14']=0x2002f7fc
    initial=r.copy();saved=None;local={};trace=[];index=0
    for _ in range(200000):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];next_pc=pc+width
        if op=='push':
            if saved is not None or args not in ('r15','r4, r15'):raise ValueError('main frame')
            names=(15,) if args=='r15' else (4,15);saved={n:r[f'r{n}'] for n in names};r['r14']-=4*len(names)
        elif op in ('subi','addi'):
            if p[:2]!=['r14','r14']:raise ValueError('main stack adjustment')
            r['r14']+=int(p[2],0)*(1 if op=='addi' else -1)
        elif op in ('st.w','ld.w'):
            if args!='r0, (r14, 0x0)' or r['r14']!=initial['r14']-8 or len(saved)!=1:raise ValueError('main local')
            if op=='st.w':local[r['r14']]=r['r0']
            else:r['r0']=local[r['r14']]
        elif op=='movi':r[p[0]]=int(p[1],0)
        elif op=='mov':r[p[0]]=r[p[1]]
        elif op=='bsr':
            if saved is None or r['r14']!=initial['r14']-8:raise ValueError('main call frame')
            target=int(args,0)+delta
            if target not in BINDINGS.values():raise ValueError('unknown main helper')
            if target==BINDINGS['LvpModeTick'] and index==len(ticks):
                if prefix:return {'trace':trace,'tick_checkpoint':True}
                raise ValueError('missing tick result')
            if target==BINDINGS['LvpInitMode'] and r['r0']!=1:raise ValueError('wrong initial mode')
            trace.append(['call',target,[r['r0']] if target==BINDINGS['LvpInitMode'] else []])
            for i in (0,1,2,3,12,13,15,*range(18,32)):r[f'r{i}']=(seed^0xcafe0000^i)&MASK
            if target==BINDINGS['LvpModeTick']:r['r0']=ticks[index];index+=1
        elif op=='bnez':
            if r[p[0]]:next_pc=int(p[1],0)
        elif op=='br':next_pc=int(args,0)
        elif op=='pop':
            if saved is None or args!=('r15' if len(saved)==1 else 'r4, r15') or r['r14']!=initial['r14']-4*len(saved):raise ValueError('main return frame')
            for n,v in saved.items():r[f'r{n}']=v
            r['r14']+=4*len(saved)
            if any(r[f'r{i}']!=initial[f'r{i}'] for i in (*range(4,12),14,15,16,17)):raise ValueError('main ABI')
            if index!=len(ticks):raise ValueError('unused tick results')
            return {'trace':trace,'result':r['r0']}
        else:raise ValueError('unknown main instruction '+op)
        pc=next_pc
    raise ValueError('main execution bound')

def expected(ticks,terminate=True):
    t=[['call',BINDINGS[n],[1] if n=='LvpInitMode' else []] for n in ('LvpSystemInit','LvpInitMode','LvpInitializeAppEvent')]
    for result in ticks:
        t.append(['call',BINDINGS['LvpModeTick'],[]])
        if result:t.append(['call',BINDINGS['LvpAppEventTick'],[]])
    if terminate:t.append(['call',BINDINGS['LvpSystemDone'],[]])
    return t

def verify():
    evidence=build();out=ROOT/'build/gx8002-board';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');w=out/'main-stock.elf'
    subprocess.run([pre+'objcopy','-I','binary','-O','elf32-csky-little','-B','csky',str(IMAGE),str(w)],check=True)
    b=bytearray(w.read_bytes());struct.pack_into('<I',b,36,0x21006009);w.write_bytes(b)
    old=decode(subprocess.check_output([pre+'objdump','-D','--start-address=0x18328','--stop-address=0x18354',str(w)],text=True));new=decode((out/'main-candidate.disassembly.txt').read_text())
    cases=0
    for count in (0,1,2,3,7,31,255,1024):
     for value in (1,2,0x7fffffff,0x80000000,0xffffffff):
      ticks=[value]*count+[0]
      for seed in (0,0xffffffff,0x12345678):
       for code,entry,delta in ((old,0x18328,0x1000dfec),(new,0x10026314,0)):
        if execute(code,entry,delta,ticks,seed)!={'trace':expected(ticks),'result':0}:raise ValueError('main behavior')
       cases+=1
    prefixes=0
    for ticks in ([1],[0xffffffff]*3,[1,0x80000000]*16):
     for code,entry,delta in ((old,0x18328,0x1000dfec),(new,0x10026314,0)):
      if execute(code,entry,delta,ticks,prefix=True)!={'trace':expected(ticks,False),'tick_checkpoint':True}:raise ValueError('main loop prefix')
     prefixes+=1
    report={'build':evidence,'cases':cases,'nonterminating_prefix_checks':prefixes,'frame_bytes':8,'source_admitted':False,
            'limits':['Finite traces and continued-loop checkpoints with modeled returning helpers. A nonzero tick always returns to the next tick query; no hardware timing or system/mode dependency qualification.']}
    (ROOT/'docs/research/gx8002-main-comparison.json').write_text(json.dumps(report,indent=2)+'\n');print(cases,prefixes);return report
if __name__=='__main__':verify()
