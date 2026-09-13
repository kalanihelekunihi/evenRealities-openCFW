# SPDX-License-Identifier: MIT
"""Decoded playback interrupt effects and callback mutation."""
import json,re,subprocess
from itertools import product
from build_gx8002_audio_output_handle_isr import build,ROOT,IMAGE_SHA,sha,Elf32
from verify_gx8002_memcpy_source import decode
HANDLE=0x20010000
FRAME=0x10201100
DONE=0x10201104
from verify_gx8002_audio_output_bits import execute as bit_execute
from build_gx8002_audio_output_bits import build as bit_build
BASE=0xa0b00000

def execute(code,entry,irq,initial,status,enabled,seed,mutation,helpers):
    r={f'r{i}':0x98760000+i for i in range(32)};r.update(r0=irq,r1=HANDLE,r14=0x20070000);saved=r.copy();stack={};trace=[];state=bytearray(initial);memory={BASE+i:seed for i in (0,8,12,24,28)};memory[BASE+12]=status;memory[BASE+8]=enabled;pc=entry;condition=False
    for _ in range(150):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];jump=None
        if op=='push':
            if args!='r4-r5, r15':raise ValueError('Allocation frame')
            r['r14']-=12
            for i,name in enumerate(('r4','r5','r15')):stack[r['r14']+4*i]=r[name]
        elif op=='pop':
            if args!='r4-r5, r15':raise ValueError('Allocation restore')
            for i,name in enumerate(('r4','r5','r15')):r[name]=stack[r['r14']+4*i]
            r['r14']+=12
            if any(r[f'r{i}']!=saved[f'r{i}'] for i in (*range(4,12),14,15,16,17)):raise ValueError('Allocation ABI')
            return r['r0'],trace,bytes(state),memory
        elif op in ('mov','movi','movih','lrw'):r[p[0]]=r[p[1]] if op=='mov' else int(p[1],0)<<(16 if op=='movih' else 0)
        elif op=='cmpnei':condition=r[p[0]]!=int(p[1],0)
        elif op in ('bt','bf'):
            if condition==(op=='bt'):jump=int(args,0)
        elif op in ('bez','bnez'):
            if bool(r[p[0]])==(op=='bnez'):jump=int(p[1],0)
        elif op=='br':jump=int(args,0)
        elif op=='addi':r[p[0]]=((r[p[1]] if len(p)==3 else r[p[0]])+int(p[-1],0))&0xffffffff
        elif op=='addu':r[p[0]]=(r[p[0]]+r[p[1]])&0xffffffff
        elif op=='zextb':r[p[0]]=r[p[1]]&255
        elif op=='zext':r[p[0]]=(r[p[1]]>>int(p[3],0))&((1<<(int(p[2],0)-int(p[3],0)+1))-1)
        elif op in ('bseti','bclri'):
            value=r[p[1]] if len(p)==3 else r[p[0]];mask=1<<int(p[-1],0);r[p[0]]=value|mask if op=='bseti' else value&~mask
        elif op in ('andi','andni'):r[p[0]]=r[p[1]]&(int(p[2],0) if op=='andi' else ~int(p[2],0))
        elif op=='or':r[p[0]]|=r[p[1]]
        elif op=='and':r[p[0]]&=r[p[1]]
        elif op in ('ld.w','st.w','ld.b','st.b'):
            m=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args);reg,base,off=m.groups();a=r[base]+int(off,0);size=4 if op.endswith('w') else 1
            if a in memory:
                if size!=4:raise ValueError('Allocation MMIO width')
                if op.startswith('ld'):r[reg]=memory[a];trace.append(('read',a,r[reg]))
                else:memory[a]=r[reg];trace.append(('write',a,r[reg]))
            elif HANDLE<=a<=HANDLE+64-size:
                offset=a-HANDLE
                if op.startswith('ld'):r[reg]=int.from_bytes(state[offset:offset+size],'little');trace.append(('state_read',offset,size,r[reg]))
                else:
                    value=r[reg]&((1<<(size*8))-1);state[offset:offset+size]=value.to_bytes(size,'little');trace.append(('state_write',offset,size,value))
            else:raise ValueError(('IRQ address',hex(a),op))
        elif op in ('bsr','jsr'):
            if op=='bsr':
                target=(int(args,0)+(0x101f6a74 if entry==0xe658 else 0))&0xffffffff
                if target not in (0x102049d8,0x102049c8) or (r['r0'],r['r1'])!=(BASE,0):raise ValueError('IRQ helper call')
                offset=0 if target==0x102049d8 else 8
                trace.append(('helper',target,BASE,0));_,events,value=bit_execute(helpers,target,BASE,0,memory[BASE+offset],offset);trace.extend(events);memory[BASE+offset]=value
            else:
                target=r[args]
                if target==FRAME:
                    if (r['r0'],r['r1'])!=(0x20040000,0x20040fff):raise ValueError('Frame callback bounds')
                    trace.append(('frame',r['r0'],r['r1']))
                    if mutation:
                        memory[BASE+12]^=0xffffffff;memory[BASE+8]^=0xffffffff
                        state[44:48]=(0 if int.from_bytes(state[44:48],'little') else DONE).to_bytes(4,'little')
                elif target==DONE:trace.append(('done',))
                else:raise ValueError('IRQ callback target')
            for i in (0,1,2,3,12,13,15,*range(18,32)):r[f'r{i}']=0xb0000000+i
        else:raise ValueError('Allocation opcode '+op)
        pc=jump if jump is not None else pc+width
    raise ValueError('Allocation bound')

