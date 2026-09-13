# SPDX-License-Identifier: MIT
"""Decoded model-task initialization with ordered memory and alias checks."""
import json,re,subprocess
from analyze_gx8002_upstream_objects import ROOT,IMAGE,IMAGE_SHA,sha
from verify_gx8002_analog_source import FLAGS
from verify_gx8002_memcpy_source import decode
from build_transparent_image import Elf32
STATE=0x2002e85c

def execute(code,entry,memory,destination):
    r={f'r{i}':0x98760000+i for i in range(32)};r['r0']=destination;initial=r.copy();pc=entry;trace=[]
    for _ in range(40):
        op,args,w=code[pc];p=[x.strip() for x in args.split(',')]
        if op in ('movi','lrw'):r[p[0]]=int(p[1],0)
        elif op=='lsli':r[p[0]]=(r[p[1]]<<int(p[2],0))&0xffffffff
        elif op=='zext':r[p[0]]=(r[p[1]]>>int(p[3],0))&((1<<(int(p[2],0)-int(p[3],0)+1))-1)
        elif op in ('ld.w','st.w'):
            reg,base,offset=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args).groups();a=r[base]+int(offset,0)
            if a not in memory or a%4:raise ValueError('Memory bounds')
            if op=='ld.w':r[reg]=memory[a];trace.append(('read',a,r[reg]))
            else:memory[a]=r[reg];trace.append(('write',a,r[reg]))
        elif op=='rts':
            if any(r[f'r{i}']!=initial[f'r{i}'] for i in range(4,32)):raise ValueError('ABI')
            return r['r0'],trace
        else:raise ValueError('Opcode '+op)
        pc+=w
    raise ValueError('Bound')

def verify():
    stock=IMAGE.read_bytes()
    if sha(stock)!=IMAGE_SHA:raise ValueError('Stock identity')
    from verify_gx8002_model_interface import verify as interface_verify
    out=ROOT/'build/gx8002-ctc-task-init';out.mkdir(parents=True,exist_ok=True)
    prefix=ROOT/'build/csky-macos/install/bin';pre=str(prefix/'csky-unknown-elf-')
    interface=interface_verify(prefix,ROOT/'build/upstream-nationalchip-lvp-kws',out)
    source=ROOT/'components/shared/gx8002/runtime_gx8002_model_interface.c'
    obj=out/'runtime_gx8002_model_interface.o'
    elf=Elf32(obj.read_bytes(),str(obj));section=next(s for s in elf.sections if s['name']=='.text.LvpCTCModelInitSnpuTask');payload=elf.contents(section)
    wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';e=Elf32(wrapper.read_bytes(),'stock')
    if sha(e.contents(next(s for s in e.sections if s['name']=='.data')))!=IMAGE_SHA:raise ValueError('Wrapper')
    old=decode(subprocess.check_output([pre+'objdump','-D','--start-address=0x121b4','--stop-address=0x121ec',str(wrapper)],text=True))
    dis=subprocess.check_output([pre+'objdump','-d','--section=.text.LvpCTCModelInitSnpuTask',str(obj)],text=True);(out/'task.disassembly.txt').write_text(dis);new=decode(dis);cases=0
    for seed in (0,1,0xffffffff,0xa5a5a5a5,0x80000000,0x0fffffff):
        for destination in (0x20030000,*range(STATE-28,STATE+32,4)):
            memory={a:(seed^(a*37))&0xffffffff for a in {*range(STATE,STATE+32,4),*range(destination,destination+32,4)}};wanted=memory.copy();trace=[]
            def put(a,v):wanted[a]=v;trace.append(('write',a,v))
            def get(a):trace.append(('read',a,wanted[a]));return wanted[a]
            put(destination,256)
            for offset in (20,28,4):put(destination+offset,get(STATE+offset)&0x0fffffff)
            data=get(STATE+8);temporary=get(STATE+24)
            put(destination+8,data&0x0fffffff);put(destination+24,temporary&0x0fffffff)
            for code,entry in ((old,0x121b4),(new,0)):
                actual=memory.copy()
                if execute(code,entry,actual,destination)!=(0,trace) or actual!=wanted:raise ValueError('Task effects')
            cases+=1
    return {'decoded_cases':cases,'compiled_bytes':len(payload),'compiled_sha256':sha(payload),'source_sha256':sha(source.read_bytes()),'stock_sha256':sha(stock[0x121b4:0x121ec]),'source_admitted':False,'limits':['Ordered word accesses and aliasing checked; Existing source admission independently exercised; whole-model closure pending.']}
if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-ctc-task-init-verification.json').write_text(json.dumps(r,indent=2)+'\n');print(r['decoded_cases'])
