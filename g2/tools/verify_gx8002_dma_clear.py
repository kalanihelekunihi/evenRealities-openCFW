# SPDX-License-Identifier: MIT
import json,re,subprocess
from itertools import product
from build_gx8002_dma_clear import build,ROOT,IMAGE_SHA,sha,Elf32
from verify_gx8002_memcpy_source import decode


def execute(code,pc,channel,device):
    r={f'r{i}':0x98760000+i for i in range(32)};r.update(r0=channel);initial=r.copy();writes=[]
    for _ in range(10):
        op,args,width=code[pc];p=[x.strip() for x in args.split(',')]
        if op in ('lrw','movi'):r[p[0]]=int(p[1],0)
        elif op in ('lsli','lsl','addu'):
            a=r[p[-2]] if len(p)==3 else r[p[0]];b=r[p[-1]] if p[-1] in r else int(p[-1],0)
            r[p[0]]=(a<<b if op in ('lsli','lsl') else a+b)&0xffffffff
        elif op in ('st.w','str.w','ld.w'):
            m=re.fullmatch(r'(r\d+), \((r\d+), (0x[0-9a-f]+|r\d+ << 2)\)',args)
            if not m:raise ValueError('Callback store syntax')
            reg,base,offset=m.groups();off=r[offset.split()[0]]<<2 if '<<' in offset else int(offset,0)
            address=(r[base]+off)&0xffffffff
            if op=='ld.w':
                if address!=0x2002e93c:raise ValueError('Clear state read')
                r[reg]=device;writes.append(('read',address,device))
            else:writes.append(('write',address,r[reg]))
        elif op=='rts':
            if any(r[f'r{i}']!=initial[f'r{i}'] for i in (*range(4,12),14,15,16,17)):raise ValueError('Callback ABI')
            return writes
        else:raise ValueError('Callback instruction '+op)
        pc+=width
    raise ValueError('Callback execution bound')


def verify():
    candidate=build();wrapper=ROOT/'build/gx8002-board/padmux-get-stock.elf';elf=Elf32(wrapper.read_bytes(),str(wrapper))
    if sha(elf.contents(next(s for s in elf.sections if s['name']=='.data')))!=IMAGE_SHA:raise ValueError('Stock identity')
    pre=str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump')
    old=decode(subprocess.check_output([pre,'-D','--start-address=0xcd90','--stop-address=0xcdb4',str(wrapper)],text=True))
    new=decode((ROOT/'build/gx8002-dma-clear/clear.disassembly.txt').read_text());cases=0
    for channel,device in product(range(32),(0,0xa1000000,0xfffffe00)):
        wanted=[('read',0x2002e93c,device)]+[('write',(device+offset)&0xffffffff,1<<channel) for offset in (0x338,0x340,0x348,0x350,0x358)]
        if execute(old,0xcd90,channel,device)!=wanted or execute(new,0x10203804,channel,device)!=wanted:raise ValueError('Clear ordered effects')
        cases+=1
    return {'candidate':candidate,'decoded_cases':cases,'source_admitted':False,'hardware_qualified':False,'limits':['Shifts 0..31 are arithmetic checks; initialized hardware channel domain is 0/1. No physical status register effects proved.']}

if __name__=='__main__':
    result=verify();(ROOT/'docs/research/gx8002-dma-clear-verification.json').write_text(json.dumps(result,indent=2)+'\n');print('Clear cases:',result['decoded_cases'])
