# SPDX-License-Identifier: MIT
"""Decoded release effects including modeled clearing and live active byte."""
import json,re,subprocess
from itertools import product
from build_gx8002_audio_output_free import build,ROOT,IMAGE_SHA,sha,Elf32
from verify_gx8002_memcpy_source import decode
HANDLE=0x20010000

def execute(code,entry,active,seed,mutation):
    r={f'r{i}':0x98760000+i for i in range(32)};r.update(r0=HANDLE,r14=0x20070000);saved=r.copy();stack={};trace=[]
    memory={a:seed for a in (0xa0b00008,0xa0b80014,0xa0b80018)};state=bytearray([0xa5]*64);state[4]=active;pc=entry
    for _ in range(64):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];jump=None
        if op=='push':
            if args!='r4-r5, r15':raise ValueError('Free frame')
            r['r14']-=12
            for i,name in enumerate(('r4','r5','r15')):stack[r['r14']+4*i]=r[name]
        elif op=='pop':
            if args!='r4-r5, r15':raise ValueError('Free restore')
            for i,name in enumerate(('r4','r5','r15')):r[name]=stack[r['r14']+4*i]
            r['r14']+=12
            if any(r[f'r{i}']!=saved[f'r{i}'] for i in (*range(4,12),14,15,16,17)):raise ValueError('Free ABI')
            return r['r0'],trace,memory,bytes(state)
        elif op in ('mov','movi','movih'):r[p[0]]=r[p[1]] if op=='mov' else int(p[1],0)<<(16 if op=='movih' else 0)
        elif op=='andni':r[p[0]]=r[p[1]]&~int(p[2],0)
        elif op=='bclri':r[p[0]] &= ~(1<<int(p[1],0))
        elif op=='addi':r[p[0]]+=int(p[1],0)
        elif op=='bez':
            if not r[p[0]]:jump=int(p[1],0)
        elif op in ('ld.w','st.w','ld.b','st.b'):
            m=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args)
            if not m:raise ValueError('Free operand')
            reg,base,off=m.groups();a=r[base]+int(off,0)
            if op.endswith('w'):
                if a not in memory:raise ValueError('Free MMIO address')
                if op=='ld.w':r[reg]=memory[a];trace.append(('read',a,r[reg]))
                else:memory[a]=r[reg];trace.append(('write',a,r[reg]))
            else:
                if a!=HANDLE+4:raise ValueError('Free state address')
                if op=='ld.b':r[reg]=state[4];trace.append(('read_byte',a,r[reg]))
                else:state[4]=r[reg]&255;trace.append(('write_byte',a,state[4]))
        elif op=='bsr':
            target=(int(args,0)+(0x101f6a74 if entry==0xe86c else 0))&0xffffffff
            if target!=0x102099cc or (r['r0'],r['r1'],r['r2'])!=(HANDLE+16,0,36):raise ValueError('Free memset arguments')
            trace.append(('memset',HANDLE+16,0,36));state[16:52]=bytes(36)
            if mutation:state[4]^=255
            for i in (0,1,2,3,12,13,15,*range(18,32)):r[f'r{i}']=0xb0000000+i
        else:raise ValueError('Free instruction '+op)
        pc=jump if jump is not None else pc+width
    raise ValueError('Free bound')

def verify():
    candidate=build();wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(wrapper.read_bytes(),str(wrapper))
    if sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))!=IMAGE_SHA:raise ValueError('Free stock identity')
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump');old=decode(subprocess.check_output([pre,'-D','--start-address=0xe86c','--stop-address=0xe8a4',str(wrapper)],text=True));new=decode((ROOT/'build/gx8002-audio-output-free/bits.disassembly.txt').read_text());cases=0
    for active,seed,mutation in product(range(256),(0,0xffffffff,0xa5a5a5a5),(False,True)):
        memory={0xa0b00008:seed&~1,0xa0b80014:0,0xa0b80018:0};trace=[('read',0xa0b00008,seed),('write',0xa0b00008,seed&~1)]
        for a in (0xa0b80014,0xa0b80018):trace.extend((('read',a,seed),('write',a,0)))
        trace.append(('memset',HANDLE+16,0,36));state=bytearray([0xa5]*64);state[16:52]=bytes(36);state[4]=active^(255 if mutation else 0)
        trace.append(('read_byte',HANDLE+4,state[4]))
        if state[4]:state[4]=0;trace.append(('write_byte',HANDLE+4,0))
        wanted=(0,trace,memory,bytes(state))
        if execute(old,0xe86c,active,seed,mutation)!=wanted or execute(new,0x102052e0,active,seed,mutation)!=wanted:raise ValueError('Free ordered effects')
        cases+=1
    return {'candidate':candidate,'decoded_cases':cases,'source_admitted':False,'hardware_qualified':False,'limits':['Valid RAM handle only. Memset modeled, with caller clobbers and optional active-byte mutation. Null handle writes before late guard in stock; no safe-null claim.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-audio-output-free-verification.json').write_text(json.dumps(r,indent=2)+'\n');print(r['decoded_cases'])
