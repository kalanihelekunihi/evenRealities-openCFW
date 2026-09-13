# SPDX-License-Identifier: MIT
"""Decoded public DAC wrapper with alias-sensitive ordered copies."""
import json,re,subprocess
from itertools import product
from build_gx8002_audio_output_config_dac import build,ROOT,IMAGE_SHA,sha,Elf32
from verify_gx8002_memcpy_source import decode
HANDLE=0x20010000
STATE=0x20020000
DEST=STATE+48
STACK=0x20070000
FIELDS=((0,4),(4,2),(6,2),(8,2),(12,4),(16,2),(18,2),(20,2))
def initial(pointer,seed):
    memory={STATE+i:(seed+i*17)&255 for i in range(128)}
    if pointer and not STATE<=pointer<STATE+128:memory.update({pointer+i:(seed+i*29+71)&255 for i in range(24)})
    memory.update({HANDLE+48+i:b for i,b in enumerate(STATE.to_bytes(4,'little'))})
    return memory

def run(code,pc,pointer,seed,dac_hook=None):
    memory=initial(pointer,seed);trace=[];r={f'r{i}':0x87650000+i for i in range(32)};r.update(r0=HANDLE,r1=pointer,r14=STACK);saved=r.copy();stack={}
    for _ in range(100):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];jump=None
        if op in ('rts','pop'):
            if op=='pop':
                if args!='r15':raise ValueError('Wrapper pop')
                r['r15']=stack[r['r14']];r['r14']+=4
            if any(r[f'r{i}']!=saved[f'r{i}'] for i in (*range(4,12),14,15,16,17)):raise ValueError('Wrapper ABI')
            return r['r0'],trace,memory
        if op=='push':
            if args!='r15':raise ValueError('Wrapper push')
            r['r14']-=4;stack[r['r14']]=r['r15']
        elif op in ('mov','movi','movih'):r[p[0]]=r[p[1]] if op=='mov' else int(p[1],0)<<(16 if op=='movih' else 0)
        elif op in ('addi','subi'):
            value=r[p[1]] if len(p)==3 else r[p[0]];n=int(p[-1],0);r[p[0]]=(value+(n if op=='addi' else -n))&0xffffffff
        elif op=='bez':
            if not r[p[0]]:jump=int(p[1],0)
        elif op=='br':jump=int(args,0)
        elif op in ('ld.w','ld.h','st.w','st.h'):
            m=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args)
            if not m:raise ValueError('Wrapper operand')
            reg,base,off=m.groups();a=r[base]+int(off,0);size=4 if op.endswith('w') else 2
            if any(a+i not in memory for i in range(size)):raise ValueError('Wrapper bounds')
            if op.startswith('ld'):r[reg]=int.from_bytes(bytes(memory[a+i] for i in range(size)),'little');trace.append(('read',a,size,r[reg]))
            else:
                value=r[reg]&((1<<(size*8))-1);trace.append(('write',a,size,value));memory.update({a+i:b for i,b in enumerate(value.to_bytes(size,'little'))})
        elif op=='bsr':
            if int(args,0) not in (0xdf74,0x102049e8) or (r['r0'],r['r1'])!=(0xa0b00000,DEST):raise ValueError('Wrapper DAC target/args')
            trace.append(('dac',r['r0'],r['r1'],bytes(memory[DEST+i] for i in range(36)).hex()))
            if dac_hook is not None:
                trace.extend(dac_hook(bytes(memory[DEST+i] for i in range(36))))
            for i in (0,1,2,3,12,13,15,*range(18,32)):r[f'r{i}']=0xb0000000+i
        else:raise ValueError('Wrapper instruction '+op)
        pc=jump if jump is not None else pc+width
    raise ValueError('Wrapper bound')

def oracle(pointer,seed):
    memory=initial(pointer,seed);trace=[]
    if not pointer:return 0xffffffff,trace,memory
    trace.append(('read',HANDLE+48,4,STATE))
    for offset,size in FIELDS:
        value=int.from_bytes(bytes(memory[pointer+offset+i] for i in range(size)),'little')
        trace.extend((('read',pointer+offset,size,value),('write',DEST+offset,size,value)))
        memory.update({DEST+offset+i:b for i,b in enumerate(value.to_bytes(size,'little'))})
    trace.append(('dac',0xa0b00000,DEST,bytes(memory[DEST+i] for i in range(36)).hex()))
    return 0,trace,memory

def verify():
    candidate=build();wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';e=Elf32(wrapper.read_bytes(),str(wrapper))
    if sha(e.contents(next(s for s in e.sections if s['name']=='.data')))!=IMAGE_SHA:raise ValueError('Wrapper stock identity')
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump');old=decode(subprocess.check_output([pre,'-D','--start-address=0xe21c','--stop-address=0xe260',str(wrapper)],text=True));new=decode((ROOT/'build/gx8002-audio-output-config-dac/bits.disassembly.txt').read_text());cases=0
    for pointer,seed in product((0,0x20040000,*range(DEST-24,DEST+28,4)),range(256)):
        wanted=oracle(pointer,seed)
        if run(old,0xe21c,pointer,seed)!=wanted or run(new,0x10204c90,pointer,seed)!=wanted:raise ValueError('Wrapper effects mismatch '+repr((pointer,seed)))
        cases+=1
    return {'candidate':candidate,'decoded_cases':cases,'source_admitted':False,'hardware_qualified':False,'limits':['Null, disjoint and aligned overlapping configurations checked with ordered reads/writes and untouched internal bytes. DAC call modeled; nested source execution pending.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-audio-output-config-dac-verification.json').write_text(json.dumps(r,indent=2)+'\n');print(r['decoded_cases'])
