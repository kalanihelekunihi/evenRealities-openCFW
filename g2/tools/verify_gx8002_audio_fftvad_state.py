# SPDX-License-Identifier: MIT
import json,re,subprocess
from itertools import product
from build_gx8002_audio_fftvad_state import build,ROOT,IMAGE_SHA,sha,Elf32
from verify_gx8002_memcpy_source import decode

def execute(code,entry,pointer,values):
    r={f'r{i}':0x98760000+i for i in range(32)};r['r0']=pointer;initial=r.copy();trace=[];memory=bytearray([0xa5]*20);pc=entry
    registers=dict(zip((0xa0a00174,0xa0a00178,0xa0a0017c,0xa0a0010c),values))
    for _ in range(30):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];jump=None
        if op=='rts':
            if any(r[f'r{i}']!=initial[f'r{i}'] for i in (*range(4,12),14,15,16,17)):raise ValueError('State ABI')
            return r['r0'],trace,memory.hex()
        elif op in ('movi','movih'):r[p[0]]=int(p[1],0)<<(16 if op=='movih' else 0)
        elif op=='bseti':r[p[0]]|=1<<int(p[-1],0)
        elif op=='subi':r[p[0]]=(r[p[0]]-int(p[-1],0))&0xffffffff
        elif op=='bez':
            if r[p[0]]==0:jump=int(p[1],0)
        elif op=='br':jump=int(args,0)
        elif op=='zext':r[p[0]]=(r[p[1]]>>int(p[3]))&((1<<(int(p[2])-int(p[3])+1))-1)
        elif op in ('ld.w','st.w','st.h'):
            m=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args)
            if not m:raise ValueError('State operand')
            reg,base,off=m.groups();a=r[base]+int(off,0)
            if op=='ld.w':r[reg]=registers[a];trace.append(('read',a,r[reg]))
            else:
                n=4 if op=='st.w' else 2;offset=a-pointer
                if not pointer or (offset,n) not in ((0,4),(4,4),(8,4),(12,2)):raise ValueError('State output bounds')
                value=r[reg]&((1<<(8*n))-1);memory[2+offset:2+offset+n]=value.to_bytes(n,'little');trace.append(('write',a,n,value))
        else:raise ValueError('State instruction '+op)
        pc=jump if jump is not None else pc+width
    raise ValueError('State bound')

def verify():
    candidate=build();wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';e=Elf32(wrapper.read_bytes(),str(wrapper))
    if sha(e.contents(next(s for s in e.sections if s['name']=='.data')))!=IMAGE_SHA:raise ValueError('State stock identity')
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    old=decode(subprocess.check_output([pre,'-D','--start-address=0xdd08','--stop-address=0xdd38',str(wrapper)],text=True));new=decode((ROOT/'build/gx8002-audio-fftvad-state/gain.disassembly.txt').read_text());cases=0
    for pointer,index,seed in product((0,0x20050000,0x20060004),range(256),(0,0xa5a5a5a5,0xffffffff)):
        values=(seed,seed^0x12345678,seed^0xfedcba98,(seed&~0xff0000)|(index<<16));trace=[];memory=bytearray([0xa5]*20)
        if pointer:
            for a,off,n,value in ((0xa0a00174,8,4,values[0]),(0xa0a00178,4,4,values[1]),(0xa0a0017c,0,4,values[2]),(0xa0a0010c,12,2,index&127)):
                trace.append(('read',a,dict(zip((0xa0a00174,0xa0a00178,0xa0a0017c,0xa0a0010c),values))[a]));trace.append(('write',pointer+off,n,value));memory[2+off:2+off+n]=value.to_bytes(n,'little')
        wanted=(0 if pointer else 0xffffffff,trace,memory.hex())
        if execute(old,0xdd08,pointer,values)!=wanted or execute(new,0x1020477c,pointer,values)!=wanted:raise ValueError('State oracle')
        cases+=1
    return {'candidate':candidate,'decoded_cases':cases,'source_admitted':False,'hardware_qualified':False,'limits':['Null no-access path, ordered MMIO/output writes, seven-bit index, output padding and bounds checked. No atomic hardware snapshot guarantee. Physical sampling unqualified.']}

if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-audio-fftvad-state-verification.json').write_text(json.dumps(r,indent=2)+'\n');print(r['decoded_cases'])