def oracle(irq,initial,status,enabled,seed,mutation):
    state=bytearray(initial);memory={BASE+i:seed for i in (0,8,12,24,28)};memory[BASE+12]=status;memory[BASE+8]=enabled;trace=[]
    def read(offset):trace.append(('read',BASE+offset,memory[BASE+offset]));return memory[BASE+offset]
    def write(offset,value):memory[BASE+offset]=value;trace.append(('write',BASE+offset,value))
    def state_read(offset,size):value=int.from_bytes(state[offset:offset+size],'little');trace.append(('state_read',offset,size,value));return value
    if irq!=13:return 0,trace,bytes(state),memory
    pending=read(12)&read(8)
    for bit,offset in ((4,24),(8,28)):
        if pending&bit:
            write(offset,read(offset)&0x7fffffff);write(12,read(12)&bit);write(8,read(8)&~bit)
    if pending&64:write(12,read(12)&64)
    if pending&1:
        write(12,read(12)&1)
        if state_read(40,4):
            end=state_read(36,4);start=state_read(32,4);trace.append(('frame',start,end))
            if mutation:
                memory[BASE+12]^=0xffffffff;memory[BASE+8]^=0xffffffff
                state[44:48]=(0 if int.from_bytes(state[44:48],'little') else DONE).to_bytes(4,'little')
    if pending&2:
        for bit in (4,8,64,1):write(12,read(12)&bit)
        for target,offset in ((0x102049d8,0),(0x102049c8,8)):
            trace.append(('helper',target,BASE,0));write(offset,read(offset)&~2)
        write(12,read(12)&2);state[28]=1;trace.append(('state_write',28,1,1))
        if state_read(44,4):trace.append(('done',))
    return 0,trace,bytes(state),memory

def verify():
    candidate=build();bit_build();wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(wrapper.read_bytes(),str(wrapper))
    if sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))!=IMAGE_SHA:raise ValueError('Stock identity')
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump');old=decode(subprocess.check_output([pre,'-D','--start-address=0xe658','--stop-address=0xe734',str(wrapper)],text=True));new=decode((ROOT/'build/gx8002-audio-output-handle-isr/bits.disassembly.txt').read_text());helpers=decode((ROOT/'build/gx8002-audio-output-bits/bits.disassembly.txt').read_text());cases=0
    masks=tuple((i&15)|((i&16)<<2) for i in range(32))
    for status,enabled,frame,done,seed,mutation in product(masks,masks,(0,FRAME),(0,DONE),(0,0xffffffff),(False,True)):
        initial=bytearray([0xa5]*64)
        for offset,value in ((32,0x20040000),(36,0x20040fff),(40,frame),(44,done)):initial[offset:offset+4]=value.to_bytes(4,'little')
        wanted=oracle(13,initial,status,enabled,seed,mutation)
        for code,entry in ((old,0xe658),(new,0x102050cc)):
            if execute(code,entry,13,initial,status,enabled,seed,mutation,helpers)!=wanted:raise ValueError(('IRQ effects',entry,status,enabled,frame,done,seed,mutation))
        cases+=1
    for irq in (0,12,14,0xffffffff):
        for code,entry in ((old,0xe658),(new,0x102050cc)):
            if execute(code,entry,irq,bytes(64),0xffffffff,0xffffffff,0,False,helpers)!=oracle(irq,bytes(64),0xffffffff,0xffffffff,0,False):raise ValueError('Other IRQ effects')
    return {'candidate':candidate,'decoded_cases':cases,'other_irq_paths':8,'source_admitted':False,'hardware_qualified':False,'limits':['All combinations of serviced pending/enabled bits; callbacks modeled with caller clobbers and optional changes to status, enables and completion pointer. Both interrupt helpers execute decoded C. Physical status acknowledgment semantics and real callback bodies remain unqualified.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-audio-output-handle-isr-verification.json').write_text(json.dumps(r,indent=2)+'\n');print(r['decoded_cases'])
