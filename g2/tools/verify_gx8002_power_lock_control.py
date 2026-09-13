# SPDX-License-Identifier: MIT
"""Decode lock allocation and query, including aliased publication."""
import json,re,subprocess,random
from build_gx8002_power_lock_control import build,ROOT,IMAGE_SHA,sha,Elf32
from verify_gx8002_memcpy_source import decode
from verify_gx8002_power_initialize import word,BASE,MASK

def execute(code,entry,memory,destination):
    memory=memory.copy();r={f'r{i}':0xabc00000+i for i in range(32)};r['r0']=destination;initial=r.copy();pc=entry;events=[];condition=False
    for _ in range(250):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];nxt=pc+width
        if op=='rts':
            if any(r[f'r{i}']!=initial[f'r{i}'] for i in (*range(4,12),14,15,16,17)):raise ValueError('ABI')
            return r['r0'],memory,events
        if op in ('movi','lrw'):r[p[0]]=int(p[1],0)
        elif op in ('addi','subi'):r[p[0]]=(r[p[0] if len(p)==2 else p[1]]+(1 if op=='addi' else -1)*int(p[-1],0))&MASK
        elif op in ('lsl','rotl'):
            count=r[p[-1]]&63;value=r[p[0]]
            r[p[0]]=0 if count>=32 else ((value<<count)&MASK if op=='lsl' else ((value<<count)|(value>>((-count)&31)))&MASK)
        elif op=='and':r[p[0]]&=r[p[1]]
        elif op=='cmplti':condition=(r[p[0]] if r[p[0]]<0x80000000 else r[p[0]]-0x100000000)<int(p[1],0)
        elif op=='bf':
            if not condition:nxt=int(args,0)
        elif op=='bez':
            if r[p[0]]==0:nxt=int(p[1],0)
        elif op=='or':r[p[0]]|=r[p[1]]
        elif op=='cmpnei':condition=r[p[0]]!=int(p[1],0)
        elif op=='mvc':r[p[0]]=int(condition)
        elif op=='br':nxt=int(args,0)
        elif op in ('bnez','bnezad'):
            if op=='bnezad':r[p[0]]=(r[p[0]]-1)&MASK
            if r[p[0]]:nxt=int(p[1],0)
        elif op in ('ld.w','st.w'):
            reg,base,off=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args).groups();address=(r[base]+int(off,0))&MASK
            if op=='ld.w':r[reg]=word(memory,address);events.append(('read',address,r[reg]))
            else:word(memory,address,r[reg]);events.append(('write',address,r[reg]))
        else:raise ValueError('Opcode '+op)
        pc=nxt
    raise ValueError('Bound')

def oracle(memory,handle,unlock):
    memory=memory.copy();events=[];signed=handle if handle<0x80000000 else handle-0x100000000
    shift=(handle-1)%64
    if unlock:
        if signed>32:return MASK,memory,events
        before=word(memory,BASE);keep=MASK^(1<<shift) if shift<32 else 0
        after=before&keep;events=[('read',BASE,before),('write',BASE,after)];word(memory,BASE,after)
        return 0,memory,events
    allocated=word(memory,BASE+4);events=[('read',BASE+4,allocated)]
    bit=1<<shift if shift<32 else 0
    if not allocated&bit or signed>32:return MASK,memory,events
    before=word(memory,BASE);after=before|bit;events.extend([('read',BASE,before),('write',BASE,after)]);word(memory,BASE,after)
    return 0,memory,events

def verify():
    candidate=build();pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-');wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(wrapper.read_bytes(),'stock')
    if sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))!=IMAGE_SHA:raise ValueError('Wrapper')
    old=decode(subprocess.check_output([pre+'objdump','-D','--start-address=0x10d34','--stop-address=0x10d84',str(wrapper)],text=True));new=decode((ROOT/'build/gx8002-power-lock-control/buffers.disassembly.txt').read_text());cases=0
    handles=sorted({*(i&MASK for i in range(-128,129)),*(0x7fffffc0+i for i in range(128))})
    masks=(0,1,0x80000000,MASK,0x55555555,0xaaaaaaaa)
    for handle in handles:
        shift=(handle-1)&63;bit=1<<(shift&31)
        for allocated in (*masks,bit,MASK^bit):
            for active in masks:
                memory={BASE+i:(i*37+handle)&255 for i in range(-16,24)};word(memory,BASE,active);word(memory,BASE+4,allocated)
                for unlock,offset in ((False,0x10d34),(True,0x10d60)):
                    expected=oracle(memory,handle,unlock)
                    for code,base in ((old,0),(new,0x101f6a74)):
                        if execute(code,offset+base,memory,handle)!=expected:raise ValueError(('Control',handle,active,allocated,unlock))
                cases+=1
    return {'candidate':candidate,'decoded_cases':cases,'source_admitted':False,'shift_evidence':json.loads((ROOT/'docs/research/gx8002-power-lock-shifts.json').read_text()),'limits':['All six-bit shift classes across positive/negative and signed-boundary handles, ordered memory and ABI checked. C uses two reviewed inline instruction wrappers with defined host equivalents. Vendor emulator semantics, not physical hardware qualification; asynchronous accesses unqualified.']}

if __name__=='__main__':
    report=verify();(ROOT/'docs/research/gx8002-power-lock-control-verification.json').write_text(json.dumps(report,indent=2)+'\n');print(report['decoded_cases'])
