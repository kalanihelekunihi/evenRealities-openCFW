# SPDX-License-Identifier: MIT
"""Decoded frame submission, including ordered RAM/MMIO and helper effects."""
import json,re,subprocess
from itertools import product
from build_gx8002_audio_output_push_frame import build,ROOT,IMAGE_SHA,sha,Elf32
from verify_gx8002_memcpy_source import decode
from verify_gx8002_audio_output_bits import execute as bit_execute
from build_gx8002_audio_output_bits import build as bit_build
HANDLE=0x20010000
FRAME=0x20020000
BASE=0xa0b00000
SDC=0xa0b80000

def execute(code,entry,initial,frame,seed,helpers):
    r={f'r{i}':0x98760000+i for i in range(32)};r.update(r0=HANDLE,r1=FRAME if frame is not None else 0,r14=0x20070000);saved=r.copy();stack={};trace=[]
    state=bytearray(initial);memory={a:seed for a in (SDC+20,SDC+24,SDC+36,SDC+44,BASE,BASE+8)};pc=entry;frame_names=None
    for _ in range(100):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];jump=None
        if op=='push':
            if args not in ('r4-r5, r15','r4, r15'):raise ValueError('Push frame save set')
            frame_names=('r4','r5','r15') if args=='r4-r5, r15' else ('r4','r15');r['r14']-=4*len(frame_names)
            for i,name in enumerate(frame_names):stack[r['r14']+4*i]=r[name]
        elif op in ('pop','rts'):
            if op=='pop':
                expected='r4-r5, r15' if len(frame_names)==3 else 'r4, r15'
                if args!=expected:raise ValueError('Push frame restore set')
                for i,name in enumerate(frame_names):r[name]=stack[r['r14']+4*i]
                r['r14']+=4*len(frame_names)
            if any(r[f'r{i}']!=saved[f'r{i}'] for i in (*range(4,12),14,15,16,17)):raise ValueError('Push frame ABI')
            return r['r0'],trace,memory,bytes(state)
        elif op in ('mov','movi','movih'):r[p[0]]=r[p[1]] if op=='mov' else int(p[1],0)<<(16 if op=='movih' else 0)
        elif op in ('addi','subi'):
            base=r[p[1]] if len(p)==3 else r[p[0]];value=int(p[-1],0);r[p[0]]=(base+(value if op=='addi' else -value))&0xffffffff
        elif op=='subu':r[p[0]]=(r[p[0]]-r[p[1]])&0xffffffff
        elif op=='divs':
            numerator=r[p[1]];numerator=numerator if numerator<0x80000000 else numerator-0x100000000
            divisor=r[p[2]]
            if not 1<=divisor<=255:raise ValueError('Unqualified stride')
            r[p[0]]=((abs(numerator)//divisor)*(-1 if numerator<0 else 1))&0xffffffff
        elif op in ('lsli','lsri'):r[p[0]]=((r[p[1]]<<int(p[2],0)) if op=='lsli' else (r[p[1]]>>int(p[2],0)))&0xffffffff
        elif op=='zext':r[p[0]]=(r[p[1]]>>int(p[3],0))&((1<<(int(p[2],0)-int(p[3],0)+1))-1)
        elif op in ('and','or'):r[p[0]]=r[p[0]]&r[p[1]] if op=='and' else r[p[0]]|r[p[1]]
        elif op=='ori':r[p[0]]=r[p[1]]|int(p[2],0)
        elif op in ('bez','bnez'):
            if bool(r[p[0]])==(op=='bnez'):jump=int(p[1],0)
        elif op=='br':jump=int(args,0)
        elif op in ('ld.w','st.w','ld.b','st.b'):
            m=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args)
            if not m:raise ValueError('Push frame memory operand')
            reg,base,off=m.groups();a=r[base]+int(off,0);size=4 if op.endswith('w') else 1
            if a in memory:
                if size!=4:raise ValueError('Narrow MMIO')
                if op.startswith('ld'):r[reg]=memory[a];trace.append(('read',a,r[reg]))
                else:memory[a]=r[reg];trace.append(('write',a,r[reg]))
            elif HANDLE<=a<=HANDLE+64-size:
                offset=a-HANDLE
                if op.startswith('ld'):r[reg]=int.from_bytes(state[offset:offset+size],'little');trace.append(('ram_read',offset,size,r[reg]))
                else:
                    value=r[reg]&((1<<(size*8))-1);state[offset:offset+size]=value.to_bytes(size,'little');trace.append(('ram_write',offset,size,value))
            else:raise ValueError('Push frame memory address')
        elif op=='bsr':
            target=(int(args,0)+(0x101f6a74 if entry==0xe734 else 0))&0xffffffff
            if target==0x10025738:
                if (r['r0'],r['r1'],r['r2'])!=(HANDLE+32,FRAME,8) or frame is None:raise ValueError('Frame copy arguments')
                trace.append(('memcpy',HANDLE+32,FRAME,8));state[32:40]=frame
            elif target in (0x102049d8,0x102049c8):
                if (r['r0'],r['r1'])!=(BASE,1):raise ValueError('Frame helper arguments')
                offset=0 if target==0x102049d8 else 8
                trace.append(('helper',target,BASE,1));_,events,value=bit_execute(helpers,target,BASE,1,memory[BASE+offset],offset);trace.extend(events);memory[BASE+offset]=value
            else:raise ValueError('Frame call target')
            for i in (0,1,2,3,12,13,15,*range(18,32)):r[f'r{i}']=0xb0000000+i
        else:raise ValueError('Push frame instruction '+op)
        pc=jump if jump is not None else pc+width
    raise ValueError('Push frame execution bound')

def oracle(initial,frame,seed):
    state=bytearray(initial);memory={a:seed for a in (SDC+20,SDC+24,SDC+36,SDC+44,BASE,BASE+8)};trace=[]
    if frame is None:return 0xffffffff,trace,memory,bytes(state)
    state[32:40]=frame;start=int.from_bytes(frame[:4],'little');end=int.from_bytes(frame[4:],'little');stride=state[25]
    trace=[('memcpy',HANDLE+32,FRAME,8),('ram_read',36,4,end),('ram_read',32,4,start),('ram_read',25,1,stride)]
    difference=(end+1-start)&0xffffffff;signed=difference if difference<0x80000000 else difference-0x100000000
    count=(abs(signed)//stride)*(-1 if signed<0 else 1)
    for address,value in ((SDC+20,start),(SDC+24,end),(SDC+36,(seed&0xff000000)|(count&0xffffff)),(SDC+44,seed|2)):
        if address==SDC+24:trace.append(('ram_read',36,4,end))
        trace.extend((('read',address,seed),('write',address,value)));memory[address]=value
    active=state[26];trace.append(('ram_read',26,1,active))
    if not active:
        callback=int.from_bytes(state[44:48],'little');trace.append(('ram_read',44,4,callback))
        if callback:
            state[26]=1;trace.append(('ram_write',26,1,1))
            for target,address in ((0x102049d8,BASE),(0x102049c8,BASE+8)):
                trace.extend((('helper',target,BASE,1),('read',address,seed),('write',address,seed|2)));memory[address]=seed|2
    return 0,trace,memory,bytes(state)

def verify():
    candidate=build();bit_build();wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(wrapper.read_bytes(),str(wrapper))
    if sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))!=IMAGE_SHA:raise ValueError('Frame stock identity')
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump');old=decode(subprocess.check_output([pre,'-D','--start-address=0xe734','--stop-address=0xe7a8',str(wrapper)],text=True));new=decode((ROOT/'build/gx8002-audio-output-push-frame/bits.disassembly.txt').read_text());helpers=decode((ROOT/'build/gx8002-audio-output-bits/bits.disassembly.txt').read_text());cases=0
    bounds=((0,0),(0,0xffffffff),(0xffffffff,0),(0x1000,0x1fff),(0,0x7ffffffe),(0,0x7fffffff),(0x80000000,0),(0x1000,0xffe))
    for (start,end),stride,active,callback,seed in product(bounds,range(1,256),(0,1,255),(0,0x10201234),(0,0xffffffff,0xa5a5a5a5)):
        state=bytearray([0xa5]*64);state[25]=stride;state[26]=active;state[44:48]=callback.to_bytes(4,'little');frame=start.to_bytes(4,'little')+end.to_bytes(4,'little')
        wanted=oracle(state,frame,seed)
        for code,entry in ((old,0xe734),(new,0x102051a8)):
            actual=execute(code,entry,state,frame,seed,helpers)
            if actual!=wanted:raise ValueError(('Frame ordered effects',hex(entry),start,end,stride,active,callback,actual,wanted))
        cases+=1
    state=bytes(64)
    for code,entry in ((old,0xe734),(new,0x102051a8)):
        if execute(code,entry,state,None,0,helpers)!=oracle(state,None,0):raise ValueError('Null frame effects')
    return {'candidate':candidate,'decoded_cases':cases,'null_frame_paths':2,'source_admitted':False,'hardware_qualified':False,'limits':['Valid RAM handle and disjoint 8-byte frame; memcpy modeled with caller clobbers. Configured stride must be nonzero; zero-divisor hardware behavior is unqualified. Both decoded interrupt helper bodies are executed. Physical hardware and asynchronous state mutation remain unqualified.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-audio-output-push-frame-verification.json').write_text(json.dumps(r,indent=2)+'\n');print(r['decoded_cases'])
