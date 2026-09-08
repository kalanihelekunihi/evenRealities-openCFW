#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Decoded asynchronous task submission against independent state/call model."""
import json,re,shutil,struct,subprocess
from build_gx8002_snpu_run_task_candidate import ROOT,IMAGE,build,sha
from model_gx8002_snpu_run_task import Case,Model,expected,MASK,STATE
from verify_gx8002_memcpy_source import decode
from verify_gx8002_logging import check_paths
OFFSET=0xf2ec
ADDRESS=0x10205d60
DELTA=0x101f6a74
HELPERS={0x1020599c:'resume',0x10205a00:'submit'}

def execute(code,pc,delta,case,model=None,call_hook=None):
    m=Model(case) if model is None else model;r={f'r{i}':(case.seed+i*0x1020304)&MASK for i in range(32)}
    r['r0']=case.task;r['r1']=case.callback;r['r2']=case.private;r['r14']=0x2002f7fc;initial=r.copy();saved=None;scratch={};condition=False
    read=m.read;write=m.write
    for _ in range(100):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];nxt=pc+width
        if op=='push':
            if args!='r4, r15' or saved is not None:raise ValueError('submit frame')
            saved={f'r{i}':r[f'r{i}'] for i in (4,15)};r['r14']-=8
        elif op in ('movi','lrw'):r[p[0]]=int(p[1],0)&MASK
        elif op=='mov':r[p[0]]=r[p[1]]
        elif op in ('addi','subi','addu','and','lsli'):
            a=r[p[1]] if len(p)==3 else r[p[0]];x=p[-1];b=r[x] if x in r else int(x,0)
            v=a+b if op in ('addi','addu') else a-b if op=='subi' else a&b if op=='and' else a<<b
            r[p[0]]=v&MASK
        elif op=='mult':
            a=r[p[1]] if len(p)==3 else r[p[0]];r[p[0]]=(a*r[p[-1]])&MASK
        elif op=='mula.32.l':r[p[0]]=(r[p[0]]+r[p[1]]*r[p[2]])&MASK
        elif op=='divs':
            a=r[p[1]];b=r[p[2]];a=a if a<0x80000000 else a-0x100000000;b=b if b<0x80000000 else b-0x100000000
            r[p[0]]=((abs(a)//abs(b))*(-1 if (a<0)!=(b<0) else 1))&MASK
        elif op=='subu':
            a=r[p[1]] if len(p)==3 else r[p[0]];r[p[0]]=(a-r[p[-1]])&MASK
        elif op=='str.w':
            match=re.fullmatch(r'(r\d+), \((r\d+), (r\d+) << (\d+)\)',args)
            if not match:raise ValueError('run indexed store')
            reg,base,index,shift=match.groups();write((r[base]+(r[index]<<int(shift)))&MASK,r[reg])
        elif op=='bmaski':r[p[0]]=(1<<int(p[1],0))-1
        elif op=='zext':r[p[0]]=(r[p[1]]>>int(p[3],0))&((1<<(int(p[2],0)-int(p[3],0)+1))-1)
        elif op in ('ld.w','st.w'):
            match=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args)
            if not match:raise ValueError('submit memory operand')
            reg,base,offset=match.groups();address=(r[base]+int(offset,0))&MASK
            if op=='ld.w':r[reg]=read(address)
            else:write(address,r[reg])
        elif op=='cmpne':condition=r[p[0]]!=r[p[1]]
        elif op=='bf':
            if not condition:nxt=int(args,0)
        elif op=='cmpnei':condition=r[p[0]]!=int(p[1],0)
        elif op in ('bt','br'):
            if op=='br' or condition:nxt=int(args,0)
        elif op in ('bez','bnez'):
            if (r[p[0]]==0)==(op=='bez'):nxt=int(p[1],0)
        elif op=='bsr':
            if saved is None or r['r14']!=initial['r14']-8:raise ValueError('submit call frame')
            target=(int(args,0)+delta)&MASK
            if target not in HELPERS:raise ValueError('submit call target')
            name=HELPERS[target]
            if call_hook is not None:call_hook(name,r['r0'],r['r14'],m)
            elif name=='resume':m.call(name)
            else:m.call(name,r['r0'])
            for i in (0,1,2,3,12,13,15,*range(18,32)):r[f'r{i}']=(case.seed^m.calls*0x1234567^i)&MASK
        elif op=='pop':
            if saved is None or args!='r4, r15' or r['r14']!=initial['r14']-8:raise ValueError('submit return frame')
            r.update(saved);r['r14']+=8
            if any(r[f'r{i}']!=initial[f'r{i}'] for i in (*range(4,12),14,15,16,17)):raise ValueError('submit ABI')
            return m.trace,m.words,r['r0']
        elif op=='rts':
            if saved is not None or any(r[f'r{i}']!=initial[f'r{i}'] for i in (*range(4,12),14,15,16,17)):raise ValueError('run leaf ABI')
            return m.trace,m.words,r['r0']
        else:raise ValueError('submit unknown instruction '+op)
        pc=nxt
    raise ValueError('submit execution bound')

def programs():
    out=ROOT/'build/gx8002-board';pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');w=out/'snpu-run-task-stock.elf'
    subprocess.run([pre+'objcopy','-I','binary','-O','elf32-csky-little','-B','csky',str(IMAGE),str(w)],check=True)
    b=bytearray(w.read_bytes());struct.pack_into('<I',b,36,0x21006009);w.write_bytes(b)
    old=decode(subprocess.check_output([pre+'objdump','-D','--start-address=0xf2ec','--stop-address=0xf3b4',str(w)],text=True))
    return old,decode((out/'snpu-run-task-candidate.disassembly.txt').read_text())

def verify(prefix=None,sdk=None,output=None):
    check_paths(prefix,sdk);evidence=build();old,new=programs();cases=0
    for start in range(10):
        for end in range(10):
            for state in (0,1,2):
                for mutation in (False,True):
                    for seed in (0,MASK,0x12345678):
                        case=Case(start=start,end=end,state=state,seed=seed,mutation=mutation);wanted=expected(case)
                        if execute(old,OFFSET,DELTA,case)!=wanted or execute(new,ADDRESS,0,case)!=wanted:raise ValueError('run task trace/state mismatch')
                        cases+=1
    for case in (Case(task=0),Case(registers=0)):
        wanted=expected(case)
        if execute(old,OFFSET,DELTA,case)!=wanted or execute(new,ADDRESS,0,case)!=wanted:raise ValueError('run task rejection mismatch')
        cases+=1
    if not evidence['fits']:raise ValueError('submit envelope')
    row={k:evidence[k] for k in ('symbol','section_name','compiled_bytes','compiled_sha256')}
    row['stock_occurrences']=[{'symbol':evidence['symbol'],'package_offset':OFFSET,'bytes':200,'sha256':evidence['stock_sha256'],'region':'image_a_xip_text'}]
    if output:
        output.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/'build/gx8002-board/snpu-run-task-candidate.elf',output/'snpu-run-task.elf')
    return {'functions':[row],'evidence':evidence,'model_sha256':sha((ROOT/'tools/model_gx8002_snpu_run_task.py').read_bytes()),'cases':cases,'source_admitted':True,'hardware_qualified':False,'limits':['All valid ring indices, ordered task/state writes and reads, helper changes and ABI. Helper bodies modeled; full composed execution remains pending. Negative/out-of-range indices excluded.']}
if __name__=='__main__':(ROOT/'docs/research/gx8002-snpu-run-task-verification.json').write_text(json.dumps(verify(),indent=2)+'\n')
