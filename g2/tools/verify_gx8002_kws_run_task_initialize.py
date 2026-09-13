# SPDX-License-Identifier: MIT
"""Decoded model initializer writes runner's shared local SNPU task."""
import json,re,subprocess
from verify_gx8002_kws_run_model_buffers import verify as qualify,ROOT,sha,Elf32,decode
from verify_gx8002_kws_run import expected
from execute_gx8002_kws_run import execute

def initialize(code,pointer,memory,saved):
    r={f'r{i}':0xabc00000+i for i in range(32)};r['r0']=pointer;initial=r.copy();pc=0;trace=[]
    for _ in range(40):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')]
        if op in ('movi','lrw'):r[p[0]]=int(p[1],0)
        elif op=='lsli':r[p[0]]=(r[p[1]]<<int(p[2],0))&0xffffffff
        elif op=='zext':
            hi,lo=map(int,p[2:]);r[p[0]]=(r[p[1]]>>lo)&((1<<(hi-lo+1))-1)
        elif op in ('ld.w','st.w'):
            reg,base,off=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args).groups();address=r[base]+int(off,0)
            if op=='ld.w':r[reg]=saved[address];trace.append(('read',address,r[reg]))
            else:assert pointer<=address<pointer+32;memory[address]=r[reg];trace.append(('write',address-pointer,r[reg]))
        elif op=='rts':
            assert r['r0']==0 and all(r[f'r{i}']==initial[f'r{i}'] for i in range(4,32));return trace
        else:raise ValueError(op)
        pc+=width
    raise ValueError('initializer bound')

def verify():
    evidence=qualify();path=ROOT/'build/gx8002-source-candidate/model/runtime_gx8002_model_interface.o';elf=Elf32(path.read_bytes(),'model');name='LvpCTCModelInitSnpuTask';section=next(s for s in elf.sections if s['name']=='.text.'+name);report=json.loads((ROOT/'docs/research/gx8002-model-interface-verification.json').read_text());row=next(r for r in report['functions'] if r['symbol']==name);assert sha(elf.contents(section))==row['compiled_sha256'] and not elf.relocations(section['index'])
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump');code=decode(subprocess.check_output([pre,'-d','-j',section['name'],str(path)],text=True));runner=decode((ROOT/'build/gx8002-board/kws-run.disassembly.txt').read_text());bindings=json.loads((ROOT/'docs/research/gx8002-kws-run-candidate.json').read_text())['bindings'];cases=0
    for pattern in (0,0xffffffff,0x20000000,0xf1234567):
      for stride in (0,1,13):
       for seed in (0,91):
        saved={0x2002e85c+i*4:(pattern+i*0x1020304)&0xffffffff for i in range(8)};observed=[]
        def hook(pointer,memory):observed.append(initialize(code,pointer,memory,saved))
        args=(0x20030000,1,stride,0x20058000,0x20059000,520,seed)
        result=execute(runner,0x100260e4,bindings,*args,task_hook=hook);wanted,events=expected(*args)
        task=list(events[-1][1]);task[0]=256
        for i in (1,2,5,6,7):task[i]=saved[0x2002e85c+i*4]&0xfffffff
        events[-1]=(events[-1][0],tuple(task),*events[-1][2:])
        assert result==(wanted,events) and len(observed)==1;cases+=1
    return {'evidence':evidence,'task_cases':cases,'source_admitted':False,'limits':['Actual decoded source task initializer writes shared runner task, with saved pointer masking and runner input/output replacement checked. Saved task contents scripted; saved-task ownership/model graph and SNPU submission remain unqualified.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-kws-run-task-initialize.json').write_text(json.dumps(r,indent=2)+'\n');print(r['task_cases'])
