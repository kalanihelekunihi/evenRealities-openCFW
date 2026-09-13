# SPDX-License-Identifier: MIT
"""Byte-accurate callback publication and alias-sensitive ordered effects."""
import json,re,subprocess
from itertools import product
from build_gx8002_audio_output_callbacks import build,ROOT,IMAGE_SHA,sha,Elf32
from verify_gx8002_memcpy_source import decode
HANDLE=0x20010000
IRQ=0xa0b00008

def initial(pointer,frame,over,seed):
    memory={HANDLE+i:(seed+i*17)&255 for i in range(64)}
    for a,value in ((pointer,frame),(pointer+4,over),(IRQ,seed)):
        memory.update({a+i:b for i,b in enumerate(value.to_bytes(4,'little'))})
    return memory

def access(memory,trace,op,address,size,value=0):
    if any(address+i not in memory for i in range(size)):raise ValueError('Callback access bounds')
    if address==IRQ and size!=4:raise ValueError('Narrow callback IRQ')
    if op=='read':value=int.from_bytes(bytes(memory[address+i] for i in range(size)),'little')
    else:
        value &= (1<<(size*8))-1
        memory.update({address+i:b for i,b in enumerate(value.to_bytes(size,'little'))})
    trace.append((op,address,size,value));return value

def execute(code,pc,pointer,frame,over,seed):
    memory=initial(pointer,frame,over,seed);trace=[];r={f'r{i}':0x87650000+i for i in range(32)};r.update(r0=HANDLE,r1=pointer);saved=r.copy()
    for _ in range(32):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];jump=None
        if op=='rts':
            if any(r[f'r{i}']!=saved[f'r{i}'] for i in (*range(4,12),14,15,16,17)):raise ValueError('Callback ABI')
            return r['r0'],trace,memory
        if op in ('movi','movih'):r[p[0]]=int(p[1],0)<<(16 if op=='movih' else 0)
        elif op=='ori':r[p[0]]=r[p[1]]|int(p[2],0)
        elif op=='bez':
            if r[p[0]]==0:jump=int(p[1],0)
        elif op in ('ld.w','st.w','st.b'):
            m=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args)
            if not m:raise ValueError('Callback operand')
            reg,base,off=m.groups();a=r[base]+int(off,0);size=1 if op=='st.b' else 4
            if op=='ld.w':r[reg]=access(memory,trace,'read',a,size)
            else:access(memory,trace,'write',a,size,r[reg])
        else:raise ValueError('Callback instruction '+op)
        pc=jump if jump is not None else pc+width
    raise ValueError('Callback bound')

def oracle(pointer,frame,over,seed):
    memory=initial(pointer,frame,over,seed);trace=[]
    callback=access(memory,trace,'read',pointer,4)
    if callback:
        irq=access(memory,trace,'read',IRQ,4);access(memory,trace,'write',IRQ,4,irq|1)
        access(memory,trace,'write',HANDLE+40,4,callback);access(memory,trace,'write',HANDLE+27,1,1)
    callback=access(memory,trace,'read',pointer+4,4)
    if callback:
        access(memory,trace,'write',HANDLE+44,4,callback);access(memory,trace,'write',HANDLE+26,1,0)
    return 0,trace,memory

def verify():
    candidate=build();wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(wrapper.read_bytes(),str(wrapper))
    if sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))!=IMAGE_SHA:raise ValueError('Callback stock identity')
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump');old=decode(subprocess.check_output([pre,'-D','--start-address=0xe8a4','--stop-address=0xe8d0',str(wrapper)],text=True));new=decode((ROOT/'build/gx8002-audio-output-callbacks/bits.disassembly.txt').read_text());cases=0
    for pointer,frame,over,seed in product((0x20020000,*range(HANDLE+20,HANDLE+48,4)),(0,0x10200000,0xffffffff),(0,0x10200004,0xffffffff),(0,0xffffffff,0xa5a5a5a5)):
        args=(pointer,frame,over,seed);wanted=oracle(*args)
        if execute(old,0xe8a4,*args)!=wanted or execute(new,0x10205318,*args)!=wanted:raise ValueError('Callback publication mismatch')
        cases+=1
    return {'candidate':candidate,'decoded_cases':cases,'source_admitted':False,'hardware_qualified':False,'limits':['Disjoint and aligned overlapping callback structures, absent callbacks, byte flags and word IRQ effects checked. Callback bodies are not invoked here; physical driver lifecycle remains unqualified.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-audio-output-callbacks-verification.json').write_text(json.dumps(r,indent=2)+'\n');print(r['decoded_cases'])
