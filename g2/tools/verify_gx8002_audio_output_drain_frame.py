# SPDX-License-Identifier: MIT
"""Decoded drain completion schedules, nested helpers and noncompletion prefixes."""
import json,re,subprocess
from itertools import product
from build_gx8002_audio_output_drain_frame import build,ROOT,IMAGE_SHA,sha,Elf32
from verify_gx8002_memcpy_source import decode
from verify_gx8002_audio_output_bits import execute as bit_execute
from build_gx8002_audio_output_bits import build as bit_build
HANDLE=0x20010000
BASE=0xa0b00000

def execute(code,entry,seed,schedule,value,helpers):
    r={f'r{i}':0x98760000+i for i in range(32)};r.update(r0=HANDLE,r14=0x20070000);saved=r.copy();stack={};state=bytearray([0xa5]*64);memory={BASE:seed,BASE+8:seed};trace=[];pc=entry;names=();delays=0
    for _ in range(400):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];jump=None
        if op=='push':
            if args not in ('r4, r15','r4-r5, r15'):raise ValueError('Drain frame')
            names=('r4','r15') if args=='r4, r15' else ('r4','r5','r15');r['r14']-=4*len(names)
            for i,name in enumerate(names):stack[r['r14']+4*i]=r[name]
        elif op=='pop':
            if args!=('r4, r15' if len(names)==2 else 'r4-r5, r15'):raise ValueError('Drain restore')
            for i,name in enumerate(names):r[name]=stack[r['r14']+4*i]
            r['r14']+=4*len(names)
            if any(r[f'r{i}']!=saved[f'r{i}'] for i in (*range(4,12),14,15,16,17)):raise ValueError('Drain ABI')
            return r['r0'],trace,bytes(state),memory
        elif op in ('mov','movi','movih'):r[p[0]]=r[p[1]] if op=='mov' else int(p[1],0)<<(16 if op=='movih' else 0)
        elif op=='addi':r[p[0]]=(r[p[1]] if len(p)==3 else r[p[0]])+int(p[-1],0)
        elif op in ('bez','bnez'):
            if bool(r[p[0]])==(op=='bnez'):jump=int(p[1],0)
        elif op=='br':jump=int(args,0)
        elif op in ('ld.b','st.b'):
            m=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args);reg,base,offset=m.groups();offset=r[base]+int(offset,0)-HANDLE
            if offset not in (26,28) or (op=='ld.b' and offset!=28):raise ValueError('Drain state address')
            if op=='ld.b':
                r[reg]=state[offset];trace.append(('read_byte',offset,r[reg]))
                if schedule is None and delays==16:return 'waiting_prefix',trace,bytes(state),memory
            else:state[offset]=r[reg]&255;trace.append(('write_byte',offset,state[offset]))
        elif op=='bsr':
            target=(int(args,0)+(0x101f6a74 if entry==0xe290 else 0))&0xffffffff
            if target in (0x102049d8,0x102049c8):
                if (r['r0'],r['r1'])!=(BASE,1):raise ValueError('Drain helper arguments')
                offset=0 if target==0x102049d8 else 8
                trace.append(('helper',target,BASE,1));_,events,word=bit_execute(helpers,target,BASE,1,memory[BASE+offset],offset);trace.extend(events);memory[BASE+offset]=word
                if target==0x102049c8 and schedule==0:state[28]=value
            elif target==0x1002598c:
                if r['r0']!=1:raise ValueError('Drain delay argument')
                delays+=1;trace.append(('delay',1))
                if delays==schedule:state[28]=value
            else:raise ValueError('Drain call target')
            for i in (0,1,2,3,12,13,15,*range(18,32)):r[f'r{i}']=0xb0000000+i
        else:raise ValueError('Drain opcode '+op)
        pc=jump if jump is not None else pc+width
    raise ValueError('Drain execution bound')

def verify():
    candidate=build();bit_build();wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(wrapper.read_bytes(),str(wrapper))
    if sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))!=IMAGE_SHA:raise ValueError('Stock identity')
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump');old=decode(subprocess.check_output([pre,'-D','--start-address=0xe290','--stop-address=0xe2c4',str(wrapper)],text=True));new=decode((ROOT/'build/gx8002-audio-output-drain-frame/bits.disassembly.txt').read_text());helpers=decode((ROOT/'build/gx8002-audio-output-bits/bits.disassembly.txt').read_text());cases=0
    for seed,schedule,value in product((0,0xffffffff,0xa5a5a5a5),(0,1,2,7,16,None),(1,2,127,128,255)):
        state=bytearray([0xa5]*64);state[26]=1;state[28]=value if schedule is not None else 0;memory={BASE:seed|2,BASE+8:seed|2};trace=[('write_byte',28,0),('write_byte',26,1)]
        for target,offset in ((0x102049d8,0),(0x102049c8,8)):trace.extend((('helper',target,BASE,1),('read',BASE+offset,seed),('write',BASE+offset,seed|2)))
        for _ in range(16 if schedule is None else schedule):trace.extend((('read_byte',28,0),('delay',1)))
        trace.append(('read_byte',28,state[28]));wanted=('waiting_prefix' if schedule is None else 0,trace,bytes(state),memory)
        for code,entry in ((old,0xe290),(new,0x10204d04)):
            if execute(code,entry,seed,schedule,value,helpers)!=wanted:raise ValueError(('Drain effects',entry,seed,schedule,value))
        cases+=1
    return {'candidate':candidate,'decoded_cases':cases,'source_admitted':False,'hardware_qualified':False,'limits':['Completion is modeled at second-helper return or selected delay return. Actual decoded control helpers execute. Noncompletion checked through16 delays without return; no termination guarantee, real elapsed-time or interrupt scheduling qualification.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-audio-output-drain-frame-verification.json').write_text(json.dumps(r,indent=2)+'\n');print(r['decoded_cases'])
