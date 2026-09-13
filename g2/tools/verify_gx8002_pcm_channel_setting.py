# SPDX-License-Identifier: MIT
"""Decode PCM parameter validation and ordered register programming."""
import json,re,subprocess
from itertools import product
from build_gx8002_pcm_channel_setting_candidate import build,ROOT,IMAGE,IMAGE_SHA,sha,Elf32,OFFSET,ADDRESS,SIZE
from verify_gx8002_memcpy_source import decode


def execute(code,entry,channel,left,right,size,control):
    r={f'r{i}':0x98760000+i for i in range(32)};r.update(r0=channel,r1=left,r2=right,r3=size,r14=0x20070000)
    initial=r.copy();pc=entry;trace=[]
    for _ in range(40):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')];jump=None
        if op=='rts':
            if any(r[f'r{i}']!=initial[f'r{i}'] for i in (*range(4,12),14,15,16,17)):raise ValueError('PCM setting ABI')
            return r['r0'],trace
        elif op in ('mov','movi','movih'):r[p[0]]=r[p[1]] if p[1] in r else int(p[1],0)<<(16 if op=='movih' else 0)
        elif op in ('or','andi','addu','addi','subi','lsli','lsl','mult'):
            a=r[p[-2]] if len(p)==3 else r[p[0]];b=r[p[-1]] if p[-1] in r else int(p[-1],0)
            r[p[0]]=(a|b if op=='or' else a&b if op=='andi' else a+b if op in ('addu','addi') else a-b if op=='subi' else a*b if op=='mult' else a<<b)&0xffffffff
        elif op=='mula.32.l':r[p[0]]=(r[p[0]]+r[p[1]]*r[p[2]])&0xffffffff
        elif op=='bseti':r[p[0]]|=1<<int(p[1],0)
        elif op=='bnez':
            if r[p[0]]:jump=int(p[1],0)
        elif op=='br':jump=int(args,0)
        elif op in ('ld.w','st.w'):
            match=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+)\)',args)
            if not match:raise ValueError('PCM setting memory operand')
            reg,base,off=match.groups();address=(r[base]+int(off,0))&0xffffffff
            if op=='ld.w':
                if address!=initial['r14']:raise ValueError('PCM setting stack argument')
                r[reg]=control
            else:trace.append(('write',address,r[reg]))
        else:raise ValueError('PCM setting instruction '+op)
        pc=jump if jump is not None else pc+width
    raise ValueError('PCM setting bound')


def verify():
    candidate=build();wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(wrapper.read_bytes(),str(wrapper))
    if sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))!=IMAGE_SHA:raise ValueError('PCM stock identity')
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    old=decode(subprocess.check_output([pre,'-D','--start-address='+hex(OFFSET),'--stop-address='+hex(OFFSET+SIZE),str(wrapper)],text=True))
    new=decode((ROOT/'build/gx8002-board/pcm-channel-setting-candidate.disassembly.txt').read_text());cases=0
    for channel,left,right,size,control in product((0,1,2,20),[base+i for base in (0x20050000,0xfffffff8) for i in range(8)],range(0x20060000,0x20060008),(0,1,127,128,129,0xffffff80,0xffffffff),(0,0x12345678,0xffffffff)):
        invalid=bool(size%128 or left%8 or right%8);base=0xa0a00000+channel*36
        wanted=(0xffffffff,[]) if invalid else (0,[('write',base+0x110,control),('write',base+0x114,left),('write',base+0x11c,right),('write',base+0x120,size),('write',0xa0a00104,1<<(channel+11))])
        if execute(old,OFFSET,channel,left,right,size,control)!=wanted or execute(new,ADDRESS,channel,left,right,size,control)!=wanted:raise ValueError('PCM setting independent oracle')
        cases+=1
    return {'candidate':candidate,'decoded_cases':cases,'source_admitted':False,'hardware_qualified':False,
        'limits':['Alignment rejections and accepted ordered MMIO checked with defined shifts, including arithmetic boundary channel20. Hardware channel validity remains a caller contract; no physical buffer/DMA delivery qualification.']}

if __name__=='__main__':
    r=verify();(ROOT/'docs/research/gx8002-pcm-channel-setting-verification.json').write_text(json.dumps(r,indent=2)+'\n');print('PCM setting cases:',r['decoded_cases'])
