# SPDX-License-Identifier: MIT
import json,re,subprocess
from itertools import product
from build_gx8002_audio_fftvad_chipping import build,ROOT,IMAGE_SHA,sha,Elf32
from verify_gx8002_memcpy_source import decode

def execute(code,entry,packed,word):
    r={f'r{i}':0x98760000+i for i in range(32)};r.update(r0=packed&0xffffffff,r1=packed>>32,r14=0x20070000);initial=r.copy();word={0xa0a00198:word,0xa0a0019c:word^0xffffffff};stack={};trace=[];pc=entry
    for _ in range(40):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')]
        if op=='rts':
            if any(r[f'r{i}']!=initial[f'r{i}'] for i in (*range(4,12),14,15,16,17)):raise ValueError('Weights ABI')
            return r['r0'],trace,word
        elif op in ('movi','movih','lrw'):r[p[0]]=int(p[1],0)<<(16 if op=='movih' else 0)
        elif op in ('addi','subi'):
            a=r[p[1]] if len(p)==3 else r[p[0]];n=int(p[-1],0);r[p[0]]=a+n if op=='addi' else a-n
        elif op=='bseti':r[p[0]]|=1<<int(p[-1],0)
        elif op=='zexth':r[p[0]]=r[p[1]]&65535
        elif op=='ins':
            hi,lo=int(p[2]),int(p[3]);mask=((1<<(hi-lo+1))-1)<<lo;r[p[0]]=(r[p[0]]&~mask)|((r[p[1]]<<lo)&mask)
        elif op in ('st.w','ld.w','ld.h'):
            m=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args)
            if not m:raise ValueError('Weights operand')
            reg,base,off=m.groups();a=r[base]+int(off,0)
            if a in (0x2006fff8,0x2006fffc) and op=='st.w':
                for i in range(4):stack[a+i]=(r[reg]>>(i*8))&255
            elif a in stack and op=='ld.h':r[reg]=stack[a]|(stack[a+1]<<8)
            elif a in word and op=='ld.w':r[reg]=word[a];trace.append(('read',a,word[a]))
            elif a in word and op=='st.w':word[a]=r[reg];trace.append(('write',a,word[a]))
            else:raise ValueError('Weights unexpected access')
        else:raise ValueError('Weights instruction '+op)
        pc+=width
    raise ValueError('Weights bound')

def verify():
    candidate=build();wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';e=Elf32(wrapper.read_bytes(),str(wrapper))
    if sha(e.contents(next(s for s in e.sections if s['name']=='.data')))!=IMAGE_SHA:raise ValueError('Weights stock identity')
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    old=decode(subprocess.check_output([pre,'-D','--start-address=0xdcb8','--stop-address=0xdd08',str(wrapper)],text=True));new=decode((ROOT/'build/gx8002-audio-fftvad-chipping/gain.disassembly.txt').read_text());cases=0
    for index,value,seed in product(range(4),(0,1,255,256,32767,32768,65534,65535),(0,0xffffffff,0xa5a5a5a5)):
        values=[0x1234,0x5678,0x9abc,0xdef0];values[index]=value;packed=sum(v<<(16*i) for i,v in enumerate(values));word={0xa0a00198:seed,0xa0a0019c:seed^0xffffffff};trace=[]
        for i,v in enumerate(values):
            address=0xa0a00198+(i//2)*4;low=(i%2)*16;trace.append(('read',address,word[address]));word[address]=(word[address]&~(65535<<low))|(v<<low);trace.append(('write',address,word[address]))
        wanted=(0,trace,word)
        if execute(old,0xdcb8,packed,seed)!=wanted or execute(new,0x1020472c,packed,seed)!=wanted:raise ValueError('Chipping oracle')
        cases+=1
    return {'candidate':candidate,'decoded_cases':cases,'source_admitted':False,'hardware_qualified':False,'limits':['Halfword boundaries in each field, independent packed words, ordered word RMW and eight-byte stack ABI checked. Physical FFTVAD clipping unqualified.']}

if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-audio-fftvad-chipping-verification.json').write_text(json.dumps(r,indent=2)+'\n');print(r['decoded_cases'])
