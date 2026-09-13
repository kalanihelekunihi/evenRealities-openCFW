# SPDX-License-Identifier: MIT
import json,re,subprocess
from itertools import product
from build_gx8002_audio_fftvad_w import build,ROOT,IMAGE_SHA,sha,Elf32
from verify_gx8002_memcpy_source import decode

def execute(code,entry,packed,word):
    r={f'r{i}':0x98760000+i for i in range(32)};r.update(r0=packed,r14=0x20070000);initial=r.copy();stack={};trace=[];pc=entry
    for _ in range(40):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')]
        if op=='rts':
            if any(r[f'r{i}']!=initial[f'r{i}'] for i in (*range(4,12),14,15,16,17)):raise ValueError('Weights ABI')
            return r['r0'],trace,word
        elif op in ('movi','movih'):r[p[0]]=int(p[1],0)<<(16 if op=='movih' else 0)
        elif op in ('addi','subi'):
            a=r[p[1]] if len(p)==3 else r[p[0]];n=int(p[-1],0);r[p[0]]=a+n if op=='addi' else a-n
        elif op=='bseti':r[p[0]]|=1<<int(p[-1],0)
        elif op=='ins':
            hi,lo=int(p[2]),int(p[3]);mask=((1<<(hi-lo+1))-1)<<lo;r[p[0]]=(r[p[0]]&~mask)|((r[p[1]]<<lo)&mask)
        elif op in ('st.w','ld.w','ld.b'):
            m=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args)
            if not m:raise ValueError('Weights operand')
            reg,base,off=m.groups();a=r[base]+int(off,0)
            if a==0x2006fffc and op=='st.w':
                for i in range(4):stack[a+i]=(r[reg]>>(i*8))&255
            elif a in stack and op=='ld.b':r[reg]=stack[a]
            elif a==0xa0a00158 and op=='ld.w':r[reg]=word;trace.append(('read',a,word))
            elif a==0xa0a00158 and op=='st.w':word=r[reg];trace.append(('write',a,word))
            else:raise ValueError('Weights unexpected access')
        else:raise ValueError('Weights instruction '+op)
        pc+=width
    raise ValueError('Weights bound')

def verify():
    candidate=build();wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';e=Elf32(wrapper.read_bytes(),str(wrapper))
    if sha(e.contents(next(s for s in e.sections if s['name']=='.data')))!=IMAGE_SHA:raise ValueError('Weights stock identity')
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    old=decode(subprocess.check_output([pre,'-D','--start-address=0xdb80','--stop-address=0xdbbc',str(wrapper)],text=True));new=decode((ROOT/'build/gx8002-audio-fftvad-w/gain.disassembly.txt').read_text());cases=0
    for index,value,padding,seed in product(range(3),range(256),(0,255),(0,0xffffffff,0xa5a5a5a5)):
        values=[0x12,0x34,0x56];values[index]=value;packed=sum(v<<(8*i) for i,v in enumerate(values))|(padding<<24);word=seed;trace=[]
        for i,v in enumerate(values):
            low=8+4*i;trace.append(('read',0xa0a00158,word));word=(word&~(15<<low))|((v&15)<<low);trace.append(('write',0xa0a00158,word))
        wanted=(0,trace,word)
        if execute(old,0xdb80,packed,seed)!=wanted or execute(new,0x102045f4,packed,seed)!=wanted:raise ValueError('Weights oracle')
        cases+=1
    return {'candidate':candidate,'decoded_cases':cases,'source_admitted':False,'hardware_qualified':False,'limits':['All256 values in each byte with other bytes fixed, padding independence, word RMW ordering and stack ABI checked. Physical FFTVAD weighting unqualified.']}

if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-audio-fftvad-w-verification.json').write_text(json.dumps(r,indent=2)+'\n');print(r['decoded_cases'])
