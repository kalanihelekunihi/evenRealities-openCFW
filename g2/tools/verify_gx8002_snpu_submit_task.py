#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Decoded command-chain publication against independent state/call model."""
import json,re,shutil,struct,subprocess
from build_gx8002_snpu_submit_task_candidate import ROOT,IMAGE,build,sha
from model_gx8002_snpu_submit_task import Case,Model,expected,MASK,STATE
from verify_gx8002_memcpy_source import decode
from verify_gx8002_logging import check_paths
OFFSET=0xef8c
ADDRESS=0x10205a00
DELTA=0x101f6a74
HELPERS={0x10205898:'set_head',0x10205860:'get_completed',0x102055f4:'enable',0x102059e8:'flush_descriptor',0x10025664:'clean_range'}

def execute(code,pc,delta,case,cache_call=None,model=None,stack_top=0x2002f7fc):
    m=Model(case) if model is None else model;r={f'r{i}':(case.seed+i*0x1020304)&MASK for i in range(32)}
    r['r0']=case.descriptor;r['r14']=stack_top;initial=r.copy();saved=None;scratch={};condition=False
    def read(address):
        if address==initial['r14']-20:
            if address not in scratch:raise ValueError('submit uninitialized scratch')
            return scratch[address]
        return m.read(address)
    def write(address,value):
        if address==initial['r14']-20:scratch[address]=value
        else:m.write(address,value)
    for _ in range(100):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];nxt=pc+width
        if op=='push':
            if args!='r4-r6, r15' or saved is not None:raise ValueError('submit frame')
            saved={f'r{i}':r[f'r{i}'] for i in (4,5,6,15)};r['r14']-=16
        elif op in ('movi','lrw'):r[p[0]]=int(p[1],0)&MASK
        elif op=='mov':r[p[0]]=r[p[1]]
        elif op in ('addi','subi','addu','and','lsli'):
            a=r[p[1]] if len(p)==3 else r[p[0]];x=p[-1];b=r[x] if x in r else int(x,0)
            v=a+b if op in ('addi','addu') else a-b if op=='subi' else a&b if op=='and' else a<<b
            r[p[0]]=v&MASK
        elif op=='bmaski':r[p[0]]=(1<<int(p[1],0))-1
        elif op=='zext':r[p[0]]=(r[p[1]]>>int(p[3],0))&((1<<(int(p[2],0)-int(p[3],0)+1))-1)
        elif op in ('ld.w','st.w'):
            match=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args)
            if not match:raise ValueError('submit memory operand')
            reg,base,offset=match.groups();address=(r[base]+int(offset,0))&MASK
            if op=='ld.w':r[reg]=read(address)
            else:write(address,r[reg])
        elif op=='cmpnei':condition=r[p[0]]!=int(p[1],0)
        elif op in ('bt','br'):
            if op=='br' or condition:nxt=int(args,0)
        elif op in ('bez','bnez'):
            if (r[p[0]]==0)==(op=='bez'):nxt=int(p[1],0)
        elif op=='bsr':
            if saved is None or r['r14']!=initial['r14']-20:raise ValueError('submit call frame')
            target=(int(args,0)+delta)&MASK
            if target not in HELPERS:raise ValueError('submit call target')
            name=HELPERS[target]
            if cache_call is not None and name in ('clean_range','flush_descriptor'):
                cache_call(name,r['r0'],r['r1'],r['r14'],m.trace)
            if name=='get_completed':
                if r['r1']!=r['r14']:raise ValueError('submit scratch pointer')
                m.call(name,r['r0']);scratch[r['r1']]=case.completed
            elif name in ('set_head','clean_range'):m.call(name,r['r0'],r['r1'])
            else:m.call(name,r['r0'])
            for i in (0,1,2,3,12,13,15,*range(18,32)):r[f'r{i}']=(case.seed^m.calls*0x1234567^i)&MASK
        elif op=='pop':
            if saved is None or args!='r4-r6, r15' or r['r14']!=initial['r14']-16:raise ValueError('submit return frame')
            r.update(saved);r['r14']+=16
            if any(r[f'r{i}']!=initial[f'r{i}'] for i in (*range(4,12),14,15,16,17)):raise ValueError('submit ABI')
            return m.trace,m.words
        else:raise ValueError('submit unknown instruction '+op)
        pc=nxt
    raise ValueError('submit execution bound')

def programs():
    out=ROOT/'build/gx8002-board';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');w=out/'snpu-submit-task-stock.elf'
    subprocess.run([pre+'objcopy','-I','binary','-O','elf32-csky-little','-B','csky',str(IMAGE),str(w)],check=True)
    b=bytearray(w.read_bytes());struct.pack_into('<I',b,36,0x21006009);w.write_bytes(b)
    old=decode(subprocess.check_output([pre+'objdump','-D','--start-address=0xef8c','--stop-address=0xf01c',str(w)],text=True))
    return old,decode((out/'snpu-submit-task-candidate.disassembly.txt').read_text())

def verify(prefix=None,sdk=None,output=None):
    check_paths(prefix,sdk);evidence=build();old,new=programs();cases=0
    for descriptor in (0x20027360,0x20027870,0x20029000):
        for previous in (0,0x20028000):
            for state in (0,1,2,MASK):
                for completed in (0,0x40000):
                    for mutation in (False,True):
                        for seed in (0,MASK,0x12345678,*[1<<i for i in range(32)]):
                            case=Case(descriptor,previous,state,completed,seed,mutation,seed);wanted=expected(case)
                            if execute(old,OFFSET,DELTA,case)!=wanted or execute(new,ADDRESS,0,case)!=wanted:raise ValueError('submit trace/state mismatch')
                            cases+=1
    if not evidence['fits']:raise ValueError('submit envelope')
    row={k:evidence[k] for k in ('symbol','section_name','compiled_bytes','compiled_sha256')}
    row['stock_occurrences']=[{'symbol':evidence['symbol'],'package_offset':OFFSET,'bytes':144,'sha256':evidence['stock_sha256'],'region':'image_a_xip_text'}]
    if output:
        output.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/'build/gx8002-board/snpu-submit-task-candidate.elf',output/'snpu-submit-task.elf')
    return {'functions':[row],'evidence':evidence,'model_sha256':sha((ROOT/'tools/model_gx8002_snpu_submit_task.py').read_bytes()),'cases':cases,'source_admitted':True,'hardware_qualified':False,'limits':['Ordered state and link reads/writes, helper calls and live pointer changes, caller clobbers and 20-byte frame. Scratch rewrite is local; void return ignored. Hardware cache coherence and full task composition remain separate.']}
if __name__=='__main__':(ROOT/'docs/research/gx8002-snpu-submit-task-verification.json').write_text(json.dumps(verify(),indent=2)+'\n')
